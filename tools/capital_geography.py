#!/usr/bin/env python3
"""Project sourced capital coordinates onto the local EU5 map for review."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from io import StringIO
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
COORDINATES = ROOT / "docs/world_1ad/capital_coordinates.csv"
ANCHORS = ROOT / "docs/world_1ad/map_projection_anchors.csv"
MAP_COORDINATES = ROOT / "docs/vanilla_symbols/location_coordinates.json"
OUTPUT = ROOT / "docs/world_1ad/capital_geo_candidates.csv"
LOCATION_LOC = (
    "game/main_menu/localization/english/location_names/location_names_l_english.yml"
)
LOC_LINE = re.compile(r'^\s*([\w.-]+):\s*"([^"]+)"')
REQUIRED_COORDINATES = ("tag", "latitude", "longitude", "source", "confidence")
REQUIRED_ANCHORS = ("location", "latitude", "longitude", "source")


def game_dir() -> Path:
    return Path(json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))["game_dir"])


def rows(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path.relative_to(ROOT)} has an unexpected header")
        return list(reader)


def location_names() -> dict[str, str]:
    result: dict[str, str] = {}
    path = game_dir() / LOCATION_LOC
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        match = LOC_LINE.match(line)
        if match:
            result[match.group(1)] = match.group(2)
    return result


def projection(map_locations: dict[str, dict[str, float]]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    anchors = rows(ANCHORS, REQUIRED_ANCHORS)
    longitudes = np.asarray([float(row["longitude"]) for row in anchors])
    latitudes = np.asarray([float(row["latitude"]) for row in anchors])
    try:
        xs = np.asarray([map_locations[row["location"]]["x"] for row in anchors])
        ys = np.asarray([map_locations[row["location"]]["y"] for row in anchors])
    except KeyError as exc:
        raise ValueError(f"projection anchor has no local map coordinate: {exc}") from exc
    matrix = np.column_stack((longitudes, latitudes, np.ones(len(anchors))))
    x_model = np.linalg.lstsq(matrix, xs, rcond=None)[0]
    y_model = np.linalg.lstsq(matrix, ys, rcond=None)[0]
    x_residuals = xs - matrix @ x_model
    y_residuals = ys - matrix @ y_model
    residual = float(np.sqrt(np.mean(x_residuals**2 + y_residuals**2)))
    return x_model, y_model, latitudes, longitudes, x_residuals, y_residuals, residual


def project(
    latitude: float,
    longitude: float,
    x_model: np.ndarray,
    y_model: np.ndarray,
    anchor_latitudes: np.ndarray,
    anchor_longitudes: np.ndarray,
    x_residuals: np.ndarray,
    y_residuals: np.ndarray,
) -> tuple[float, float]:
    """Fit an affine world map, then locally correct its residuals by IDW."""
    point = np.asarray((longitude, latitude, 1.0))
    x = float(point @ x_model)
    y = float(point @ y_model)
    longitude_distance = (anchor_longitudes - longitude) * np.cos(
        np.radians((anchor_latitudes + latitude) / 2)
    )
    distances = np.hypot(anchor_latitudes - latitude, longitude_distance)
    nearest = np.argsort(distances)[: min(6, len(distances))]
    weights = 1.0 / np.maximum(distances[nearest], 0.05) ** 2
    x += float(np.average(x_residuals[nearest], weights=weights))
    y += float(np.average(y_residuals[nearest], weights=weights))
    return x, y


def rendered() -> tuple[str, list[str]]:
    roster = rows(ROSTER, ("tag", "name", "tier", "kind", "region", "historical_capital", "map_capital", "source", "confidence", "status"))
    roster_by_tag = {row["tag"]: row for row in roster}
    source_rows = rows(COORDINATES, REQUIRED_COORDINATES)
    map_payload = json.loads(MAP_COORDINATES.read_text(encoding="utf-8"))
    map_locations = map_payload["locations"]
    names = location_names()
    x_model, y_model, anchor_latitudes, anchor_longitudes, x_residuals, y_residuals, residual = projection(map_locations)
    image_width = float(map_payload["image_size"]["width"])
    location_items = [
        (key, float(value["x"]), float(value["y"]))
        for key, value in map_locations.items()
    ]
    failures: list[str] = []
    output_rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in source_rows:
        tag = row["tag"]
        if tag not in roster_by_tag:
            failures.append(f"coordinate tag {tag} is not in the roster")
            continue
        if tag in seen:
            failures.append(f"duplicate coordinate tag {tag}")
            continue
        seen.add(tag)
        try:
            latitude = float(row["latitude"])
            longitude = float(row["longitude"])
        except ValueError:
            failures.append(f"{tag}: latitude/longitude must be numeric")
            continue
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            failures.append(f"{tag}: coordinate outside geographic bounds")
            continue
        projected_x, projected_y = project(
            latitude,
            longitude,
            x_model,
            y_model,
            anchor_latitudes,
            anchor_longitudes,
            x_residuals,
            y_residuals,
        )
        projected_x %= image_width
        nearest = sorted(
            location_items,
            key=lambda item: (item[1] - projected_x) ** 2 + (item[2] - projected_y) ** 2,
        )[:5]
        display = "; ".join(
            f"{key} ({names.get(key, key)}; {math.hypot(x - projected_x, y - projected_y):.1f}px)"
            for key, x, y in nearest
        )
        roster_row = roster_by_tag[tag]
        output_rows.append(
            {
                "tag": tag,
                "historical_capital": roster_row["historical_capital"],
                "latitude": f"{latitude:.5f}",
                "longitude": f"{longitude:.5f}",
                "source": row["source"],
                "confidence": row["confidence"],
                "current_map_capital": roster_row["map_capital"],
                "predicted_x": f"{projected_x:.1f}",
                "predicted_y": f"{projected_y:.1f}",
                "nearest_locations": display,
            }
        )
    fieldnames = (
        "tag", "historical_capital", "latitude", "longitude", "source", "confidence",
        "current_map_capital", "predicted_x", "predicted_y", "nearest_locations",
    )
    stream = StringIO(newline="")
    stream.write(f"# Projection RMSE: {residual:.1f}px; anchors are in map_projection_anchors.csv\n")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(output_rows)
    return stream.getvalue(), failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    expected, failures = rendered()
    if args.write:
        if failures:
            print("capital_geography: FAIL", file=sys.stderr)
            print("\n".join(f"  - {failure}" for failure in failures), file=sys.stderr)
            return 1
        OUTPUT.write_text(expected, encoding="utf-8-sig", newline="")
        print(f"capital_geography: wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file():
        failures.append(f"missing generated report {OUTPUT.relative_to(ROOT)}")
    elif OUTPUT.read_text(encoding="utf-8-sig") != expected:
        failures.append("geographic candidate report is stale; run tools/capital_geography.py --write")
    if failures:
        print("capital_geography: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print(f"capital_geography: PASS ({len(rows(COORDINATES, REQUIRED_COORDINATES))} sourced coordinates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

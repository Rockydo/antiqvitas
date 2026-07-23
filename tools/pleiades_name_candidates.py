#!/usr/bin/env python3
"""Queue conservative AD 1 Pleiades location-name candidates for review.

The report is deliberately not an automatic naming layer.  It only identifies
precisely located Pleiades settlement points alive in AD 1 that project to an
installed location at a very short distance.  A human-agent evidence review
must still choose a form, language adapter, and explicit ledger row.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import sys
from collections import defaultdict
from io import StringIO
from pathlib import Path

import capital_geography

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".cache/pleiades/pleiades-places-latest.csv.gz"
MAP_COORDINATES = ROOT / "docs/vanilla_symbols/location_coordinates.json"
CURRENT_NAMES = ROOT / "docs/m4/dynamic_location_names.csv"
OUTPUT = ROOT / "docs/m4/pleiades_name_candidates.csv"
MAX_DISTANCE_PX = 3.25
GRID_SIZE_PX = 10.0


def current_locations() -> set[str]:
    with CURRENT_NAMES.open(encoding="utf-8-sig", newline="") as handle:
        return {row["location"] for row in csv.DictReader(handle)}


def ad_one(row: dict[str, str]) -> bool:
    try:
        return float(row["minDate"]) <= 1 <= float(row["maxDate"])
    except ValueError:
        return False


def render() -> str:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"missing cached Pleiades snapshot: {SOURCE.relative_to(ROOT)}")
    payload = json.loads(MAP_COORDINATES.read_text(encoding="utf-8"))
    locations = payload["locations"]
    width = float(payload["image_size"]["width"])
    location_items = [(key, float(value["x"]), float(value["y"])) for key, value in locations.items()]
    grid: dict[tuple[int, int], list[tuple[str, float, float]]] = defaultdict(list)
    for item in location_items:
        grid[(int(item[1] // GRID_SIZE_PX), int(item[2] // GRID_SIZE_PX))].append(item)
    projection = capital_geography.projection(locations)
    installed_names = capital_geography.location_names()
    existing = current_locations()
    candidates: list[dict[str, str]] = []
    with gzip.open(SOURCE, "rt", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("locationPrecision") != "precise" or "settlement" not in row.get("featureTypes", ""):
                continue
            if not row.get("reprLat") or not row.get("reprLong") or not ad_one(row):
                continue
            latitude, longitude = float(row["reprLat"]), float(row["reprLong"])
            x, y = capital_geography.project(latitude, longitude, *projection[:6])
            x %= width
            cell_x, cell_y = int(x // GRID_SIZE_PX), int(y // GRID_SIZE_PX)
            nearby = [
                item
                for grid_x in range(cell_x - 1, cell_x + 2)
                for grid_y in range(cell_y - 1, cell_y + 2)
                for item in grid.get((grid_x, grid_y), [])
            ]
            if not nearby:
                continue
            key, local_x, local_y = min(nearby, key=lambda item: (item[1] - x) ** 2 + (item[2] - y) ** 2)
            distance = math.hypot(local_x - x, local_y - y)
            if distance > MAX_DISTANCE_PX or key in existing:
                continue
            candidates.append(
                {
                    "location": key,
                    "vanilla_name": installed_names.get(key, key),
                    "pleiades_title": row["title"],
                    "pleiades_id": row["id"],
                    "feature_types": row["featureTypes"],
                    "min_date": row["minDate"],
                    "max_date": row["maxDate"],
                    "latitude": f"{latitude:.5f}",
                    "longitude": f"{longitude:.5f}",
                    "offset_px": f"{distance:.2f}",
                    "source": f"PLE:{row['id']}",
                }
            )
    candidates.sort(key=lambda row: (row["location"], float(row["offset_px"]), row["pleiades_id"]))
    stream = StringIO(newline="")
    stream.write(
        "# Review queue only: no row is a game-visible name until it is source-reviewed and added to dynamic_location_name_overrides.csv.\n"
    )
    writer = csv.DictWriter(
        stream,
        fieldnames=("location", "vanilla_name", "pleiades_title", "pleiades_id", "feature_types", "min_date", "max_date", "latitude", "longitude", "offset_px", "source"),
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(candidates)
    return stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        expected = render()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"pleiades_name_candidates: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8-sig", newline="")
        print(f"pleiades_name_candidates: wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != expected:
        print(f"pleiades_name_candidates: FAIL\n  - stale or missing {OUTPUT.relative_to(ROOT)}")
        return 1
    count = max(0, len(expected.splitlines()) - 2)
    print(f"pleiades_name_candidates: PASS ({count} conservative review candidates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate the remote, explicitly provisional Pleiades naming layer.

This is deliberately broader than the normal Tier-2 pass, not stronger
evidence: a precise, AD 1 Pleiades settlement can label a nearby installed
city field when its projected point is 3.25--6.00 pixels away.  Every output
row records that it is a remote map proxy, and direct, bounded Tier-2, and
wide Tier-2 ledgers all retain precedence.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import re
import sys
from collections import defaultdict
from io import StringIO
from pathlib import Path

import capital_geography
from generate_m4_tier2_names import (
    CURATED,
    QUALIFIED,
    CULTURES,
    ENGINE_LOCATIONS,
    HEADER,
    capital_locations,
    csv_rows,
    pop_cultures,
)
from generate_m4_tier2_wide_names import normalized, wide_title

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".cache/pleiades/pleiades-places-latest.csv.gz"
MAP_COORDINATES = ROOT / "docs/vanilla_symbols/location_coordinates.json"
TIER2 = ROOT / "docs/m4/tier2_location_name_overrides.csv"
TIER2_WIDE = ROOT / "docs/m4/tier2_wide_location_name_overrides.csv"
OUTPUT = ROOT / "docs/m4/tier2_remote_location_name_overrides.csv"
MIN_OFFSET_PX = 3.25
MAX_OFFSET_PX = 6.00
GRID_SIZE_PX = 10.0
SEARCH_RADIUS_CELLS = 1
LABEL = "Remote"
SOURCE_SUFFIX = "T2R"
EXTRA_LEDGER_PATHS: tuple[Path, ...] = ()


def ledger_locations(path: Path) -> set[str]:
    rows = csv_rows(path)
    if not rows or tuple(rows[0]) != HEADER:
        raise ValueError(f"{path.relative_to(ROOT)} must use header {','.join(HEADER)}")
    return {row["location"].strip() for row in rows}


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
    grid: dict[tuple[int, int], list[tuple[str, float, float]]] = defaultdict(list)
    for key, value in locations.items():
        x, y = float(value["x"]), float(value["y"])
        grid[(int(x // GRID_SIZE_PX), int(y // GRID_SIZE_PX))].append((key, x, y))
    installed = set(json.loads(ENGINE_LOCATIONS.read_text(encoding="utf-8-sig")))
    installed_names = capital_geography.location_names()
    cultures = {row["key"] for row in csv_rows(CULTURES)}
    excluded = capital_locations() | ledger_locations(CURATED) | ledger_locations(QUALIFIED) | ledger_locations(TIER2) | ledger_locations(TIER2_WIDE)
    for path in EXTRA_LEDGER_PATHS:
        excluded.update(ledger_locations(path))
    population_cultures = pop_cultures()
    projection = capital_geography.projection(locations)
    candidates: dict[str, list[tuple[float, dict[str, str]]]] = defaultdict(list)
    with gzip.open(SOURCE, "rt", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("locationPrecision") != "precise" or "settlement" not in row.get("featureTypes", "") or not ad_one(row):
                continue
            if not row.get("reprLat") or not row.get("reprLong") or not wide_title(row.get("title", "")):
                continue
            latitude, longitude = float(row["reprLat"]), float(row["reprLong"])
            x, y = capital_geography.project(latitude, longitude, *projection[:6])
            x %= width
            cell_x, cell_y = int(x // GRID_SIZE_PX), int(y // GRID_SIZE_PX)
            nearby = [
                item
                for grid_x in range(cell_x - SEARCH_RADIUS_CELLS, cell_x + SEARCH_RADIUS_CELLS + 1)
                for grid_y in range(cell_y - SEARCH_RADIUS_CELLS, cell_y + SEARCH_RADIUS_CELLS + 1)
                for item in grid.get((grid_x, grid_y), [])
            ]
            if not nearby:
                continue
            location, local_x, local_y = min(nearby, key=lambda item: (item[1] - x) ** 2 + (item[2] - y) ** 2)
            distance = math.hypot(local_x - x, local_y - y)
            culture = population_cultures.get(location)
            title = row["title"].strip()
            if (
                location not in installed
                or location in excluded
                or not MIN_OFFSET_PX < distance <= MAX_OFFSET_PX
                or not culture or culture not in cultures
                or normalized(title) == normalized(installed_names.get(location, location))
            ):
                continue
            candidates[location].append((distance, row))
    output: list[dict[str, str]] = []
    for location, rows in candidates.items():
        distance, row = min(rows, key=lambda item: (item[0], item[1]["id"]))
        output.append(
            {
                "location": location,
                "culture": population_cultures[location],
                "historical_name": row["title"].strip(),
                "source": f"PLE:{row['id']};{SOURCE_SUFFIX}",
                "confidence": "tier2",
                "note": (
                    f"{LABEL} Tier-2 AD 1 Pleiades settlement adapter; nearest installed city field "
                    f"at {distance:.2f}px; {LABEL.casefold()} lower-confidence map proxy."
                ),
            }
        )
    output.sort(key=lambda row: row["location"])
    if not output:
        raise ValueError(f"{LABEL.casefold()} Tier-2 selector produced no adapters")
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=HEADER, lineterminator="\n")
    writer.writeheader()
    writer.writerows(output)
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
        print(f"m4_tier2_remote_names: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8-sig", newline="")
        print(f"m4_tier2_remote_names: wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != expected:
        print(f"m4_tier2_remote_names: FAIL\n  - stale or missing {OUTPUT.relative_to(ROOT)}")
        return 1
    print(f"m4_tier2_remote_names: PASS ({max(0, len(expected.splitlines()) - 1)} {LABEL.casefold()} lower-confidence adapters)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

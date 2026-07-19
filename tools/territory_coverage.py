#!/usr/bin/env python3
"""Verify that every ownable AD 1 location is claimed or intentionally empty."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from ownership_map import descendants, vanilla_owned_locations

ROOT = Path(__file__).resolve().parents[1]
RESOLVED = ROOT / "docs/world_1ad/ownership_resolved.csv"
EMPTY = ROOT / "docs/world_1ad/intentional_empty_areas.csv"
HIERARCHY = ROOT / "docs/vanilla_symbols/geography_hierarchy.json"
LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
FIELDS = ("geography", "source", "note")


def read_empty_rows() -> list[dict[str, str]]:
    with EMPTY.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or tuple(rows[0]) != FIELDS:
        raise ValueError("intentional_empty_areas.csv has an invalid header or no rows")
    for row in rows:
        if not all(row.get(field, "").strip() for field in FIELDS):
            raise ValueError("intentional_empty_areas.csv has a blank required field")
    return rows


def main() -> int:
    try:
        locations = set(json.loads(LOCATIONS.read_text(encoding="utf-8-sig")))
        hierarchy = json.loads(HIERARCHY.read_text(encoding="utf-8-sig"))
        ownable = vanilla_owned_locations(locations)
        with RESOLVED.open(encoding="utf-8-sig", newline="") as handle:
            assigned = {
                row["location"]
                for row in csv.DictReader(line for line in handle if not line.startswith("#"))
            }
        intentional: set[str] = set()
        for row in read_empty_rows():
            intentional.update(descendants(row["geography"], hierarchy, locations) & ownable)
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"territory_coverage: FAIL\n  - {exc}")
        return 1

    covered = assigned & ownable
    overlap = covered & intentional
    missing = ownable - covered - intentional
    if overlap or missing:
        print("territory_coverage: FAIL")
        if overlap:
            print("  - intentionally empty locations assigned: " + ", ".join(sorted(overlap)))
        if missing:
            sample = ", ".join(sorted(missing)[:30])
            suffix = " ..." if len(missing) > 30 else ""
            print(f"  - {len(missing)} unassigned ownable locations: {sample}{suffix}")
        return 1
    print(
        "territory_coverage: PASS "
        f"({len(ownable)} ownable; {len(covered)} assigned; {len(intentional)} intentional empty)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

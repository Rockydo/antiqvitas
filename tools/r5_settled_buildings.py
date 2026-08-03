#!/usr/bin/env python3
"""Guarantee a modest four-placement opening floor for every settled minor."""

from __future__ import annotations

import argparse
import csv
import io
import sys
from collections import Counter, defaultdict
from pathlib import Path

from m5_regional_buildings import (
    FAMILY_CULTURE_GROUP_GATES,
    FAMILY_EXACT_TAG_GATES,
    expanded_seed_rows,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/m5/settled_opening_floor.csv"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
SPECIALS = ROOT / "docs/m5/special_buildings.csv"
FORTS = ROOT / "docs/m7/forts.csv"
FAMILIES = ROOT / "docs/m5/regional_building_families.csv"
FIELDS = ("key", "location", "building", "level", "source", "confidence", "note")
FLOOR_BUILDINGS = (
    "antq_reg_pottery_kiln",
    "antq_reg_grain_mill",
    "antq_reg_granary",
    "antq_reg_loomweight_weavery",
    "antq_reg_copper_smithy",
)


def read(path: Path, comments: bool = False) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        lines = (line for line in handle if not comments or not line.startswith("#"))
        return list(csv.DictReader(lines))


def floor_rows() -> list[dict[str, str]]:
    roster = read(ROSTER)
    ownership = read(OWNERSHIP, comments=True)
    owned: dict[str, list[str]] = defaultdict(list)
    owner: dict[str, str] = {}
    for row in ownership:
        owned[row["tag"]].append(row["location"])
        owner[row["location"]] = row["tag"]
    counts: Counter[str] = Counter()
    pairs: set[tuple[str, str]] = set()
    for row in expanded_seed_rows():
        tag = owner.get(row["location"])
        if tag:
            counts[tag] += 1
            pairs.add((row["location"], row["family"]))
    for path in (SPECIALS, FORTS):
        for row in read(path):
            tag = owner.get(row["location"])
            if tag:
                counts[tag] += 1
                pairs.add((row["location"], row["building"]))

    result: list[dict[str, str]] = []
    for polity in sorted(roster, key=lambda row: row["tag"]):
        tag = polity["tag"]
        if polity["kind"] == "sop" or tag == "ROM" or counts[tag] >= 4:
            continue
        locations = sorted(set(owned[tag]))
        capital = polity["map_capital"]
        if capital in locations:
            locations.remove(capital)
            locations.insert(0, capital)
        if not locations:
            raise ValueError(f"settled polity {tag} has no owned location")
        needed = 4 - counts[tag]
        added = 0
        candidate = 0
        while added < needed:
            building = FLOOR_BUILDINGS[candidate % len(FLOOR_BUILDINGS)]
            location = locations[candidate % len(locations)]
            candidate += 1
            if (location, building) in pairs:
                if candidate > len(locations) * len(FLOOR_BUILDINGS) * 2:
                    raise ValueError(f"cannot place settled opening floor for {tag}")
                continue
            pairs.add((location, building))
            added += 1
            result.append({
                "key": f"r5_settled_{tag.lower()}_{added}",
                "location": location,
                "building": building,
                "level": "1",
                "source": "P12.1;P12.3;P13",
                "confidence": "contested",
                "note": "Balanced settled-minor craft and storage floor; not an excavated workshop claim.",
            })
    return result


def render(rows: list[dict[str, str]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def validate(rows: list[dict[str, str]]) -> None:
    family_keys = {row["key"] for row in read(FAMILIES)}
    if not set(FLOOR_BUILDINGS) <= family_keys:
        raise ValueError("settled opening floor references an unknown regional family")
    if any(key in FAMILY_EXACT_TAG_GATES or key in FAMILY_CULTURE_GROUP_GATES for key in FLOOR_BUILDINGS):
        raise ValueError("settled opening floor may use only universal ancient families")
    if len({(row["location"], row["building"]) for row in rows}) != len(rows):
        raise ValueError("settled opening floor repeats a building/location pair")
    # Re-run the same ownership count with generated rows included.
    owner = {row["location"]: row["tag"] for row in read(OWNERSHIP, comments=True)}
    counts: Counter[str] = Counter()
    for row in expanded_seed_rows():
        counts[owner.get(row["location"], "")] += 1
    for path in (SPECIALS, FORTS):
        for row in read(path):
            counts[owner.get(row["location"], "")] += 1
    for row in rows:
        counts[owner.get(row["location"], "")] += 1
    deficient = [
        row["tag"] for row in read(ROSTER)
        if row["kind"] != "sop" and row["tag"] != "ROM" and counts[row["tag"]] < 4
    ]
    if deficient:
        raise ValueError(f"settled polities below four opening placements: {deficient}")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        rows = floor_rows()
        content = render(rows)
        if args.write:
            OUTPUT.write_text(content, encoding="utf-8-sig", newline="\n")
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != content:
            raise ValueError(f"stale or missing {OUTPUT.relative_to(ROOT)}")
        validate(rows)
    except (OSError, ValueError) as exc:
        print(f"r5_settled_buildings: FAIL\n  - {exc}")
        return 1
    print(f"r5_settled_buildings: PASS ({len(rows)} floor placements; every settled non-Roman polity >=4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

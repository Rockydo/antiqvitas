#!/usr/bin/env python3
"""Render/check population geography, culture, city, and ranking cross-tables."""

from __future__ import annotations

import argparse
import csv
import io
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from generate_start_mirror import (
    load_population_plan,
    population_city_targets,
    population_geographic_allocations,
    population_location_overrides,
)
from popcheck import COMPATIBILITY_POP_FILE, POP_FILE, parse_records

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/m4/population_audit.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
FIELDS = (
    "section",
    "key",
    "location",
    "parent",
    "size_thousands",
    "share_percent",
    "source",
    "confidence",
    "note",
)


def csv_rows(path: Path, *, comments: bool = False) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        lines = (line for line in handle if not comments or not line.startswith("#"))
        return list(csv.DictReader(lines))


def percentage(value: Decimal, total: Decimal) -> str:
    return f"{value * Decimal(100) / total:.3f}"


def render() -> str:
    roster = {row["tag"]: row for row in csv_rows(ROSTER)}
    owners = {
        row["location"]: row["tag"] for row in csv_rows(OWNERSHIP, comments=True)
    }
    macros, allocations = load_population_plan()
    overrides = population_location_overrides(owners, allocations)
    geographic, location_groups = population_geographic_allocations(
        owners, roster, allocations, overrides
    )
    cities, _ = population_city_targets(owners)
    records = parse_records(POP_FILE)
    by_location: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    sizes: defaultdict[str, Decimal] = defaultdict(Decimal)
    for record in records:
        by_location[record["location"]].append(record)
        sizes[record["location"]] += Decimal(record["size"])
    region_totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    macro_totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    culture_totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    geographic_totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    geographic_cultures: defaultdict[tuple[str, str], Decimal] = defaultdict(Decimal)
    for location, location_records in by_location.items():
        record = location_records[0]
        region = overrides.get(location, {}).get(
            "region", roster[owners[location]]["region"]
        )
        macro = allocations[region].macro
        size = sizes[location]
        region_totals[region] += size
        macro_totals[macro] += size
        for stratum in location_records:
            culture_totals[stratum["culture"]] += Decimal(stratum["size"])
        if location in location_groups:
            group = location_groups[location]
            geographic_totals[group] += size
            for stratum in location_records:
                geographic_cultures[(group, stratum["culture"])] += Decimal(stratum["size"])
    for record in parse_records(COMPATIBILITY_POP_FILE):
        location = record["location"]
        region = overrides.get(location, {}).get(
            "region", roster[owners[location]]["region"]
        )
        size = Decimal(record["size"])
        region_totals[region] += size
        macro_totals[allocations[region].macro] += size
    italy_total = sum(geographic_totals.values(), Decimal())
    italy_cultures: defaultdict[str, Decimal] = defaultdict(Decimal)
    for (_, culture), size in geographic_cultures.items():
        italy_cultures[culture] += size

    rows: list[dict[str, str]] = []

    def add(
        section: str,
        key: str,
        location: str,
        parent: str,
        size: Decimal,
        share: str,
        source: str,
        confidence: str,
        note: str,
    ) -> None:
        rows.append(
            {
                "section": section,
                "key": key,
                "location": location,
                "parent": parent,
                "size_thousands": f"{size:.3f}",
                "share_percent": share,
                "source": source,
                "confidence": confidence,
                "note": note,
            }
        )

    world_total = macros["world"].target
    for macro in sorted(macro_totals):
        add(
            "macro",
            macro,
            "",
            "world",
            macro_totals[macro],
            percentage(macro_totals[macro], world_total),
            macros[macro].source,
            macros[macro].confidence,
            "Exact plan section 12.4 macro total",
        )
    for region in sorted(region_totals):
        macro = allocations[region].macro
        add(
            "roster_region",
            region,
            "",
            macro,
            region_totals[region],
            percentage(region_totals[region], macro_totals[macro]),
            allocations[region].source,
            allocations[region].confidence,
            "Observed geography after macro allocation and caps",
        )
    for group in sorted(geographic):
        allocation = geographic[group]
        add(
            "italy_subregion",
            group,
            "",
            allocation.parent_region,
            geographic_totals[group],
            percentage(geographic_totals[group], italy_total),
            allocation.source,
            allocation.confidence,
            allocation.note,
        )
    for culture, size in sorted(
        italy_cultures.items(), key=lambda item: (-item[1], item[0])
    ):
        add(
            "italy_culture",
            culture,
            "",
            "italy",
            size,
            percentage(size, italy_total),
            "generated-cross-table",
            "audit",
            "Culture is reported separately from Italian geography",
        )
    for culture, size in sorted(
        culture_totals.items(), key=lambda item: (-item[1], item[0])
    ):
        add(
            "global_culture",
            culture,
            "",
            "world",
            size,
            percentage(size, world_total),
            "generated-cross-table",
            "audit",
            "Generated AD 1 base-pop total",
        )
    for rank, record in enumerate(
        sorted(by_location, key=lambda location: (-sizes[location], location))[:20],
        start=1,
    ):
        location = record
        representative = by_location[location][0]
        add(
            "top_location",
            f"{rank:02d}",
            location,
            representative["culture"],
            sizes[location],
            percentage(sizes[location], world_total),
            "generated-ranking",
            "audit",
            "Top 20 generated game locations after fixed targets and residual cap",
        )
    for city in cities:
        add(
            "city_target",
            city.place,
            city.location,
            city.mode,
            sizes[city.location],
            percentage(sizes[city.location], world_total),
            city.source,
            city.confidence,
            city.note,
        )
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        expected = render()
    except Exception as exc:
        print(f"population_audit: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8", newline="")
        print(f"population_audit: wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    actual = OUTPUT.read_text(encoding="utf-8-sig") if OUTPUT.is_file() else ""
    if actual != expected:
        print(
            "population_audit: FAIL\n"
            f"  - run {Path(__file__).name} --write to refresh {OUTPUT.relative_to(ROOT)}"
        )
        return 1
    sections: defaultdict[str, int] = defaultdict(int)
    for row in csv.DictReader(io.StringIO(expected)):
        sections[row["section"]] += 1
    summary = ", ".join(f"{key}={sections[key]}" for key in sorted(sections))
    print(f"population_audit: PASS ({summary})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate generated M4 population totals, profiles, and geographic coverage."""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from extract_vanilla import tokenize
from generate_country_definitions import historical_profile_for
from generate_start_mirror import (
    COMPATIBILITY_LOCATION,
    COMPATIBILITY_POP_SIZE,
    COMPATIBILITY_RELIGION,
    MAX_UNTARGETED_LOCATION_POPULATION,
    culture_presence_cultures,
    load_population_plan,
    population_city_targets,
    population_culture_remaps,
    population_religion_remaps,
    population_geographic_allocations,
    population_location_overrides,
)

ROOT = Path(__file__).resolve().parents[1]
POP_FILE = ROOT / "main_menu/setup/start/06_pops.txt"
COMPATIBILITY_POP_FILE = ROOT / "main_menu/setup/start/21_locations.txt"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
M4_SYMBOLS = ROOT / "docs/m4/definition_symbols.json"
POP_TYPES = ROOT / "docs/vanilla_symbols/pop_type.json"
EPSILON = Decimal("0.001")


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_records(path: Path) -> list[dict[str, str]]:
    """Read `locations` / `define_pop` blocks with the shared tolerant tokenizer."""
    tokens = list(tokenize(path.read_text(encoding="utf-8-sig", errors="replace")))
    stack: list[str] = []
    records: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    index = 0
    while index < len(tokens):
        value = tokens[index].value
        if (
            index + 2 < len(tokens)
            and tokens[index + 1].value == "="
            and tokens[index + 2].value == "{"
        ):
            stack.append(value)
            if len(stack) == 3 and stack[0] == "locations" and stack[2] == "define_pop":
                current = {"location": stack[1]}
            index += 3
            continue
        if value == "}":
            if current is not None and len(stack) == 3 and stack[2] == "define_pop":
                records.append(current)
                current = None
            if stack:
                stack.pop()
            index += 1
            continue
        if (
            current is not None
            and len(stack) == 3
            and stack[0] == "locations"
            and stack[2] == "define_pop"
            and index + 2 < len(tokens)
            and tokens[index + 1].value == "="
        ):
            current[value] = tokens[index + 2].value
            index += 3
            continue
        index += 1
    return records


def main() -> int:
    if not POP_FILE.is_file():
        print(f"popcheck: FAIL\n  - missing generated population file {POP_FILE.relative_to(ROOT)}")
        return 1
    records = parse_records(POP_FILE)
    if not records:
        print("popcheck: FAIL\n  - no generated define_pop records")
        return 1
    roster = {row["tag"]: row for row in csv_rows(ROSTER)}
    owners: dict[str, str] = {}
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(line for line in handle if not line.startswith("#")):
            if row["location"] in owners:
                print(f"popcheck: FAIL\n  - duplicate ownership for {row['location']}")
                return 1
            owners[row["location"]] = row["tag"]
    m4_symbols = json.loads(M4_SYMBOLS.read_text(encoding="utf-8"))
    valid_cultures = set(m4_symbols["cultures"])
    valid_religions = set(m4_symbols["religions"])
    valid_types = set(json.loads(POP_TYPES.read_text(encoding="utf-8-sig")))
    macros, allocations = load_population_plan()
    overrides = population_location_overrides(owners, allocations)
    geographic_allocations, geographic_location_groups = population_geographic_allocations(
        owners, roster, allocations, overrides
    )
    city_rows, city_targets = population_city_targets(owners)
    culture_remaps = population_culture_remaps(owners)
    religion_remaps = population_religion_remaps(owners)
    failures: list[str] = []
    records_by_location: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    region_totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    macro_totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    geographic_totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    italy_cultures: defaultdict[str, Decimal] = defaultdict(Decimal)
    location_sizes: defaultdict[str, Decimal] = defaultdict(Decimal)
    type_totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    total = Decimal()
    for record in records:
        location = record.get("location", "")
        records_by_location[location].append(record)
        required = ("type", "size", "culture", "religion")
        missing = [field for field in required if not record.get(field)]
        if missing:
            failures.append(f"{location}: missing {', '.join(missing)}")
            continue
        if location not in owners:
            failures.append(f"{location}: pop is outside controlled ownership")
            continue
        if record["type"] not in valid_types:
            failures.append(f"{location}: invalid pop type {record['type']}")
        if record["culture"] not in valid_cultures:
            failures.append(f"{location}: invalid M4 culture {record['culture']}")
        if record["religion"] not in valid_religions:
            failures.append(f"{location}: invalid M4 religion {record['religion']}")
        try:
            size = Decimal(record["size"])
        except Exception:
            failures.append(f"{location}: invalid size {record['size']!r}")
            continue
        if size <= 0:
            failures.append(f"{location}: non-positive size {size}")
            continue
        location_sizes[location] += size
        type_totals[record["type"]] += size
        tag = owners[location]
        profile = historical_profile_for(roster[tag])
        override = overrides.get(location, {})
        expected_culture = override.get("culture", culture_remaps.get(location, {}).get("culture", profile.culture))
        expected_religion = override.get(
            "religion",
            religion_remaps.get(location, {}).get("religion", profile.religion),
        )
        if record["culture"] != expected_culture or record["religion"] != expected_religion:
            failures.append(
                f"{location}: profile {record['culture']}/{record['religion']} does not match {tag} "
                f"({expected_culture}/{expected_religion})"
            )
        region = override.get("region", roster[tag]["region"])
        region_totals[region] += size
        macro_totals[allocations[region].macro] += size
        if location in geographic_location_groups:
            group = geographic_location_groups[location]
            geographic_totals[group] += size
            italy_cultures[record["culture"]] += size
        total += size
    compatibility = parse_records(COMPATIBILITY_POP_FILE)
    expected_cultures = culture_presence_cultures()
    if len(compatibility) != len(expected_cultures):
        failures.append(
            f"compatibility manager has {len(compatibility)} records, expected {len(expected_cultures)}"
        )
    seen_compatibility: set[str] = set()
    for record in compatibility:
        culture = record.get("culture", "")
        seen_compatibility.add(culture)
        if record.get("location") != COMPATIBILITY_LOCATION:
            failures.append(f"compatibility pop is not at {COMPATIBILITY_LOCATION}")
        if record.get("type") != "peasants" or record.get("religion") != COMPATIBILITY_RELIGION:
            failures.append(f"{culture}: invalid compatibility population contract")
        if culture not in valid_cultures and culture not in set(json.loads((ROOT / "docs/vanilla_symbols/culture.json").read_text(encoding="utf-8-sig"))):
            failures.append(f"{culture}: invalid compatibility culture")
        try:
            size = Decimal(record.get("size", ""))
        except Exception:
            failures.append(f"{culture}: invalid compatibility size")
            continue
        if size != COMPATIBILITY_POP_SIZE:
            failures.append(f"{culture}: compatibility size {size} is not {COMPATIBILITY_POP_SIZE}")
            continue
        region = overrides.get(COMPATIBILITY_LOCATION, {}).get(
            "region", roster[owners[COMPATIBILITY_LOCATION]]["region"]
        )
        region_totals[region] += size
        macro_totals[allocations[region].macro] += size
        total += size
    if seen_compatibility != set(expected_cultures):
        failures.append("compatibility culture ledger and generated manager differ")
    for location in sorted(owners):
        count = len(records_by_location[location])
        if count < 1:
            failures.append(f"{location}: expected at least one generated base pop, found {count}")
        size = location_sizes[location]
        if location in city_targets:
            city = city_targets[location]
            if size != city.game_target:
                failures.append(f"{location}: city target is {size}, expected exact {city.game_target}")
            if not (city.game_minimum <= size <= city.game_maximum):
                failures.append(f"{location}: city target {size} outside {city.game_minimum}-{city.game_maximum}")
            if count < 4:
                failures.append(f"{location}: mapped major city has only {count} social strata")
        elif size > MAX_UNTARGETED_LOCATION_POPULATION:
            failures.append(
                f"{location}: untargeted population {size} exceeds {MAX_UNTARGETED_LOCATION_POPULATION}"
            )
    absent_types = sorted(valid_types - set(type_totals))
    if absent_types:
        failures.append(f"opening world has no substantive strata for {absent_types}")
    for group, allocation in geographic_allocations.items():
        actual = geographic_totals[group]
        if abs(actual - allocation.target) > EPSILON:
            failures.append(f"{group}: {actual} thousand, expected {allocation.target}")
    for macro, target in macros.items():
        actual = total if macro == "world" else macro_totals[macro]
        if abs(actual - target.target) > EPSILON:
            failures.append(f"{macro}: {actual} thousand, expected {target.target}")
        if target.minimum is not None and not (target.minimum <= actual <= target.maximum):
            failures.append(f"{macro}: {actual} outside plan range {target.minimum}-{target.maximum}")
    if failures:
        print("popcheck: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures[:80]))
        if len(failures) > 80:
            print(f"  - ... {len(failures) - 80} more")
        return 1
    mapped_cities = [row for row in city_rows if row.game_target is not None]
    top_cities = sorted(
        mapped_cities,
        key=lambda row: (location_sizes[row.location], row.place),
        reverse=True,
    )[:20]
    city_summary = ", ".join(
        f"{row.place}={location_sizes[row.location]:,.0f}" for row in top_cities
    )
    italy_summary = ", ".join(
        f"{group}={geographic_totals[group]:,.0f}"
        for group in sorted(geographic_allocations)
    )
    italy_culture_summary = ", ".join(
        f"{culture}={size:,.0f}"
        for culture, size in sorted(
            italy_cultures.items(), key=lambda item: (item[1], item[0]), reverse=True
        )[:8]
    )
    macro_summary = ", ".join(
        f"{macro}={macro_totals[macro]:,.3f}" for macro in sorted(macro_totals)
    )
    print(
        f"popcheck: PASS ({total:,.3f} thousand people; {len(records)} stratified pops; "
        f"{len(records_by_location)} populated locations; {len(mapped_cities)} fixed cities; "
        f"{macro_summary})"
    )
    print(f"  Italy geography: {italy_summary}")
    print(f"  Italy cultures: {italy_culture_summary}")
    print(f"  Top mapped cities: {city_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

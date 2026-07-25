#!/usr/bin/env python3
"""Audit the generated AD 1 Galatian culture and ownership surface."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from decimal import Decimal
from io import StringIO
from pathlib import Path

from generate_start_mirror import population_culture_remaps


ROOT = Path(__file__).resolve().parents[1]
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
HIERARCHY = ROOT / "docs/vanilla_symbols/geography_hierarchy.json"
PROVINCES = ROOT / "docs/vanilla_symbols/provinces.json"
AREAS = ROOT / "docs/vanilla_symbols/areas.json"
START_POPS = ROOT / "main_menu/setup/start/06_pops.txt"
M4_SYMBOLS = ROOT / "docs/m4/definition_symbols.json"
DYNAMIC_NAMES = ROOT / "docs/m4/dynamic_location_names.csv"
LOCATION_OUTPUT = ROOT / "docs/m4/galatian_location_audit.csv"
TOTAL_OUTPUT = ROOT / "docs/m4/galatian_culture_totals.csv"

PROVINCE_CULTURES = {
    "ankara_province": "antq_galatian_tectosagian",
    "sivrihisar_province": "antq_tolistobogian",
    "bozok_province": "antq_trocmian",
}
DIRECT_CULTURES = {"huseyinabad": "antq_trocmian"}
CENTRES = {
    "ankara": "Ancyra",
    "sivrihisar": "Pessinous",
    "bozok": "Tavium",
}
GALATIAN_CULTURES = frozenset(PROVINCE_CULTURES.values())
GENERIC = "antq_galatian"
OBSOLETE = "antq_trocman"
POP = re.compile(
    r"(?m)^\t(?P<location>[a-z0-9_]+) = \{\r?\n"
    r"\t\tdefine_pop = \{[^\r\n]*\bsize = (?P<size>[0-9.]+) "
    r"culture = (?P<culture>[a-z0-9_]+)"
)


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(line for line in handle if not line.startswith("#")))


def leaves(
    key: str,
    hierarchy: dict[str, list[str]],
    trail: tuple[str, ...] = (),
) -> set[str]:
    if key in trail:
        raise ValueError(f"cyclic geography path {' -> '.join((*trail, key))}")
    children = hierarchy.get(key)
    if not children:
        return {key}
    result: set[str] = set()
    for child in children:
        if child == key:
            result.add(child)
        else:
            result.update(leaves(child, hierarchy, (*trail, key)))
    return result


def render() -> tuple[dict[Path, str], int, Decimal]:
    ownership_rows = csv_rows(OWNERSHIP)
    owners = {row["location"]: row["tag"] for row in ownership_rows}
    hierarchy = json.loads(HIERARCHY.read_text(encoding="utf-8-sig"))
    provinces = set(json.loads(PROVINCES.read_text(encoding="utf-8-sig")))
    areas = set(json.loads(AREAS.read_text(encoding="utf-8-sig")))
    remaps = population_culture_remaps(owners)
    pops = {
        match.group("location"): (
            match.group("culture"),
            Decimal(match.group("size")),
        )
        for match in POP.finditer(START_POPS.read_text(encoding="utf-8-sig"))
    }
    symbols = set(json.loads(M4_SYMBOLS.read_text(encoding="utf-8"))["cultures"])
    names = {row["location"]: row["historical_name"] for row in csv_rows(DYNAMIC_NAMES)}

    expected: dict[str, str] = {}
    for province, culture in PROVINCE_CULTURES.items():
        for location in leaves(province, hierarchy) & set(owners):
            expected[location] = culture
    expected.update(DIRECT_CULTURES)

    parent_province: dict[str, str] = {}
    parent_area: dict[str, str] = {}
    for parent, children in hierarchy.items():
        for child in children:
            if child in expected and parent in provinces:
                parent_province[child] = parent
            if child in provinces and parent in areas:
                parent_area[child] = parent

    failures: list[str] = []
    if GENERIC in symbols:
        failures.append(f"obsolete generic culture {GENERIC} remains defined")
    if OBSOLETE in symbols:
        failures.append(f"obsolete culture key {OBSOLETE} remains defined")
    actual_galatians = {
        location for location, (culture, _) in pops.items() if culture in GALATIAN_CULTURES
    }
    if actual_galatians != set(expected):
        failures.append(
            "Galatian location surface mismatch; "
            f"missing={sorted(set(expected) - actual_galatians)}, "
            f"extra={sorted(actual_galatians - set(expected))}"
        )
    if any(culture in {GENERIC, OBSOLETE} for culture, _ in pops.values()):
        failures.append("generic or obsolete Galatian population remains generated")
    for location, name in CENTRES.items():
        if names.get(location) != name:
            failures.append(
                f"{location}: expected reviewed centre name {name}, got {names.get(location)!r}"
            )

    audit_rows: list[dict[str, str]] = []
    totals: Counter[str] = Counter()
    populations: dict[str, Decimal] = {}
    for location in sorted(expected):
        if location not in pops:
            failures.append(f"{location}: no generated population")
            continue
        if location not in remaps:
            failures.append(f"{location}: no explicit culture-atlas selector")
            continue
        culture, size = pops[location]
        selected = remaps[location]
        if culture != expected[location]:
            failures.append(
                f"{location}: generated culture {culture} != expected {expected[location]}"
            )
        if culture != selected["culture"]:
            failures.append(
                f"{location}: generated culture {culture} != atlas {selected['culture']}"
            )
        if owners.get(location) != "ROM":
            failures.append(f"{location}: Galatian homeland is not Roman-owned at AD 1")
        province = parent_province.get(location, "")
        area = parent_area.get(province, "")
        if not province or not area:
            failures.append(f"{location}: missing province/area ancestry")
        totals[culture] += 1
        populations[culture] = populations.get(culture, Decimal()) + size
        audit_rows.append(
            {
                "location": location,
                "province": province,
                "area": area,
                "owner": owners.get(location, ""),
                "culture": culture,
                "population_thousands": f"{size:.3f}",
                "reviewed_centre": CENTRES.get(location, ""),
                "selector_type": selected["selector_type"],
                "selector": selected["selector"],
                "source": selected["source"],
                "confidence": selected["confidence"],
                "note": selected["note"],
            }
        )
    if len(expected) != 19:
        failures.append(f"reviewed Galatian surface must contain 19 locations, got {len(expected)}")
    if set(totals) != GALATIAN_CULTURES:
        failures.append(f"expected all three Galatian communities, got {sorted(totals)}")
    if failures:
        raise ValueError("\n".join(failures))

    location_stream = StringIO(newline="")
    location_writer = csv.DictWriter(
        location_stream,
        fieldnames=(
            "location",
            "province",
            "area",
            "owner",
            "culture",
            "population_thousands",
            "reviewed_centre",
            "selector_type",
            "selector",
            "source",
            "confidence",
            "note",
        ),
        lineterminator="\n",
    )
    location_writer.writeheader()
    location_writer.writerows(audit_rows)

    total_stream = StringIO(newline="")
    total_writer = csv.DictWriter(
        total_stream,
        fieldnames=("culture", "locations", "population_thousands"),
        lineterminator="\n",
    )
    total_writer.writeheader()
    for culture in sorted(totals):
        total_writer.writerow(
            {
                "culture": culture,
                "locations": totals[culture],
                "population_thousands": f"{populations[culture]:.3f}",
            }
        )
    return (
        {LOCATION_OUTPUT: location_stream.getvalue(), TOTAL_OUTPUT: total_stream.getvalue()},
        len(expected),
        sum(populations.values(), Decimal()),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        outputs, locations, population = render()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"m4_galatian_atlas: FAIL\n  - {exc}")
        return 1
    if args.write:
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8-sig", newline="")
        print(
            f"m4_galatian_atlas: wrote {locations} locations / "
            f"{len(GALATIAN_CULTURES)} cultures ({population:.3f} thousand people)"
        )
        return 0
    stale = [
        path.relative_to(ROOT)
        for path, content in outputs.items()
        if not path.is_file() or path.read_text(encoding="utf-8-sig") != content
    ]
    if stale:
        print(f"m4_galatian_atlas: FAIL\n  - stale outputs: {', '.join(map(str, stale))}")
        return 1
    print(
        f"m4_galatian_atlas: PASS ({locations} Roman-owned locations; "
        f"{len(GALATIAN_CULTURES)} communities; {population:.3f} thousand people; "
        "Ancyra/Pessinous/Tavium anchored)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

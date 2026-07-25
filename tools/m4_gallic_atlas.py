#!/usr/bin/env python3
"""Audit the generated AD 1 culture surface of Gaul location by location."""

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
LOCATION_OUTPUT = ROOT / "docs/m4/gallic_location_audit.csv"
TOTAL_OUTPUT = ROOT / "docs/m4/gallic_culture_totals.csv"

# France-region geography plus the three Belgic areas that the installed map
# stores in its north-German region. Roman ownership is deliberately irrelevant
# to this cultural audit.
SCOPES = (
    "france_region",
    "brabant_area",
    "flanders_area",
    "wallonia_area",
)
GENERIC = "antq_gallic"
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


def render() -> tuple[dict[Path, str], int, int, Decimal]:
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
    target = set().union(*(leaves(scope, hierarchy) for scope in SCOPES)) & set(owners)

    parent_province: dict[str, str] = {}
    parent_area: dict[str, str] = {}
    for parent, children in hierarchy.items():
        for child in children:
            if child in target and parent in provinces:
                parent_province[child] = parent
            if child in provinces and parent in areas:
                parent_area[child] = parent

    failures: list[str] = []
    if GENERIC in set(json.loads(M4_SYMBOLS.read_text(encoding="utf-8"))["cultures"]):
        failures.append(f"obsolete generic culture {GENERIC} remains defined")
    audit_rows: list[dict[str, str]] = []
    totals: Counter[str] = Counter()
    populations: dict[str, Decimal] = {}
    for location in sorted(target):
        if location not in pops:
            failures.append(f"{location}: no generated population")
            continue
        if location not in remaps:
            failures.append(f"{location}: no explicit culture-atlas selector")
            continue
        culture, size = pops[location]
        selected = remaps[location]
        if culture != selected["culture"]:
            failures.append(
                f"{location}: generated culture {culture} != atlas {selected['culture']}"
            )
        if culture == GENERIC:
            failures.append(
                f"{location}: unexplained generic {GENERIC} remains in reviewed Gaul"
            )
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
                "owner": owners[location],
                "culture": culture,
                "population_thousands": f"{size:.3f}",
                "selector_type": selected["selector_type"],
                "selector": selected["selector"],
                "source": selected["source"],
                "confidence": selected["confidence"],
                "note": selected["note"],
            }
        )
    if len(target) < 500:
        failures.append(f"reviewed Gaul surface unexpectedly small: {len(target)} locations")
    if len(totals) < 35:
        failures.append(f"reviewed Gaul has only {len(totals)} populated cultures")
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
        len(target),
        len(totals),
        sum(populations.values(), Decimal()),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        outputs, locations, cultures, population = render()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"m4_gallic_atlas: FAIL\n  - {exc}")
        return 1
    if args.write:
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8-sig", newline="")
        print(
            f"m4_gallic_atlas: wrote {locations} locations / {cultures} cultures "
            f"({population:.3f} thousand people)"
        )
        return 0
    stale = [
        path.relative_to(ROOT)
        for path, content in outputs.items()
        if not path.is_file() or path.read_text(encoding="utf-8-sig") != content
    ]
    if stale:
        print(f"m4_gallic_atlas: FAIL\n  - stale outputs: {', '.join(map(str, stale))}")
        return 1
    print(
        f"m4_gallic_atlas: PASS ({locations} locations; {cultures} cultures; "
        f"{population:.3f} thousand people; zero generic Gallic)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

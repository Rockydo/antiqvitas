#!/usr/bin/env python3
"""Render and validate named AD 1 Roman civic and naval-building specials.

The ledger is deliberately data-first: source, confidence, named UI text,
engine contract, modest economic inputs, and artwork subject stay together.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/m5/roman_buildings.csv"
SPECIALS = ROOT / "docs/m5/special_buildings.csv"
GOODS = ROOT / "docs/vanilla_symbols/good.json"
OUTPUT = ROOT / "in_game/common/building_types/00_antiquitas_roman_buildings.txt"
ICON_DIR = ROOT / "main_menu/gfx/interface/icons/buildings"
LOC_ROOT = ROOT / "main_menu/localization"
DDS = ROOT / "tools/dds.py"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian", "braz_por",
    "simp_chinese", "japanese", "korean", "turkish",
)
FIELDS = (
    "key", "location", "name", "description", "category", "pop_type",
    "employment_size", "build_time", "modifier", "maintenance", "goods", "source",
    "confidence", "note", "icon_subject",
)
CATEGORIES = {
    "basic_industry_category", "cultural_category", "government_category",
    "defense_category", "infrastructure_category", "naval_category", "religious_category", "trade_category",
}
POP_TYPES = {"burghers", "clergy", "laborers", "nobles", "soldiers"}
EMPLOYMENT = {
    "cultural_employment", "dock_employment", "generic_burgher_employment", "generic_peasant_building_employment",
    "guild_employment", "religious_building_employment", "stockade_employment", "trade_employment",
}
BUILD_TIMES = {
    "cultural_building_time", "government_build_time", "guild_build_time",
    "infrastructure_build_time", "market_build_time", "medium_port_building_time", "religious_building_time", "small_fort_building",
}
MODIFIERS = {
    "local_clergy_max_literacy", "local_cultural_tradition", "local_disease_resistance",
    "local_garrison_size", "local_life_expectancy", "local_max_control", "local_merchant_capacity",
    "local_merchant_power", "local_monthly_food_modifier", "local_population_capacity",
    "local_production_efficiency", "local_repair_speed", "local_sailors", "local_unrest",
}
ROMAN_SPECIAL_LOCATIONS = {"augsburg", "basel", "bonn", "mainz", "neuss", "nijmegen", "ravenna", "recklinghausen", "rome", "strasbourg"}
START_KEY_PREFIX = {"augsburg": "augsburg", "basel": "basel", "bonn": "bonn", "mainz": "mainz", "neuss": "neuss", "nijmegen": "nijmegen", "ravenna": "ravenna", "recklinghausen": "recklinghausen", "rome": "roma", "strasbourg": "strasbourg"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError(f"{path.relative_to(ROOT)} must use header {','.join(FIELDS)}")
        return [{field: (row.get(field) or "").strip() for field in FIELDS} for row in reader]


def pairs(value: str, label: str) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for part in value.split(";"):
        key, separator, amount = part.partition("=")
        key, amount = key.strip(), amount.strip()
        if not separator or not key or not amount:
            raise ValueError(f"invalid {label} pair {part!r}")
        try:
            if float(amount) == 0:
                raise ValueError
        except ValueError as exc:
            raise ValueError(f"invalid {label} amount {amount!r}") from exc
        result.append((key, amount))
    return result


def load() -> list[dict[str, str]]:
    items = rows(LEDGER)
    if len(items) < 12:
        raise ValueError("Roman building ledger must contain at least twelve named AD 1 buildings")
    goods = set(json.loads(GOODS.read_text(encoding="utf-8-sig")))
    failures: list[str] = []
    seen: set[str] = set()
    for number, row in enumerate(items, start=2):
        prefix = f"{LEDGER.relative_to(ROOT)}:{number}"
        if any(not row[field] for field in FIELDS):
            failures.append(f"{prefix}: blank required field")
        if not re.fullmatch(r"antq_[a-z0-9_]+", row["key"]):
            failures.append(f"{prefix}: key must be an antq_ identifier")
        if row["key"] in seen:
            failures.append(f"{prefix}: duplicate key {row['key']}")
        if row["location"] not in ROMAN_SPECIAL_LOCATIONS:
            failures.append(f"{prefix}: Roman named special must use a reviewed location {sorted(ROMAN_SPECIAL_LOCATIONS)}")
        if row["category"] not in CATEGORIES:
            failures.append(f"{prefix}: unknown verified category {row['category']}")
        if row["pop_type"] not in POP_TYPES or row["employment_size"] not in EMPLOYMENT:
            failures.append(f"{prefix}: unknown verified population/employment contract")
        if row["build_time"] not in BUILD_TIMES:
            failures.append(f"{prefix}: unknown verified build-time contract")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"{prefix}: confidence must be secure or contested")
        try:
            modifier_pairs = pairs(row["modifier"], "modifier")
            for modifier, _amount in modifier_pairs:
                if modifier not in MODIFIERS:
                    failures.append(f"{prefix}: unverified modifier {modifier}")
            maintenance_pairs = pairs(row["maintenance"], "maintenance")
            listed_goods = {good.strip() for good in row["goods"].split(";") if good.strip()}
            if listed_goods != {good for good, _amount in maintenance_pairs}:
                failures.append(f"{prefix}: goods must exactly describe maintenance inputs")
            unknown = listed_goods - goods
            if unknown:
                failures.append(f"{prefix}: unknown installed goods {sorted(unknown)}")
        except ValueError as exc:
            failures.append(f"{prefix}: {exc}")
        seen.add(row["key"])
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    special_rows: list[dict[str, str]]
    with SPECIALS.open(encoding="utf-8-sig", newline="") as handle:
        special_rows = list(csv.DictReader(handle))
    special = {row["building"].strip(): row for row in special_rows if row["building"].strip().startswith("antq_")}
    missing = seen - set(special)
    extra = set(special) - seen
    if missing or extra:
        raise ValueError(f"Roman custom building ledger/start ledger divergence: missing={sorted(missing)} extra={sorted(extra)}")
    for key, row in special.items():
        expected = next(item for item in items if item["key"] == key)
        prefix = START_KEY_PREFIX[expected["location"]] + "_"
        if row["location"].strip() != expected["location"] or not row["key"].strip().startswith(prefix):
            raise ValueError(f"special_buildings.csv entry for {key} must use its ledger location and a {prefix!r}-prefixed start key")
    return items


def definition(items: list[dict[str, str]]) -> str:
    lines = [
        "# Generated by tools/m5_roman_buildings.py --write.",
        "# Named, one-level Roman civic and naval specials; historical ledger: docs/m5/roman_buildings.csv.",
        "",
    ]
    for row in items:
        lines.extend((f"{row['key']} = {{", "\taudio_tier = 2", "\tis_special = yes", "\tis_foreign = no",
                      f"\tpop_type = {row['pop_type']}", "\tmax_levels = 1", f"\tcategory = {row['category']}",
                      f"\temployment_size = {row['employment_size']}", "\ttown = yes", "\tcity = yes", "\tmegalopolis = yes",
                      f"\tbuild_time = {row['build_time']}", "\tmodifier = {"))
        for key, amount in pairs(row["modifier"], "modifier"):
            lines.append(f"\t\t{key} = {amount}")
        lines.extend(("\t}", "\tunique_production_methods = {", f"\t\t{row['key']}_maintenance = {{"))
        for good, amount in pairs(row["maintenance"], "maintenance"):
            lines.append(f"\t\t\t{good} = {amount}")
        lines.extend(("\t\t\tcategory = building_maintenance", "\t\t}", "\t}", "\tconstruction_demand = town_building_construction"))
        if row["category"] == "defense_category":
            lines.extend(("\traw_modifier = {", "\t\tfort_level = 1", "\t\tpure_tooltip_entry = pte_no_propagating_zone_of_control", "\t}"))
        lines.extend(("}", ""))
    return "\n".join(lines)


def loc(items: list[dict[str, str]], language: str) -> str:
    lines = [f"l_{language}:", " # Generated named AD 1 Roman civic and naval building localization; English mirrored by design."]
    for row in items:
        name = row["name"].replace('"', "'")
        description = row["description"].replace('"', "'")
        lines.append(f" {row['key']}: \"{name}\"")
        lines.append(f" {row['key']}_desc: \"{description}\"")
        lines.append(f" {row['key']}_maintenance: \"{name} Upkeep\"")
    return "\n".join(lines) + "\n"


def expected(items: list[dict[str, str]]) -> dict[Path, tuple[str, str]]:
    # The installed common/building_types directory is UTF-8 with BOM; the
    # engine emits a diagnostics line for a plain UTF-8 definition here.
    result: dict[Path, tuple[str, str]] = {OUTPUT: (definition(items), "utf-8-sig")}
    for language in LANGUAGES:
        result[LOC_ROOT / language / f"antq_m5_roman_buildings_l_{language}.yml"] = (loc(items, language), "utf-8-sig")
    return result


def dds_ok(path: Path) -> bool:
    result = subprocess.run([sys.executable, str(DDS), "identify", str(path)], text=True, capture_output=True)
    if result.returncode:
        return False
    try:
        details = json.loads(result.stdout)
    except json.JSONDecodeError:
        return False
    return details == {"format": "DDS", "width": "128", "height": "128", "depth": "8", "channels": "srgba 4.0"}


def validate_art(items: list[dict[str, str]]) -> None:
    failures = []
    for row in items:
        icon = ICON_DIR / f"{row['key']}.dds"
        if not icon.is_file():
            failures.append(f"missing direct Roman building icon {icon.relative_to(ROOT)}")
        elif not dds_ok(icon):
            failures.append(f"invalid 128px RGBA DDS Roman building icon {icon.relative_to(ROOT)}")
    if failures:
        raise ValueError("\n".join(failures))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        items = load()
        outputs = expected(items)
        if args.write:
            for path, (content, encoding) in outputs.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding=encoding, newline="\n")
        stale = [path.relative_to(ROOT) for path, (content, encoding) in outputs.items() if not path.is_file() or path.read_text(encoding=encoding) != content]
        if stale:
            raise ValueError(f"stale or missing generated Roman building output: {stale}")
        validate_art(items)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m5_roman_buildings: FAIL\n  - {exc}")
        return 1
    print(f"m5_roman_buildings: PASS ({len(items)} named Roman buildings with direct icon contracts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

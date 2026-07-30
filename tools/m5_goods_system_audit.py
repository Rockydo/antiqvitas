#!/usr/bin/env python3
"""Audit every good used by the active ANTIQVITAS building economy."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path

from m5_regional_buildings import PRODUCTION_RECIPES


ROOT = Path(__file__).resolve().parents[1]
CUSTOM = ROOT / "docs/m5/custom_goods.csv"
VANILLA = ROOT / "docs/vanilla_symbols/good.json"
RGO_REPORT = ROOT / "docs/m5/rgo_remap_report.csv"
SEEDS = ROOT / "docs/m5/regional_building_seeds.csv"
OUTPUT = ROOT / "docs/m5/active_goods_audit.csv"
REPORT = ROOT / "docs/m5/ACTIVE_GOODS_AUDIT.md"
BUILDING_LEDGERS = (
    ROOT / "docs/m5/regional_building_families.csv",
    ROOT / "docs/m5/roman_buildings.csv",
    ROOT / "docs/m5/ancient_building_replacements.csv",
)
OUTPUT_FIELDS = (
    "good", "display", "origin", "period_role", "rgo_locations",
    "building_families", "productive_inputs", "productive_outputs",
    "roman_profile_families", "source", "status",
)

PERIOD_ROLE_GROUPS = {
    "food_crop_or_animal": {
        "fish", "fruit", "livestock", "millet", "olives", "rice",
        "wheat", "wild_game", "antq_barley",
    },
    "organic_raw_or_exchange": {
        "amber", "beeswax", "cotton", "fiber_crops", "incense", "ivory",
        "lumber", "pepper", "silk", "tar", "wool",
        "antq_camels", "antq_papyrus", "antq_silphium",
    },
    "mineral_or_quarried_raw": {
        "alum", "clay", "coal", "copper", "gems", "goods_gold", "iron",
        "lead", "marble", "mercury", "salt", "sand", "silver", "stone",
        "tin", "antq_jade", "antq_naphtha",
    },
    "processed_food_or_drink": {
        "beer", "wine", "antq_grain_products", "antq_olive_oil",
        "antq_preserved_fish",
    },
    "processed_craft_or_service": {
        "books", "cloth", "dyes", "fine_cloth", "furniture", "glass",
        "jewelry", "leather", "masonry", "medicaments", "naval_supplies",
        "paper", "pottery", "steel", "tools", "weaponry",
        "antq_bronze_wares", "antq_lead_wares", "antq_perfumes",
        "antq_soap", "antq_wax_goods", "antq_fine_ceramics",
        "antq_glasswares", "antq_iron_hardware", "antq_leather_goods",
        "antq_cordage", "antq_parchment", "antq_lacquerware",
        "antq_amber_ornaments", "antq_glass_beads", "antq_carpets",
        "antq_felt_goods", "antq_sailcloth",
    },
}
FORBIDDEN_POST_ANTIQUE = {
    "cannons", "chili", "cloves", "cocoa", "coffee", "firearms", "potatoes",
    "rubber", "sugar", "tea", "tobacco",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: str(value or "").strip() for key, value in row.items() if key}
            for row in csv.DictReader(handle)
            if row
        ]


def goods_from_field(value: str) -> set[str]:
    return {
        token.partition("=")[0].strip()
        for token in value.split(";")
        if token.strip()
    }


def build() -> tuple[str, str, dict[str, int]]:
    failures: list[str] = []
    custom_rows = {row["key"]: row for row in rows(CUSTOM)}
    installed = set(json.loads(VANILLA.read_text(encoding="utf-8-sig")))
    building_rows = [
        row
        for ledger in BUILDING_LEDGERS
        for row in rows(ledger)
    ]
    building_keys = [row["key"] for row in building_rows]
    if len(building_keys) != 280 or len(building_keys) != len(set(building_keys)):
        failures.append(
            f"active building ledger must contain 280 unique keys, got "
            f"{len(building_keys)}/{len(set(building_keys))}"
        )

    family_goods: dict[str, set[str]] = {}
    for row in building_rows:
        family_goods[row["key"]] = (
            goods_from_field(row.get("goods", ""))
            | goods_from_field(row.get("maintenance", ""))
        )

    input_families: dict[str, set[str]] = defaultdict(set)
    output_families: dict[str, set[str]] = defaultdict(set)
    for family, (output, _amount, inputs) in PRODUCTION_RECIPES.items():
        output_families[output].add(family)
        for good, _input_amount in inputs:
            input_families[good].add(family)

    active = set(custom_rows)
    active.update(good for goods in family_goods.values() for good in goods)
    active.update(input_families)
    active.update(output_families)
    missing_definitions = active - installed - custom_rows.keys()
    if missing_definitions:
        failures.append(f"active goods lack definitions: {sorted(missing_definitions)}")
    forbidden = active & FORBIDDEN_POST_ANTIQUE
    if forbidden:
        failures.append(f"post-antique goods are active: {sorted(forbidden)}")

    role_by_good = {
        good: role
        for role, goods in PERIOD_ROLE_GROUPS.items()
        for good in goods
    }
    duplicate_roles = sum(len(goods) for goods in PERIOD_ROLE_GROUPS.values()) - len(role_by_good)
    if duplicate_roles:
        failures.append(f"period-role groups contain {duplicate_roles} duplicate assignments")
    unclassified = active - role_by_good.keys()
    stale_roles = role_by_good.keys() - active
    if unclassified:
        failures.append(f"active goods lack period-role review: {sorted(unclassified)}")
    if stale_roles:
        failures.append(f"period-role review contains inactive goods: {sorted(stale_roles)}")

    rgo_locations: dict[str, set[str]] = defaultdict(set)
    for row in rows(RGO_REPORT):
        good = row.get("replacement_good", "")
        location = row.get("location", "")
        if good and location and not location.startswith("#"):
            rgo_locations[good].add(location)
    for key, row in custom_rows.items():
        if row["category"] == "raw_material" and not rgo_locations[key]:
            failures.append(f"{key}: custom raw good lacks an AD 1 RGO anchor")
        if row["category"] == "produced" and not output_families[key]:
            failures.append(f"{key}: custom processed good lacks a productive family")

    roman_families = {
        row["family"]
        for row in rows(SEEDS)
        if row["key"].startswith("reg_roman_economy_")
    }
    roman_uses: dict[str, set[str]] = defaultdict(set)
    for family in roman_families:
        for good in family_goods.get(family, set()):
            roman_uses[good].add(family)
        recipe = PRODUCTION_RECIPES.get(family)
        if recipe:
            roman_uses[recipe[0]].add(family)
            for good, _amount in recipe[2]:
                roman_uses[good].add(family)

    output_rows: list[dict[str, str | int]] = []
    for good in sorted(active):
        users = {family for family, goods in family_goods.items() if good in goods}
        custom = custom_rows.get(good)
        source = custom["source"] if custom else "P12.1;P12.3"
        origin = custom["category"] if custom else "installed_ancient_adapter"
        display = custom["name"] if custom else good.replace("goods_", "").replace("_", " ").title()
        status = "active_reviewed"
        output_rows.append(
            {
                "good": good,
                "display": display,
                "origin": origin,
                "period_role": role_by_good.get(good, ""),
                "rgo_locations": len(rgo_locations[good]),
                "building_families": len(users),
                "productive_inputs": len(input_families[good]),
                "productive_outputs": len(output_families[good]),
                "roman_profile_families": len(roman_uses[good]),
                "source": source,
                "status": status,
            }
        )
        if not (
            rgo_locations[good] or users or input_families[good] or output_families[good]
        ):
            failures.append(f"{good}: active good has no RGO, building, or recipe role")
        if not source:
            failures.append(f"{good}: missing source")

    if len(active) < 60:
        failures.append(f"active economy exposes only {len(active)} reviewed goods")
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))

    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(output_rows)
    counts = Counter(row["period_role"] for row in output_rows)
    metrics = {
        "active_goods": len(active),
        "custom_raw": sum(row["category"] == "raw_material" for row in custom_rows.values()),
        "custom_processed": sum(row["category"] == "produced" for row in custom_rows.values()),
        "active_buildings": len(building_keys),
        "productive_families": len(PRODUCTION_RECIPES),
        "roman_profile_families": len(roman_families),
        "rgo_anchored_goods": sum(bool(rgo_locations[good]) for good in active),
    }
    report = [
        "# Active Goods Audit",
        "",
        "Generated by `tools/m5_goods_system_audit.py`; the CSV is the exact",
        "machine-readable active economy union.",
        "",
        f"- {metrics['active_goods']} reviewed active goods: "
        f"{metrics['custom_raw']} custom raw, {metrics['custom_processed']} custom processed.",
        f"- {metrics['active_buildings']} active ancient buildings; "
        f"{metrics['productive_families']} productive families.",
        f"- {metrics['roman_profile_families']} Roman-profile families and "
        f"{metrics['rgo_anchored_goods']} RGO-anchored active goods.",
        "- Zero active cannon, firearm, colonial-crop, coffee, tea, tobacco, or",
        "  other prohibited post-antique goods.",
        "- `paper`, `coal`, `beer`, and `steel` remain engine keys only; mounted",
        "  localization and recipes present writing materials, charcoal/fuel,",
        "  fermented drinks, and bounded crucible steel.",
        "",
        "Period-role coverage:",
        "",
    ]
    report.extend(f"- {role}: {counts[role]}" for role in sorted(counts))
    report.extend(
        [
            "",
            "This audit proves registry, source-class, RGO, building-use, recipe,",
            "and Roman-profile coverage. It does not claim reconstructed quantities,",
            "prices, labor shares, or a surveyed workshop in every seeded map field.",
            "",
        ]
    )
    return stream.getvalue(), "\n".join(report), metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        csv_text, report_text, metrics = build()
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f"m5_goods_system_audit: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.write_text(csv_text, encoding="utf-8-sig", newline="")
        REPORT.write_text(report_text, encoding="utf-8", newline="\n")
    stale = []
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != csv_text:
        stale.append(OUTPUT.relative_to(ROOT))
    if not REPORT.is_file() or REPORT.read_text(encoding="utf-8") != report_text:
        stale.append(REPORT.relative_to(ROOT))
    if stale:
        print(f"m5_goods_system_audit: FAIL\n  - stale or missing {stale}")
        return 1
    print(
        "m5_goods_system_audit: PASS "
        f"({metrics['active_goods']} goods; {metrics['active_buildings']} buildings; "
        f"{metrics['productive_families']} productive families)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

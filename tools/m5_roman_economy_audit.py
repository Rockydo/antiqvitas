#!/usr/bin/env python3
"""Audit Roman provincial development paths and ancient commodity coherence."""

from __future__ import annotations

import argparse
import csv
from io import StringIO
from pathlib import Path

from m5_regional_buildings import CITY_ONLY_FAMILIES, PRODUCTION_RECIPES


ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "docs/m5/roman_economy_profiles.csv"
URBAN_NODES = ROOT / "docs/m5/urban_nodes.csv"
FAMILIES = ROOT / "docs/m5/regional_building_families.csv"
SEEDS = ROOT / "docs/m5/regional_building_seeds.csv"
GOODS = ROOT / "docs/m5/custom_goods.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
ADVANCES = ROOT / "docs/m8/advances.csv"
DEFINITIONS = ROOT / "in_game/common/building_types/00_antiquitas_regional_buildings.txt"
REPORT = ROOT / "docs/m5/ROMAN_ECONOMY_AUDIT.md"
METRICS = ROOT / "docs/m5/roman_economy_metrics.csv"
PROFILE_FIELDS = ("profile", "name", "locations", "families", "source", "confidence", "note")

SEMANTIC_OUTPUTS = {
    "antq_reg_olive_press": "antq_olive_oil",
    "antq_reg_olive_estate": "antq_olive_oil",
    "antq_reg_oil_bottler": "antq_olive_oil",
    "antq_reg_fish_saltery": "antq_preserved_fish",
    "antq_reg_garum_workshop": "antq_preserved_fish",
    "antq_reg_grain_mill": "antq_grain_products",
    "antq_reg_bread_oven": "antq_grain_products",
    "antq_reg_annona_bakery": "antq_grain_products",
    "antq_reg_villa_rustica": "antq_grain_products",
    "antq_reg_incense_workshop": "antq_perfumes",
    "antq_reg_perfumery": "antq_perfumes",
    "antq_reg_unguentarium": "antq_perfumes",
    "antq_reg_wax_workshop": "antq_wax_goods",
    "antq_reg_torchmaker": "antq_wax_goods",
    "antq_reg_soapworks": "antq_soap",
    "antq_reg_bronze_foundry": "antq_bronze_wares",
    "antq_reg_copper_smithy": "antq_bronze_wares",
    "antq_reg_tin_smelter": "antq_bronze_wares",
    "antq_reg_weightmaker": "antq_bronze_wares",
    "antq_reg_bronze_vessel_shop": "antq_bronze_wares",
    "antq_reg_cauldron_smithy": "antq_bronze_wares",
    "antq_reg_bell_foundry": "antq_bronze_wares",
    "antq_reg_bronze_workers_collegium": "antq_bronze_wares",
    "antq_reg_lead_foundry": "antq_lead_wares",
    "antq_reg_lead_pipeworks": "antq_lead_wares",
    "antq_reg_brickworks": "masonry",
    "antq_reg_lime_kiln": "masonry",
    "antq_reg_marble_yard": "masonry",
    "antq_reg_mosaic_workshop": "masonry",
    "antq_reg_stuccoworks": "masonry",
    "antq_reg_quarry_contractors": "masonry",
    "antq_reg_quernworks": "masonry",
    "antq_reg_stone_carver": "masonry",
    "antq_reg_mortar_grinder": "masonry",
    "antq_reg_silk_loom": "fine_cloth",
    "antq_reg_dye_workshop": "fine_cloth",
    "antq_reg_alum_dyehouse": "fine_cloth",
    "antq_reg_mordant_dyehouse": "fine_cloth",
    "antq_reg_purple_dyehouse": "fine_cloth",
    "antq_reg_textile_dye_finisher": "fine_cloth",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(line for line in handle if not line.startswith("#"))
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def expected() -> tuple[str, str]:
    failures: list[str] = []
    profiles = rows(PROFILES)
    town_locations = {
        row["location"] for row in rows(URBAN_NODES) if row["profile"] == "town"
    }
    families = {row["key"]: row for row in rows(FAMILIES)}
    owners = {row["location"]: row["tag"] for row in rows(OWNERSHIP)}
    seeds = [row for row in rows(SEEDS) if row["key"].startswith("reg_roman_economy_")]
    generated_keys = {row["family"] for row in seeds}
    custom_goods = {row["key"]: row for row in rows(GOODS)}
    advances = rows(ADVANCES)
    definitions = DEFINITIONS.read_text(encoding="utf-8-sig")

    if len(profiles) < 11:
        failures.append("Roman economy must cover Rome/Italy plus at least ten contrasting provincial profiles")
    if not any(row["profile"] == "latium" and row["families"] == "all" for row in profiles):
        failures.append("Latium/Rome must carry the complete portfolio")

    unlocked = {
        target
        for advance in advances
        for token in advance["unlocks"].split(";")
        for field, separator, target in (token.partition("="),)
        if separator and field == "unlock_building"
    }
    metrics: list[tuple[str, str, int, int, int, int, str]] = []
    for profile in profiles:
        locations = [value for value in profile["locations"].split(";") if value]
        selected = (
            {key.removeprefix("antq_reg_") for key in generated_keys}
            if profile["families"] == "all"
            else set(profile["families"].split(";"))
        )
        keys = {f"antq_reg_{slug}" for slug in selected}
        unknown = keys - families.keys()
        if unknown:
            failures.append(f"{profile['profile']}: unknown families {sorted(unknown)}")
            continue
        non_roman = [location for location in locations if owners.get(location) != "ROM"]
        if non_roman:
            failures.append(f"{profile['profile']}: non-Roman start locations {non_roman}")
        productive = keys & PRODUCTION_RECIPES.keys()
        categories = {families[key]["category"] for key in keys}
        outputs = {PRODUCTION_RECIPES[key][0] for key in productive}
        inputs = {good for key in productive for good, _amount in PRODUCTION_RECIPES[key][2]}
        if len(keys) < 12:
            failures.append(f"{profile['profile']}: only {len(keys)} development choices")
        if len(productive) < 5 or len(outputs) < 4:
            failures.append(
                f"{profile['profile']}: needs at least five productive choices and four outputs; "
                f"got {len(productive)}/{len(outputs)}"
            )
        if len(categories) < 5 or len(inputs) < 7:
            failures.append(
                f"{profile['profile']}: insufficient role/input diversity "
                f"({len(categories)} categories, {len(inputs)} inputs)"
            )
        expected_pairs = {
            (location, key)
            for location in locations
            for key in keys
            if not (location in town_locations and key in CITY_ONLY_FAMILIES)
        }
        actual_pairs = {
            (row["location"], row["family"])
            for row in seeds
            if row["key"].startswith(f"reg_roman_economy_{profile['profile']}_")
        }
        if actual_pairs != expected_pairs:
            failures.append(
                f"{profile['profile']}: generated placement mismatch "
                f"missing={len(expected_pairs - actual_pairs)} extra={len(actual_pairs - expected_pairs)}"
            )
        metrics.append((
            profile["profile"], profile["name"], len(locations), len(keys),
            len(productive), len(categories), ";".join(sorted(outputs)),
        ))

    for key, output in SEMANTIC_OUTPUTS.items():
        actual = PRODUCTION_RECIPES.get(key)
        if not actual or actual[0] != output:
            failures.append(f"semantic recipe mismatch: {key} must produce {output}")

    produced_custom = {
        recipe[0] for recipe in PRODUCTION_RECIPES.values() if recipe[0].startswith("antq_")
    }
    processed = {key for key, row in custom_goods.items() if row["category"] == "produced"}
    if produced_custom != processed:
        failures.append(
            f"custom processed-good coverage mismatch missing={sorted(processed - produced_custom)} "
            f"extra={sorted(produced_custom - processed)}"
        )
    for key in processed:
        row = custom_goods[key]
        demand = sum(float(row[field]) for field in ("all", "nobles", "burghers", "clergy"))
        if demand <= 0:
            failures.append(f"{key}: no pop-demand contract")
    # Every generated family is gated by the engine-native advance unlock.
    # The variable-backed trigger is only for unlock_building_effect event paths.
    for key in generated_keys:
        if key not in unlocked:
            failures.append(f"{key}: lacks advance unlock")
        marker = f"has_unlocked_building_trigger = {{ type = {key} }}"
        if marker in definitions:
            failures.append(f"{key}: duplicates the engine-native advance gate")

    if failures:
        raise ValueError("\n".join(sorted(set(failures))))

    stream = StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("profile", "name", "locations", "choices", "productive", "categories", "outputs"))
    writer.writerows(metrics)
    report = [
        "# Roman Economy Audit",
        "",
        "Generated by `tools/m5_roman_economy_audit.py`; evidence ledgers are authoritative.",
        "",
        f"- Profiles: {len(profiles)}",
        f"- Profile placements: {len(seeds)}",
        f"- Active regional families: {len(families)}",
        f"- Productive regional families: {len(PRODUCTION_RECIPES)}",
        f"- Custom processed goods: {len(processed)}",
        "- Construction: every profiled family uses an engine-native advance unlock; Roman packages also carry culture/institution potential.",
        "- Profitability: default-price recipes are held to the local engine's 19%-21% guild-margin contract.",
        "",
        "| Profile | Locations | Choices | Productive | Categories | Outputs |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    report.extend(
        f"| {name} | {locations} | {choices} | {productive} | {categories} | {len(outputs.split(';'))} |"
        for _profile, name, locations, choices, productive, categories, outputs in metrics
    )
    report.append("")
    return "\n".join(report), stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        report, metrics = expected()
    except (OSError, ValueError, csv.Error) as exc:
        print(f"m5_roman_economy_audit: FAIL\n  - {exc}")
        return 1
    if args.write:
        REPORT.write_text(report, encoding="utf-8", newline="\n")
        METRICS.write_text(metrics, encoding="utf-8-sig", newline="")
    stale = []
    if not REPORT.is_file() or REPORT.read_text(encoding="utf-8") != report:
        stale.append(REPORT.relative_to(ROOT))
    if not METRICS.is_file() or METRICS.read_text(encoding="utf-8-sig") != metrics:
        stale.append(METRICS.relative_to(ROOT))
    if stale:
        print(f"m5_roman_economy_audit: FAIL\n  - stale or missing {stale}")
        return 1
    print("m5_roman_economy_audit: PASS (semantic chains, profile diversity, unlocks, demand, and placements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

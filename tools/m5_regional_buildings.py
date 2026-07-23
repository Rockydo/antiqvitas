#!/usr/bin/env python3
"""Render and validate reusable AD 1 production-building families.

The M5 ledger distinguishes a small number of documented antique production
types from their many deliberately bounded city-point placements.  A seed is
never evidence that a particular excavated workshop stood in the game's
location polygon: it is a market/hinterland proxy, source-labelled as such.
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
FAMILIES = ROOT / "docs/m5/regional_building_families.csv"
SEEDS = ROOT / "docs/m5/regional_building_seeds.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
GOODS = ROOT / "docs/vanilla_symbols/good.json"
LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
ICON_DIR = ROOT / "main_menu/gfx/interface/icons/buildings"
OUTPUT = ROOT / "in_game/common/building_types/00_antiquitas_regional_buildings.txt"
LOC_ROOT = ROOT / "main_menu/localization"
DDS = ROOT / "tools/dds.py"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian", "braz_por",
    "simp_chinese", "japanese", "korean", "turkish",
)
FAMILY_FIELDS = (
    "key", "name", "description", "category", "pop_type", "employment_size",
    "build_time", "modifier", "maintenance", "goods", "source", "confidence",
    "note", "icon_subject",
)
SEED_FIELDS = ("key", "family", "location", "macro", "source", "confidence", "note")
CATEGORIES = {
    "basic_industry_category", "cultural_category", "government_category",
    "consumer_goods_category", "defense_category", "infrastructure_category",
    "naval_category", "religious_category", "trade_category", "weapons_industry_category",
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
MACROS = {
    "Europe": {"Rome", "Britain", "Ireland", "Germania", "Balkans", "Danube", "Eastern Europe", "Baltic", "Finland", "Scandinavia", "Pontic"},
    "North Africa": {"Africa"},
    "Middle East": {"Anatolia", "Levant", "Mesopotamia", "Iran", "Arabia", "Caucasus"},
    "South Asia": {"India"},
    "East Asia": {"China"},
}
# The AD 1 polity ledger uses political/cultural regions, not a geographic
# continent taxonomy: Roman Alexandria and Carthage are therefore tagged
# ``Rome`` there, while Antioch and Sidon can be Iranian-client space.  These
# reviewed city-point overrides keep the placement audit geographical.
MACRO_LOCATION_OVERRIDES = {
    "alexandria": "North Africa", "tunis": "North Africa",
    "annaba": "North Africa", "bizerte": "North Africa",
    "gabes": "North Africa", "sousse": "North Africa",
    "antioch": "Middle East", "baghdad": "Middle East", "ayasuluk": "Middle East",
    "shoubak": "Middle East", "homs": "Middle East", "sidon": "Middle East",
}
# Exact installed Age-of-Traditions guild recipes.  These seven productive
# families deliberately reuse the local game's proven 20% guild-margin inputs;
# the remaining three are bounded maintenance-only service/primary proxies.
PRODUCTION_RECIPES = {
    "antq_reg_wine_press": ("wine", "1", (("fruit", "1.154"), ("lumber", "0.157"), ("tools", "0.092"))),
    "antq_reg_pottery_kiln": ("pottery", "1.0", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_fullonica": ("cloth", "1", (("wool", "1.0"),)),
    "antq_reg_glassworks": ("glass", "0.75", (("lumber", "0.1933"), ("sand", "0.9657"), ("tools", "0.3674"))),
    "antq_reg_dye_workshop": ("dyes", "0.2", (("lumber", "0.4444"),)),
    "antq_reg_metalwork": ("tools", "1", (("iron", "0.8333"),)),
    "antq_reg_shipyard": ("naval_supplies", "1", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    # These additions are direct transcriptions of installed Age-of-Traditions
    # guild contracts (including the event-only silk contract). They create
    # antique craft texture without inventing an unverified economic formula.
    "antq_reg_silk_loom": ("silk", "0.6", (("fiber_crops", "1.0"),)),
    "antq_reg_scriptorium": ("books", "0.3", (("dyes", "0.0503"), ("paper", "0.1995"), ("lumber", "0.0998"))),
    "antq_reg_jeweler": ("jewelry", "1", (("goods_gold", "0.5208"),)),
    "antq_reg_weapon_smith": ("weaponry", "1", (("lumber", "0.2521"), ("coal", "0.3034"), ("tools", "0.505"))),
    "antq_reg_cotton_weavery": ("cloth", "1", (("cotton", "0.8333"),)),
    "antq_reg_linen_weavery": ("cloth", "0.8", (("fiber_crops", "1.0"),)),
    "antq_reg_alum_dyehouse": ("dyes", "0.3", (("alum", "0.021"), ("lumber", "0.6247"))),
    "antq_reg_joinery": ("furniture", "1", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    "antq_reg_bronze_foundry": ("tools", "0.6", (("copper", "0.475"), ("tin", "0.038"))),
    "antq_reg_ivory_carver": ("jewelry", "0.1", (("ivory", "0.1042"),)),
    "antq_reg_leatherworks": ("leather", "1", (("livestock", "1.0873"), ("sand", "0.4345"), ("tar", "0.0819"), ("tools", "0.1627"))),
    # Each second-pass recipe is an exact installed guild-margin contract
    # selected for its finished good; the family ledger retains the historical
    # material vocabulary without introducing unsupported price assumptions.
    "antq_reg_ropewalk": ("naval_supplies", "1", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    "antq_reg_brickworks": ("pottery", "1.0", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_lampworks": ("pottery", "1.0", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_tile_yard": ("pottery", "1.0", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_papyrus_workshop": ("books", "0.3", (("dyes", "0.0503"), ("paper", "0.1995"), ("lumber", "0.0998"))),
    "antq_reg_incense_workshop": ("dyes", "0.2", (("lumber", "0.4444"),)),
    "antq_reg_basketry": ("furniture", "1", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    "antq_reg_linen_bleachery": ("cloth", "0.8", (("fiber_crops", "1.0"),)),
    "antq_reg_copper_smithy": ("tools", "0.6", (("copper", "0.475"), ("tin", "0.038"))),
    "antq_reg_spice_grinder": ("dyes", "0.2", (("lumber", "0.4444"),)),
    "antq_reg_reed_boatyard": ("naval_supplies", "1", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    "antq_reg_oil_bottler": ("wine", "1", (("fruit", "1.154"), ("lumber", "0.157"), ("tools", "0.092"))),
    "antq_reg_garum_workshop": ("dyes", "0.2", (("lumber", "0.4444"),)),
    "antq_reg_lime_kiln": ("pottery", "1.0", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_marble_yard": ("tools", "1", (("iron", "0.8333"),)),
    "antq_reg_wool_carder": ("cloth", "1", (("wool", "1.0"),)),
    "antq_reg_mordant_dyehouse": ("dyes", "0.3", (("alum", "0.021"), ("lumber", "0.6247"))),
    "antq_reg_scale_armoury": ("weaponry", "1", (("lumber", "0.2521"), ("coal", "0.3034"), ("tools", "0.505"))),
    "antq_reg_wheelwright": ("furniture", "1", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    "antq_reg_beadworks": ("jewelry", "0.1", (("ivory", "0.1042"),)),
    "antq_reg_loomweight_weavery": ("cloth", "0.8", (("fiber_crops", "1.0"),)),
    "antq_reg_bargeyard": ("naval_supplies", "1", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    # Fourth pass: new subjects retain only locally harvested guild formulas.
    "antq_reg_saddlery": ("leather", "1", (("livestock", "1.0873"), ("sand", "0.4345"), ("tar", "0.0819"), ("tools", "0.1627"))),
    "antq_reg_parchmentery": ("books", "0.3", (("dyes", "0.0503"), ("paper", "0.1995"), ("lumber", "0.0998"))),
    "antq_reg_mosaic_workshop": ("tools", "1", (("iron", "0.8333"),)),
    "antq_reg_stuccoworks": ("pottery", "1.0", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_lead_foundry": ("tools", "1", (("iron", "0.8333"),)),
    "antq_reg_lapidary": ("jewelry", "1", (("goods_gold", "0.5208"),)),
    "antq_reg_sailmaker": ("naval_supplies", "1", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    "antq_reg_brewhouse": ("wine", "1", (("fruit", "1.154"), ("lumber", "0.157"), ("tools", "0.092"))),
    "antq_reg_quernworks": ("tools", "1", (("iron", "0.8333"),)),
    "antq_reg_textile_dye_finisher": ("dyes", "0.3", (("alum", "0.021"), ("lumber", "0.6247"))),
    # Fifth pass: every productive output below reuses a locally harvested
    # guild recipe; the ledger carries the historically specific input story.
    "antq_reg_monetal_workshop": ("jewelry", "1", (("goods_gold", "0.5208"),)),
    "antq_reg_hide_curing_yard": ("leather", "1", (("livestock", "1.0873"), ("sand", "0.4345"), ("tar", "0.0819"), ("tools", "0.1627"))),
    "antq_reg_bread_oven": ("wine", "1", (("fruit", "1.154"), ("lumber", "0.157"), ("tools", "0.092"))),
    "antq_reg_tegula_kiln": ("pottery", "1.0", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_stationer": ("books", "0.3", (("dyes", "0.0503"), ("paper", "0.1995"), ("lumber", "0.0998"))),
    "antq_reg_weightmaker": ("tools", "0.6", (("copper", "0.475"), ("tin", "0.038"))),
    "antq_reg_chariotwright": ("furniture", "1", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    "antq_reg_ferry_quay": ("naval_supplies", "1", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    # Sixth pass: exact local guild recipes remain the economy contract;
    # historical specificity belongs to the family ledger and art subject.
    "antq_reg_purple_dyehouse": ("dyes", "0.2", (("lumber", "0.4444"),)),
    "antq_reg_iron_bloomery": ("tools", "1", (("iron", "0.8333"),)),
    "antq_reg_tin_smelter": ("tools", "0.6", (("copper", "0.475"), ("tin", "0.038"))),
    "antq_reg_glass_bead_furnace": ("glass", "0.75", (("lumber", "0.1933"), ("sand", "0.9657"), ("tools", "0.3674"))),
    "antq_reg_cordwainer": ("leather", "1", (("livestock", "1.0873"), ("sand", "0.4345"), ("tar", "0.0819"), ("tools", "0.1627"))),
    "antq_reg_netmaker": ("naval_supplies", "1", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    "antq_reg_packsaddle_workshop": ("leather", "1", (("livestock", "1.0873"), ("sand", "0.4345"), ("tar", "0.0819"), ("tools", "0.1627"))),
    "antq_reg_stone_carver": ("tools", "1", (("iron", "0.8333"),)),
    "antq_reg_cooperage": ("furniture", "1", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    # Seventh pass: household, organic-material, and ornament crafts use the
    # same verified guild formulas while their specific antique inputs remain
    # transparent in the family ledger.
    "antq_reg_honey_house": ("wine", "1", (("fruit", "1.154"), ("lumber", "0.157"), ("tools", "0.092"))),
    "antq_reg_soapworks": ("dyes", "0.2", (("lumber", "0.4444"),)),
    "antq_reg_flax_retting_yard": ("cloth", "0.8", (("fiber_crops", "1.0"),)),
    "antq_reg_bone_carver": ("jewelry", "0.1", (("ivory", "0.1042"),)),
    "antq_reg_hornworker": ("jewelry", "0.1", (("ivory", "0.1042"),)),
    "antq_reg_amber_carver": ("jewelry", "1", (("goods_gold", "0.5208"),)),
    "antq_reg_coral_workshop": ("jewelry", "1", (("goods_gold", "0.5208"),)),
    "antq_reg_sponge_drying_yard": ("naval_supplies", "1", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    "antq_reg_reed_matmaker": ("furniture", "1", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    "antq_reg_lacquer_workshop": ("furniture", "1", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    "antq_reg_instrument_maker": ("furniture", "1", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    "antq_reg_figurine_kiln": ("pottery", "1.0", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    # Ninth pass: locally harvested guild formulas keep this dense material
    # expansion productive without inventing a new economic equation.
    "antq_reg_ironmongery": ("tools", "1", (("iron", "0.8333"),)),
    "antq_reg_bronze_vessel_shop": ("tools", "0.6", (("copper", "0.475"), ("tin", "0.038"))),
    "antq_reg_oil_lamp_kiln": ("pottery", "1.0", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_fineware_kiln": ("pottery", "1.0", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_scroll_workshop": ("books", "0.3", (("dyes", "0.0503"), ("paper", "0.1995"), ("lumber", "0.0998"))),
    "antq_reg_silverworkshop": ("jewelry", "1", (("goods_gold", "0.5208"),)),
    "antq_reg_arrow_fletchery": ("weaponry", "1", (("lumber", "0.2521"), ("coal", "0.3034"), ("tools", "0.505"))),
    "antq_reg_harness_maker": ("leather", "1", (("livestock", "1.0873"), ("sand", "0.4345"), ("tar", "0.0819"), ("tools", "0.1627"))),
    "antq_reg_wickerwork": ("furniture", "1", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    "antq_reg_loom_house": ("cloth", "0.8", (("fiber_crops", "1.0"),)),
    "antq_reg_cauldron_smithy": ("tools", "0.6", (("copper", "0.475"), ("tin", "0.038"))),
    "antq_reg_barge_chandlery": ("naval_supplies", "1", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
}


def csv_rows(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path.relative_to(ROOT)} must use header {','.join(fields)}")
        return [{field: (row.get(field) or "").strip() for field in fields} for row in reader]


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


def owner_regions() -> dict[str, str]:
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        roster = {row["tag"]: row["region"] for row in csv.DictReader(handle)}
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        result = {
            row["location"]: roster[row["tag"]]
            for row in csv.DictReader(line for line in handle if not line.startswith("#"))
        }
    return result


def load() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    families = csv_rows(FAMILIES, FAMILY_FIELDS)
    seeds = csv_rows(SEEDS, SEED_FIELDS)
    goods = set(json.loads(GOODS.read_text(encoding="utf-8-sig")))
    locations = set(json.loads(LOCATIONS.read_text(encoding="utf-8-sig")))
    regions = owner_regions()
    failures: list[str] = []
    family_keys: set[str] = set()
    for number, row in enumerate(families, start=2):
        prefix = f"{FAMILIES.relative_to(ROOT)}:{number}"
        if any(not row[field] for field in FAMILY_FIELDS):
            failures.append(f"{prefix}: blank required field")
        if not re.fullmatch(r"antq_reg_[a-z0-9_]+", row["key"]):
            failures.append(f"{prefix}: key must be a namespaced antq_reg_ identifier")
        if row["key"] in family_keys:
            failures.append(f"{prefix}: duplicate family key {row['key']}")
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
            if any(key not in MODIFIERS for key, _ in modifier_pairs):
                failures.append(f"{prefix}: unverified modifier")
            maintenance_pairs = pairs(row["maintenance"], "maintenance")
            listed_goods = {good.strip() for good in row["goods"].split(";") if good.strip()}
            if listed_goods != {good for good, _ in maintenance_pairs}:
                failures.append(f"{prefix}: goods must exactly describe maintenance inputs")
            unknown = listed_goods - goods
            if unknown:
                failures.append(f"{prefix}: unknown installed goods {sorted(unknown)}")
        except ValueError as exc:
            failures.append(f"{prefix}: {exc}")
        family_keys.add(row["key"])
    if len(family_keys) < 10:
        failures.append("regional building ledger must contain at least ten reusable production families")
    if len(PRODUCTION_RECIPES) / len(family_keys) < 0.7:
        failures.append("at least 70% of regional families must use calibrated productive guild recipes")
    unknown_recipes = set(PRODUCTION_RECIPES) - family_keys
    if unknown_recipes:
        failures.append(f"productive recipe map has unknown families {sorted(unknown_recipes)}")
    seen_keys: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    used: set[str] = set()
    macro_counts = {macro: 0 for macro in MACROS}
    for number, row in enumerate(seeds, start=2):
        prefix = f"{SEEDS.relative_to(ROOT)}:{number}"
        if any(not row[field] for field in SEED_FIELDS):
            failures.append(f"{prefix}: blank required field")
        if not re.fullmatch(r"reg_[a-z0-9_]+", row["key"]):
            failures.append(f"{prefix}: key must be a reg_ identifier")
        if row["key"] in seen_keys:
            failures.append(f"{prefix}: duplicate seed key {row['key']}")
        pair = (row["location"], row["family"])
        if pair in seen_pairs:
            failures.append(f"{prefix}: duplicate family/location placement {pair}")
        if row["family"] not in family_keys:
            failures.append(f"{prefix}: unknown family {row['family']}")
        if row["location"] not in locations or row["location"] not in regions:
            failures.append(f"{prefix}: location is unknown or uncontrolled at AD 1")
        if row["macro"] not in MACROS:
            failures.append(f"{prefix}: macro must be one of {sorted(MACROS)}")
        else:
            geographic_macro = MACRO_LOCATION_OVERRIDES.get(row["location"])
            if geographic_macro and geographic_macro != row["macro"]:
                failures.append(f"{prefix}: {row['location']} is outside declared {row['macro']} scope")
            elif not geographic_macro and regions.get(row["location"]) not in MACROS[row["macro"]]:
                failures.append(f"{prefix}: {row['location']} is outside declared {row['macro']} scope")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"{prefix}: confidence must be secure or contested")
        if row["macro"] in macro_counts:
            macro_counts[row["macro"]] += 1
        used.add(row["family"])
        seen_keys.add(row["key"])
        seen_pairs.add(pair)
    if len(seeds) < 100:
        failures.append("regional building seed ledger must contain at least 100 placements")
    if used != family_keys:
        failures.append(f"every family must be placed; missing={sorted(family_keys - used)}")
    if any(count == 0 for count in macro_counts.values()):
        failures.append(f"regional buildings must cover every requested macro: {macro_counts}")
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return families, seeds


def definition(families: list[dict[str, str]]) -> str:
    lines = [
        "# Generated by tools/m5_regional_buildings.py --write.",
        "# Reusable AD 1 regional production specials; ledger: docs/m5/regional_building_families.csv.",
        "",
    ]
    for row in families:
        lines.extend((f"{row['key']} = {{", "\taudio_tier = 2", "\tis_special = no", "\tis_foreign = no",
                      f"\tpop_type = {row['pop_type']}", "\tmax_levels = guild_max_level", "\tstartup_ramp_target = guild_startup_ramp_target", f"\tcategory = {row['category']}",
                      f"\temployment_size = {row['employment_size']}", "\ttown = yes", "\tcity = yes", "\tmegalopolis = yes",
                      f"\tbuild_time = {row['build_time']}", "\tmodifier = {"))
        for key, amount in pairs(row["modifier"], "modifier"):
            lines.append(f"\t\t{key} = {amount}")
        lines.extend(("\t}", "\tunique_production_methods = {", f"\t\t{row['key']}_maintenance = {{"))
        recipe = PRODUCTION_RECIPES.get(row["key"])
        if recipe:
            produced, output, inputs = recipe
            for good, amount in inputs:
                lines.append(f"\t\t\t{good} = {amount}")
            lines.extend((f"\t\t\tproduced = {produced}", f"\t\t\toutput = {output}", "\t\t\tdebug_max_profit = guild_profit_margin", "\t\t\tcategory = guild_input"))
        else:
            for good, amount in pairs(row["maintenance"], "maintenance"):
                lines.append(f"\t\t\t{good} = {amount}")
            lines.append("\t\t\tcategory = building_maintenance")
        lines.extend(("\t\t}", "\t}", "\tcustom_tags = { guild }", "\tconstruction_demand = guild_construction", "}", ""))
    return "\n".join(lines)


def loc(families: list[dict[str, str]], language: str) -> str:
    lines = [f"l_{language}:", " # Generated reusable AD 1 production-building localization; English mirrored by design."]
    for row in families:
        name = row["name"].replace('"', "'")
        description = row["description"].replace('"', "'")
        lines.append(f" {row['key']}: \"{name}\"")
        lines.append(f" {row['key']}_desc: \"{description}\"")
        lines.append(f" {row['key']}_maintenance: \"{name} Upkeep\"")
    return "\n".join(lines) + "\n"


def expected(families: list[dict[str, str]]) -> dict[Path, tuple[str, str]]:
    result: dict[Path, tuple[str, str]] = {OUTPUT: (definition(families), "utf-8-sig")}
    for language in LANGUAGES:
        result[LOC_ROOT / language / f"antq_m5_regional_buildings_l_{language}.yml"] = (loc(families, language), "utf-8-sig")
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


def validate_art(families: list[dict[str, str]]) -> None:
    failures = []
    for row in families:
        icon = ICON_DIR / f"{row['key']}.dds"
        if not icon.is_file():
            failures.append(f"missing direct regional building icon {icon.relative_to(ROOT)}")
        elif not dds_ok(icon):
            failures.append(f"invalid 128px RGBA DDS regional building icon {icon.relative_to(ROOT)}")
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
        families, seeds = load()
        outputs = expected(families)
        if args.write:
            for path, (content, encoding) in outputs.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding=encoding, newline="\n")
        stale = [path.relative_to(ROOT) for path, (content, encoding) in outputs.items() if not path.is_file() or path.read_text(encoding=encoding) != content]
        if stale:
            raise ValueError(f"stale or missing generated regional-building output: {stale}")
        validate_art(families)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m5_regional_buildings: FAIL\n  - {exc}")
        return 1
    print(f"m5_regional_buildings: PASS ({len(families)} direct-art families; {len(PRODUCTION_RECIPES)} calibrated productive / {len(families) - len(PRODUCTION_RECIPES)} maintenance families; {len(seeds)} regional AD 1 placements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

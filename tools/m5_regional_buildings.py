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
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

from extract_vanilla import tokenize
from economy_chains import (
    ai_capital_affordability_trigger,
    construction_package,
    institutional_upkeep,
    merge_goods,
)


ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ROOT / "docs/m5/regional_building_families.csv"
SEEDS = ROOT / "docs/m5/regional_building_seeds.csv"
CORE_MARKET_SEEDS = ROOT / "docs/m5/opening_market_building_seeds.csv"
REGIONAL_SEED_BUNDLES = ROOT / "docs/m5/s2_britain_ireland_building_seeds.csv"
FOOD_SEEDS = ROOT / "docs/m5/food_building_seeds.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
URBAN_NODES = ROOT / "docs/m5/urban_nodes.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
GOODS = ROOT / "docs/vanilla_symbols/good.json"
CUSTOM_GOODS = ROOT / "docs/m5/custom_goods.csv"
ADVANCES = ROOT / "docs/m8/advances.csv"
LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
ICON_DIR = ROOT / "main_menu/gfx/interface/icons/buildings"
OUTPUT = ROOT / "in_game/common/building_types/00_antiquitas_regional_buildings.txt"
METHOD_LEDGER = ROOT / "docs/m5/regional_production_methods.csv"
LATER_ANTIQUE_GOODS = ROOT / "docs/m5/later_antique_goods.csv"
LOC_ROOT = ROOT / "main_menu/localization"
DDS = ROOT / "tools/dds.py"
LOCAL_PATHS = ROOT / "config/local_paths.json"
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
BUNDLE_FIELDS = ("key", "families", "location", "macro", "source", "confidence", "note")
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
    "local_distance_from_capital_speed_propagation", "local_max_literacy",
    "local_garrison_size", "local_life_expectancy", "local_max_control", "local_merchant_capacity",
    "local_merchant_power", "local_monthly_control", "local_monthly_food_modifier", "local_population_capacity",
    "local_proximity_source",
    "local_production_efficiency", "local_repair_speed", "local_sailors", "local_unrest",
}
MACROS = {
    "Europe": {"Rome", "Britain", "Ireland", "Germania", "Balkans", "Danube", "Eastern Europe", "Baltic", "Finland", "Scandinavia", "Pontic"},
    "North Africa": {"Africa"},
    "Middle East": {"Anatolia", "Levant", "Mesopotamia", "Iran", "Arabia", "Caucasus"},
    "Central Asia": {"Steppe", "Central Asia", "Tarim"},
    "South Asia": {"India", "Lanka"},
    "Southeast Asia": {"Southeast Asia"},
    "East Asia": {"China", "Korea", "Japan"},
    "West Africa": {"West Africa"},
    "Americas": {"Andes", "Northern Andes", "Mesoamerica", "North America", "Caribbean-Amazon"},
    "Oceania": {"Oceania"},
}
# The AD 1 polity ledger uses political/cultural regions, not a geographic
# continent taxonomy: Roman Alexandria and Carthage are therefore tagged
# ``Rome`` there, while Antioch and Sidon can be Iranian-client space.  These
# reviewed city-point overrides keep the placement audit geographical.
MACRO_LOCATION_OVERRIDES = {
    "alexandria": "North Africa", "tunis": "North Africa",
    "annaba": "North Africa", "bizerte": "North Africa",
    "gabes": "North Africa", "sousse": "North Africa",
    "ashmunayn": "North Africa", "siwa": "North Africa",
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
    # Tenth pass: all additions use existing harvested guild recipes.
    "antq_reg_combmaker": ("jewelry", "0.1", (("ivory", "0.1042"),)),
    "antq_reg_bell_foundry": ("tools", "0.6", (("copper", "0.475"), ("tin", "0.038"))),
    "antq_reg_oarwright": ("naval_supplies", "1", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    "antq_reg_spindlework": ("cloth", "0.8", (("fiber_crops", "1.0"),)),
    "antq_reg_torchmaker": ("furniture", "1", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    "antq_reg_sieve_maker": ("furniture", "1", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    "antq_reg_mortar_grinder": ("tools", "1", (("iron", "0.8333"),)),
    "antq_reg_seal_cutter": ("jewelry", "1", (("goods_gold", "0.5208"),)),
    "antq_reg_kiln_furniture": ("pottery", "1.0", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_reed_pen_maker": ("books", "0.3", (("dyes", "0.0503"), ("paper", "0.1995"), ("lumber", "0.0998"))),
    "antq_reg_sail_needle_shop": ("naval_supplies", "1", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    "antq_reg_pulley_workshop": ("naval_supplies", "1", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    # Eleventh pass: exact harvested guild outputs keep a dense craft system
    # productive without creating unsupported price or output coefficients.
    "antq_reg_locksmith": ("tools", "0.6", (("copper", "0.475"), ("tin", "0.038"))),
    "antq_reg_nailery": ("tools", "1", (("iron", "0.8333"),)),
    "antq_reg_chainmaker": ("tools", "1", (("iron", "0.8333"),)),
    "antq_reg_wiredrawer": ("tools", "0.6", (("copper", "0.475"), ("tin", "0.038"))),
    "antq_reg_shieldmaker": ("weaponry", "1", (("lumber", "0.2521"), ("coal", "0.3034"), ("tools", "0.505"))),
    "antq_reg_scabbard_maker": ("leather", "1", (("livestock", "1.0873"), ("sand", "0.4345"), ("tar", "0.0819"), ("tools", "0.1627"))),
    "antq_reg_fishing_tackle": ("naval_supplies", "1", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    "antq_reg_feltworks": ("cloth", "1", (("wool", "1.0"),)),
    "antq_reg_carpet_loom": ("cloth", "1", (("wool", "1.0"),)),
    "antq_reg_cork_workshop": ("furniture", "1", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    "antq_reg_brushmaker": ("furniture", "1", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    "antq_reg_tesserae_kiln": ("glass", "0.75", (("lumber", "0.1933"), ("sand", "0.9657"), ("tools", "0.3674"))),
    # Twelfth pass: these contracts deliberately expose finished goods that
    # mattered to an AD 1 urban economy (medicaments, fine cloth, fermented
    # drink, masonry, and crucible steel).  Inputs/output coefficients are
    # copied from the installed productive methods rather than guessed.
    "antq_reg_herbal_apothecary": ("medicaments", "0.5", (("wild_game", "0.0461"), ("fiber_crops", "0.1853"))),
    "antq_reg_wool_drapery": ("fine_cloth", "0.5", (("wool", "1.0"),)),
    "antq_reg_silk_drapery": ("fine_cloth", "0.7", (("silk", "0.875"),)),
    "antq_reg_dye_finishing_house": ("fine_cloth", "0.2", (("alum", "0.0522"), ("dyes", "0.2108"))),
    "antq_reg_wheat_brewery": ("beer", "1", (("wheat", "0.9944"), ("lumber", "0.2484"), ("tools", "0.0999"))),
    "antq_reg_millet_brewery": ("beer", "1", (("millet", "0.9944"), ("lumber", "0.2484"), ("tools", "0.0999"))),
    "antq_reg_fruit_brewery": ("beer", "1", (("fruit", "1.0412"), ("lumber", "0.208"), ("tools", "0.1045"))),
    "antq_reg_rice_brewery": ("beer", "1", (("rice", "0.9944"), ("lumber", "0.2484"), ("tools", "0.0999"))),
    "antq_reg_stone_masonry_yard": ("masonry", "0.5", (("stone", "0.417"),)),
    "antq_reg_clay_brickworks": ("masonry", "0.5", (("clay", "0.833"),)),
    # The installed steel-mill input pair is retained, while the output is
    # calibrated against the live guild profit guard (20% +/- 1%) rather than
    # inheriting the later mill's higher margin.
    "antq_reg_crucible_steel_workshop": ("steel", "3.56", (("iron", "2.963"), ("coal", "2.963"))),
    "antq_reg_materia_medica": ("medicaments", "0.5", (("mercury", "0.0181"), ("ivory", "0.0906"))),
}

# The older expansion passes deliberately copied exact installed guild
# equations even when their output had little to do with the workshop name.
# These source-led overrides make the economic identity real.  Coefficients
# preserve the locally verified 20% guild margin at default prices.
COHERENT_RECIPE_OVERRIDES = {
    "antq_reg_olive_press": ("antq_olive_oil", "0.76", (("olives", "1.20"), ("pottery", "0.12"), ("tools", "0.05"), ("lumber", "0.08"))),
    "antq_reg_fish_saltery": ("antq_preserved_fish", "0.77", (("fish", "1.20"), ("salt", "0.12"), ("pottery", "0.10"), ("tools", "0.05"))),
    "antq_reg_grain_mill": ("antq_grain_products", "1.10", (("wheat", "1.00"), ("lumber", "0.15"), ("tools", "0.05"))),
    "antq_reg_bread_oven": ("antq_grain_products", "1.10", (("wheat", "1.00"), ("lumber", "0.15"), ("tools", "0.05"))),
    "antq_reg_oil_bottler": ("antq_olive_oil", "0.76", (("olives", "1.20"), ("pottery", "0.12"), ("tools", "0.05"), ("lumber", "0.08"))),
    "antq_reg_garum_workshop": ("antq_preserved_fish", "0.77", (("fish", "1.20"), ("salt", "0.12"), ("pottery", "0.10"), ("tools", "0.05"))),
    "antq_reg_incense_workshop": ("antq_perfumes", "0.52", (("incense", "0.80"), ("olives", "0.20"), ("pottery", "0.10"), ("tools", "0.10"))),
    "antq_reg_perfumery": ("antq_perfumes", "0.52", (("incense", "0.80"), ("olives", "0.20"), ("pottery", "0.10"), ("tools", "0.10"))),
    "antq_reg_wax_workshop": ("antq_wax_goods", "0.82", (("beeswax", "0.80"), ("fiber_crops", "0.20"), ("pottery", "0.10"), ("tools", "0.10"))),
    "antq_reg_torchmaker": ("antq_wax_goods", "0.82", (("beeswax", "0.80"), ("fiber_crops", "0.20"), ("pottery", "0.10"), ("tools", "0.10"))),
    "antq_reg_soapworks": ("antq_soap", "0.80", (("olives", "0.70"), ("lumber", "0.25"), ("pottery", "0.10"), ("tools", "0.05"))),
    "antq_reg_bronze_foundry": ("antq_bronze_wares", "0.86", (("copper", "0.70"), ("tin", "0.15"), ("coal", "0.15"), ("tools", "0.05"))),
    "antq_reg_copper_smithy": ("antq_bronze_wares", "0.86", (("copper", "0.70"), ("tin", "0.15"), ("coal", "0.15"), ("tools", "0.05"))),
    "antq_reg_tin_smelter": ("antq_bronze_wares", "0.86", (("copper", "0.70"), ("tin", "0.15"), ("coal", "0.15"), ("tools", "0.05"))),
    "antq_reg_weightmaker": ("antq_bronze_wares", "0.86", (("copper", "0.70"), ("tin", "0.15"), ("coal", "0.15"), ("tools", "0.05"))),
    "antq_reg_bronze_vessel_shop": ("antq_bronze_wares", "0.86", (("copper", "0.70"), ("tin", "0.15"), ("coal", "0.15"), ("tools", "0.05"))),
    "antq_reg_cauldron_smithy": ("antq_bronze_wares", "0.86", (("copper", "0.70"), ("tin", "0.15"), ("coal", "0.15"), ("tools", "0.05"))),
    "antq_reg_bell_foundry": ("antq_bronze_wares", "0.86", (("copper", "0.70"), ("tin", "0.15"), ("coal", "0.15"), ("tools", "0.05"))),
    "antq_reg_lead_foundry": ("antq_lead_wares", "0.88", (("lead", "0.80"), ("coal", "0.15"), ("tools", "0.10"))),
    "antq_reg_dye_workshop": ("fine_cloth", "0.49", (("cloth", "0.50"), ("dyes", "0.20"), ("tools", "0.05"))),
    "antq_reg_alum_dyehouse": ("fine_cloth", "0.49", (("cloth", "0.50"), ("dyes", "0.20"), ("tools", "0.05"))),
    "antq_reg_mordant_dyehouse": ("fine_cloth", "0.49", (("cloth", "0.50"), ("dyes", "0.20"), ("tools", "0.05"))),
    "antq_reg_purple_dyehouse": ("fine_cloth", "0.49", (("cloth", "0.50"), ("dyes", "0.20"), ("tools", "0.05"))),
    "antq_reg_textile_dye_finisher": ("fine_cloth", "0.49", (("cloth", "0.50"), ("dyes", "0.20"), ("tools", "0.05"))),
    "antq_reg_silk_loom": ("fine_cloth", "0.70", (("silk", "0.875"),)),
    "antq_reg_scriptorium": ("books", "0.78", (("antq_papyrus", "0.40"), ("dyes", "0.05"), ("lumber", "0.10"))),
    "antq_reg_papyrus_workshop": ("paper", "1.17", (("antq_papyrus", "0.40"), ("dyes", "0.05"), ("lumber", "0.10"))),
    "antq_reg_scroll_workshop": ("books", "0.78", (("antq_papyrus", "0.40"), ("dyes", "0.05"), ("lumber", "0.10"))),
    "antq_reg_stationer": ("books", "0.78", (("antq_papyrus", "0.40"), ("dyes", "0.05"), ("lumber", "0.10"))),
    "antq_reg_reed_pen_maker": ("books", "0.78", (("antq_papyrus", "0.40"), ("dyes", "0.05"), ("lumber", "0.10"))),
    "antq_reg_weapon_smith": ("weaponry", "1.06", (("iron", "0.60"), ("lumber", "0.20"), ("coal", "0.20"), ("tools", "0.05"))),
    "antq_reg_scale_armoury": ("weaponry", "1.08", (("iron", "0.50"), ("copper", "0.15"), ("leather", "0.20"), ("tools", "0.05"))),
    "antq_reg_arrow_fletchery": ("weaponry", "1.20", (("lumber", "0.60"), ("iron", "0.35"), ("tools", "0.35"))),
    "antq_reg_shieldmaker": ("weaponry", "1.20", (("lumber", "0.50"), ("leather", "0.35"), ("iron", "0.20"), ("tools", "0.20"))),
    "antq_reg_brickworks": ("masonry", "0.96", (("clay", "1.60"),)),
    "antq_reg_lime_kiln": ("masonry", "1.38", (("stone", "0.70"), ("lumber", "0.20"), ("tools", "0.05"))),
    "antq_reg_marble_yard": ("masonry", "5.94", (("marble", "0.80"), ("stone", "0.50"), ("tools", "0.15"))),
    "antq_reg_mosaic_workshop": ("masonry", "3.48", (("stone", "0.80"), ("glass", "0.50"), ("tools", "0.20"))),
    "antq_reg_stuccoworks": ("masonry", "1.80", (("stone", "0.60"), ("clay", "0.60"), ("lumber", "0.20"), ("tools", "0.10"))),
    "antq_reg_quernworks": ("masonry", "1.80", (("stone", "1.20"), ("iron", "0.05"), ("tools", "0.05"))),
    "antq_reg_stone_carver": ("masonry", "2.40", (("stone", "1.20"), ("marble", "0.10"), ("tools", "0.10"))),
    "antq_reg_mortar_grinder": ("masonry", "1.80", (("stone", "1.20"), ("iron", "0.05"), ("tools", "0.05"))),
    "antq_reg_brewhouse": ("beer", "1.00", (("wheat", "0.9944"), ("lumber", "0.2484"), ("tools", "0.0999"))),
    "antq_reg_honey_house": ("beer", "1.00", (("fruit", "1.0412"), ("lumber", "0.208"), ("tools", "0.1045"))),
    "antq_reg_bone_carver": ("jewelry", "0.396", (("livestock", "0.80"), ("tools", "0.15"))),
    "antq_reg_hornworker": ("jewelry", "0.396", (("livestock", "0.80"), ("tools", "0.15"))),
    "antq_reg_beadworks": ("jewelry", "1.08", (("glass", "0.80"), ("dyes", "0.30"), ("tools", "0.30"))),
    # Exact installed tar-kiln contract: a period-safe wood-pitch producer.
    "antq_reg_charcoal_hearth": ("tar", "1.0", (("lumber", "1.1111"),)),
    "antq_reg_villa_rustica": ("antq_grain_products", "1.10", (("wheat", "1.00"), ("lumber", "0.15"), ("tools", "0.05"))),
    "antq_reg_annona_bakery": ("antq_grain_products", "1.10", (("wheat", "1.00"), ("lumber", "0.15"), ("tools", "0.05"))),
    "antq_reg_quarry_contractors": ("masonry", "2.16", (("stone", "1.20"), ("lumber", "0.20"), ("tools", "0.10"))),
    "antq_reg_olive_estate": ("antq_olive_oil", "0.76", (("olives", "1.20"), ("pottery", "0.12"), ("tools", "0.05"), ("lumber", "0.08"))),
    "antq_reg_vineyard_estate": ("wine", "1", (("fruit", "1.154"), ("lumber", "0.157"), ("tools", "0.092"))),
    "antq_reg_textile_quarter": ("cloth", "1", (("wool", "1.0"),)),
    "antq_reg_ceramic_quarter": ("pottery", "1.0", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_castra_fabrica": ("weaponry", "1.06", (("iron", "0.60"), ("lumber", "0.20"), ("coal", "0.20"), ("tools", "0.05"))),
    "antq_reg_bronze_workers_collegium": ("antq_bronze_wares", "0.86", (("copper", "0.70"), ("tin", "0.15"), ("coal", "0.15"), ("tools", "0.05"))),
    "antq_reg_lead_pipeworks": ("antq_lead_wares", "0.88", (("lead", "0.80"), ("coal", "0.15"), ("tools", "0.10"))),
    "antq_reg_unguentarium": ("antq_perfumes", "0.52", (("incense", "0.80"), ("olives", "0.20"), ("pottery", "0.10"), ("tools", "0.10"))),
    # Thirteenth pass: historically specific processed goods replace the last
    # conspicuous generic output aliases. Each coefficient preserves the
    # locally checked 20% default-price guild margin.
    "antq_reg_fineware_kiln": ("antq_fine_ceramics", "0.249", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_oil_lamp_kiln": ("antq_fine_ceramics", "0.249", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_ceramic_quarter": ("antq_fine_ceramics", "0.249", (("clay", "1.0039"), ("lumber", "0.1201"), ("tools", "0.0504"))),
    "antq_reg_glassworks": ("antq_glasswares", "0.450", (("lumber", "0.1933"), ("sand", "0.9657"), ("tools", "0.3674"))),
    "antq_reg_ironmongery": ("antq_iron_hardware", "1.000", (("iron", "0.8333"),)),
    "antq_reg_nailery": ("antq_iron_hardware", "1.000", (("iron", "0.8333"),)),
    "antq_reg_chainmaker": ("antq_iron_hardware", "1.000", (("iron", "0.8333"),)),
    "antq_reg_locksmith": ("antq_iron_hardware", "1.000", (("iron", "0.8333"),)),
    "antq_reg_wiredrawer": ("antq_iron_hardware", "0.600", (("copper", "0.475"), ("tin", "0.038"))),
    "antq_reg_leatherworks": ("antq_leather_goods", "1.000", (("livestock", "1.0873"), ("sand", "0.4345"), ("tar", "0.0819"), ("tools", "0.1627"))),
    "antq_reg_cordwainer": ("antq_leather_goods", "1.000", (("livestock", "1.0873"), ("sand", "0.4345"), ("tar", "0.0819"), ("tools", "0.1627"))),
    "antq_reg_saddlery": ("antq_leather_goods", "1.000", (("livestock", "1.0873"), ("sand", "0.4345"), ("tar", "0.0819"), ("tools", "0.1627"))),
    "antq_reg_harness_maker": ("antq_leather_goods", "1.000", (("livestock", "1.0873"), ("sand", "0.4345"), ("tar", "0.0819"), ("tools", "0.1627"))),
    "antq_reg_packsaddle_workshop": ("antq_leather_goods", "1.000", (("livestock", "1.0873"), ("sand", "0.4345"), ("tar", "0.0819"), ("tools", "0.1627"))),
    "antq_reg_scabbard_maker": ("antq_leather_goods", "1.000", (("livestock", "1.0873"), ("sand", "0.4345"), ("tar", "0.0819"), ("tools", "0.1627"))),
    "antq_reg_ropewalk": ("antq_cordage", "1.200", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    "antq_reg_netmaker": ("antq_cordage", "1.200", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    "antq_reg_fishing_tackle": ("antq_cordage", "1.200", (("lumber", "0.1963"), ("fiber_crops", "0.4906"), ("tar", "0.5393"), ("cloth", "0.0486"))),
    "antq_reg_parchmentery": ("antq_parchment", "0.773", (("leather", "0.80"), ("dyes", "0.05"), ("tools", "0.10"))),
    "antq_reg_lacquer_workshop": ("antq_lacquerware", "0.500", (("lumber", "0.9817"), ("dyes", "0.1468"), ("tools", "0.1468"))),
    "antq_reg_amber_carver": ("antq_amber_ornaments", "0.874", (("amber", "0.80"), ("goods_gold", "0.20"), ("tools", "0.10"))),
    "antq_reg_beadworks": ("antq_glass_beads", "1.350", (("glass", "0.80"), ("dyes", "0.30"), ("tools", "0.30"))),
    "antq_reg_glass_bead_furnace": ("antq_glass_beads", "1.350", (("glass", "0.80"), ("dyes", "0.30"), ("tools", "0.30"))),
    "antq_reg_carpet_loom": ("antq_carpets", "0.948", (("wool", "1.00"), ("dyes", "0.25"), ("tools", "0.15"))),
    "antq_reg_feltworks": ("antq_felt_goods", "1.200", (("wool", "1.00"),)),
    "antq_reg_sailmaker": ("antq_sailcloth", "0.960", (("fiber_crops", "0.60"), ("cloth", "0.30"), ("tools", "0.10"))),
    "antq_reg_shipyard": ("naval_supplies", "1.140", (("lumber", "0.30"), ("antq_cordage", "0.30"), ("antq_sailcloth", "0.25"), ("tar", "0.30"), ("iron", "0.10"))),
    # Fourteenth pass: regionally bounded foods use their own goods and retain
    # the same checked 20% default-price guild margin as the craft expansion.
    "antq_reg_date_drying_yard": ("antq_dried_fruit", "0.825", (("antq_dates", "1.00"), ("pottery", "0.05"), ("lumber", "0.05"))),
    "antq_reg_sesame_oil_press": ("antq_sesame_oil", "1.002", (("antq_sesame", "1.00"), ("pottery", "0.08"), ("lumber", "0.05"), ("tools", "0.05"))),
    "antq_reg_nut_grinding_house": ("antq_nut_pastes", "0.953", (("antq_tree_nuts", "1.00"), ("pottery", "0.05"), ("tools", "0.05"))),
    "antq_reg_coconut_workshop": ("antq_coconut_products", "0.923", (("antq_coconuts", "1.00"), ("pottery", "0.05"), ("tools", "0.05"))),
    "antq_reg_cheese_dairy": ("antq_cheese_curds", "0.975", (("livestock", "1.00"), ("salt", "0.10"), ("pottery", "0.05"))),
    "antq_reg_meat_curing_yard": ("antq_cured_meat", "0.891", (("livestock", "1.00"), ("salt", "0.20"), ("lumber", "0.05"))),
    "antq_reg_rice_wine_house": ("antq_rice_wine", "0.470", (("rice", "1.00"), ("pottery", "0.10"), ("lumber", "0.05"))),
    "antq_reg_soy_fermentary": ("antq_soy_condiments", "0.750", (("legumes", "1.00"), ("salt", "0.10"), ("pottery", "0.10"))),
    # Supply-gated later-antique product classes.  None is seeded at AD 1;
    # their dated building unlock is the first source and therefore the first
    # point at which no_demand_if_no_market_availability permits pop demand.
    "antq_reg_yue_celadon_kiln": ("antq_yue_celadon", "1.000", (("clay", "5.0000"), ("coal", "1.0000"), ("tools", "0.4444"))),
    "antq_reg_codex_bindery": ("antq_bound_codices", "1.000", (("antq_parchment", "1.0000"), ("leather", "0.3000"), ("antq_wax_goods", "0.2000"), ("tools", "0.1889"))),
    "antq_reg_diatretum_glasshouse": ("antq_cage_glass", "1.000", (("glass", "2.0000"), ("tools", "0.5000"))),
    "antq_reg_polychrome_goldsmith": ("antq_garnet_cloisonne", "1.000", (("gems", "1.0000"), ("goods_gold", "0.4000"), ("tools", "0.3778"))),
}
PRODUCTION_RECIPES.update(COHERENT_RECIPE_OVERRIDES)

# These handling/service buildings are intentionally non-productive: forcing a
# fake export good would again make their labels cosmetic.
for _service_key in ("antq_reg_sponge_drying_yard",):
    PRODUCTION_RECIPES.pop(_service_key, None)

# Productive families remain constructible through advances, but opening
# placement must respect securely different ancient production geographies.
_OLD_WORLD = {
    "Europe", "North Africa", "Middle East", "Central Asia", "South Asia",
    "Southeast Asia", "East Asia", "West Africa",
}
_OLD_WORLD_METAL = _OLD_WORLD - {"West Africa"}
_MEDITERRANEAN = {"Europe", "North Africa", "Middle East"}
_OUTPUT_MACRO_RESTRICTIONS = {
    "steel": {"South Asia"},
    "paper": {"North Africa"},
    "books": _OLD_WORLD,
    "antq_grain_products": _OLD_WORLD,
    "antq_olive_oil": _MEDITERRANEAN,
    "antq_soap": _MEDITERRANEAN,
    "antq_perfumes": _OLD_WORLD,
    "antq_lacquerware": {"East Asia"},
    "antq_amber_ornaments": {"Europe"},
    "antq_bronze_wares": _OLD_WORLD_METAL,
    "antq_lead_wares": _OLD_WORLD_METAL,
    "antq_iron_hardware": _OLD_WORLD,
    "antq_glasswares": {"Europe", "North Africa", "Middle East", "South Asia"},
    "antq_glass_beads": {
        "Europe", "North Africa", "Middle East", "Central Asia",
        "South Asia", "East Asia",
    },
    "antq_parchment": {
        "Europe", "North Africa", "Middle East", "Central Asia", "South Asia",
    },
    "antq_carpets": {
        "Europe", "Middle East", "Central Asia", "South Asia", "East Asia",
    },
    "antq_felt_goods": {"Europe", "Middle East", "Central Asia", "East Asia"},
    "antq_sailcloth": _OLD_WORLD | {"Oceania"},
    "antq_yue_celadon": {"East Asia"},
    "antq_bound_codices": _MEDITERRANEAN,
    "antq_cage_glass": _MEDITERRANEAN,
    "antq_garnet_cloisonne": {"Europe", "Central Asia"},
}
FAMILY_MACRO_RESTRICTIONS = {
    family: frozenset(_OUTPUT_MACRO_RESTRICTIONS[output])
    for family, (output, _amount, _inputs) in PRODUCTION_RECIPES.items()
    if output in _OUTPUT_MACRO_RESTRICTIONS
}
FAMILY_MACRO_RESTRICTIONS.update(
    {
        "antq_reg_silk_loom": frozenset({"East Asia"}),
        "antq_reg_silk_drapery": frozenset({"East Asia"}),
    }
)
PRODUCTIVE_METHOD_TIERS = (
    ("maintenance", "Established Practice", 1.00, 1.00, "opening"),
    ("organized", "Organized Workshop", 1.081, 1.08, "age_3_discovery"),
    ("intensive", "Specialist Workshop", 1.182, 1.18, "age_4_reformation"),
)


def productive_method_key(building: str, suffix: str) -> str:
    # EU5's 32-bit localization hash collides for the ordinary honey-house
    # intensive slug and the installed location key `fatezh`.
    if building == "antq_reg_honey_house" and suffix == "intensive":
        return "antq_reg_honey_house_specialist"
    return f"{building}_{suffix}"

TAR_KILN_FAMILIES = {"antq_reg_charcoal_hearth"}
WATER_OR_PORT_FAMILIES = {
    "antq_reg_shipyard", "antq_reg_reed_boatyard", "antq_reg_bargeyard",
    "antq_reg_ferry_quay", "antq_reg_wharf_crane", "antq_reg_barge_chandlery",
    "antq_reg_oarwright", "antq_reg_sailmaker", "antq_reg_sail_needle_shop",
    "antq_reg_pulley_workshop", "antq_reg_river_port",
}
# Fresh-bookmark probes on installed build 24187685 reject these engine-map
# points for coastal/river-only potential. Keep the observed contract here so
# later bulk seed passes cannot silently restore invalid maritime placements.
RUNTIME_NON_WATER_LOCATIONS = {"damascus", "jerusalem", "milano"}
ROMAN_ECONOMY_FAMILIES = {
    "antq_reg_villa_rustica", "antq_reg_tabernae_row", "antq_reg_forum_basilica",
    "antq_reg_horrea_complex", "antq_reg_annona_bakery", "antq_reg_aqueduct_distribution",
    "antq_reg_thermae_complex", "antq_reg_cursus_mansio", "antq_reg_river_port",
    "antq_reg_colonia_forum", "antq_reg_castra_fabrica", "antq_reg_frontier_magazine",
    "antq_reg_quarry_contractors", "antq_reg_olive_estate", "antq_reg_vineyard_estate",
    "antq_reg_textile_quarter", "antq_reg_ceramic_quarter", "antq_reg_insulae_quarter",
    "antq_reg_temple_precinct", "antq_reg_collegia_hall", "antq_reg_bronze_workers_collegium",
    "antq_reg_lead_pipeworks", "antq_reg_unguentarium",
}
FAMILY_EXACT_TAG_GATES = {
    "antq_reg_south_arabian_terrace_sluices": ("HAD", "HIM", "QAT", "SAB"),
    "antq_reg_arabian_caravan_station": ("AGR", "BED", "NAB", "THM"),
    "antq_reg_aromatic_resin_sorting_house": ("HAD", "HIM", "QAT", "SAB"),
    "antq_reg_eastern_arabian_aflaj": ("GRH", "OMN"),
    "antq_reg_marcomannic_royal_compound": ("MCM",),
    "antq_reg_semnonian_sacred_grove": ("SEM",),
    "antq_reg_rhine_frontier_market": ("BRC", "BTV", "CHT"),
    "antq_reg_batavian_auxiliary_muster": ("BTV",),
    "antq_reg_aestian_amber_sorting_ground": ("AES",),
    "antq_reg_vistula_migration_staging": ("GUT",),
    "antq_reg_north_sea_boat_landing": ("FRI", "LAN"),
    "antq_reg_southern_rock_shelter_custody": ("LMP", "ZHF"),
    "antq_reg_seasonal_waterhole_camp": ("LMP", "ZHF"),
    "antq_reg_riverine_gathering_ground": ("LMP", "ZHF"),
}
FAMILY_CULTURE_GROUP_GATES = {
    "antq_reg_germanic_assembly_field": ("antq_germanic_group",),
    "antq_reg_silk_loom": (
        "antq_sinitic_group", "antq_korean_group", "antq_japonic_group",
    ),
    "antq_reg_silk_drapery": (
        "antq_sinitic_group", "antq_korean_group", "antq_japonic_group",
    ),
    "antq_reg_lacquer_workshop": (
        "antq_sinitic_group", "antq_korean_group", "antq_japonic_group",
    ),
    "antq_reg_yue_celadon_kiln": (
        "antq_sinitic_group", "antq_korean_group", "antq_japonic_group",
    ),
}
FAMILY_REGION_RESTRICTIONS = {
    **{key: frozenset({"Arabia"}) for key in (
        "antq_reg_south_arabian_terrace_sluices",
        "antq_reg_arabian_caravan_station",
        "antq_reg_aromatic_resin_sorting_house",
        "antq_reg_eastern_arabian_aflaj",
    )},
    **{key: frozenset({"Germania"}) for key in (
        "antq_reg_marcomannic_royal_compound",
        "antq_reg_germanic_assembly_field",
        "antq_reg_semnonian_sacred_grove",
        "antq_reg_rhine_frontier_market",
        "antq_reg_batavian_auxiliary_muster",
        "antq_reg_north_sea_boat_landing",
    )},
    "antq_reg_aestian_amber_sorting_ground": frozenset({"Baltic"}),
    # Gutones are a Germania polity profile on the lower-Vistula Baltic macro.
    "antq_reg_vistula_migration_staging": frozenset({"Germania"}),
    **{key: frozenset({"Africa"}) for key in (
        "antq_reg_southern_rock_shelter_custody",
        "antq_reg_seasonal_waterhole_camp",
        "antq_reg_riverine_gathering_ground",
    )},
    **{key: frozenset({"China", "Korea", "Japan"}) for key in (
        "antq_reg_silk_loom",
        "antq_reg_silk_drapery",
        "antq_reg_lacquer_workshop",
    )},
    **{key: frozenset({"Rome"}) for key in ROMAN_ECONOMY_FAMILIES},
}
CITY_ONLY_FAMILIES = {
    "antq_reg_forum_basilica", "antq_reg_horrea_complex", "antq_reg_aqueduct_distribution",
    "antq_reg_thermae_complex", "antq_reg_insulae_quarter", "antq_reg_temple_precinct",
    "antq_reg_collegia_hall",
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


def engine_tags() -> dict[str, str]:
    return {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8"))["entries"]
    }


def good_prices() -> dict[str, float]:
    """Read default prices from the pinned local engine and custom-goods ledger."""
    config = json.loads(LOCAL_PATHS.read_text(encoding="utf-8-sig"))
    directory = Path(str(config["game_dir"])) / "game/in_game/common/goods"
    if not directory.is_dir():
        raise ValueError(f"installed goods directory is missing: {directory}")
    result: dict[str, float] = {}
    for path in directory.glob("*.txt"):
        tokens = list(tokenize(path.read_text(encoding="utf-8-sig", errors="strict")))
        depth = 0
        current = ""
        index = 0
        while index < len(tokens):
            value = tokens[index].value
            if depth == 0 and index + 2 < len(tokens) and tokens[index + 1].value == "=" and tokens[index + 2].value == "{":
                current = value
            if value == "{":
                depth += 1
            elif value == "}":
                depth -= 1
                if depth == 0:
                    current = ""
            elif (
                depth == 1 and current and value == "default_market_price"
                and index + 2 < len(tokens) and tokens[index + 1].value == "="
            ):
                try:
                    result[current] = float(tokens[index + 2].value)
                except ValueError as exc:
                    raise ValueError(f"{path.name}: nonnumeric default price for {current}") from exc
            index += 1
    with CUSTOM_GOODS.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            result[(row.get("key") or "").strip()] = float((row.get("price") or "").strip())
    return result


def expanded_seed_rows() -> list[dict[str, str]]:
    """Return every regional seed, including compact reviewed regional bundles."""
    seeds = csv_rows(SEEDS, SEED_FIELDS)
    seeds.extend(csv_rows(FOOD_SEEDS, SEED_FIELDS))
    seeds.extend(csv_rows(CORE_MARKET_SEEDS, SEED_FIELDS))
    for bundle in csv_rows(REGIONAL_SEED_BUNDLES, BUNDLE_FIELDS):
        bundled_families = tuple(part.strip() for part in bundle["families"].split("|"))
        if len(bundled_families) != 2 or any(not family for family in bundled_families):
            raise ValueError(
                f"{REGIONAL_SEED_BUNDLES.relative_to(ROOT)} bundle {bundle['key']} "
                "must contain exactly two families"
            )
        for index, family in enumerate(bundled_families, start=1):
            seeds.append({
                "key": f"reg_{bundle['key']}_{index}",
                "family": family,
                "location": bundle["location"],
                "macro": bundle["macro"],
                "source": bundle["source"],
                "confidence": bundle["confidence"],
                "note": bundle["note"],
            })
    return seeds


def load() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    families = csv_rows(FAMILIES, FAMILY_FIELDS)
    seeds = expanded_seed_rows()
    goods = set(json.loads(GOODS.read_text(encoding="utf-8-sig")))
    with CUSTOM_GOODS.open(encoding="utf-8-sig", newline="") as handle:
        goods.update((row.get("key") or "").strip() for row in csv.DictReader(handle))
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
            # Scalable guild families can reach ten levels.  EU5 validates
            # their aggregate local_sailors contribution against a 0.025 cap,
            # so each level must stay at or below 0.0025.  V25 reached level
            # ten on the fishing-tackle family and proved this is enforced at
            # runtime rather than merely being a tooltip-balance convention.
            sailor_values = [
                float(amount) for key, amount in modifier_pairs
                if key == "local_sailors"
            ]
            if any(amount > 0.0025 for amount in sailor_values):
                failures.append(
                    f"{prefix}: scalable local_sailors exceeds the 0.0025 "
                    "per-level engine cap"
                )
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
    for key, (produced, _output, inputs) in PRODUCTION_RECIPES.items():
        unknown_goods = {produced, *(good for good, _amount in inputs)} - goods
        if unknown_goods:
            failures.append(f"{key}: productive recipe uses unknown goods {sorted(unknown_goods)}")
    prices = good_prices()
    for key, (produced, output, inputs) in PRODUCTION_RECIPES.items():
        missing_prices = {produced, *(good for good, _amount in inputs)} - prices.keys()
        if missing_prices:
            failures.append(f"{key}: missing local default prices {sorted(missing_prices)}")
            continue
        input_value = sum(prices[good] * float(amount) for good, amount in inputs)
        output_value = prices[produced] * float(output)
        margin = output_value / input_value - 1 if input_value else -1
        if not 0.19 <= margin <= 0.21:
            failures.append(
                f"{key}: default-price guild margin {margin:.1%} must remain within 19%-21%"
            )
    with ADVANCES.open(encoding="utf-8-sig", newline="") as handle:
        unlock_profiles: dict[str, list[str]] = {key: [] for key in family_keys}
        for advance in csv.DictReader(handle):
            for token in (advance.get("unlocks") or "").split(";"):
                kind, separator, target = token.strip().partition("=")
                if separator and kind == "unlock_building" and target in unlock_profiles:
                    unlock_profiles[target].append((advance.get("eligibility") or "").strip())
    missing_unlocks = sorted(key for key, profiles in unlock_profiles.items() if not profiles)
    duplicate_unlocks = sorted(
        key for key, profiles in unlock_profiles.items()
        if len(profiles) != len(set(profiles))
        or (len(profiles) > 1 and any("Shared Foundations" in profile for profile in profiles))
    )
    if missing_unlocks:
        failures.append(f"regional families lack an advance unlock: {missing_unlocks}")
    if duplicate_unlocks:
        failures.append(
            "regional families repeat an unlock inside one profile or mix shared "
            f"and regional placement: {duplicate_unlocks}"
        )
    seen_keys: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    used: set[str] = set()
    macro_counts = {macro: 0 for macro in MACROS}
    urban_profiles = {
        row["location"]: row["profile"]
        for row in csv_rows(
            URBAN_NODES,
            ("key", "location", "profile", "source", "confidence", "note"),
        )
    }
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
        if row["family"] in CITY_ONLY_FAMILIES and urban_profiles.get(row["location"]) == "town":
            failures.append(f"{prefix}: city-only family is seeded at a town-profile location")
        if (
            row["family"] in WATER_OR_PORT_FAMILIES
            and row["location"] in RUNTIME_NON_WATER_LOCATIONS
        ):
            failures.append(f"{prefix}: water/port family is invalid at this runtime-checked location")
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
        allowed_macros = FAMILY_MACRO_RESTRICTIONS.get(row["family"])
        if allowed_macros is not None and row["macro"] not in allowed_macros:
            failures.append(
                f"{prefix}: {row['family']} is outside its reviewed production "
                f"macros {sorted(allowed_macros)}"
            )
        allowed_regions = FAMILY_REGION_RESTRICTIONS.get(row["family"])
        owner_region = regions.get(row["location"])
        if allowed_regions is not None and owner_region not in allowed_regions:
            failures.append(
                f"{prefix}: {row['family']} is outside its reviewed polity "
                f"regions {sorted(allowed_regions)}"
            )
        if row["macro"] in macro_counts:
            macro_counts[row["macro"]] += 1
        used.add(row["family"])
        seen_keys.add(row["key"])
        seen_pairs.add(pair)
    if len(seeds) < 100:
        failures.append("regional building seed ledger must contain at least 100 placements")
    # The bookmark intentionally samples regional capacity rather than placing
    # one instance of every buildable family. Productive recipes must remain
    # represented, while specialised civic families may begin uninstantiated.
    with LATER_ANTIQUE_GOODS.open(encoding="utf-8-sig", newline="") as handle:
        later_buildings = {
            (row.get("building") or "").strip() for row in csv.DictReader(handle)
        }
    if not later_buildings or not later_buildings <= set(PRODUCTION_RECIPES):
        failures.append("dated later-antique building portfolio is missing from recipes")
    seeded_late = sorted(later_buildings & used)
    if seeded_late:
        failures.append(f"later-antique buildings must not be seeded at AD 1: {seeded_late}")
    opening_productive = set(PRODUCTION_RECIPES) - later_buildings
    represented_productive = opening_productive & used
    productive_coverage = len(represented_productive) / len(opening_productive)
    if productive_coverage < 0.95:
        failures.append(
            "at least 95% of productive families must be represented in the "
            f"bounded bookmark sample; coverage={productive_coverage:.1%}"
        )
    required_macros = set(MACROS) - {"West Africa"}
    missing_macros = sorted(macro for macro in required_macros if macro_counts[macro] == 0)
    if missing_macros:
        failures.append(
            f"settled-country regional buildings miss required macros {missing_macros}: {macro_counts}"
        )
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return families, seeds


def definition(families: list[dict[str, str]]) -> str:
    lines = [
        "# Generated by tools/m5_regional_buildings.py --write.",
        "# Reusable AD 1 regional production specials; ledger: docs/m5/regional_building_families.csv.",
        "",
    ]
    tags = engine_tags()
    for row in families:
        lines.extend((f"{row['key']} = {{", "\taudio_tier = 2", "\tis_special = no", "\tis_foreign = no",
                      f"\tpop_type = {row['pop_type']}", "\tmax_levels = guild_max_level", "\tstartup_ramp_target = guild_startup_ramp_target", f"\tcategory = {row['category']}",
                      f"\temployment_size = {row['employment_size']}"))
        if row["key"] not in CITY_ONLY_FAMILIES:
            lines.append("\ttown = yes")
        lines.extend(("\tcity = yes", "\tmegalopolis = yes", f"\tbuild_time = {row['build_time']}",
                      "\tcountry_potential = {", *ai_capital_affordability_trigger()))
        if row["key"] in ROMAN_ECONOMY_FAMILIES:
            lines.extend((
                "\t\tOR = {",
                "\t\t\tculture = { has_culture_group = culture_group:antq_italic_group }",
                "\t\t\tculture = { has_culture_group = culture_group:antq_iberian_group }",
                "\t\t\tculture = { has_culture_group = culture_group:antq_balkan_group }",
                "\t\t\thas_embraced_institution = institution:antq_roman_law_engineering",
                "\t\t}",
            ))
        elif row["key"] in FAMILY_EXACT_TAG_GATES:
            lines.extend((
                "\t\tOR = {",
                *(
                    f"\t\t\thas_or_had_tag = {tags[design_tag]}"
                    for design_tag in FAMILY_EXACT_TAG_GATES[row["key"]]
                ),
                "\t\t}",
            ))
        elif row["key"] in FAMILY_CULTURE_GROUP_GATES:
            lines.extend((
                "\t\tOR = {",
                *(
                    "\t\t\tculture = { has_culture_group = "
                    f"culture_group:{culture_group} }}"
                    for culture_group in FAMILY_CULTURE_GROUP_GATES[row["key"]]
                ),
                "\t\t}",
            ))
        lines.extend((
            "\t}",
            "\tallow = {",
            "\t\talways = yes",
            "\t}",
        ))
        if row["key"] in TAR_KILN_FAMILIES:
            lines.append("\trural_settlement = yes")
        if row["key"] in WATER_OR_PORT_FAMILIES | CITY_ONLY_FAMILIES | TAR_KILN_FAMILIES:
            lines.append("\tlocation_potential = {")
            if row["key"] in WATER_OR_PORT_FAMILIES:
                lines.extend(("\t\tOR = {", "\t\t\tis_coastal = yes", "\t\t\thas_river = yes", "\t\t}"))
            if row["key"] in TAR_KILN_FAMILIES:
                lines.extend((
                    "\t\tOR = {",
                    "\t\t\tvegetation = forest",
                    "\t\t\tvegetation = woods",
                    "\t\t\tvegetation = jungle",
                    "\t\t\traw_material = goods:lumber",
                    "\t\t\tlocation_rank = location_rank:town",
                    "\t\t\tlocation_rank = location_rank:city",
                    "\t\t\tlocation_rank = location_rank:megalopolis",
                    "\t\t}",
                ))
            if row["key"] in CITY_ONLY_FAMILIES:
                lines.extend((
                    "\t\tOR = {",
                    "\t\t\tlocation_rank = location_rank:city",
                    "\t\t\tlocation_rank = location_rank:megalopolis",
                    "\t\t}",
                ))
            lines.append("\t}")
        lines.append("\tmodifier = {")
        for key, amount in pairs(row["modifier"], "modifier"):
            lines.append(f"\t\t{key} = {amount}")
        lines.extend(("\t}", "\tunique_production_methods = {"))
        recipe = PRODUCTION_RECIPES.get(row["key"])
        if recipe:
            produced, output, inputs = recipe
            for suffix, _name, output_mult, input_mult, _age in PRODUCTIVE_METHOD_TIERS:
                lines.append(f"\t\t{productive_method_key(row['key'], suffix)} = {{")
                for good, amount in inputs:
                    lines.append(f"\t\t\t{good} = {float(amount)*input_mult:.4f}")
                lines.extend((f"\t\t\tproduced = {produced}", f"\t\t\toutput = {float(output)*output_mult:.4f}", "\t\t\tdebug_max_profit = guild_profit_margin", "\t\t\tcategory = guild_input", "\t\t}"))
        else:
            lines.append(f"\t\t{row['key']}_maintenance = {{")
            maintenance = merge_goods(
                pairs(row["maintenance"], "maintenance"),
                institutional_upkeep(
                    row["key"], row["category"], productive=False,
                ),
            )
            for good, amount in maintenance:
                lines.append(f"\t\t\t{good} = {amount}")
            lines.append("\t\t\tcategory = building_maintenance")
            lines.append("\t\t}")
        lines.extend((
            "\t}", "\tcustom_tags = { guild }",
            f"\tconstruction_demand = {construction_package(row['key'], row['category'])}",
            "}", "",
        ))
    return "\n".join(lines)


def loc(families: list[dict[str, str]], language: str) -> str:
    lines = [f"l_{language}:", " # Generated reusable AD 1 production-building localization; English mirrored by design."]
    for row in families:
        name = row["name"].replace('"', "'")
        description = row["description"].replace('"', "'")
        lines.append(f" {row['key']}: \"{name}\"")
        lines.append(f" {row['key']}_desc: \"{description}\"")
        lines.append(f" {row['key']}_maintenance: \"{name} Upkeep\"")
        if row["key"] in PRODUCTION_RECIPES:
            for suffix, method_name, _output_mult, _input_mult, _age in PRODUCTIVE_METHOD_TIERS[1:]:
                lines.append(f" {productive_method_key(row['key'], suffix)}: \"{name}: {method_name}\"")
    return "\n".join(lines) + "\n"


def method_ledger(families: list[dict[str, str]]) -> str:
    fields=("key","building","tier","name","unlock_age","profile","output_multiplier","input_multiplier","source")
    stream=io.StringIO(newline=""); writer=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n"); writer.writeheader()
    by_key={row["key"]:row for row in families}
    for building in sorted(PRODUCTION_RECIPES):
        row=by_key[building]
        for suffix,name,output_mult,input_mult,age in PRODUCTIVE_METHOD_TIERS:
            writer.writerow({"key":productive_method_key(building, suffix),"building":building,"tier":suffix,"name":name,"unlock_age":age,"profile":"shared","output_multiplier":f"{output_mult:.3f}","input_multiplier":f"{input_mult:.3f}","source":row["source"]})
    return stream.getvalue()


def expected(families: list[dict[str, str]]) -> dict[Path, tuple[str, str]]:
    result: dict[Path, tuple[str, str]] = {OUTPUT: (definition(families), "utf-8-sig"), METHOD_LEDGER:(method_ledger(families),"utf-8-sig")}
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
    hashes: dict[str, str] = {}
    for row in families:
        icon = ICON_DIR / f"{row['key']}.dds"
        if not icon.is_file():
            failures.append(f"missing direct regional building icon {icon.relative_to(ROOT)}")
        elif not dds_ok(icon):
            failures.append(f"invalid 128px RGBA DDS regional building icon {icon.relative_to(ROOT)}")
        else:
            digest = hashlib.sha256(icon.read_bytes()).hexdigest()
            previous = hashes.setdefault(digest, row["key"])
            if previous != row["key"]:
                failures.append(f"regional building icons must be distinct: {previous} and {row['key']}")
    if failures:
        raise ValueError("\n".join(failures))


def validate_ai_affordability(families: list[dict[str, str]]) -> None:
    rendered = definition(families)
    failures = []
    if rendered.count("\tcountry_potential = {") != len(families):
        failures.append("regional country-affordability gate coverage drift")
    if rendered.count("\tallow = {") != len(families):
        failures.append("regional live affordability gate coverage drift")
    if rendered.count("\n".join(ai_capital_affordability_trigger())) != len(families):
        failures.append("regional country-affordability gate contract drift")
    if rendered.count("\tallow = {\n\t\talways = yes\n\t}") != len(families):
        failures.append("regional live construction allow must be player-reachable")
    if rendered.count("\trural_settlement = yes") != len(TAR_KILN_FAMILIES):
        failures.append("wood-tar kiln must be rural-constructible")
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
        validate_ai_affordability(families)
        validate_art(families)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m5_regional_buildings: FAIL\n  - {exc}")
        return 1
    print(f"m5_regional_buildings: PASS ({len(families)} direct-art families; {len(PRODUCTION_RECIPES)} calibrated productive / {len(families) - len(PRODUCTION_RECIPES)} maintenance families; {len(seeds)} regional AD 1 placements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

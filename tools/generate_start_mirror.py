#!/usr/bin/env python3
"""Generate ANTIQVITAS's exact-filename M3 start-manager mirror.

Setup managers are additive in EU5.  Replacing every installed start filename
is therefore the only locally verified way to prevent the 1337 snapshot from
surviving beneath the AD 1 database.  Content generators extend these roots in
later M3 batches; this first batch proves the empty roots are valid on build
24187685 before historical ownership is introduced.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from extract_vanilla import tokenize
from generate_country_definitions import historical_profile_for, load_integration_profiles
from m5_regional_buildings import CITY_ONLY_FAMILIES, expanded_seed_rows
from m6_power import character_manager, dynasty_manager, government_block, load_power_data
from m7_war import load_units, tag_map as m7_tag_map, validate_start_ledgers
from m8_knowledge import institution_manager as m8_institution_manager, technology_level as m8_technology_level
from m9_diplomacy import (
    START_ADAPTERS,
    discovery_regions as m9_discovery_regions,
    international_organization_manager as m9_international_organization_manager,
)
from s2_ancient_laws import starting_laws_by_tag

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "main_menu/setup/start"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
SUBJECTS = ROOT / "docs/world_1ad/subjects.csv"
SUBJECT_TYPES = ROOT / "docs/vanilla_symbols/subject_type.json"
POPULATION_TARGETS = ROOT / "docs/m4/population_targets.csv"
POPULATION_ALLOCATIONS = ROOT / "docs/m4/population_region_allocations.csv"
POPULATION_LOCATION_OVERRIDES = ROOT / "docs/m4/population_location_overrides.csv"
POPULATION_GEOGRAPHIC_ALLOCATIONS = ROOT / "docs/m4/population_geographic_allocations.csv"
POPULATION_CITY_TARGETS = ROOT / "docs/m4/population_city_targets.csv"
POPULATION_GEOGRAPHY = ROOT / "docs/m5/global_rgo_audit.csv"
CULTURE_REMAP = ROOT / "docs/culture_remap.csv"
RELIGION_REMAP = ROOT / "docs/religion_remap.csv"
M4_SYMBOLS = ROOT / "docs/m4/definition_symbols.json"
CULTURE_PRESENCE = ROOT / "docs/m12/culture_presence.csv"
GEOGRAPHY_HIERARCHY = ROOT / "docs/vanilla_symbols/geography_hierarchy.json"
VANILLA_AREAS = ROOT / "docs/vanilla_symbols/areas.json"
VANILLA_PROVINCES = ROOT / "docs/vanilla_symbols/provinces.json"
VANILLA_LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
VANILLA_REGIONS = ROOT / "docs/vanilla_symbols/regions.json"
MARKETS = ROOT / "docs/m5/markets.csv"
URBAN_NODES = ROOT / "docs/m5/urban_nodes.csv"
ROAD_SEGMENTS = ROOT / "docs/m5/road_segments.csv"
DEVELOPMENT_PROFILE = ROOT / "docs/m5/development_profile.csv"
SPECIAL_BUILDINGS = ROOT / "docs/m5/special_buildings.csv"
ROMAN_BUILDINGS = ROOT / "docs/m5/roman_buildings.csv"
ANCIENT_BUILDING_REPLACEMENTS = ROOT / "docs/m5/ancient_building_replacements.csv"
REGIONAL_BUILDINGS = ROOT / "docs/m5/regional_building_families.csv"
HISTORIC_BUILDING_SITES = ROOT / "docs/m5/historic_building_sites.csv"
M7_FORTS = ROOT / "docs/m7/forts.csv"
M7_ARMIES = ROOT / "docs/m7/armies.csv"
URBAN_SETUP_OUTPUT = ROOT / "in_game/common/town_setups/00_antiquitas.txt"
SUBJECT_FIELDS = ("overlord", "subject", "relationship", "source", "confidence", "note")

# Country rank is a game-facing title as well as a balance tier.  The AD 1
# roster's collective societies use the installed tribal title at county rank;
# sovereign and client courts use the installed kingdom title; only the three
# contemporary transregional empires receive the empire rank.  This prevents
# the engine's implicit county default from labelling every polity a county.
EMPIRE_RANK_TAGS = frozenset({"ROM", "PAR", "HAN"})


def country_rank(row: dict[str, str]) -> str:
    if row["tag"] in EMPIRE_RANK_TAGS:
        return "rank_empire"
    if row["kind"] == "sop":
        return "rank_county"
    return "rank_kingdom"


def m9_subject_adapter(row: dict[str, str]) -> str:
    """Map the checked AD 1 relationships to M9's ancient mechanics."""
    return START_ADAPTERS.get(row["overlord"], row["relationship"])
THOUSANDTH = Decimal("0.001")
MIN_LOCATION_POPULATION = Decimal("0.001")
MAX_UNTARGETED_LOCATION_POPULATION = Decimal("75.000")
OPENING_LIQUIDITY_POPULATION_CEILING = Decimal("500.000")
OPENING_LIQUIDITY_FLOOR = 250
COMPATIBILITY_LOCATION = "aachen"
COMPATIBILITY_POP_SIZE = Decimal("0.001")
COMPATIBILITY_RELIGION = "antq_germanic_religion"

TOWN_SETUP_BUILDINGS = (
    ("antq_reg_tabernae_row", 1),
    ("antq_reg_granary", 1),
)
CITY_SETUP_BUILDINGS = (
    ("antq_reg_temple_precinct", 1),
    ("antq_reg_tabernae_row", 1),
    ("antq_reg_horrea_complex", 1),
    ("antq_reg_granary", 1),
    ("antq_reg_stone_yard", 1),
)


def urban_town_setups() -> str:
    lines = [
        "# Generated by tools/generate_start_mirror.py --write.",
        "# M5 namespaced ancient buildings for AD 1 source-labelled market settlements.",
        "antiqvitas_market_town = {",
    ]
    lines.extend(f"\t{building} = {level}" for building, level in TOWN_SETUP_BUILDINGS)
    lines.extend(("}", "", "antiqvitas_market_city = {"))
    lines.extend(f"\t{building} = {level}" for building, level in CITY_SETUP_BUILDINGS)
    lines.extend(("}", ""))
    return "\n".join(lines)

DISEASE_MANAGER = """# Generated by tools/generate_start_mirror.py --write.
# M12 disease-manager initialization. Geographic values are broad population-
# immunity/endemicity adapters, not claims of a continuously recorded outbreak.
# Sources and interpretation: docs/m12/DISEASE_CRASH_FIX.md; docs/ASSUMPTIONS.md.
disease_outbreak_manager = {
\t# Long-connected Old World urban and exchange circuits had recurring exposure
\t# to acute crowd diseases; modest values avoid treating exposure as immunity.
\tadd_disease_resistance = {
\t\ttype = bubonic_plague
\t\tresistance = 0.02
\t\tregions = {
\t\t\titaly_region balkan_region anatolia_region crescent_region egypt_region
\t\t\tmaghreb_region nubia_region ethiopia_region arabia_region persia_region
\t\t\tkhorasan_region western_india_region central_india_region deccan_region
\t\t\tbengal_region hindustan_region indochina_region south_china_region
\t\t\teast_china_region north_china_region west_china_region
\t\t}
\t}
\tadd_disease_resistance = {
\t\ttype = great_pestilence
\t\tresistance = 0.01
\t\tregions = {
\t\t\titaly_region balkan_region anatolia_region crescent_region egypt_region
\t\t\tpersia_region khorasan_region western_india_region central_india_region
\t\t\tdeccan_region bengal_region hindustan_region north_china_region
\t\t\tsouth_china_region east_china_region
\t\t}
\t}
\tadd_disease_resistance = {
\t\ttype = influenza
\t\tresistance = 0.05
\t\tregions = {
\t\t\tscandinavian_region north_german_region south_german_region
\t\t\tgreat_britain_region ireland_region france_region iberia_region
\t\t\titaly_region carpathia_region baltic_region caucasus_region
\t\t\tsteppes_region russian_region ruthenia_region ural_region balkan_region
\t\t\tanatolia_region crescent_region egypt_region maghreb_region
\t\t\tarabia_region persia_region khorasan_region western_india_region
\t\t\tcentral_india_region deccan_region bengal_region hindustan_region
\t\t\tindochina_region indonesia_region north_china_region south_china_region
\t\t\teast_china_region west_china_region japan_region korea_region
\t\t\tmanchuria_region mongolia_region tibet_region xinjiang_region
\t\t}
\t}
\tadd_disease_resistance = {
\t\ttype = measles
\t\tresistance = 0.10
\t\tregions = {
\t\t\tnorth_german_region south_german_region great_britain_region
\t\t\tireland_region france_region iberia_region italy_region carpathia_region
\t\t\tbalkan_region anatolia_region crescent_region egypt_region maghreb_region
\t\t\tarabia_region persia_region khorasan_region western_india_region
\t\t\tcentral_india_region deccan_region bengal_region hindustan_region
\t\t\tindochina_region indonesia_region north_china_region south_china_region
\t\t\teast_china_region west_china_region japan_region korea_region
\t\t}
\t}
\tadd_disease_resistance = {
\t\ttype = smallpox
\t\tresistance = 0.15
\t\tregions = {
\t\t\tnorth_german_region south_german_region great_britain_region
\t\t\tireland_region france_region iberia_region italy_region carpathia_region
\t\t\tbalkan_region anatolia_region crescent_region egypt_region maghreb_region
\t\t\tnubia_region ethiopia_region arabia_region persia_region
\t\t\tkhorasan_region western_india_region central_india_region deccan_region
\t\t\tbengal_region hindustan_region indochina_region indonesia_region
\t\t\tnorth_china_region south_china_region east_china_region west_china_region
\t\t\tjapan_region korea_region manchuria_region
\t\t}
\t}
\tadd_disease_resistance = {
\t\ttype = typhus
\t\tresistance = 0.05
\t\tregions = {
\t\t\tiberia_region italy_region balkan_region anatolia_region crescent_region
\t\t\tegypt_region maghreb_region nubia_region ethiopia_region arabia_region
\t\t\tpersia_region khorasan_region western_india_region central_india_region
\t\t\tdeccan_region bengal_region hindustan_region indochina_region
\t\t\tindonesia_region north_china_region south_china_region east_china_region
\t\t}
\t}

\t# Malaria was an endemic ecological burden rather than a one-off dated event.
\tadd_disease_outbreaks = {
\t\ttype = malaria
\t\tregions = {
\t\t\titaly_region balkan_region anatolia_region crescent_region egypt_region
\t\t\tmaghreb_region nubia_region ethiopia_region arabia_region persia_region
\t\t\twestern_india_region central_india_region deccan_region bengal_region
\t\t\thindustan_region indochina_region indonesia_region south_china_region
\t\t\tguinea_region sahel_region kongo_region swahili_coast_region
\t\t\tgreat_lakes_region madagascar_region melanesia_region
\t\t}
\t}
\tadd_disease_resistance = {
\t\ttype = malaria
\t\tresistance = 0.20
\t\tregions = {
\t\t\titaly_region balkan_region anatolia_region crescent_region egypt_region
\t\t\tmaghreb_region nubia_region ethiopia_region arabia_region persia_region
\t\t\twestern_india_region central_india_region deccan_region bengal_region
\t\t\thindustan_region indochina_region indonesia_region south_china_region
\t\t\tguinea_region sahel_region kongo_region swahili_coast_region
\t\t\tgreat_lakes_region madagascar_region melanesia_region
\t\t}
\t}
}
"""

STATIC_FILES = {
    "02_core.txt": """institution_manager = {\n}\n\nreligion_manager = {\n}\n""",
    "08_institutions.txt": "locations = {\n}\n",
    "11_art.txt": "work_of_art_manager = {\n}\n",
    "13_religion.txt": "building_manager = {\n}\n",
    "16_wars.txt": "war_manager = {\n}\n",
    "18_opinions.txt": "diplomacy_manager = {\n}\n",
    "19_diseases.txt": DISEASE_MANAGER,
    "20_rivals.txt": "diplomacy_manager = {\n}\n",
    "21_locations.txt": "locations = {\n}\n",
    "22_situations.txt": "situation_manager = {\n}\n",
    "23_colonies.txt": "colony_manager = {\n}\n",
    "24_town_rights.txt": "townrights_manager = {\n}\n",
    "25_area_preferences.txt": "countries = {\n\tcountries = {\n\t}\n}\n",
    "26_ai_personalities.txt": "",
}


@dataclass(frozen=True)
class MacroTarget:
    target: Decimal
    minimum: Decimal | None
    maximum: Decimal | None
    source: str
    confidence: str
    note: str


@dataclass(frozen=True)
class RegionalAllocation:
    macro: str
    target: Decimal
    source: str
    confidence: str
    note: str


@dataclass(frozen=True)
class GeographicAllocation:
    parent_region: str
    target: Decimal
    locations: frozenset[str]
    source: str
    confidence: str
    note: str


@dataclass(frozen=True)
class CityPopulationTarget:
    place: str
    location: str
    mode: str
    city_proper_minimum: Decimal
    city_proper_maximum: Decimal
    agglomeration_minimum: Decimal
    agglomeration_maximum: Decimal
    game_target: Decimal | None
    game_minimum: Decimal | None
    game_maximum: Decimal | None
    hinterland_scope: str
    source: str
    confidence: str
    note: str


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def geography_leaves(selector: str, trail: tuple[str, ...] = ()) -> set[str]:
    """Expand a harvested region/area/province selector to installed locations."""
    hierarchy = json.loads(GEOGRAPHY_HIERARCHY.read_text(encoding="utf-8-sig"))

    def expand(key: str, path: tuple[str, ...]) -> set[str]:
        if key in path:
            raise ValueError(
                f"{GEOGRAPHY_HIERARCHY.relative_to(ROOT)} has cyclic selector "
                f"{' -> '.join((*path, key))}"
            )
        children = hierarchy.get(key)
        if not children:
            return {key}
        leaves: set[str] = set()
        for child in children:
            if child == key:
                leaves.add(child)
            else:
                leaves.update(expand(child, (*path, key)))
        return leaves

    return expand(selector, trail)


def market_manager() -> tuple[str, int]:
    """Render source-labelled AD 1 market hubs with installed location keys.

    The exact-name generic market overlay guards the installed selector against
    unset market locations and owner self-relations, so source-led hubs can be
    present from the first frame without the former monthly assertion.
    """
    locations = set(json.loads((ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")))
    required = ("key", "name", "location", "source", "confidence", "note")
    entries = csv_rows(MARKETS)
    if not entries:
        raise ValueError("markets.csv has no market entries")
    seen_keys: set[str] = set()
    seen_locations: set[str] = set()
    failures: list[str] = []
    for row in entries:
        if any(not row.get(field, "").strip() for field in required):
            failures.append("markets.csv contains a blank required field")
            continue
        key = row["key"].strip()
        location = row["location"].strip()
        if key in seen_keys:
            failures.append(f"markets.csv repeats key {key}")
        if location in seen_locations:
            failures.append(f"markets.csv repeats location {location}")
        if location not in locations:
            failures.append(f"markets.csv {key} uses unknown installed location {location}")
        if row["confidence"].strip() not in {"secure", "contested"}:
            failures.append(f"markets.csv {key} has invalid confidence {row['confidence']}")
        startup_mode = (row.get("startup_mode") or "seeded").strip()
        if startup_mode != "seeded":
            failures.append(f"markets.csv {key} has invalid startup_mode {startup_mode}")
        seen_keys.add(key)
        seen_locations.add(location)
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    lines = [
        "# Generated by tools/generate_start_mirror.py --write.",
        "# M5 AD 1 market hubs; source and proxy rationale: docs/m5/markets.csv.",
        "# tools/m8_knowledge.py guards the installed market selector against unset",
        "# location comparisons and owner self-relations.",
        "market_manager = {",
    ]
    for row in sorted(entries, key=lambda item: item["key"]):
        lines.append(
            f"\tadd_market = {row['location']} # {row['name']}; {row['source']}"
        )

    lines.extend(("}", ""))
    return "\n".join(lines), len(entries)


def ai_personality_manager() -> str:
    """Give every opening polity a bounded strategic posture."""
    mapping = {
        entry["design_tag"]: entry["engine_tag"]
        for entry in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    rows = csv_rows(ROSTER)
    assignments: list[tuple[str, str, str]] = []
    for row in rows:
        tag = row["tag"]
        tier = int(row["tier"])
        region = row["region"]
        if tag in {"ROM", "HAN"}:
            personality = "ai_balanced"
        elif tag == "PAR":
            personality = "ai_aggressive"
        elif row["kind"] == "subject":
            personality = "ai_defensive"
        elif tier == 1:
            personality = "ai_expansionist"
        elif region in {"Steppe", "Pontic", "Germania", "Danube"} and tier <= 2:
            personality = "ai_aggressive"
        elif tier == 2 and region in {
            "Arabia", "India", "Lanka", "Southeast Asia", "Oceania",
            "Levant", "Africa", "West Africa",
        }:
            personality = "ai_opportunistic"
        elif tier == 2:
            personality = "ai_cautious"
        elif row["kind"] == "sop":
            personality = "ai_defensive"
        else:
            personality = "ai_balanced"
        assignments.append((mapping[tag], personality, tag))
    if len(assignments) != len(rows) or len({engine for engine, _, _ in assignments}) != len(rows):
        raise ValueError("AI personality manager does not cover the unique opening engine roster")
    lines = [
        "# Generated by tools/generate_start_mirror.py --write.",
        "# AD 1 roster-wide strategic postures; no opening country uses engine defaults.",
        "countries = {",
        "\tcountries = {",
    ]
    for engine, personality, design in sorted(assignments):
        lines.append(f"\t\t{engine} = {{ ai_personality = {personality} }} # {design}")
    lines.extend(("\t}", "}", ""))
    return "\n".join(lines)


def urban_manager() -> tuple[str, int]:
    """Render major cities plus the dispersed opening settlement network."""
    required = ("key", "location", "profile", "source", "confidence", "note")
    market_rows = csv_rows(MARKETS)
    markets = {row["key"]: row for row in market_rows}
    if len(markets) != len(market_rows):
        raise ValueError("markets.csv has duplicate keys")
    entries = csv_rows(URBAN_NODES)
    locations = set(json.loads((ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")))
    valid_buildings: set[str] = set()
    for ledger in (ROMAN_BUILDINGS, ANCIENT_BUILDING_REPLACEMENTS, REGIONAL_BUILDINGS):
        with ledger.open(encoding="utf-8-sig", newline="") as handle:
            valid_buildings.update(
                (row.get("key") or "").strip() for row in csv.DictReader(handle)
            )
    required_buildings = {
        building for building, _level in TOWN_SETUP_BUILDINGS + CITY_SETUP_BUILDINGS
    }
    if required_buildings - valid_buildings:
        raise ValueError(f"installed building symbols missing {sorted(required_buildings - valid_buildings)}")
    invalid_town_buildings = {
        building for building, _level in TOWN_SETUP_BUILDINGS
    } & CITY_ONLY_FAMILIES
    if invalid_town_buildings:
        raise ValueError(
            "town setup includes city-only buildings "
            f"{sorted(invalid_town_buildings)}"
        )
    if any(level != 1 for _building, level in TOWN_SETUP_BUILDINGS + CITY_SETUP_BUILDINGS):
        raise ValueError("opening town setups must respect the Age-1 one-level guild cap")
    owners: dict[str, str] = {}
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(line for line in handle if not line.startswith("#")):
            location = row["location"]
            if location in owners:
                raise ValueError(f"ownership has duplicate location {location}")
            owners[location] = row["engine_tag"]
    nodes: dict[str, dict[str, str]] = {}
    failures: list[str] = []
    for row in entries:
        if any(not row.get(field, "").strip() for field in required):
            failures.append("urban_nodes.csv contains a blank required field")
            continue
        key = row["key"].strip()
        location = row["location"].strip()
        if key in nodes:
            failures.append(f"urban_nodes.csv repeats key {key}")
        if key not in markets:
            failures.append(f"urban_nodes.csv has no matching market {key}")
        elif location != markets[key]["location"]:
            failures.append(f"urban_nodes.csv {key} location differs from markets.csv")
        if location not in locations:
            failures.append(f"urban_nodes.csv {key} uses unknown installed location {location}")
        if location not in owners:
            failures.append(f"urban_nodes.csv {key} has no controlled AD 1 location")
        if row["profile"].strip() not in {"town", "city"}:
            failures.append(f"urban_nodes.csv {key} has invalid profile {row['profile']}")
        if row["confidence"].strip() not in {"secure", "contested"}:
            failures.append(f"urban_nodes.csv {key} has invalid confidence {row['confidence']}")
        nodes[key] = row
    missing = sorted(set(markets) - set(nodes))
    if missing:
        failures.append(f"urban_nodes.csv is missing market nodes {missing}")
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    settlement_locations = {row["location"] for row in expanded_seed_rows()}
    lines = [
        "# Generated by tools/generate_start_mirror.py --write.",
        "# M5 AD 1 urban hubs and global settlement network.",
        "# Major ranks: docs/m5/urban_nodes.csv; ordinary capacity proxies:",
        "# docs/m5/regional_building_seeds.csv and docs/m5/global_settlement_audit.csv.",
        "locations = {",
    ]
    for key, row in sorted(nodes.items()):
        location = row["location"].strip()
        profile = row["profile"].strip()
        lines.append(
            f"\t{location} = {{ rank = {profile} town_setup = antiqvitas_market_{profile} }} "
            f"# {key}; {row['source']}"
        )
    major_locations = {row["location"].strip() for row in nodes.values()}
    for location in sorted(settlement_locations - major_locations):
        lines.append(
            f"\t{location} = {{ rank = town }} "
            "# P12.1;P12.3;P13;PER; contested regional settlement-capacity proxy"
        )
    lines.extend(("}", ""))
    return "\n".join(lines), len(settlement_locations | major_locations)


def special_building_manager() -> tuple[str, int, int]:
    """Render source-led M5 buildings, regional production families, and M7 forts."""
    required = ("key", "location", "building", "level", "source", "confidence", "note")
    entries = [(row, "M5") for row in csv_rows(SPECIAL_BUILDINGS)]
    for row in expanded_seed_rows():
        entry = dict(row)
        entry["building"] = row["family"]
        entry["level"] = "1"
        entries.append((entry, "M5 regional"))
    entries.extend((row, "M7") for row in csv_rows(M7_FORTS))
    if not entries:
        raise ValueError("special_buildings.csv has no specialist-building entries")
    locations = set(json.loads((ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")))
    buildings = set(json.loads((ROOT / "docs/vanilla_symbols/building.json").read_text(encoding="utf-8-sig")))
    # M5's named Roman specials are mod-owned building types.  Their complete
    # contracts, source ledger, generated definitions, direct icons, and start
    # rows are checked by tools/m5_roman_buildings.py before this manager is
    # emitted; include only its explicit antq_ keys here.
    with ROMAN_BUILDINGS.open(encoding="utf-8-sig", newline="") as handle:
        buildings.update((row.get("key") or "").strip() for row in csv.DictReader(handle))
    with ANCIENT_BUILDING_REPLACEMENTS.open(encoding="utf-8-sig", newline="") as handle:
        buildings.update((row.get("key") or "").strip() for row in csv.DictReader(handle))
    with REGIONAL_BUILDINGS.open(encoding="utf-8-sig", newline="") as handle:
        buildings.update((row.get("key") or "").strip() for row in csv.DictReader(handle))
    urban_locations = {row["location"].strip() for row in csv_rows(URBAN_NODES)}
    capital_sites = {
        row["map_capital"].strip()
        for row in csv_rows(ROSTER)
        if row.get("map_capital", "").strip() not in {"", "TBD"}
    }
    owners: dict[str, str] = {}
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(line for line in handle if not line.startswith("#")):
            location = row["location"]
            if location in owners:
                raise ValueError(f"ownership has duplicate location {location}")
            owners[location] = row["engine_tag"]
    historic_required = ("key", "location", "source", "confidence", "note")
    historic_sites: set[str] = set()
    historic_keys: set[str] = set()
    site_failures: list[str] = []
    for row in csv_rows(HISTORIC_BUILDING_SITES):
        if any(not row.get(field, "").strip() for field in historic_required):
            site_failures.append("historic_building_sites.csv contains a blank required field")
            continue
        key = row["key"].strip()
        location = row["location"].strip()
        if key in historic_keys:
            site_failures.append(f"historic_building_sites.csv repeats key {key}")
        if location in historic_sites:
            site_failures.append(f"historic_building_sites.csv repeats location {location}")
        if location not in locations:
            site_failures.append(f"historic_building_sites.csv {key} uses unknown installed location {location}")
        if location not in owners:
            site_failures.append(f"historic_building_sites.csv {key} has no controlled AD 1 location")
        if row["confidence"].strip() not in {"secure", "contested"}:
            site_failures.append(f"historic_building_sites.csv {key} has invalid confidence {row['confidence']}")
        historic_keys.add(key)
        historic_sites.add(location)
    if site_failures:
        raise ValueError("\n".join(sorted(set(site_failures))))
    failures: list[str] = []
    seen_keys: set[str] = set()
    seen_buildings: set[tuple[str, str]] = set()
    fort_count = 0
    for row, layer in entries:
        if any(not row.get(field, "").strip() for field in required):
            failures.append(f"{layer} building ledger contains a blank required field")
            continue
        key = row["key"].strip()
        location = row["location"].strip()
        building = row["building"].strip()
        try:
            level = int(row["level"])
        except ValueError:
            failures.append(f"{layer} building ledger {key} has non-integer level {row['level']}")
            continue
        if key in seen_keys:
            failures.append(f"building ledgers repeat key {key}")
        pair = (location, building)
        if pair in seen_buildings:
            failures.append(f"building ledgers repeat {building} at {location}")
        if location not in locations:
            failures.append(f"{layer} building ledger {key} uses unknown installed location {location}")
        if location not in owners:
            failures.append(f"{layer} building ledger {key} has no controlled AD 1 location")
        if layer == "M5" and location not in urban_locations | historic_sites | capital_sites:
            failures.append(
                f"{layer} building ledger {key} is not an AD 1 market node, "
                "historic site, or reviewed polity capital"
            )
        if layer == "M7" and building != "antq_earthwork_stockade":
            failures.append(f"forts.csv {key} must use the namespaced ancient stockade")
        if building not in buildings:
            failures.append(f"{layer} building ledger {key} uses unknown installed building {building}")
        if not 1 <= level <= 10:
            failures.append(f"{layer} building ledger {key} level must be 1 through 10")
        if row["confidence"].strip() not in {"secure", "contested"}:
            failures.append(f"{layer} building ledger {key} has invalid confidence {row['confidence']}")
        seen_keys.add(key)
        seen_buildings.add(pair)
        fort_count += layer == "M7"
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    lines = [
        "# M5 specialist/regional-production buildings plus M7 castra/limes proxies; source rationale: docs/m5/ and docs/m7/.",
        "building_manager = {",
    ]
    for row, _layer in sorted(entries, key=lambda item: item[0]["key"]):
        location = row["location"].strip()
        lines.append(
            f"\t{row['building'].strip()} = {{ tag = {owners[location]} level = {row['level'].strip()} "
            f"location = {location} }} # {row['key'].strip()}; {row['source'].strip()}"
        )
    lines.extend(("}", ""))
    return "\n".join(lines), len(entries), fort_count


def m7_unit_manager() -> tuple[str, int]:
    """Render M7's source-labelled army and navy seeds into the exact start manager."""
    units = load_units()
    validate_start_ledgers(units)
    unit_keys = {unit.key for unit in units}
    tags = m7_tag_map()
    entries = csv_rows(M7_ARMIES)
    groups: dict[str, list[dict[str, str]]] = {}
    for row in entries:
        if row["unit_type"] not in unit_keys:
            raise ValueError(f"armies.csv references unknown M7 unit {row['unit_type']}")
        groups.setdefault(row["key"], []).append(row)
    lines = [
        "# Generated by tools/generate_start_mirror.py --write.",
        "# M7 technical force seeds; sources state broad force context, never a reconstructed order of battle.",
        "unit_manager = {",
    ]
    for key in sorted(groups):
        rows = groups[key]
        first = rows[0]
        lines.extend((
            f"\t{first['kind']} = {{",
            f"\t\tcountry = {tags[first['country']]}",
            f"\t\tlocation = {first['location']}",
            "\t\tsub_units = {",
        ))
        lines.extend(f"\t\t\t{row['unit_type']} = {{ strength = {row['strength']} }}" for row in rows)
        lines.extend(("\t\t}", "\t}", ""))
    lines.extend(("}", ""))
    return "\n".join(lines), len(groups)


def road_network() -> tuple[str, int]:
    """Render a small, source-labelled AD 1 road network using installed syntax."""
    required = ("origin", "destination", "corridor", "source", "confidence", "note")
    locations = set(json.loads((ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")))
    controlled: set[str] = set()
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(line for line in handle if not line.startswith("#")):
            controlled.add(row["location"])
    entries = csv_rows(ROAD_SEGMENTS)
    if not entries:
        raise ValueError("road_segments.csv has no segments")
    failures: list[str] = []
    seen: set[tuple[str, str]] = set()
    for row in entries:
        if any(not row.get(field, "").strip() for field in required):
            failures.append("road_segments.csv contains a blank required field")
            continue
        origin, destination = row["origin"].strip(), row["destination"].strip()
        if origin == destination:
            failures.append(f"road_segments.csv has a self-link at {origin}")
        pair = tuple(sorted((origin, destination)))
        if pair in seen:
            failures.append(f"road_segments.csv duplicates undirected segment {pair[0]}-{pair[1]}")
        if origin not in locations or destination not in locations:
            failures.append(f"road_segments.csv has unknown installed endpoint {origin}-{destination}")
        if origin not in controlled or destination not in controlled:
            failures.append(f"road_segments.csv has endpoint outside AD 1 control {origin}-{destination}")
        if row["confidence"].strip() not in {"secure", "contested"}:
            failures.append(f"road_segments.csv {origin}-{destination} has invalid confidence")
        seen.add(pair)
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    lines = [
        "# Generated by tools/generate_start_mirror.py --write.",
        "# M5 AD 1 road corridors; source and route rationale: docs/m5/road_segments.csv.",
        "# Bare endpoint syntax matches the installed start manager's base-road contract.",
        "road_network = {",
    ]
    for row in sorted(entries, key=lambda item: (item["origin"], item["destination"])):
        lines.append(
            f"\t{row['origin']} = {row['destination']} # {row['corridor']}; {row['source']}"
        )
    lines.extend(("}", ""))
    return "\n".join(lines), len(entries)


def development_manager() -> tuple[str, int]:
    """Render the transparent M5 rank-and-road development foundation."""
    required = ("selector", "value", "source", "confidence", "note")
    allowed = {"base", "road", "town", "city"}
    locations = set(json.loads((ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")))
    controlled: set[str] = set()
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(line for line in handle if not line.startswith("#")):
            controlled.add(row["location"])
    entries = csv_rows(DEVELOPMENT_PROFILE)
    selectors: set[str] = set()
    failures: list[str] = []
    for row in entries:
        if any(not row.get(field, "").strip() for field in required):
            failures.append("development_profile.csv contains a blank required field")
            continue
        selector = row["selector"].strip()
        if selector in selectors:
            failures.append(f"development_profile.csv repeats selector {selector}")
        if selector not in allowed and selector not in locations:
            failures.append(f"development_profile.csv has unknown selector {selector}")
        if selector in locations and selector not in controlled:
            failures.append(f"development_profile.csv has uncontrolled location {selector}")
        try:
            value = Decimal(row["value"])
        except Exception:
            failures.append(f"development_profile.csv {selector} has invalid value {row['value']!r}")
        else:
            if value < -10 or value > 30:
                failures.append(f"development_profile.csv {selector} value is outside -10..30")
        if row["confidence"].strip() not in {"secure", "contested"}:
            failures.append(f"development_profile.csv {selector} has invalid confidence")
        selectors.add(selector)
    required_selectors = {"base", "road", "town", "city"}
    if selectors != required_selectors:
        failures.append(
            f"development_profile.csv selectors must be exactly {sorted(required_selectors)} for this foundation"
        )
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    values = {row["selector"].strip(): row["value"].strip() for row in entries}
    lines = [
        "# Generated by tools/generate_start_mirror.py --write.",
        "# M5 technical development scaling; historical evidence remains in M4 population and M5 urban ledgers.",
        "development = {",
    ]
    for selector in ("base", "road", "town", "city"):
        lines.append(f"\t{selector} = {values[selector]}")
    lines.extend(("}", ""))
    return "\n".join(lines), len(entries)


def decimal_field(row: dict[str, str], field: str, path: Path) -> Decimal:
    value = row.get(field, "").strip()
    if not value:
        raise ValueError(f"{path.relative_to(ROOT)} has a blank {field}")
    try:
        parsed = Decimal(value)
    except Exception as exc:
        raise ValueError(f"{path.relative_to(ROOT)} has invalid {field}={value!r}") from exc
    if parsed <= 0:
        raise ValueError(f"{path.relative_to(ROOT)} has non-positive {field}={value!r}")
    return parsed


def load_population_plan() -> tuple[dict[str, MacroTarget], dict[str, RegionalAllocation]]:
    """Read the auditable M4 population targets and regional allocation plan."""
    macros: dict[str, MacroTarget] = {}
    for row in csv_rows(POPULATION_TARGETS):
        macro = row.get("macro", "").strip()
        if not macro or macro in macros:
            raise ValueError(f"{POPULATION_TARGETS.relative_to(ROOT)} has invalid or duplicate macro {macro!r}")
        minimum = row.get("min_thousands", "").strip()
        maximum = row.get("max_thousands", "").strip()
        if bool(minimum) != bool(maximum):
            raise ValueError(f"{POPULATION_TARGETS.relative_to(ROOT)} {macro}: min/max must both be set or blank")
        for field in ("source", "confidence", "note"):
            if not row.get(field, "").strip():
                raise ValueError(f"{POPULATION_TARGETS.relative_to(ROOT)} {macro}: blank {field}")
        macros[macro] = MacroTarget(
            decimal_field(row, "target_thousands", POPULATION_TARGETS),
            Decimal(minimum) if minimum else None,
            Decimal(maximum) if maximum else None,
            row["source"].strip(),
            row["confidence"].strip(),
            row["note"].strip(),
        )
    if "world" not in macros:
        raise ValueError(f"{POPULATION_TARGETS.relative_to(ROOT)} must define a world target")
    allocations: dict[str, RegionalAllocation] = {}
    for row in csv_rows(POPULATION_ALLOCATIONS):
        region = row.get("region", "").strip()
        macro = row.get("macro", "").strip()
        if not region or region in allocations:
            raise ValueError(f"{POPULATION_ALLOCATIONS.relative_to(ROOT)} has invalid or duplicate region {region!r}")
        if macro not in macros or macro == "world":
            raise ValueError(f"{POPULATION_ALLOCATIONS.relative_to(ROOT)} {region}: unknown macro {macro!r}")
        for field in ("source", "confidence", "note"):
            if not row.get(field, "").strip():
                raise ValueError(f"{POPULATION_ALLOCATIONS.relative_to(ROOT)} {region}: blank {field}")
        allocations[region] = RegionalAllocation(
            macro,
            decimal_field(row, "target_thousands", POPULATION_ALLOCATIONS),
            row["source"].strip(),
            row["confidence"].strip(),
            row["note"].strip(),
        )
    allocated = defaultdict(Decimal)
    for allocation in allocations.values():
        allocated[allocation.macro] += allocation.target
    for macro, target in macros.items():
        if macro == "world":
            continue
        if allocated[macro] != target.target:
            raise ValueError(
                f"{macro} allocations total {allocated[macro]} but target is {target.target} thousand"
            )
    if sum(allocated.values(), Decimal()) != macros["world"].target:
        raise ValueError(
            f"regional allocations total {sum(allocated.values(), Decimal())} but world target is "
            f"{macros['world'].target} thousand"
        )
    return macros, allocations


def population_location_overrides(
    owners: dict[str, str],
    allocations: dict[str, RegionalAllocation],
) -> dict[str, dict[str, str]]:
    """Load exceptional source-led populations without treating political
    ownership as proof of a uniform local culture or religion.
    """
    required = ("location", "culture", "religion", "pop_type", "region", "source", "confidence", "note")
    rows = csv_rows(POPULATION_LOCATION_OVERRIDES)
    overrides: dict[str, dict[str, str]] = {}
    failures: list[str] = []
    for row in rows:
        location = row.get("location", "").strip()
        if any(not row.get(field, "").strip() for field in required):
            failures.append(f"{POPULATION_LOCATION_OVERRIDES.relative_to(ROOT)} has a blank required field")
            continue
        if location in overrides:
            failures.append(f"{POPULATION_LOCATION_OVERRIDES.relative_to(ROOT)} repeats {location}")
        elif location not in owners:
            failures.append(f"{POPULATION_LOCATION_OVERRIDES.relative_to(ROOT)} {location} is not controlled")
        elif row["region"].strip() not in allocations:
            failures.append(f"{POPULATION_LOCATION_OVERRIDES.relative_to(ROOT)} {location} has an unknown region")
        elif row["confidence"].strip() not in {"secure", "contested"}:
            failures.append(f"{POPULATION_LOCATION_OVERRIDES.relative_to(ROOT)} {location} has invalid confidence")
        elif row["pop_type"].strip() not in {"peasants", "tribesmen"}:
            failures.append(f"{POPULATION_LOCATION_OVERRIDES.relative_to(ROOT)} {location} has invalid pop_type")
        else:
            overrides[location] = {key: value.strip() for key, value in row.items()}
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return overrides


def population_geographic_allocations(
    owners: dict[str, str],
    roster: dict[str, dict[str, str]],
    allocations: dict[str, RegionalAllocation],
    overrides: dict[str, dict[str, str]],
) -> tuple[dict[str, GeographicAllocation], dict[str, str]]:
    """Load source-led geographic partitions within political roster regions."""
    required = (
        "group",
        "parent_region",
        "selector_type",
        "selectors",
        "target_thousands",
        "source",
        "confidence",
        "note",
    )
    rows = csv_rows(POPULATION_GEOGRAPHIC_ALLOCATIONS)
    groups: dict[str, GeographicAllocation] = {}
    location_groups: dict[str, str] = {}
    parent_totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    failures: list[str] = []
    valid_selectors = {
        "area": set(json.loads(VANILLA_AREAS.read_text(encoding="utf-8-sig"))),
        "province": set(json.loads(VANILLA_PROVINCES.read_text(encoding="utf-8-sig"))),
        "region": set(json.loads(VANILLA_REGIONS.read_text(encoding="utf-8-sig"))),
    }
    for number, row in enumerate(rows, start=2):
        if tuple(row) != required:
            raise ValueError(
                f"{POPULATION_GEOGRAPHIC_ALLOCATIONS.relative_to(ROOT)} must use header "
                f"{','.join(required)}"
            )
        group = row["group"].strip()
        parent = row["parent_region"].strip()
        selector_type = row["selector_type"].strip()
        selectors = [item.strip() for item in row["selectors"].split(";") if item.strip()]
        if not group or group in groups:
            failures.append(f"{POPULATION_GEOGRAPHIC_ALLOCATIONS.relative_to(ROOT)}:{number}: invalid group")
            continue
        if parent not in allocations:
            failures.append(
                f"{POPULATION_GEOGRAPHIC_ALLOCATIONS.relative_to(ROOT)}:{number}: unknown parent {parent}"
            )
            continue
        if selector_type not in valid_selectors or not selectors:
            failures.append(
                f"{POPULATION_GEOGRAPHIC_ALLOCATIONS.relative_to(ROOT)}:{number}: invalid selectors"
            )
            continue
        unknown = sorted(set(selectors) - valid_selectors[selector_type])
        if unknown:
            failures.append(
                f"{POPULATION_GEOGRAPHIC_ALLOCATIONS.relative_to(ROOT)}:{number}: "
                f"unknown {selector_type} selectors {unknown}"
            )
            continue
        if row["confidence"].strip() not in {"secure", "contested"}:
            failures.append(
                f"{POPULATION_GEOGRAPHIC_ALLOCATIONS.relative_to(ROOT)}:{number}: invalid confidence"
            )
            continue
        if not row["source"].strip() or not row["note"].strip():
            failures.append(
                f"{POPULATION_GEOGRAPHIC_ALLOCATIONS.relative_to(ROOT)}:{number}: blank source/note"
            )
            continue
        locations = set().union(*(geography_leaves(selector) for selector in selectors))
        locations.intersection_update(owners)
        if not locations:
            failures.append(
                f"{POPULATION_GEOGRAPHIC_ALLOCATIONS.relative_to(ROOT)}:{number}: no controlled locations"
            )
            continue
        wrong_parent = sorted(
            location
            for location in locations
            if overrides.get(location, {}).get("region", roster[owners[location]]["region"]) != parent
        )
        overlaps = sorted(location for location in locations if location in location_groups)
        if wrong_parent:
            failures.append(
                f"{POPULATION_GEOGRAPHIC_ALLOCATIONS.relative_to(ROOT)}:{number}: "
                f"{len(wrong_parent)} location(s) outside {parent}: {wrong_parent[:5]}"
            )
            continue
        if overlaps:
            failures.append(
                f"{POPULATION_GEOGRAPHIC_ALLOCATIONS.relative_to(ROOT)}:{number}: "
                f"overlaps {overlaps[:5]}"
            )
            continue
        target = decimal_field(row, "target_thousands", POPULATION_GEOGRAPHIC_ALLOCATIONS)
        groups[group] = GeographicAllocation(
            parent,
            target,
            frozenset(locations),
            row["source"].strip(),
            row["confidence"].strip(),
            row["note"].strip(),
        )
        parent_totals[parent] += target
        location_groups.update({location: group for location in locations})
    for parent, target in parent_totals.items():
        if target >= allocations[parent].target:
            failures.append(
                f"{POPULATION_GEOGRAPHIC_ALLOCATIONS.relative_to(ROOT)}: "
                f"{parent} partitions {target} leave no residual population"
            )
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return groups, location_groups


def population_city_targets(
    owners: dict[str, str],
) -> tuple[list[CityPopulationTarget], dict[str, CityPopulationTarget]]:
    """Load uncertain historical-city ranges and exact game-location adapters."""
    required = (
        "place",
        "location",
        "mode",
        "city_proper_min_thousands",
        "city_proper_max_thousands",
        "agglomeration_min_thousands",
        "agglomeration_max_thousands",
        "game_location_target_thousands",
        "game_location_min_thousands",
        "game_location_max_thousands",
        "hinterland_scope",
        "source",
        "confidence",
        "note",
    )
    rows = csv_rows(POPULATION_CITY_TARGETS)
    targets: list[CityPopulationTarget] = []
    fixed: dict[str, CityPopulationTarget] = {}
    seen_places: set[str] = set()
    failures: list[str] = []
    for number, row in enumerate(rows, start=2):
        if tuple(row) != required:
            raise ValueError(
                f"{POPULATION_CITY_TARGETS.relative_to(ROOT)} must use header {','.join(required)}"
            )
        place = row["place"].strip()
        location = row["location"].strip()
        mode = row["mode"].strip()
        if not place or place in seen_places:
            failures.append(f"{POPULATION_CITY_TARGETS.relative_to(ROOT)}:{number}: invalid place")
            continue
        seen_places.add(place)
        if location not in owners:
            failures.append(
                f"{POPULATION_CITY_TARGETS.relative_to(ROOT)}:{number}: uncontrolled location {location}"
            )
            continue
        if mode not in {"primary", "proxy", "subsumed"}:
            failures.append(f"{POPULATION_CITY_TARGETS.relative_to(ROOT)}:{number}: invalid mode {mode}")
            continue
        if row["confidence"].strip() not in {"secure", "contested"}:
            failures.append(
                f"{POPULATION_CITY_TARGETS.relative_to(ROOT)}:{number}: invalid confidence"
            )
            continue
        if not row["hinterland_scope"].strip() or not row["source"].strip() or not row["note"].strip():
            failures.append(
                f"{POPULATION_CITY_TARGETS.relative_to(ROOT)}:{number}: blank scope/source/note"
            )
            continue
        try:
            proper_minimum = Decimal(row["city_proper_min_thousands"])
            proper_maximum = Decimal(row["city_proper_max_thousands"])
            agglomeration_minimum = Decimal(row["agglomeration_min_thousands"])
            agglomeration_maximum = Decimal(row["agglomeration_max_thousands"])
        except Exception:
            failures.append(
                f"{POPULATION_CITY_TARGETS.relative_to(ROOT)}:{number}: invalid historical range"
            )
            continue
        if not (
            Decimal() < proper_minimum <= proper_maximum
            and Decimal() < agglomeration_minimum <= agglomeration_maximum
            and proper_minimum <= agglomeration_maximum
        ):
            failures.append(
                f"{POPULATION_CITY_TARGETS.relative_to(ROOT)}:{number}: incoherent historical range"
            )
            continue
        game_fields = (
            row["game_location_target_thousands"].strip(),
            row["game_location_min_thousands"].strip(),
            row["game_location_max_thousands"].strip(),
        )
        if mode == "subsumed":
            if any(game_fields):
                failures.append(
                    f"{POPULATION_CITY_TARGETS.relative_to(ROOT)}:{number}: subsumed row has a game target"
                )
                continue
            game_target = game_minimum = game_maximum = None
        else:
            if not all(game_fields):
                failures.append(
                    f"{POPULATION_CITY_TARGETS.relative_to(ROOT)}:{number}: mapped row lacks game bounds"
                )
                continue
            game_target, game_minimum, game_maximum = map(Decimal, game_fields)
            if not (Decimal() < game_minimum <= game_target <= game_maximum):
                failures.append(
                    f"{POPULATION_CITY_TARGETS.relative_to(ROOT)}:{number}: invalid game bounds"
                )
                continue
            if location in fixed:
                failures.append(
                    f"{POPULATION_CITY_TARGETS.relative_to(ROOT)}:{number}: duplicate fixed location {location}"
                )
                continue
        target = CityPopulationTarget(
            place,
            location,
            mode,
            proper_minimum,
            proper_maximum,
            agglomeration_minimum,
            agglomeration_maximum,
            game_target,
            game_minimum,
            game_maximum,
            row["hinterland_scope"].strip(),
            row["source"].strip(),
            row["confidence"].strip(),
            row["note"].strip(),
        )
        targets.append(target)
        if game_target is not None:
            fixed[location] = target
    for target in targets:
        if target.mode == "subsumed" and target.location not in fixed:
            failures.append(
                f"{POPULATION_CITY_TARGETS.relative_to(ROOT)}: {target.place} is subsumed "
                f"into {target.location} without a primary target"
            )
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return targets, fixed


def population_culture_remaps(owners: dict[str, str]) -> dict[str, dict[str, str]]:
    """Resolve the source-labelled M4 culture atlas to exact owned locations.

    The source ledger deliberately accepts installed geographic selectors, not
    vanilla culture keys.  Thus an area can be assigned only after a historical
    judgment is recorded with its source, and a selector's concrete location
    expansion stays auditable after a map patch.  A narrower, independently
    sourced selector may refine a broader regional frame: precedence is
    location > province > area > region.  Equally specific overlap remains an
    error, so the ledger cannot silently choose between competing historical
    claims.  Location overrides remain the final, higher-precedence exception
    for places such as the Rinan/Linyi frontier.
    """
    required = ("selector_type", "selector", "culture", "source", "confidence", "note")
    with CULTURE_REMAP.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != required:
            raise ValueError(
                f"{CULTURE_REMAP.relative_to(ROOT)} must use header {','.join(required)}"
            )
        rows = list(reader)
    if not rows:
        raise ValueError(f"{CULTURE_REMAP.relative_to(ROOT)} has no remap rows")

    m4_symbols = json.loads(M4_SYMBOLS.read_text(encoding="utf-8"))
    cultures = set(m4_symbols["cultures"])
    hierarchy = json.loads(GEOGRAPHY_HIERARCHY.read_text(encoding="utf-8-sig"))
    valid = {
        "area": set(json.loads(VANILLA_AREAS.read_text(encoding="utf-8-sig"))),
        "province": set(json.loads(VANILLA_PROVINCES.read_text(encoding="utf-8-sig"))),
        "location": set(json.loads(VANILLA_LOCATIONS.read_text(encoding="utf-8-sig"))),
        "region": set(json.loads(VANILLA_REGIONS.read_text(encoding="utf-8-sig"))),
    }

    def leaves(selector: str, trail: tuple[str, ...] = ()) -> set[str]:
        if selector in trail:
            raise ValueError(
                f"{CULTURE_REMAP.relative_to(ROOT)} has cyclic geography selector "
                f"{' -> '.join((*trail, selector))}"
            )
        children = hierarchy.get(selector)
        # The harvested hierarchy can list a location alongside its subordinate
        # locations (for example ``kilkenny`` -> ``cullahill``, ``kilkenny``).
        # Treat that direct self member as a leaf while retaining strict cycle
        # detection for every indirect loop.
        if not children:
            return {selector}
        resolved: set[str] = set()
        for child in children:
            if child == selector:
                resolved.add(child)
            else:
                resolved.update(leaves(child, (*trail, selector)))
        return resolved

    remaps: dict[str, dict[str, str]] = {}
    specificity = {"region": 0, "area": 1, "province": 2, "location": 3}
    selectors: set[tuple[str, str]] = set()
    failures: list[str] = []
    for number, row in enumerate(rows, start=2):
        values = {key: row.get(key, "").strip() for key in required}
        if any(not values[key] for key in required):
            failures.append(f"{CULTURE_REMAP.relative_to(ROOT)}:{number}: blank required field")
            continue
        selector_type = values["selector_type"]
        selector = values["selector"]
        selector_key = (selector_type, selector)
        if selector_type not in valid:
            failures.append(
                f"{CULTURE_REMAP.relative_to(ROOT)}:{number}: invalid selector type {selector_type}"
            )
            continue
        if selector not in valid[selector_type]:
            failures.append(
                f"{CULTURE_REMAP.relative_to(ROOT)}:{number}: unknown {selector_type} {selector}"
            )
            continue
        if selector_key in selectors:
            failures.append(
                f"{CULTURE_REMAP.relative_to(ROOT)}:{number}: duplicate selector {selector_type} {selector}"
            )
            continue
        selectors.add(selector_key)
        if values["culture"] not in cultures:
            failures.append(
                f"{CULTURE_REMAP.relative_to(ROOT)}:{number}: unknown M4 culture {values['culture']}"
            )
            continue
        if values["confidence"] not in {"secure", "contested"}:
            failures.append(
                f"{CULTURE_REMAP.relative_to(ROOT)}:{number}: invalid confidence {values['confidence']}"
            )
            continue
        selected = leaves(selector) & set(owners)
        if not selected:
            failures.append(
                f"{CULTURE_REMAP.relative_to(ROOT)}:{number}: {selector_type} {selector} has no controlled locations"
            )
            continue
        for location in selected:
            existing = remaps.get(location)
            if existing:
                current_rank = specificity[selector_type]
                existing_rank = specificity[existing["selector_type"]]
                if current_rank == existing_rank:
                    failures.append(
                        f"{CULTURE_REMAP.relative_to(ROOT)}:{number}: equally-specific overlap at {location} from "
                        f"{existing['selector_type']} {existing['selector']}"
                    )
                    continue
                if current_rank < existing_rank:
                    continue
            remaps[location] = values
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return remaps


def population_religion_remaps(owners: dict[str, str]) -> dict[str, dict[str, str]]:
    """Resolve source-labelled local-faith selectors to controlled locations."""
    required = ("selector_type", "selector", "religion", "source", "confidence", "note")
    with RELIGION_REMAP.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != required:
            raise ValueError(
                f"{RELIGION_REMAP.relative_to(ROOT)} must use header {','.join(required)}"
            )
        rows = list(reader)
    if not rows:
        raise ValueError(f"{RELIGION_REMAP.relative_to(ROOT)} has no remap rows")

    symbols = json.loads(M4_SYMBOLS.read_text(encoding="utf-8"))
    religions = set(symbols["religions"])
    hierarchy = json.loads(GEOGRAPHY_HIERARCHY.read_text(encoding="utf-8-sig"))
    valid = {
        "area": set(json.loads(VANILLA_AREAS.read_text(encoding="utf-8-sig"))),
        "province": set(json.loads(VANILLA_PROVINCES.read_text(encoding="utf-8-sig"))),
        "location": set(json.loads(VANILLA_LOCATIONS.read_text(encoding="utf-8-sig"))),
        "region": set(json.loads(VANILLA_REGIONS.read_text(encoding="utf-8-sig"))),
    }

    def leaves(selector: str, trail: tuple[str, ...] = ()) -> set[str]:
        if selector in trail:
            raise ValueError(
                f"{RELIGION_REMAP.relative_to(ROOT)} has cyclic geography selector "
                f"{' -> '.join((*trail, selector))}"
            )
        children = hierarchy.get(selector)
        if not children:
            return {selector}
        resolved: set[str] = set()
        for child in children:
            if child == selector:
                resolved.add(child)
            else:
                resolved.update(leaves(child, (*trail, selector)))
        return resolved

    remaps: dict[str, dict[str, str]] = {}
    specificity = {"region": 0, "area": 1, "province": 2, "location": 3}
    selectors: set[tuple[str, str]] = set()
    failures: list[str] = []
    for number, row in enumerate(rows, start=2):
        values = {key: row.get(key, "").strip() for key in required}
        if any(not values[key] for key in required):
            failures.append(f"{RELIGION_REMAP.relative_to(ROOT)}:{number}: blank required field")
            continue
        selector_type = values["selector_type"]
        selector = values["selector"]
        selector_key = (selector_type, selector)
        if selector_type not in valid:
            failures.append(
                f"{RELIGION_REMAP.relative_to(ROOT)}:{number}: invalid selector type {selector_type}"
            )
            continue
        if selector not in valid[selector_type]:
            failures.append(
                f"{RELIGION_REMAP.relative_to(ROOT)}:{number}: unknown {selector_type} {selector}"
            )
            continue
        if selector_key in selectors:
            failures.append(
                f"{RELIGION_REMAP.relative_to(ROOT)}:{number}: duplicate selector "
                f"{selector_type} {selector}"
            )
            continue
        selectors.add(selector_key)
        if values["religion"] not in religions:
            failures.append(
                f"{RELIGION_REMAP.relative_to(ROOT)}:{number}: unknown M4 religion "
                f"{values['religion']}"
            )
            continue
        if values["confidence"] not in {"secure", "contested"}:
            failures.append(
                f"{RELIGION_REMAP.relative_to(ROOT)}:{number}: invalid confidence "
                f"{values['confidence']}"
            )
            continue
        selected = leaves(selector) & set(owners)
        if not selected:
            failures.append(
                f"{RELIGION_REMAP.relative_to(ROOT)}:{number}: {selector_type} "
                f"{selector} has no controlled locations"
            )
            continue
        for location in selected:
            existing = remaps.get(location)
            if existing:
                current_rank = specificity[selector_type]
                existing_rank = specificity[existing["selector_type"]]
                if current_rank == existing_rank:
                    failures.append(
                        f"{RELIGION_REMAP.relative_to(ROOT)}:{number}: equally-specific "
                        f"overlap at {location} from {existing['selector_type']} "
                        f"{existing['selector']}"
                    )
                    continue
                if current_rank < existing_rank:
                    continue
            remaps[location] = values
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return remaps


def ancient_pop_weights(owners: dict[str, str]) -> dict[str, Decimal]:
    """Derive residual density from the reviewed AD 1 geography/economy ledgers."""
    topography = {
        "flatland": Decimal("1.20"), "hills": Decimal("0.90"),
        "plateau": Decimal("0.80"), "wetlands": Decimal("0.75"),
        "mountains": Decimal("0.50"),
    }
    vegetation = {
        "farmland": Decimal("1.65"), "grasslands": Decimal("1.20"),
        "woods": Decimal("0.90"), "forest": Decimal("0.72"),
        "jungle": Decimal("0.58"), "sparse": Decimal("0.42"),
        "desert": Decimal("0.24"),
    }
    resource = {
        "staple_crop": Decimal("0.45"), "orchard_vine": Decimal("0.30"),
        "pastoral": Decimal("0.22"), "aquatic": Decimal("0.18"),
        "fiber_dye": Decimal("0.16"), "forest": Decimal("0.10"),
        "mineral_or_quarried": Decimal("0.08"),
    }
    weights: dict[str, Decimal] = {}
    for row in csv_rows(POPULATION_GEOGRAPHY):
        location = row["location"].strip()
        if location not in owners:
            continue
        value = topography.get(row["topography"].strip(), Decimal("0.70"))
        value *= vegetation.get(row["vegetation"].strip(), Decimal("0.65"))
        value += resource.get(row["resource_family"].strip(), Decimal("0.05"))
        access = row["trade_access"].strip()
        if access == "major_harbor":
            value += Decimal("0.80")
        elif access == "coastal_access":
            value += Decimal("0.30")
        weights[location] = value
    missing = sorted(set(owners) - set(weights))
    if missing:
        raise ValueError(f"AD 1 population geography lacks {len(missing)} controlled locations")
    urban = {row["location"].strip(): row["profile"].strip() for row in csv_rows(URBAN_NODES)}
    for location, profile in urban.items():
        if location in weights:
            weights[location] += Decimal("8.0" if profile == "city" else "3.0")
    for row in csv_rows(MARKETS):
        location = row["location"].strip()
        if location in weights:
            weights[location] += Decimal("2.0")
    for row in csv_rows(ROAD_SEGMENTS):
        for field in ("origin", "destination"):
            location = row[field].strip()
            if location in weights:
                weights[location] += Decimal("0.75")
    return weights


def population_strata(
    total: Decimal, primary: str, kind: str, rank: str, region: str
) -> tuple[tuple[str, Decimal], ...]:
    """Split a location total into ancient social strata with exact preservation."""
    if primary == "tribesmen" or kind == "sop":
        shares = {
            "tribesmen": Decimal("0.74"), "peasants": Decimal("0.08"),
            "soldiers": Decimal("0.07"), "nobles": Decimal("0.04"),
            "clergy": Decimal("0.03"), "laborers": Decimal("0.02"),
            "burghers": Decimal("0.02"),
        }
    elif rank == "city":
        shares = {
            "peasants": Decimal("0.40"), "burghers": Decimal("0.18"),
            "laborers": Decimal("0.13"), "soldiers": Decimal("0.07"),
            "nobles": Decimal("0.05"), "clergy": Decimal("0.05"),
            "slaves": Decimal("0.12"),
        }
    elif rank == "town":
        shares = {
            "peasants": Decimal("0.58"), "burghers": Decimal("0.12"),
            "laborers": Decimal("0.09"), "soldiers": Decimal("0.06"),
            "nobles": Decimal("0.04"), "clergy": Decimal("0.04"),
            "slaves": Decimal("0.07"),
        }
    else:
        shares = {
            "peasants": Decimal("0.79"), "laborers": Decimal("0.06"),
            "soldiers": Decimal("0.05"), "nobles": Decimal("0.025"),
            "clergy": Decimal("0.025"), "slaves": Decimal("0.05"),
        }
    # Dependent labor was important but not uniform. Keep the highest opening
    # shares in Mediterranean and Near Eastern state economies; elsewhere it
    # becomes free cultivator/laborer population rather than invented slavery.
    if "slaves" in shares and region not in {"Rome", "Levant", "Mesopotamia", "Iran", "Egypt", "Maghreb", "Greece-Anatolia"}:
        transfer = shares.pop("slaves")
        shares["peasants"] += transfer * Decimal("0.65")
        shares["laborers"] += transfer * Decimal("0.35")
    units = int(total / THOUSANDTH)
    if units <= 1:
        return ((primary, total),)
    exact = {key: value * units for key, value in shares.items()}
    allocated = {key: int(value) for key, value in exact.items() if value >= 1}
    if primary not in allocated:
        allocated[primary] = 1
    remainder = units - sum(allocated.values())
    order = sorted(
        allocated,
        key=lambda key: (exact.get(key, Decimal()), shares.get(key, Decimal()), key),
        reverse=True,
    )
    for index in range(remainder):
        allocated[order[index % len(order)]] += 1
    return tuple(
        (key, Decimal(value) * THOUSANDTH)
        for key, value in sorted(allocated.items())
        if value > 0
    )


def culture_presence_cultures() -> list[str]:
    """Read locally observed initializer-required, otherwise-unused cultures."""
    with CULTURE_PRESENCE.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(line for line in handle if not line.startswith("#"))
        if tuple(reader.fieldnames or ()) != ("culture",):
            raise ValueError(f"{CULTURE_PRESENCE.relative_to(ROOT)} must contain only a culture column")
        cultures = [row["culture"].strip() for row in reader]
    symbols = json.loads(M4_SYMBOLS.read_text(encoding="utf-8"))
    known = set(symbols["cultures"]) | set(json.loads((ROOT / "docs/vanilla_symbols/culture.json").read_text(encoding="utf-8-sig")))
    if not cultures or cultures != sorted(set(cultures)) or set(cultures) - known:
        raise ValueError(f"{CULTURE_PRESENCE.relative_to(ROOT)} is not a sorted active-culture ledger")
    return cultures


def compatibility_presence_manager(cultures: list[str]) -> str:
    """Render engine-only sub-thousand culture presences in an additive manager."""
    lines = [
        "# Generated by tools/generate_start_mirror.py --write.",
        "# M12 EU5 initializer compatibility presences; ledgered, non-historical, and population-offset.",
        "locations = {",
        f"\t{COMPATIBILITY_LOCATION} = {{",
    ]
    for culture in cultures:
        lines.append(
            f"\t\tdefine_pop = {{ type = peasants size = {COMPATIBILITY_POP_SIZE:.3f} "
            f"culture = {culture} religion = {COMPATIBILITY_RELIGION} }}"
        )
    lines.extend(("\t}", "}", ""))
    return "\n".join(lines)


def allocate_population_group(
    locations: list[str],
    target: Decimal,
    weights: dict[str, Decimal],
    fixed_targets: dict[str, Decimal],
) -> dict[str, Decimal]:
    """Allocate one exact group total with positive floors and a rural cap."""
    ordered = sorted(locations)
    unknown_fixed = sorted(set(fixed_targets) - set(ordered))
    if unknown_fixed:
        raise ValueError(f"population group has fixed targets outside it: {unknown_fixed}")
    free = [location for location in ordered if location not in fixed_targets]
    fixed_total = sum(fixed_targets.values(), Decimal())
    floor_total = MIN_LOCATION_POPULATION * len(free)
    remaining = target - fixed_total - floor_total
    if remaining < 0:
        raise ValueError(
            f"population fixed targets {fixed_total} plus floors {floor_total} exceed group target {target}"
        )
    headroom = MAX_UNTARGETED_LOCATION_POPULATION - MIN_LOCATION_POPULATION
    if remaining > headroom * len(free):
        raise ValueError(
            f"population group target {target} cannot fit {len(free)} untargeted locations "
            f"under the {MAX_UNTARGETED_LOCATION_POPULATION} cap"
        )
    assigned = dict(fixed_targets)
    for location in free:
        assigned[location] = MIN_LOCATION_POPULATION
    active = set(free)
    extra: dict[str, Decimal] = {location: Decimal() for location in free}
    while active and remaining > 0:
        total_weight = sum(
            (max(weights.get(location, Decimal()), Decimal("0.050")) for location in active),
            Decimal(),
        )
        if not total_weight:
            raise ValueError("population group has no usable geographic weight")
        saturated = {
            location
            for location in active
            if max(weights.get(location, Decimal()), Decimal("0.050"))
            * remaining
            / total_weight
            >= headroom
        }
        if not saturated:
            for location in active:
                extra[location] = (
                    max(weights.get(location, Decimal()), Decimal("0.050"))
                    * remaining
                    / total_weight
                )
            remaining = Decimal()
            break
        for location in saturated:
            extra[location] = headroom
            remaining -= headroom
        active.difference_update(saturated)
    for location in free:
        assigned[location] = (
            MIN_LOCATION_POPULATION + extra[location]
        ).quantize(THOUSANDTH, rounding=ROUND_HALF_UP)
    correction = target - sum(assigned.values(), Decimal())
    if correction:
        candidates = sorted(
            free,
            key=lambda location: (
                MAX_UNTARGETED_LOCATION_POPULATION - assigned[location],
                max(weights.get(location, Decimal()), Decimal("0.050")),
                location,
            ),
            reverse=True,
        )
        for location in candidates:
            revised = assigned[location] + correction
            if MIN_LOCATION_POPULATION <= revised <= MAX_UNTARGETED_LOCATION_POPULATION:
                assigned[location] = revised
                correction = Decimal()
                break
    if correction:
        raise ValueError(f"population rounding correction {correction} cannot fit group bounds")
    if sum(assigned.values(), Decimal()) != target:
        raise ValueError("population group allocation did not preserve its exact target")
    return assigned


def population_manager(
    compatibility_cultures: list[str],
) -> tuple[str, int, Decimal, dict[str, set[str]], dict[str, Decimal]]:
    """Render all controlled AD 1 locations against section 12.4 target totals."""
    roster_rows = csv_rows(ROSTER)
    roster = {row["tag"]: row for row in roster_rows}
    macros, allocations = load_population_plan()
    roster_regions = {row["region"] for row in roster_rows}
    missing_regions = sorted(roster_regions - set(allocations))
    extra_regions = sorted(set(allocations) - roster_regions)
    if missing_regions or extra_regions:
        raise ValueError(f"population regional coverage mismatch; missing={missing_regions}, extra={extra_regions}")
    owners: dict[str, str] = {}
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        for entry in csv.DictReader(line for line in handle if not line.startswith("#")):
            location = entry["location"]
            tag = entry["tag"]
            if tag not in roster:
                raise ValueError(f"population ownership references unknown tag {tag}")
            if location in owners:
                raise ValueError(f"population ownership assigns {location} more than once")
            owners[location] = tag
    overrides = population_location_overrides(owners, allocations)
    culture_remaps = population_culture_remaps(owners)
    religion_remaps = population_religion_remaps(owners)
    if COMPATIBILITY_LOCATION not in owners:
        raise ValueError(f"compatibility location {COMPATIBILITY_LOCATION} is not controlled")
    geographic_allocations, geographic_location_groups = population_geographic_allocations(
        owners, roster, allocations, overrides
    )
    _, city_targets = population_city_targets(owners)
    compatibility_total = COMPATIBILITY_POP_SIZE * len(compatibility_cultures)
    weights = ancient_pop_weights(owners)
    effective_regions = {
        location: overrides.get(location, {}).get("region", roster[tag]["region"])
        for location, tag in owners.items()
    }
    locations_by_region: defaultdict[str, list[str]] = defaultdict(list)
    for location, region in effective_regions.items():
        locations_by_region[region].append(location)
    normalized_weights: dict[str, Decimal] = {}
    for region, locations in locations_by_region.items():
        regional_weights = {
            location: max(weights.get(location, Decimal()), Decimal("0.050"))
            for location in locations
        }
        regional_total = sum(regional_weights.values(), Decimal())
        if not regional_total:
            raise ValueError(f"population region {region} has no usable geographic weight")
        for location, weight in regional_weights.items():
            normalized_weights[location] = weight * allocations[region].target / regional_total
    group_targets = {
        macro: target.target for macro, target in macros.items() if macro != "world"
    }
    for group, allocation in geographic_allocations.items():
        parent_macro = allocations[allocation.parent_region].macro
        group_targets[parent_macro] -= allocation.target
        group_targets[group] = allocation.target
    by_group: defaultdict[str, list[str]] = defaultdict(list)
    location_group: dict[str, str] = {}
    for location, tag in owners.items():
        region = effective_regions[location]
        group = geographic_location_groups.get(location, allocations[region].macro)
        location_group[location] = group
        by_group[group].append(location)
    compatibility_group = location_group[COMPATIBILITY_LOCATION]
    sizes: dict[str, Decimal] = {}
    for group, locations in by_group.items():
        target = group_targets[group] - (
            compatibility_total if group == compatibility_group else Decimal()
        )
        if target <= 0:
            raise ValueError("compatibility presence exceeds its regional population target")
        fixed = {
            location: city_targets[location].game_target
            for location in locations
            if location in city_targets
        }
        sizes.update(
            allocate_population_group(
                locations,
                target,
                normalized_weights,
                {location: value for location, value in fixed.items() if value is not None},
            )
        )
    lines = [
        "# Generated by tools/generate_start_mirror.py --write.",
        "# M4 AD 1 population totals: plan section 12.4; allocation inputs are source-labelled in docs/m4/.",
        "# Ancient city and Italy targets are fixed first; residual geography uses reviewed AD 1 environment and networks.",
        "# Roster regions weight macro allocation but do not become political-tag population bins.",
        "# No installed 1337 population value participates in allocation.",
        "locations = {",
    ]
    resident_cultures: defaultdict[str, set[str]] = defaultdict(set)
    country_populations: defaultdict[str, Decimal] = defaultdict(Decimal)
    urban_profiles = {
        entry["location"].strip(): entry["profile"].strip()
        for entry in csv_rows(URBAN_NODES)
    }
    for location in sorted(owners):
        row = roster[owners[location]]
        profile = historical_profile_for(row)
        override = overrides.get(location, {})
        pop_type = override.get("pop_type", "tribesmen" if row["kind"] == "sop" else "peasants")
        culture = override.get("culture", culture_remaps.get(location, {}).get("culture", profile.culture))
        religion = override.get(
            "religion",
            religion_remaps.get(location, {}).get("religion", profile.religion),
        )
        resident_cultures[owners[location]].add(culture)
        country_populations[owners[location]] += sizes[location]
        rank = urban_profiles.get(location, "rural")
        lines.append(f"\t{location} = {{")
        for stratum, stratum_size in population_strata(
            sizes[location], pop_type, row["kind"], rank, row["region"]
        ):
            lines.append(
                f"\t\tdefine_pop = {{ type = {stratum} size = {stratum_size:.3f} "
                f"culture = {culture} religion = {religion} }}"
            )
        lines.append("\t}")
    lines.extend(("}", ""))
    return (
        "\n".join(lines),
        len(owners),
        sum(sizes.values(), Decimal()) + compatibility_total,
        dict(resident_cultures),
        dict(country_populations),
    )


def fallback_government_block(kind: str, design_tag: str) -> list[str]:
    """Render the minimal installed government shape for unsourced profiles.

    The AD 1 source ledger deliberately leaves some collective and otherwise
    un-attested polities outside the M6 historical-government roster.  They
    still need a valid country government, but must not inherit one of the
    vanilla 1337 templates: those templates serialize medieval laws and estate
    privileges that the ANTIQVITAS government adapters correctly reject.
    """
    government_type = "tribe" if kind == "sop" else "monarchy"
    heir_selection = "tribal_oldest_male" if kind == "sop" else "cognatic_primogeniture"
    reform = "antq_advanced_chiefdom" if kind == "sop" else "antq_regional_kingship"
    lines = [
        "\t\t\tgovernment = {",
        f"\t\t\t\ttype = {government_type}",
        f"\t\t\t\their_selection = {heir_selection}",
        "\t\t\t\truler = random",
        "\t\t\t\treforms = {",
        f"\t\t\t\t\t{reform}",
        "\t\t\t\t}",
    ]
    lines.append("\t\t\t\tlaws = {")
    lines.extend(
        f"\t\t\t\t\t{law} = {option}"
        for law, option in starting_laws_by_tag()[design_tag]
    )
    lines.extend(("\t\t\t\t}", "\t\t\t}"))
    return lines


def country_manager(
    resident_cultures: dict[str, set[str]],
    country_populations: dict[str, Decimal],
) -> tuple[str, int, int]:
    """Render M3 countries from checked ownership plus verified capitals.

    Generic random-ruler scaffolding remains only for countries outside the
    source-labelled M6 foundation. M6 country profiles are generated from the
    checked `docs/m6/governments.csv` ledger.
    """
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    tag_map = {
        entry["design_tag"]: entry["engine_tag"]
        for entry in json.loads(TAG_MAP.read_text(encoding="utf-8"))["entries"]
    }
    power = load_power_data()
    integration_profiles = load_integration_profiles()
    current_terms = {term["design_tag"]: term for term in power.ruler_terms}
    ownership: dict[str, dict[str, list[str]]] = {}
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        for entry in csv.DictReader(line for line in handle if not line.startswith("#")):
            ownership.setdefault(entry["tag"], {}).setdefault(entry["tenure"], []).append(
                entry["location"]
            )
    lines = [
        "# Generated by tools/generate_start_mirror.py --write.",
        "# M3 political-map slice; generated only from sourced ownership data.",
        "current_age = age_1_traditions",
        "",
        "countries = {",
        "\tcountries = {",
    ]
    count = 0
    controlled = 0
    for row in rows:
        capital = row["map_capital"]
        if capital == "TBD":
            continue
        lines.append(f'\t\t{tag_map[row["tag"]]} = {{ # {row["name"]}; {row["source"]}')
        groups = ownership.get(row["tag"], {"own_control_core": [capital]})
        for tenure in sorted(groups):
            locations = sorted(set(groups[tenure]))
            lines.append(f"\t\t\t{tenure} = {{")
            lines.extend(f"\t\t\t\t{location}" for location in locations)
            lines.extend(("\t\t\t}", ""))
            controlled += len(locations)
        # Do not include installed vanilla country templates.  Their modern
        # default laws and estate privileges survive alongside the M6 adapter
        # and emit invalid-government diagnostics at every AD 1 startup.
        lines.append(f"\t\t\tcountry_rank = {country_rank(row)}")
        lines.append(f'\t\t\tstarting_technology_level = {m8_technology_level(row)}')
        if row["tag"] not in country_populations:
            raise ValueError(f"{row['tag']} has no allocated opening population")
        if country_populations[row["tag"]] < OPENING_LIQUIDITY_POPULATION_CEILING:
            # The engine will not initialize an affordable default mercenary
            # composition for very small treasuries. This floor is limited to
            # sub-500k polities and matches an installed 1337 setup value.
            lines.extend((
                "\t\t\tcurrency_data = {",
                f"\t\t\t\tgold = {OPENING_LIQUIDITY_FLOOR}",
                "\t\t\t}",
            ))
        lines.append("\t\t\tdiscovered_regions = {")
        lines.extend(f"\t\t\t\t{region}" for region in m9_discovery_regions(row))
        lines.append("\t\t\t}")
        integration = integration_profiles.get(row["tag"])
        if integration is not None:
            accepted = set(integration.accepted_cultures)
            if integration.tolerated_mode == "resident_remainder":
                tolerated = (
                    set(resident_cultures.get(row["tag"], set()))
                    | set(integration.tolerated_cultures)
                ) - accepted - {integration.primary_culture}
            elif integration.tolerated_mode == "explicit":
                tolerated = set(integration.tolerated_cultures)
            else:
                tolerated = set()
            if accepted:
                lines.append(
                    "\t\t\taccepted_cultures = { "
                    + " ".join(sorted(accepted))
                    + " }"
                )
            if tolerated:
                lines.append(
                    "\t\t\ttolerated_cultures = { "
                    + " ".join(sorted(tolerated))
                    + " }"
                )
        if row["tag"] in power.governments:
            lines.extend(
                government_block(
                    power.governments[row["tag"]], current_terms.get(row["tag"])
                )
            )
        else:
            lines.extend(fallback_government_block(row["kind"], row["tag"]))
        lines.extend((f"\t\t\tcapital = {capital}", "\t\t}", ""))
        count += 1
    lines.extend(("\t}", "}"))
    return "\n".join(lines) + "\n", count, controlled


def diplomacy_manager() -> tuple[str, int]:
    """Render the current M3 subject graph with locally verified mechanics.

    M3 uses the engine's current vassal/tributary contracts only as a clean
    political-map adapter. M9 replaces those entries with the plan's bespoke
    client-kingdom, satrapy, tributary, and foederati subject mechanics.
    """
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        roster = {row["tag"]: row for row in csv.DictReader(handle)}
    tag_map = {
        entry["design_tag"]: entry["engine_tag"]
        for entry in json.loads(TAG_MAP.read_text(encoding="utf-8"))["entries"]
    }
    subject_types = set(json.loads(SUBJECT_TYPES.read_text(encoding="utf-8-sig")))
    failures: list[str] = []
    seen_subjects: set[str] = set()
    dependencies: list[dict[str, str]] = []
    with SUBJECTS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != SUBJECT_FIELDS:
            raise ValueError("subjects.csv header does not match required field order")
        for row in reader:
            if any(not row[field].strip() for field in SUBJECT_FIELDS):
                failures.append("subjects.csv contains a blank required field")
                continue
            for tag in (row["overlord"], row["subject"]):
                if tag not in roster:
                    failures.append(f"subjects.csv references unknown roster tag {tag}")
                elif roster[tag]["map_capital"] == "TBD":
                    failures.append(f"subjects.csv references {tag} before its capital is mapped")
            adapter = m9_subject_adapter(row)
            if adapter not in subject_types and adapter not in set(START_ADAPTERS.values()):
                failures.append(f"unknown installed subject type {adapter}")
            if row["confidence"] not in {"secure", "contested"}:
                failures.append(f"invalid confidence {row['confidence']} for {row['subject']}")
            if row["subject"] in seen_subjects:
                failures.append(f"{row['subject']} has more than one M3 overlord")
            seen_subjects.add(row["subject"])
            dependencies.append(row)
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    lines = [
        "# Generated by tools/generate_start_mirror.py --write.",
        "# M3 dependency graph; M9 replaces vanilla adapters with ancient contracts.",
        "diplomacy_manager = {",
    ]
    for row in sorted(dependencies, key=lambda item: (item["overlord"], item["subject"])):
        lines.append(
            "\tdependency = { "
            f"first = {tag_map[row['overlord']]} second = {tag_map[row['subject']]} "
                f"subject_type = {m9_subject_adapter(row)} }} "
            f"# {row['source']}: {row['note']}"
        )
    lines.append("}")
    return "\n".join(lines) + "\n", len(dependencies)


def generated_files() -> tuple[dict[str, str], int, int, int, int, Decimal, int, int, int, int, int, int, int]:
    markets, market_count = market_manager()
    urban, urban_count = urban_manager()
    special_buildings, special_building_count, fort_count = special_building_manager()
    units, unit_manager_count = m7_unit_manager()
    roads, road_count = road_network()
    development, development_count = development_manager()
    compatibility_cultures = culture_presence_cultures()
    (
        pops,
        pop_locations,
        pop_total,
        resident_cultures,
        country_populations,
    ) = population_manager(
        compatibility_cultures
    )
    power = load_power_data()
    countries, count, controlled = country_manager(
        resident_cultures,
        country_populations,
    )
    diplomacy, dependencies = diplomacy_manager()
    return (
        {
            **STATIC_FILES,
            "02_core.txt": m8_institution_manager() + "religion_manager = {\n}\n",
            "03_markets.txt": markets,
            "04_dynasties.txt": dynasty_manager(power),
            "05_characters.txt": character_manager(power),
            "06_pops.txt": pops,
            "07_cities_and_buildings.txt": urban + "\n" + special_buildings,
            "09_roads.txt": roads,
            "10_countries.txt": countries,
            "12_diplomacy.txt": diplomacy,
            "14_development.txt": development,
            "15_international_organizations.txt": m9_international_organization_manager(),
            "21_locations.txt": compatibility_presence_manager(compatibility_cultures),
            "26_ai_personalities.txt": ai_personality_manager(),
            "27_armies.txt": units,
        },
        count,
        controlled,
        dependencies,
        pop_locations,
        pop_total,
        market_count,
        urban_count,
        special_building_count,
        fort_count,
        unit_manager_count,
        road_count,
        development_count,
    )


def installed_start_filenames() -> set[str]:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    source = Path(config["game_dir"]) / "game/main_menu/setup/start"
    return {path.name for path in source.glob("*.txt")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    failures: list[str] = []
    try:
        (
            files,
            country_count,
            controlled,
            dependencies,
            pop_locations,
            pop_total,
            market_count,
            urban_count,
            special_building_count,
            fort_count,
            unit_manager_count,
            road_count,
            development_count,
        ) = generated_files()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"start_mirror: FAIL\n  - {exc}")
        return 1
    town_setup_content = urban_town_setups()
    if args.write:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        for name, content in files.items():
            path = OUTPUT_DIR / name
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"start_mirror: wrote {path.relative_to(ROOT)}")
        URBAN_SETUP_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        URBAN_SETUP_OUTPUT.write_text(town_setup_content, encoding="utf-8-sig", newline="\n")
        print(f"start_mirror: wrote {URBAN_SETUP_OUTPUT.relative_to(ROOT)}")
        return 0
    actual = {path.name for path in OUTPUT_DIR.glob("*.txt")} if OUTPUT_DIR.is_dir() else set()
    expected = set(files)
    installed = installed_start_filenames()
    if installed != expected:
        failures.append(
            "installed start-manager inventory changed; refresh FILES before relying on the mirror"
        )
    for name in sorted(expected - actual):
        failures.append(f"missing M3 start mirror {name}")
    for name in sorted(actual - expected):
        failures.append(f"unexpected start file {name}; add it to generator inventory")
    for name, content in files.items():
        path = OUTPUT_DIR / name
        if path.is_file() and path.read_text(encoding="utf-8") != content:
            failures.append(f"stale generated start mirror {name}")
    if (
        not URBAN_SETUP_OUTPUT.is_file()
        or URBAN_SETUP_OUTPUT.read_text(encoding="utf-8-sig") != town_setup_content
    ):
        failures.append(f"stale or missing M5 town setup {URBAN_SETUP_OUTPUT.relative_to(ROOT)}")
    if failures:
        print("start_mirror: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print(
        f"start_mirror: PASS ({len(files)} exact manager filenames; "
        f"{country_count} verified-capital countries; {controlled} controlled locations; "
        f"{dependencies} dependencies; {pop_locations} populated locations; "
        f"{pop_total:,.3f} thousand people; {market_count} M5 markets; {urban_count} M5 urban nodes; "
        f"{special_building_count} M5/M7 buildings including {fort_count} M7 forts; "
        f"{unit_manager_count} M7 force seeds; {road_count} M5 road segments; "
        f"{development_count} M5 development selectors)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

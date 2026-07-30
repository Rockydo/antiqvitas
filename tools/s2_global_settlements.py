#!/usr/bin/env python3
"""Generate a dispersed, capacity-bounded AD 1 settlement economy.

Location placements are regional capacity proxies, not claims for named
excavated workshops. Secure named sites stay in the special-building ledger.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path

from m5_regional_buildings import (
    CITY_ONLY_FAMILIES,
    PRODUCTION_RECIPES,
    ROMAN_ECONOMY_FAMILIES,
    WATER_OR_PORT_FAMILIES,
)


ROOT = Path(__file__).resolve().parents[1]
DEDICATED_FOOD_FAMILIES = {
    "antq_reg_date_drying_yard",
    "antq_reg_sesame_oil_press",
    "antq_reg_nut_grinding_house",
    "antq_reg_coconut_workshop",
    "antq_reg_cheese_dairy",
    "antq_reg_meat_curing_yard",
    "antq_reg_rice_wine_house",
    "antq_reg_soy_fermentary",
}
FAMILIES = ROOT / "docs/m5/regional_building_families.csv"
SEEDS = ROOT / "docs/m5/regional_building_seeds.csv"
BUNDLES = ROOT / "docs/m5/s2_britain_ireland_building_seeds.csv"
URBAN_NODES = ROOT / "docs/m5/urban_nodes.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
POLITIES = ROOT / "docs/world_1ad/polities.csv"
RGO_AUDIT = ROOT / "docs/m5/global_rgo_audit.csv"
POPS = ROOT / "main_menu/setup/start/06_pops.txt"
AUDIT = ROOT / "docs/m5/global_settlement_audit.csv"
ROMAN_PROFILES = ROOT / "docs/m5/roman_economy_profiles.csv"

SEED_FIELDS = ("key", "family", "location", "macro", "source", "confidence", "note")
AUDIT_FIELDS = (
    "tag", "name", "region", "capital", "controlled_locations",
    "seeded_locations", "placements", "productive_placements",
    "civic_service_placements", "max_location_placements",
    "source", "confidence", "note",
)
REGION_MACRO = {
    **{region: "Europe" for region in (
        "Rome", "Britain", "Ireland", "Germania", "Balkans", "Danube",
        "Eastern Europe", "Baltic", "Finland", "Scandinavia", "Pontic",
    )},
    "Africa": "North Africa",
    **{region: "Middle East" for region in (
        "Anatolia", "Levant", "Mesopotamia", "Iran", "Arabia", "Caucasus",
    )},
    **{region: "Central Asia" for region in ("Steppe", "Central Asia", "Tarim")},
    **{region: "South Asia" for region in ("India", "Lanka")},
    "Southeast Asia": "Southeast Asia",
    **{region: "East Asia" for region in ("China", "Korea", "Japan")},
    "West Africa": "West Africa",
    **{region: "Americas" for region in (
        "Andes", "Northern Andes", "Mesoamerica", "North America",
        "Caribbean-Amazon",
    )},
    "Oceania": "Oceania",
}
LOCATION_MACRO_OVERRIDES = {
    "alexandria": "North Africa",
    "tunis": "North Africa",
    "annaba": "North Africa",
    "bizerte": "North Africa",
    "gabes": "North Africa",
    "sousse": "North Africa",
    "antioch": "Middle East",
    "baghdad": "Middle East",
    "ayasuluk": "Middle East",
    "shoubak": "Middle East",
    "homs": "Middle East",
    "sidon": "Middle East",
}

# Ubiquitous workshop inputs must not make a family look locally specific.
COMMON_INPUTS = {
    "tools", "lumber", "pottery", "cloth", "leather", "dyes", "fiber_crops",
    "coal", "tar", "sand", "goods_gold",
}
GOOD_ALIASES = {
    "barley": {"wheat"},
    "legumes": {"wheat"},
    "maize": {"millet", "wheat"},
    "potatoes": {"millet", "wheat"},
    "cassava": {"millet", "wheat"},
    "wild_game": {"livestock"},
    "horses": {"livestock"},
    "dates": {"fruit"},
    "citrus": {"fruit"},
    "spices": {"pepper", "incense"},
    "tea": {"incense"},
    "cocoa": {"fruit"},
    "coffee": {"fruit"},
}
CROP_GOODS = {
    "wheat", "barley", "millet", "rice", "maize", "legumes", "potatoes",
    "cassava", "fruit", "dates", "citrus",
}
ARID_CLIMATES = {"arid", "cold_arid", "hot_arid", "desert"}
ARABIA_CURATED_SEEDS = (
    ("reg_arabia_terraces_marib", "antq_reg_south_arabian_terrace_sluices", "marib", "UNESCO-SABA;HIMYAR-HIST;P12.1;P12.3", "secure", "Ma'rib anchors the securely attested South Arabian irrigation landscape; the building remains a market-scale terrace and sluice family rather than one reconstructed structure."),
    ("reg_arabia_terraces_dhafar", "antq_reg_south_arabian_terrace_sluices", "dhafar", "HIMYAR-HIST;UNESCO-SABA;P12.1;P12.3", "contested", "Zafar's highland setting supports a bounded terrace-water portfolio without claiming that this engine location contains a specifically excavated AD 1 installation."),
    ("reg_arabia_terraces_bayhan", "antq_reg_south_arabian_terrace_sluices", "bayhan", "UNESCO-QATABAN;UNESCO-SABA;P12.1;P12.3", "contested", "Timna's Qatabanian agricultural hinterland receives a regional terrace-water proxy, not a uniform kingdom-wide hydraulic plan."),
    ("reg_arabia_terraces_shabwa", "antq_reg_south_arabian_terrace_sluices", "shabwa", "UNESCO-INCENSE;STR-ARAB;P12.1;P12.3", "contested", "Shabwa's cultivated wadi context supports bounded water management; exact works and chronology inside the engine polygon are not asserted."),
    ("reg_arabia_station_shoubak", "antq_reg_arabian_caravan_station", "shoubak", "NABATAEA-MAP;STR-ARAB;P12.1;P12.3", "secure", "Petra's caravan and water-support role is secure; this is a scalable route-service family rather than a named excavated inn."),
    ("reg_arabia_station_dumat", "antq_reg_arabian_caravan_station", "dumat_al_jandal", "THAJ-ARCH;STR-ARAB;P12.1;P12.3", "contested", "Dumat al-Jandal's oasis-route importance supports a bounded guarded station without claiming a recovered AD 1 administrative complex."),
    ("reg_arabia_station_fayd", "antq_reg_arabian_caravan_station", "fayd", "STR-ARAB;PTO-ARAB;P12.1;P12.3", "contested", "Fayd represents an interior route halt in the engine geography; exact AD 1 fabric and institutional continuity are not asserted."),
    ("reg_arabia_station_khaybar", "antq_reg_arabian_caravan_station", "khaybar", "STR-ARAB;PTO-ARAB;P12.1;P12.3", "contested", "Khaybar's oasis position supports a caravan-service proxy while avoiding claims for a specific excavated station or later-period institution."),
    ("reg_arabia_resin_marib", "antq_reg_aromatic_resin_sorting_house", "marib", "UNESCO-SABA;UNESCO-INCENSE;P12.1", "secure", "Ma'rib's place in South Arabian aromatic exchange supports sorting and storage at market scale without a cargo-volume claim."),
    ("reg_arabia_resin_bayhan", "antq_reg_aromatic_resin_sorting_house", "bayhan", "UNESCO-QATABAN;UNESCO-INCENSE;P12.1", "secure", "Timna's Qatabanian route role supports aromatic grading and packing; the represented workshop is a reusable family, not a named building."),
    ("reg_arabia_resin_shabwa", "antq_reg_aromatic_resin_sorting_house", "shabwa", "UNESCO-INCENSE;STR-ARAB;P12.1", "secure", "Shabwa's incense nexus securely warrants an aromatic store and sorting family while exact ownership and throughput remain unspecified."),
    ("reg_arabia_resin_dhafar", "antq_reg_aromatic_resin_sorting_house", "dhafar", "HIMYAR-HIST;UNESCO-INCENSE;P12.1", "contested", "The Himyarite highland route receives a bounded aromatic handling proxy without asserting direct control of every producing district."),
    ("reg_arabia_water_suhar", "antq_reg_eastern_arabian_aflaj", "suhar", "STR-ARAB;P8.6;P12.1", "contested", "Suhar's Omanite coastal-oasis setting supports early gravity-water infrastructure, not an unchanged later legal or technical system."),
    ("reg_arabia_water_nizwa", "antq_reg_eastern_arabian_aflaj", "nizwa", "STR-ARAB;P8.6;P12.1", "contested", "Nizwa provides an interior Omanite oasis proxy for local water channels; exact AD 1 construction and terminology remain uncertain."),
    ("reg_arabia_water_ahsa", "antq_reg_eastern_arabian_aflaj", "al_ahsa", "OCD-GERRHA;STR-ARAB;P12.1", "contested", "The al-Hasa oasis warrants distributed water infrastructure while the Gerrha location mapping and individual channel chronology remain bounded."),
    ("reg_arabia_water_harad", "antq_reg_eastern_arabian_aflaj", "harad_al_ahsa", "OCD-GERRHA;STR-ARAB;P12.1", "contested", "The eastern Arabian oasis hinterland receives a water-channel proxy without claiming a single polity-wide administration or excavated plan."),
)
GERMANIA_CURATED_SEEDS = (
    ("reg_germania_depth_marcomannic_prague", "antq_reg_marcomannic_royal_compound", "prague", "P8.7;STR-GER;TAC-ANN-II", "Bohemian court-region proxy; no excavated palace or fixed royal seat."),
    ("reg_germania_depth_marcomannic_kourim", "antq_reg_marcomannic_royal_compound", "kourim", "P8.7;STR-GER;TAC-ANN-II", "Bohemian court-region proxy; no excavated palace or fixed royal seat."),
    ("reg_germania_depth_marcomannic_hradec", "antq_reg_marcomannic_royal_compound", "hradec_kralove", "P8.7;STR-GER;TAC-ANN-II", "Bohemian court-region proxy; no excavated palace or fixed royal seat."),
    ("reg_germania_depth_assembly_minden", "antq_reg_germanic_assembly_field", "minden", "P8.7;TAC-GER;STR-GER", "Cheruscan-region assembly proxy; no universal constitution or reconstructed site."),
    ("reg_germania_depth_assembly_kassel", "antq_reg_germanic_assembly_field", "kassel", "P8.7;TAC-GER;STR-GER", "Chattian-region assembly proxy; no universal constitution or reconstructed site."),
    ("reg_germania_depth_assembly_teltow", "antq_reg_germanic_assembly_field", "teltow", "P8.7;TAC-GER;STR-GER", "Semnonian-region assembly proxy distinct from the sacred-grove family."),
    ("reg_germania_depth_grove_teltow", "antq_reg_semnonian_sacred_grove", "teltow", "P8.7;TAC-GER;STR-GER", "Semnonian sacred-landscape proxy; Tacitus's grove is not fixed to one polygon."),
    ("reg_germania_depth_grove_ruppin", "antq_reg_semnonian_sacred_grove", "ruppin", "P8.7;TAC-GER;STR-GER", "Semnonian sacred-landscape proxy; no reconstructed sanctuary."),
    ("reg_germania_depth_grove_juterbog", "antq_reg_semnonian_sacred_grove", "juterbog", "P8.7;TAC-GER;STR-GER", "Semnonian sacred-landscape proxy; no reconstructed sanctuary."),
    ("reg_germania_depth_market_nijmegen", "antq_reg_rhine_frontier_market", "nijmegen", "P8.7;TAC-BAT;TAC-ANN-II", "Rhine exchange proxy; no permanent market charter or tariff regime."),
    ("reg_germania_depth_market_bonn", "antq_reg_rhine_frontier_market", "bonn", "P8.7;TAC-GER;TAC-ANN-II", "Rhine exchange proxy; no permanent market charter or tariff regime."),
    ("reg_germania_depth_market_mainz", "antq_reg_rhine_frontier_market", "mainz", "P8.7;TAC-GER;TAC-ANN-II", "Rhine exchange proxy; no permanent market charter or tariff regime."),
    ("reg_germania_depth_batavian_nijmegen", "antq_reg_batavian_auxiliary_muster", "nijmegen", "P8.7;TAC-BAT;CAH-XI", "Lower-Rhine auxiliary-service proxy; no reconstructed cohort base."),
    ("reg_germania_depth_batavian_antwerp", "antq_reg_batavian_auxiliary_muster", "antwerp", "P8.7;TAC-BAT;CAH-XI", "Lower-Rhine auxiliary-service proxy; no reconstructed cohort base."),
    ("reg_germania_depth_batavian_hertogenbosch", "antq_reg_batavian_auxiliary_muster", "hertogenbosch", "P8.7;TAC-BAT;CAH-XI", "Lower-Rhine auxiliary-service proxy; no reconstructed cohort base."),
    ("reg_germania_depth_amber_konigsberg", "antq_reg_aestian_amber_sorting_ground", "konigsberg", "P8.7;TAC-GER;PAN-WBB;VU-BRUSH", "Plural Aestian amber-shore proxy; not a central capital or monopoly."),
    ("reg_germania_depth_amber_tilsit", "antq_reg_aestian_amber_sorting_ground", "tilsit", "P8.7;TAC-GER;PAN-WBB;VU-BRUSH", "Plural Aestian amber-shore proxy; not a central capital or monopoly."),
    ("reg_germania_depth_amber_olsztyn", "antq_reg_aestian_amber_sorting_ground", "olsztyn", "P8.7;TAC-GER;PAN-WBB;LIT-WLSC", "Plural Aestian amber-shore proxy; not a central capital or monopoly."),
    ("reg_germania_depth_migration_gdansk", "antq_reg_vistula_migration_staging", "gdansk", "P8.7;PAN-WBB;STR-GER", "Lower-Vistula movement proxy; no fixed ethnic route or inevitable destination."),
    ("reg_germania_depth_migration_grudziadz", "antq_reg_vistula_migration_staging", "grudziadz", "P8.7;PAN-WBB;STR-GER", "Lower-Vistula movement proxy; no fixed ethnic route or inevitable destination."),
    ("reg_germania_depth_migration_tczew", "antq_reg_vistula_migration_staging", "tczew", "P8.7;PAN-WBB;STR-GER", "Lower-Vistula movement proxy; no fixed ethnic route or inevitable destination."),
    ("reg_germania_depth_landing_stavoren", "antq_reg_north_sea_boat_landing", "stavoren", "P8.7;TAC-GER;UT-TARAND", "North-Sea coastal-craft proxy; not a fleet base."),
    ("reg_germania_depth_landing_sloten", "antq_reg_north_sea_boat_landing", "sloten", "P8.7;TAC-GER;UT-TARAND", "North-Sea coastal-craft proxy; not a fleet base."),
    ("reg_germania_depth_landing_hamburg", "antq_reg_north_sea_boat_landing", "hamburg", "P8.7;TAC-GER;STR-GER", "Lower-Elbe coastal-craft proxy; not a navy or migration port."),
)
SOUTHERN_HUNTER_HERDER_CURATED_SEEDS = (
    ("reg_southern_hh_shelter_impakwe", "antq_reg_southern_rock_shelter_custody", "impakwe", "OUP-SOUTH-AFRICA;CAM-SA-2024;P12.1;P12.3", "Repeated-use rock-shelter capacity in the Limpopo frame; no excavated shelter, named group, rite, or ownership boundary is assigned to this engine polygon."),
    ("reg_southern_hh_shelter_mwenezi", "antq_reg_southern_rock_shelter_custody", "mwenezi", "OUP-SOUTH-AFRICA;CAM-SA-2024;P12.1;P12.3", "Repeated-use rock-shelter capacity in the Limpopo frame; no excavated shelter, named group, rite, or ownership boundary is assigned to this engine polygon."),
    ("reg_southern_hh_shelter_inyanga", "antq_reg_southern_rock_shelter_custody", "inyanga", "OUP-SOUTH-AFRICA;CAM-SA-2024;P12.1;P12.3", "Highland shelter-use proxy in the Zambezi frame; later settlement systems and a specific archaeological shelter are not projected into AD 1."),
    ("reg_southern_hh_shelter_mtoko", "antq_reg_southern_rock_shelter_custody", "mtoko", "OUP-SOUTH-AFRICA;CAM-SA-2024;P12.1;P12.3", "Highland shelter-use proxy in the Zambezi frame; later settlement systems and a specific archaeological shelter are not projected into AD 1."),
    ("reg_southern_hh_water_chumnungwa", "antq_reg_seasonal_waterhole_camp", "chumnungwa", "OUP-SOUTH-AFRICA;CAM-SA-2024;P12.1;P12.3", "Seasonal water-access capacity in the Limpopo frame; no permanent village, exclusive circuit, chief, or named camp is claimed."),
    ("reg_southern_hh_water_jahunda", "antq_reg_seasonal_waterhole_camp", "jahunda", "OUP-SOUTH-AFRICA;CAM-SA-2024;P12.1;P12.3", "Seasonal water-access capacity in the Limpopo frame; no permanent village, exclusive circuit, chief, or named camp is claimed."),
    ("reg_southern_hh_water_charumani", "antq_reg_seasonal_waterhole_camp", "charumani", "OUP-SOUTH-AFRICA;CAM-SA-2024;P12.1;P12.3", "Seasonal water-access capacity in the Save frame; no permanent village, exclusive circuit, chief, or named camp is claimed."),
    ("reg_southern_hh_water_majiri", "antq_reg_seasonal_waterhole_camp", "majiri", "OUP-SOUTH-AFRICA;CAM-SA-2024;P12.1;P12.3", "Seasonal water-access capacity in the Save frame; no permanent village, exclusive circuit, chief, or named camp is claimed."),
    ("reg_southern_hh_river_chibuene", "antq_reg_riverine_gathering_ground", "chibuene", "OUP-SOUTH-AFRICA;CAM-SA-2024;P12.1;P12.3", "Coastal-river gathering capacity in the Limpopo frame; no permanent market, later port settlement, or named institution is backdated."),
    ("reg_southern_hh_river_inhambane", "antq_reg_riverine_gathering_ground", "inhambane", "OUP-SOUTH-AFRICA;CAM-SA-2024;P12.1;P12.3", "Coastal-river gathering capacity in the Limpopo frame; no permanent market, later port settlement, or named institution is backdated."),
    ("reg_southern_hh_river_sofala", "antq_reg_riverine_gathering_ground", "sofala", "OUP-SOUTH-AFRICA;CAM-SA-2024;P12.1;P12.3", "Riverine gathering capacity in the Save frame; no later Sofala port, trade monopoly, permanent village, or named institution is backdated."),
    ("reg_southern_hh_river_chipagwe", "antq_reg_riverine_gathering_ground", "chipagwe", "OUP-SOUTH-AFRICA;CAM-SA-2024;P12.1;P12.3", "Riverine gathering capacity in the Save frame; no permanent market, settlement plan, or named institution is claimed."),
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(line for line in handle if not line.startswith("#"))
        ]


def population_totals() -> dict[str, float]:
    result: dict[str, float] = {}
    current = ""
    for line in POPS.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"^\t([a-z0-9_]+) = \{$", line)
        if match:
            current = match.group(1)
            result.setdefault(current, 0.0)
            continue
        if current:
            result[current] += sum(
                float(value)
                for value in re.findall(r"\bsize = ([0-9]+(?:\.[0-9]+)?)", line)
            )
            if line == "\t}":
                current = ""
    return result


def expanded_bundle_rows() -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for bundle in read_rows(BUNDLES):
        for index, family in enumerate(bundle["families"].split("|"), start=1):
            result.append({
                "key": f"reg_{bundle['key']}_{index}",
                "family": family,
                "location": bundle["location"],
                "macro": bundle["macro"],
                "source": bundle["source"],
                "confidence": bundle["confidence"],
                "note": bundle["note"],
            })
    return result


def curated_arabia_rows() -> list[dict[str, str]]:
    return [
        {
            "key": key,
            "family": family,
            "location": location,
            "macro": "Middle East",
            "source": source,
            "confidence": confidence,
            "note": note,
        }
        for key, family, location, source, confidence, note in ARABIA_CURATED_SEEDS
    ]


def curated_germania_rows() -> list[dict[str, str]]:
    return [
        {
            "key": key,
            "family": family,
            "location": location,
            "macro": "Europe",
            "source": source,
            "confidence": "contested",
            "note": note,
        }
        for key, family, location, source, note in GERMANIA_CURATED_SEEDS
    ]


def curated_southern_hunter_herder_rows() -> list[dict[str, str]]:
    return [
        {
            "key": key,
            "family": family,
            "location": location,
            # The polity ledger's broad ``Africa`` region is represented by
            # the legacy North Africa macro bucket in the building audit.
            "macro": "North Africa",
            "source": source,
            "confidence": "contested",
            "note": note,
        }
        for key, family, location, source, note
        in SOUTHERN_HUNTER_HERDER_CURATED_SEEDS
    ]


def candidate_score(
    family: str,
    good: str,
    owner_region: str,
    harbor: float,
    urban_profile: str,
    climate: str,
    signatures: dict[str, set[str]],
    usage: Counter[str],
) -> tuple[float, str]:
    if family in ROMAN_ECONOMY_FAMILIES and owner_region != "Rome":
        return (-10_000.0, family)
    if family in CITY_ONLY_FAMILIES and urban_profile != "city":
        return (-10_000.0, family)
    if family in WATER_OR_PORT_FAMILIES and harbor <= 0:
        return (-10_000.0, family)

    matches = {good, *GOOD_ALIASES.get(good, set())}
    score = 70.0 if matches & signatures[family] else 0.0
    if good in CROP_GOODS and any(token in family for token in ("granary", "mill", "bread", "brew")):
        score += 35.0
    if good == "rice" and "rice" in family:
        score += 50.0
    if good != "rice" and "rice" in family:
        score -= 90.0
    if good != "millet" and "millet" in family:
        score -= 70.0
    if good not in {"wheat", "barley", "legumes"} and "wheat" in family:
        score -= 50.0
    if climate in ARID_CLIMATES and any(token in family for token in ("cistern", "caravan", "pack_animal")):
        score += 18.0
    if harbor > 0 and family in WATER_OR_PORT_FAMILIES:
        score += 14.0
    if urban_profile == "city" and family in CITY_ONLY_FAMILIES:
        score += 10.0
    score -= min(usage[family], 40) * 0.8
    return (score, family)


def generate() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    families = read_rows(FAMILIES)
    family_keys = [
        row["key"] for row in families
        if row["key"] not in DEDICATED_FOOD_FAMILIES
    ]
    signatures = {
        row["key"]: {
            good for good in row["goods"].split(";")
            if good and good not in COMMON_INPUTS
        }
        for row in families
    }
    polities = {row["tag"]: row for row in read_rows(POLITIES)}
    ownership_rows = read_rows(OWNERSHIP)
    rgo = {row["location"]: row for row in read_rows(RGO_AUDIT)}
    populations = population_totals()
    urban = {row["location"]: row["profile"] for row in read_rows(URBAN_NODES)}

    locations_by_tag: dict[str, list[str]] = defaultdict(list)
    owner_by_location: dict[str, str] = {}
    for row in ownership_rows:
        locations_by_tag[row["tag"]].append(row["location"])
        owner_by_location[row["location"]] = row["tag"]

    bundle_rows = expanded_bundle_rows()
    rows = (
        curated_arabia_rows()
        + curated_germania_rows()
        + curated_southern_hunter_herder_rows()
    )
    curated_count = len(rows)
    fixed_rows = rows + bundle_rows
    used_pairs = {(row["location"], row["family"]) for row in fixed_rows}
    usage: Counter[str] = Counter(row["family"] for row in fixed_rows)
    per_location: Counter[str] = Counter(row["location"] for row in fixed_rows)

    def details(location: str) -> tuple[str, str, float, str, str]:
        tag = owner_by_location[location]
        region = polities[tag]["region"]
        data = rgo[location]
        try:
            harbor = float(data["natural_harbor_suitability"] or 0)
        except ValueError:
            harbor = 0.0
        return tag, region, harbor, urban.get(location, ""), data["ad1_good"]

    def choose_family(location: str) -> str:
        _tag, region, harbor, urban_profile, good = details(location)
        candidates = [
            family for family in family_keys
            if family in PRODUCTION_RECIPES and (location, family) not in used_pairs
        ]
        return max(
            candidates,
            key=lambda family: candidate_score(
                family, good, region, harbor, urban_profile,
                rgo[location]["climate"], signatures, usage,
            ),
        )

    def add(
        location: str,
        family: str,
        reason: str,
        *,
        key: str = "",
        source: str = "P12.1;P12.3;P13;PER",
        confidence: str = "contested",
        note: str = "",
        cap: int = 6,
    ) -> bool:
        pair = (location, family)
        if pair in used_pairs or per_location[location] >= cap:
            return False
        tag, region, _harbor, _urban_profile, good = details(location)
        index = len(rows) - curated_count + 1
        rows.append({
            "key": key or f"reg_world_{index:04d}_{location}",
            "family": family,
            "location": location,
            "macro": LOCATION_MACRO_OVERRIDES.get(location, REGION_MACRO[region]),
            "source": source,
            "confidence": confidence,
            "note": note or (
                f"AD 1 {reason} capacity proxy for {polities[tag]['name']}; "
                f"the {good} resource, generated population, settlement rank, "
                "and controlled hinterland guide placement, not a claim for a "
                "named excavated workshop in this engine polygon."
            ),
        })
        used_pairs.add(pair)
        usage[family] += 1
        per_location[location] += 1
        return True

    selected_locations: set[str] = set()
    # Preserve the deeply differentiated, source-reviewed Roman provincial
    # packages as metropolitan exceptions. Ordinary sites remain capped at six.
    roman_slugs = {family.removeprefix("antq_reg_") for family in ROMAN_ECONOMY_FAMILIES}
    for profile in read_rows(ROMAN_PROFILES):
        selected = (
            roman_slugs
            if profile["families"] == "all"
            else set(profile["families"].split(";"))
        )
        for location in profile["locations"].split(";"):
            if not location:
                continue
            selected_locations.add(location)
            for slug in sorted(selected):
                family = f"antq_reg_{slug}"
                if urban.get(location) == "town" and family in CITY_ONLY_FAMILIES:
                    continue
                add(
                    location,
                    family,
                    "reviewed Roman provincial",
                    key=f"reg_roman_economy_{profile['profile']}_{location}_{slug}",
                    source=profile["source"],
                    confidence=profile["confidence"],
                    note=profile["note"],
                    cap=32,
                )

    for tag in sorted(polities):
        controlled = locations_by_tag[tag]
        if not controlled:
            continue
        capital = polities[tag]["map_capital"]
        ordered = sorted(
            controlled,
            key=lambda location: (
                location != capital,
                -populations.get(location, 0.0),
                location,
            ),
        )
        quota = min(len(ordered), max(2, min(18, round(math.sqrt(len(ordered))))))
        chosen: list[str] = []
        seen_goods: set[str] = set()
        for location in ordered:
            good = rgo[location]["ad1_good"]
            if location == capital or good not in seen_goods:
                chosen.append(location)
                seen_goods.add(good)
            if len(chosen) == quota:
                break
        if len(chosen) < quota:
            chosen.extend(location for location in ordered if location not in chosen)
            chosen = chosen[:quota]
        for location in chosen:
            selected_locations.add(location)
            add(location, choose_family(location), "settlement-and-hinterland economic")
        if capital in controlled:
            add(capital, choose_family(capital), "capital-market")

    for location in sorted(urban):
        if location not in owner_by_location:
            continue
        selected_locations.add(location)
        add(location, choose_family(location), "urban-service and craft")

    for family in family_keys:
        if usage[family]:
            continue
        candidates: list[tuple[float, float, str]] = []
        for location in selected_locations:
            _tag, region, harbor, urban_profile, good = details(location)
            score, _ = candidate_score(
                family, good, region, harbor, urban_profile,
                rgo[location]["climate"], signatures, usage,
            )
            if score > -10_000 and per_location[location] < 6:
                candidates.append((score, populations.get(location, 0.0), location))
        if not candidates:
            raise ValueError(f"no valid global settlement candidate for {family}")
        _score, _population, location = max(candidates)
        add(location, family, "specialized regional craft")

    # A settlement system also needs storage, water, transport, exchange, and
    # civic capacity. Bring ordinary regional placements to a 75% productive
    # target, dispersed over the same reviewed settlement sample.
    def choose_service(location: str) -> str:
        _tag, region, harbor, urban_profile, good = details(location)
        candidates = [
            family for family in family_keys
            if family not in PRODUCTION_RECIPES and (location, family) not in used_pairs
        ]
        return max(
            candidates,
            key=lambda family: candidate_score(
                family, good, region, harbor, urban_profile,
                rgo[location]["climate"], signatures, usage,
            ),
        )

    productive_count = sum(
        row["family"] in PRODUCTION_RECIPES for row in rows + bundle_rows
    )
    service_count = len(rows) + len(bundle_rows) - productive_count
    service_target = math.ceil(productive_count / 3)
    service_locations = sorted(
        selected_locations,
        key=lambda location: (-populations.get(location, 0.0), location),
    )
    cursor = 0
    while service_count < service_target:
        location = service_locations[cursor % len(service_locations)]
        cursor += 1
        if per_location[location] >= 6:
            continue
        family = choose_service(location)
        score, _ = candidate_score(
            family,
            rgo[location]["ad1_good"],
            polities[owner_by_location[location]]["region"],
            details(location)[2],
            urban.get(location, ""),
            rgo[location]["climate"],
            signatures,
            usage,
        )
        if score <= -10_000:
            continue
        if add(location, family, "storage, exchange, transport, or civic-service"):
            service_count += 1

    all_rows = rows + bundle_rows
    placements_by_tag: Counter[str] = Counter()
    productive_by_tag: Counter[str] = Counter()
    locations_per_tag: dict[str, set[str]] = defaultdict(set)
    location_counts_by_tag: dict[str, Counter[str]] = defaultdict(Counter)
    for row in all_rows:
        tag = owner_by_location[row["location"]]
        placements_by_tag[tag] += 1
        productive_by_tag[tag] += row["family"] in PRODUCTION_RECIPES
        locations_per_tag[tag].add(row["location"])
        location_counts_by_tag[tag][row["location"]] += 1

    audit_rows: list[dict[str, str]] = []
    for tag, polity in sorted(polities.items()):
        total = placements_by_tag[tag]
        productive = productive_by_tag[tag]
        audit_rows.append({
            "tag": tag,
            "name": polity["name"],
            "region": polity["region"],
            "capital": polity["map_capital"],
            "controlled_locations": str(len(locations_by_tag[tag])),
            "seeded_locations": str(len(locations_per_tag[tag])),
            "placements": str(total),
            "productive_placements": str(productive),
            "civic_service_placements": str(total - productive),
            "max_location_placements": str(max(location_counts_by_tag[tag].values(), default=0)),
            "source": "P12.1;P12.3;P13;PER",
            "confidence": "contested",
            "note": (
                "Capacity-bounded opening settlement sample; named sites remain "
                "in the special-building ledger and absence is not archaeological evidence."
            ),
        })
    return rows, audit_rows


def render(rows: list[dict[str, str]], fields: tuple[str, ...]) -> str:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        seeds, audit = generate()
    except (KeyError, ValueError) as exc:
        print(f"s2_global_settlements: FAIL\n  - {exc}")
        return 1
    outputs = {
        SEEDS: render(seeds, SEED_FIELDS),
        AUDIT: render(audit, AUDIT_FIELDS),
    }
    if args.write:
        for path, text in outputs.items():
            path.write_text(text, encoding="utf-8", newline="")
        print(
            "s2_global_settlements: wrote "
            f"{len(seeds)} direct placements and {len(audit)} polity audit rows"
        )
        return 0
    stale = [
        str(path.relative_to(ROOT))
        for path, expected in outputs.items()
        if not path.exists() or path.read_text(encoding="utf-8-sig") != expected
    ]
    if stale:
        print("s2_global_settlements: FAIL (stale generated files)\n  - " + "\n  - ".join(stale))
        return 1
    print(
        "s2_global_settlements: PASS "
        f"({len(seeds)} direct placements; {len(audit)} starting polities)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render and validate ANTIQVITAS's complete M8 knowledge layer.

The installed database is deliberately replaced by exact filenames: continuing
to carry medieval and early-modern advances underneath an ancient tree would
make anachronisms reachable even when the new advances are sound.  This tool
keeps the source manifest tied to the locally pinned EU5 installation and
produces the continuous historical trees from the documented M8 design.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, M2_MIRROR_LANGUAGES
from legacy_institutions import legacy_references, neutralize_references

ROOT = Path(__file__).resolve().parents[1]
ADVANCES = ROOT / "in_game/common/advances"
INSTITUTIONS = ROOT / "in_game/common/institution"
SCRIPTED_TRIGGERS = ROOT / "in_game/common/scripted_triggers"
STATIC_MODIFIERS = ROOT / "main_menu/common/static_modifiers"
LOC_ROOT = ROOT / "main_menu/localization"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
DIRECT_ADVANCE_ART = ROOT / "docs/m11/direct_advance_icons.csv"
INSTITUTION_LEDGER = ROOT / "docs/m8/institutions.csv"
INSTALLED_INSTITUTION_LEDGER = ROOT / "docs/m8/installed_institution_inventory.csv"
VANILLA_INSTITUTION_SYMBOLS = ROOT / "docs/vanilla_symbols/institution.json"

AGE_KEYS = (
    "age_1_traditions", "age_2_renaissance", "age_3_discovery",
    "age_4_reformation", "age_5_absolutism", "age_6_revolutions",
)
AGE_NAMES = ("Principate", "High Empires", "Crisis", "Dominate", "Federate Age", "Migrations")
ICONS = (
    "abacus_advance", "legalism_advance", "road_advance_1",
    "crown_power_advance_discovery", "expansionism", "expansionism",
)
FORBIDDEN = (
    "gunpowder", "cannon", "arquebus", "musket", "flintlock", "colonial",
    "oceanic", "ocean_crossing", "steam", "printing_press",
)
UNLOCK = re.compile(r"^\s*unlock_(?:unit|levy)\s*=", re.IGNORECASE)
TOP_LEVEL = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*=\s*\{")
POTENTIAL = re.compile(r"^\s*potential\s*=")
CAN_SPAWN = re.compile(r"^\s*can_spawn\s*=")
CORE_TAGS = frozenset(("ROM", "HAN", "PAR"))
# The AD 1 setup retains a small, engine-native law/policy surface for
# administrative continuity.  M8 replaces the vanilla advances that formerly
# unlocked these categories, so matching ancient advances must carry the
# unlocks or the engine strips otherwise valid start laws at initialization.
# These are mechanics-category bridges, not claims that their vanilla labels
# describe the historical institutions represented by M6's custom adapters.
START_UNLOCKS: dict[str, tuple[tuple[str, str], ...]] = {
    # Every AD 1 technology tier receives the five depth-zero advances.  The
    # installed tribal templates set these two engine-native law categories at
    # creation, so their category bridges must live at that universally held
    # depth rather than at later thematic advances.  This is only a mechanical
    # compatibility mapping; M6's custom laws remain the historical surface.
    "antq_imperial_cult": (
        ("unlock_law", "legal_code_law"),
        ("unlock_law", "education_masses_law"),
        ("unlock_law", "tribal_legal_basis_law"),
    ),
    "antq_provincial_census": (("unlock_law", "administrative_system"),),
    "antq_tax_registers": (("unlock_law", "distribution_of_power_law"),),
    "antq_road_milestones": (("unlock_law", "royal_court_customs_law"),),
    "antq_municipal_charters": (("unlock_law", "feudal_de_jure_law"),),
    # Vanilla's first infantry advance unlocks this court policy.  Its units
    # are deliberately suppressed, but this category bridge is still needed
    # for monarchies that retain the engine-native court selection.
    "antq_professional_standing_armies": (
        ("unlock_law", "medieval_levy_law"),
        ("unlock_policy", "aristocratic_court_policy"),
    ),
    "antq_auxiliary_service": (("unlock_law", "tribal_religious_values_law"),),
    "antq_drill_routines": (("unlock_law", "tribal_organization_law"),),
    "antq_monsoon_navigation": (("unlock_law", "coin_laws"),),
    "antq_red_sea_piloting": (("unlock_law", "mining_law"),),
    "antq_caravan_accounting": (("unlock_law", "immigration_law"),),
    "antq_paper_precursors": (("unlock_law", "cultural_traditions_law"),),
    # Polygyny is a policy inside the religious marriage_law category; it is
    # not itself granted by a vanilla advance.  Unlock its parent category.
    "antq_civic_associations": (("unlock_law", "marriage_law"),),
}


# Five ten-step strands run through the plan's five conceptual arcs; the
# mandatory sixth engine slot divides the final arc into two five-step halves.
# Their names are the source-led historical statements; individual mechanical
# effects stay bounded to locally verified engine contracts in M9/M10.
TRACKS: dict[str, tuple[tuple[str, ...], ...]] = {
    "statecraft": (
        ("imperial_cult", "provincial_census", "tax_registers", "road_milestones", "legal_petitions", "municipal_charters", "public_granaries", "frontier_dispatches", "imperial_archives", "standing_administration"),
        ("jurists_law", "commentary_schools", "provincial_assizes", "civic_patronage", "municipal_accounting", "estate_registries", "imperial_rescripts", "law_of_persons", "provincial_governance", "high_empire_administration"),
        ("crisis_coinage", "emergency_levies", "fiscal_reassessment", "mint_accounting", "regional_commands", "emergency_rescripts", "grain_annona", "imperial_dioceses", "revenue_recovery", "crisis_statecraft"),
        ("diocesan_administration", "codification", "notarial_offices", "imperial_chancery", "provincial_prefects", "tax_in_kind", "public_post", "legal_compilations", "late_roman_bureaucracy", "dominate_statecraft"),
        ("kingdom_charters", "barbarian_hospitality", "land_assignment", "successor_taxation", "royal_notaries", "regional_law_codes", "mixed_courts", "settlement_registers", "kingdom_building", "post_roman_statecraft"),
    ),
    "warfare": (
        ("professional_standing_armies", "auxiliary_service", "drill_routines", "supply_columns", "field_engineering", "frontier_patrols", "river_crossings", "siegecraft_basics", "legionary_logistics", "principate_warfare"),
        ("cataphract_adoption", "composite_bow_tactics", "camel_screening", "frontier_cavalry", "mounted_scouts", "heavy_cavalry_drill", "campaign_seasons", "deep_defence", "imperial_field_forces", "high_empire_warfare"),
        ("mobile_field_armies", "crisis_fortification", "wall_building", "beacon_networks", "regional_reserves", "cavalry_screening", "siege_relief", "marching_camps", "defence_in_depth", "crisis_warfare"),
        ("comitatenses_doctrine", "limitanei_service", "foederati_settlement", "heavy_lancer_refinement", "military_bureaux", "fortified_crossings", "mobile_reserves", "frontier_commands", "late_antique_logistics", "dominate_warfare"),
        ("federate_musters", "settlement_service", "warband_integration", "horse_furniture", "shield_wall_tactics", "regional_militias", "successor_armies", "frontier_kingdoms", "migration_warfare", "late_antique_arms"),
    ),
    "exchange": (
        ("monsoon_navigation", "red_sea_piloting", "caravan_accounting", "silk_exchange", "port_customs", "desert_waystations", "merchant_diasporas", "coin_exchange", "seasonal_markets", "principate_exchange"),
        ("silk_road_caravanserais", "long_distance_credit", "market_regulation", "eastern_mediterranean_routes", "indian_ocean_monsoons", "border_customs", "merchant_associations", "warehouse_accounts", "imperial_trade", "high_empire_exchange"),
        ("crisis_trade_routes", "debased_currency_exchange", "military_supply_markets", "fortified_warehouses", "caravan_protection", "regional_exchange", "grain_convoys", "emergency_tolls", "resilient_markets", "crisis_exchange"),
        ("state_annona_routes", "bureaucratic_customs", "foederati_provisioning", "frontier_market_towns", "church_storehouses", "caravan_tolls", "late_antique_coinage", "regional_fairs", "dominate_exchange", "late_antique_commerce"),
        ("migration_market_links", "gift_exchange", "kingdom_tolls", "riverine_trade", "settlement_markets", "regional_caravans", "successor_coinage", "frontier_fairs", "kingdom_exchange", "post_roman_commerce"),
    ),
    "learning": (
        ("paper_precursors", "bamboo_registers", "library_catalogues", "han_classics", "astronomical_tables", "medical_compendia", "legal_commentaries", "surveying_methods", "scholarly_correspondence", "principate_learning"),
        ("juristic_schools", "mathematical_handbooks", "medical_schools", "textual_criticism", "observatory_records", "library_endowments", "philosophical_dialogue", "engineering_manuals", "scholarly_networks", "high_empire_learning"),
        ("crisis_scholarly_preservation", "portable_archives", "clerical_literacy", "military_manuals", "medical_relief", "calendar_revision", "epistolary_networks", "regional_schools", "crisis_learning", "survival_of_texts"),
        ("state_church", "monastic_scriptoria", "orthodoxy_debates", "codex_manuscripts", "legal_scholars", "bureaucratic_education", "commentary_traditions", "late_antique_schools", "doctrinal_debate", "dominate_learning"),
        ("monastic_libraries", "translation_circles", "kingdom_schools", "clerical_recordkeeping", "lawbook_copying", "regional_chronicles", "successor_scholarship", "pilgrim_learning", "migration_learning", "late_antique_letters"),
    ),
    "society": (
        ("civic_associations", "imperial_ceremony", "urban_waterworks", "public_baths", "religious_endowments", "veteran_settlement", "provincial_elites", "ritual_calendars", "civic_identity", "principate_society"),
        ("cosmopolitan_cities", "public_philanthropy", "legal_statuses", "religious_plurals", "urban_professions", "provincial_citizenship", "athletic_festivals", "scholarly_patronage", "high_empire_society", "imperial_cultures"),
        ("crisis_communities", "refugee_settlement", "plague_relief", "local_patronage", "religious_consolation", "fortified_towns", "rural_resilience", "civic_recovery", "crisis_society", "surviving_cities"),
        ("church_endowments", "monastic_communities", "imperial_orthodoxy", "settled_foederati", "late_antique_cities", "charitable_hospices", "regional_elites", "religious_law", "dominate_society", "late_antique_communities"),
        ("hospitality_of_barbarians", "mixed_settlements", "kingdom_churches", "regional_identities", "customary_law", "migration_networks", "successor_elites", "rural_communities", "migrations_society", "roman_successor_worlds"),
    ),
}


@dataclass(frozen=True)
class Advance:
    key: str
    name: str
    age: str
    age_index: int
    depth: int
    requires: str | None


@dataclass(frozen=True)
class Institution:
    key: str
    name: str
    description: str
    age: str
    location: str
    start_active: bool
    earliest: str
    spread_band: str
    profile: str
    trade_spread: bool
    source: str


@dataclass(frozen=True)
class InstitutionProfile:
    key: str
    summary: str
    script: tuple[str, ...]


INSTITUTION_PROFILES = {
    profile.key: profile
    for profile in (
        InstitutionProfile(
            "mediterranean_letters",
            "Mediterranean civic and learned networks",
            (
                "OR = {",
                "\tregion = region:italy_region",
                "\tregion = region:balkan_region",
                "\tregion = region:anatolia_region",
                "\tregion = region:egypt_region",
                "\tregion = region:crescent_region",
                "}",
            ),
        ),
        InstitutionProfile(
            "roman_imperial_practice",
            "Roman and provincial societies inside the historical imperial sphere",
            (
                "AND = {",
                "\tOR = {",
                "\t\tregion = region:italy_region",
                "\t\tregion = region:iberia_region",
                "\t\tregion = region:france_region",
                "\t\tregion = region:great_britain_region",
                "\t\tregion = region:north_german_region",
                "\t\tregion = region:south_german_region",
                "\t\tregion = region:balkan_region",
                "\t\tregion = region:anatolia_region",
                "\t\tregion = region:crescent_region",
                "\t\tregion = region:egypt_region",
                "\t\tregion = region:maghreb_region",
                "\t}",
                "\tOR = {",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_italic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_hellenic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_celtic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_iberian_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_anatolian_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_semitic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_berber_group }",
                "\t}",
                "}",
            ),
        ),
        InstitutionProfile(
            "east_asian_administration",
            "Sinitic, Korean, and adjacent East Asian administrative contexts",
            (
                "AND = {",
                "\tOR = {",
                "\t\tregion = region:east_china_region",
                "\t\tregion = region:north_china_region",
                "\t\tregion = region:south_china_region",
                "\t\tregion = region:west_china_region",
                "\t\tregion = region:korea_region",
                "\t\tregion = region:manchuria_region",
                "\t\tregion = region:indochina_region",
                "\t}",
                "\tOR = {",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_sinitic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_korean_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_southeast_asian_group }",
                "\t}",
                "}",
            ),
        ),
        InstitutionProfile(
            "buddhist_networks",
            "Buddhist communities across South, Central, and East Asian corridors",
            (
                "OR = {",
                "\tdominant_religion = { group = religion_group:antq_buddhist_group }",
                "\tregion = region:bengal_region",
                "\tregion = region:central_india_region",
                "\tregion = region:deccan_region",
                "\tregion = region:hindustan_region",
                "\tregion = region:western_india_region",
                "\tregion = region:xinjiang_region",
                "\tregion = region:tibet_region",
                "\tregion = region:east_china_region",
                "\tregion = region:north_china_region",
                "\tregion = region:south_china_region",
                "\tregion = region:west_china_region",
                "\tregion = region:korea_region",
                "\tregion = region:indochina_region",
                "}",
            ),
        ),
        InstitutionProfile(
            "iranian_steppe_cavalry",
            "Iranian, steppe, Caucasian, and eastern Roman military corridors",
            (
                "OR = {",
                "\tregion = region:persia_region",
                "\tregion = region:khorasan_region",
                "\tregion = region:steppes_region",
                "\tregion = region:caucasus_region",
                "\tregion = region:xinjiang_region",
                "\tregion = region:anatolia_region",
                "\tregion = region:crescent_region",
                "\tregion = region:balkan_region",
                "\tdominant_culture = { has_culture_group = culture_group:antq_iranian_group }",
                "\tdominant_culture = { has_culture_group = culture_group:antq_steppe_group }",
                "}",
            ),
        ),
        InstitutionProfile(
            "east_central_asian_paper",
            "East and Central Asian craft-transfer corridors",
            (
                "OR = {",
                "\tregion = region:east_china_region",
                "\tregion = region:north_china_region",
                "\tregion = region:south_china_region",
                "\tregion = region:west_china_region",
                "\tregion = region:korea_region",
                "\tregion = region:manchuria_region",
                "\tregion = region:xinjiang_region",
                "\tregion = region:indochina_region",
                "}",
            ),
        ),
        InstitutionProfile(
            "christian_monastic",
            "Locations whose dominant faith belongs to the Christian family",
            (
                "dominant_religion = { group = religion_group:antq_christian_group }",
            ),
        ),
        InstitutionProfile(
            "christian_councils",
            "Christian communities participating in conciliar networks",
            (
                "dominant_religion = { group = religion_group:antq_christian_group }",
            ),
        ),
        InstitutionProfile(
            "late_roman_frontier",
            "Late Roman and neighboring federate settlement zones",
            (
                "AND = {",
                "\tOR = {",
                "\t\tregion = region:balkan_region",
                "\t\tregion = region:carpathia_region",
                "\t\tregion = region:north_german_region",
                "\t\tregion = region:south_german_region",
                "\t\tregion = region:france_region",
                "\t\tregion = region:italy_region",
                "\t\tregion = region:great_britain_region",
                "\t\tregion = region:anatolia_region",
                "\t\tregion = region:steppes_region",
                "\t}",
                "\tOR = {",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_italic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_hellenic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_germanic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_celtic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_steppe_group }",
                "\t}",
                "}",
            ),
        ),
    )
}


INSTITUTION_DATA = (
    Institution("antq_hellenism", "Hellenism", "A living network of Greek civic, literary, and sacred institutions.", "age_1_traditions", "athens", True, "1.1.1", "early", "mediterranean_letters", True, "P14.3;CAH-XI"),
    Institution("antq_roman_law_engineering", "Roman Law and Engineering", "Roman legal practice and public engineering circulate through imperial networks.", "age_1_traditions", "rome", True, "1.1.1", "early", "roman_imperial_practice", True, "P14.3;OCD;CAH-XI"),
    Institution("antq_han_bureaucratic_statecraft", "Han Bureaucratic Statecraft", "Written administration, registers, and examination-minded statecraft radiate from Han China.", "age_1_traditions", "jingzhao", True, "1.1.1", "early", "east_asian_administration", False, "P14.3;BHR;Bielenstein"),
    Institution("antq_buddhist_monasticism", "Buddhist Monasticism", "Buddhist monastic communities preserve learning and create durable religious networks.", "age_1_traditions", "anuradhapura", True, "1.1.1", "early", "buddhist_networks", True, "P14.3;CAH-XI"),
    Institution("antq_cataphract_warfare", "Cataphract Warfare", "Heavy armoured cavalry methods circulate from the Iranian and steppe worlds.", "age_2_renaissance", "merv", False, "96.1.1", "early", "iranian_steppe_cavalry", False, "P14.3;CAH-XI"),
    Institution("antq_papermaking", "Papermaking", "Paper and its associated craft knowledge spread outward from Luoyang.", "age_2_renaissance", "luoyang", False, "105.1.1", "mid", "east_central_asian_paper", True, "P14.3;BHR"),
    Institution("antq_christian_monasticism", "Christian Monasticism", "Egyptian ascetic communities establish a second monastic centre of gravity.", "age_3_discovery", "alexandria", False, "270.1.1", "mid", "christian_monastic", True, "P14.3;CAH-XII"),
    Institution("antq_theological_orthodoxy", "Theological Orthodoxy", "Council-led doctrinal settlement shapes the late Roman religious world.", "age_4_reformation", "iznik", False, "325.1.1", "late", "christian_councils", False, "P14.3;CAH-XII"),
    Institution("antq_foederati_statecraft", "Foederati Statecraft", "Land-for-service settlements become a deliberate frontier and imperial practice.", "age_5_absolutism", "edirne", False, "382.1.1", "late", "late_roman_frontier", False, "P14.3;AMM-31"),
)

# The institution manager resolves an exact institution_birth static modifier
# at every origin. Each value stays below the comparable vanilla birth
# modifier: these are small local advantages, not a substitute for research,
# institutions, or the dated historical currents.
INSTITUTION_BIRTH_EFFECTS: dict[str, tuple[str, str]] = {
    "antq_hellenism": ("local_cultural_influence", "0.10"),
    "antq_roman_law_engineering": ("local_monthly_development", "0.001"),
    "antq_han_bureaucratic_statecraft": ("local_cultural_tradition", "0.10"),
    "antq_buddhist_monasticism": ("local_max_literacy", "1"),
    "antq_cataphract_warfare": ("local_manpower_modifier", "0.05"),
    "antq_papermaking": ("local_max_literacy", "2"),
    "antq_christian_monasticism": ("local_pop_conversion_speed_modifier", "0.10"),
    "antq_theological_orthodoxy": ("local_pop_conversion_speed_modifier", "0.20"),
    "antq_foederati_statecraft": ("local_levy_size_modifier", "0.05"),
}


def installed_dir(relative: str) -> Path:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    return Path(config["game_dir"]) / "game" / relative


def advance_records() -> tuple[Advance, ...]:
    records: list[Advance] = []
    for track, age_groups in TRACKS.items():
        for conceptual_index, group in enumerate(age_groups):
            # EU5 validates `requires` within one age only.  Each age thus has
            # complete strands; the engine's mandatory sixth slot divides the
            # final conceptual arc at 376 while preserving all 250 statements.
            if len(group) != 10:
                raise ValueError(f"{track} conceptual age {conceptual_index + 1} must have exactly ten advances")
            segments = (
                ((4, group[:5]), (5, group[5:]))
                if conceptual_index == 4
                else ((conceptual_index, group),)
            )
            for age_index, segment in segments:
                previous: str | None = None
                for depth, name in enumerate(segment):
                    key = f"antq_{name}"
                    records.append(Advance(
                        key, name.replace("_", " ").title(),
                        AGE_KEYS[age_index], age_index, depth, previous,
                    ))
                    previous = key
    return tuple(records)


def direct_advance_icons(records: tuple[Advance, ...]) -> dict[str, str]:
    """Return direct M11 icon identifiers for reviewed completed rows only."""
    if not DIRECT_ADVANCE_ART.is_file():
        return {}
    with DIRECT_ADVANCE_ART.open(encoding="utf-8-sig", newline="") as handle:
        entries = list(csv.DictReader(handle))
    valid = {record.key for record in records}
    direct: dict[str, str] = {}
    for row in entries:
        key = (row.get("key") or "").strip()
        if (row.get("status") or "").strip() != "complete":
            continue
        if key not in valid:
            raise ValueError(f"direct advance-art ledger has unknown advance {key}")
        if key in direct:
            raise ValueError(f"direct advance-art ledger repeats completed advance {key}")
        direct[key] = "antq_advance_" + key.removeprefix("antq_")
    return direct


def technology_level(row: dict[str, str]) -> int:
    """Tune the plan's three starting tiers from the checked M3 polity ledger."""
    if row["tag"] in CORE_TAGS:
        return 4
    if row["kind"] in {"country", "subject"} and row["tier"] in {"1", "2"}:
        return 3
    if row["kind"] == "sop":
        return 1
    return 2


def technology_tier_summary() -> tuple[int, int, int, int]:
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    counts = {level: 0 for level in range(1, 5)}
    for row in rows:
        counts[technology_level(row)] += 1
    if counts[4] != 3 or not all(counts[level] for level in (1, 2, 3)):
        raise ValueError("M8 starting-technology policy no longer partitions the M3 roster")
    return tuple(counts[level] for level in range(1, 5))


def institution_manager() -> str:
    lines = ["institution_manager = {", "\tinstitutions = {"]
    for institution in INSTITUTION_DATA:
        if institution.start_active:
            lines.append(f"\t\t{institution.key} = {{ active = yes birth_place = {institution.location} }}")
    lines.extend(("\t}", "}", ""))
    return "\n".join(lines)


def validate(records: tuple[Advance, ...]) -> None:
    failures: list[str] = []
    if len(records) != 250:
        failures.append(f"expected 250 advances, got {len(records)}")
    keys = [record.key for record in records]
    if len(keys) != len(set(keys)):
        failures.append("advance keys are not unique")
    expected_counts = (50, 50, 50, 50, 25, 25)
    for age_index, age in enumerate(AGE_KEYS):
        age_records = [record for record in records if record.age == age]
        expected = expected_counts[age_index]
        if len(age_records) != expected:
            failures.append(f"{age} has {len(age_records)}, not {expected} advances")
        depth_limit = 10 if age_index < 4 else 5
        if any(record.depth not in range(depth_limit) for record in age_records):
            failures.append(f"{age} has a depth outside 0..{depth_limit - 1}")
    roots = [record for record in records if record.requires is None]
    if len(roots) != 30:
        failures.append("the five strands in six engine ages must have exactly 30 roots")
    key_set = set(keys)
    unknown_unlock_keys = sorted(set(START_UNLOCKS) - key_set)
    if unknown_unlock_keys:
        failures.append(
            "M8 start-unlock mapping has unknown advances: " + ", ".join(unknown_unlock_keys)
        )
    unlock_targets = [target for unlocks in START_UNLOCKS.values() for _field, target in unlocks]
    if len(unlock_targets) != len(set(unlock_targets)):
        failures.append("M8 start-unlock mapping repeats a law or policy category")
    if {field for unlocks in START_UNLOCKS.values() for field, _target in unlocks} - {"unlock_law", "unlock_policy"}:
        failures.append("M8 start-unlock mapping uses an unsupported unlock field")
    by_key = {record.key: record for record in records}
    required_by = {record.requires for record in records if record.requires}
    leaves = [record.key for record in records if record.key not in required_by]
    if len(leaves) != 30:
        failures.append("the five strands in six engine ages must have exactly 30 terminal advances")
    for record in records:
        if record.requires and record.requires not in key_set:
            failures.append(f"{record.key} requires an unknown advance")
        elif record.requires and by_key[record.requires].age != record.age:
            failures.append(f"{record.key} has a cross-age requirement")
        if any(token in record.key for token in FORBIDDEN):
            failures.append(f"anachronistic token in {record.key}")
    names = " ".join(keys)
    if "stirrup" in names:
        failures.append("the contested stirrup is outside M8's research tree")
    institution_keys = [item.key for item in INSTITUTION_DATA]
    if len(institution_keys) != len(set(institution_keys)):
        failures.append("institution keys are not unique")
    for item in INSTITUTION_DATA:
        if item.age not in AGE_KEYS:
            failures.append(f"{item.key} uses an invalid age")
        try:
            AntqDate.parse(item.earliest)
        except ValueError as exc:
            failures.append(f"{item.key} has invalid date: {exc}")
        if item.spread_band not in {"early", "mid", "late"}:
            failures.append(f"{item.key} uses invalid spread band")
        if item.profile not in INSTITUTION_PROFILES:
            failures.append(f"{item.key} uses unknown eligibility profile")
        if not item.source:
            failures.append(f"{item.key} has no historical source")
    if sum(item.start_active for item in INSTITUTION_DATA) != 4:
        failures.append("M8 requires four active AD 1 institution origins")
    han = next(item for item in INSTITUTION_DATA if item.key == "antq_han_bureaucratic_statecraft")
    han_profile = "\n".join(INSTITUTION_PROFILES[han.profile].script)
    if han.trade_spread or any(
        token in han_profile
        for token in ("europe", "italy_region", "france_region", "roman_imperial")
    ):
        failures.append("Han statecraft must not have ordinary trade or European eligibility")
    if set(INSTITUTION_BIRTH_EFFECTS) != set(institution_keys):
        failures.append("institution birth modifiers do not exactly cover the M8 institutions")
    technology_tier_summary()
    if failures:
        raise ValueError("\n".join(failures))


def advance_script(records: tuple[Advance, ...]) -> str:
    lines = [
        "# Generated by tools/m8_knowledge.py --write; complete ANTIQVITAS ancient knowledge trees.",
        "# Five continuous ten-step strands per age; vanilla advances are exact-name blanked beside this file.",
    ]
    direct = direct_advance_icons(records)
    for record in records:
        icon = direct.get(record.key, ICONS[record.age_index])
        lines.extend((f"{record.key} = {{", f"\tage = {record.age}", f"\ticon = {icon}", f"\tdepth = {record.depth}", f"\tresearch_cost = {2 + record.age_index * 2 + record.depth * 0.5:.1f}"))
        for field, target in START_UNLOCKS.get(record.key, ()):
            lines.append(f"\t{field} = {target}")
        if record.age_index == 0:
            lines.append(f"\tstarting_technology_level = {min(4, 1 + record.depth // 3)}")
        if record.requires:
            lines.append(f"\trequires = {record.requires}")
        lines.extend((f"\tai_weight = {{ add = {100 - record.depth * 5} }}", "}", ""))
    return "\n".join(lines)


def brace_delta(line: str) -> int:
    """Count structural braces in a plain Paradox-script line.

    The installed advance files do not use quoted script blocks in definition
    headers. Ignoring comments avoids a prose brace from corrupting the small
    source-preserving transform below.
    """
    code = line.split("#", 1)[0]
    return code.count("{") - code.count("}")


def inject_inline_false(line: str) -> str:
    """Add `always = no` to a one-line trigger without losing its references."""
    code, marker, comment = line.partition("#")
    closing = code.rfind("}")
    if closing < 0:
        raise ValueError(f"expected inline trigger block: {line!r}")
    # The closing brace must remain before the explanatory comment; otherwise
    # the comment consumes it and corrupts the containing advance definition.
    suffix = (" " + marker + comment) if marker else ""
    return code[:closing] + " always = no" + code[closing:] + " # M8 disables vanilla" + suffix


def disabled_content(path: Path, field: re.Pattern[str], field_name: str, kind: str, strip_unlocks: bool) -> str:
    """Add a false condition without deleting references inside the source block."""
    raw = path.read_text(encoding="utf-8-sig", errors="strict")
    rendered = [
        f"# Generated by tools/m8_knowledge.py --write; M8 disables vanilla {kind} gameplay.",
        "# Keys and their dependent trigger references remain valid for loaded vanilla script.",
    ]
    depth = 0
    root_has_gate = False
    root_open = False
    for line in raw.splitlines():
        code = line.split("#", 1)[0]
        delta = brace_delta(line)
        if depth == 0 and TOP_LEVEL.match(code):
            root_open = delta > 0
            root_has_gate = False
            rendered.append(line)
            depth += delta
            continue
        if root_open and depth == 1 and field.match(code):
            if delta == 0:
                rendered.append(inject_inline_false(line))
            else:
                rendered.append(line)
                indent = code[: len(code) - len(code.lstrip())]
                rendered.append(f"{indent}\talways = no # M8 disables vanilla {kind}")
            root_has_gate = True
            depth += delta
            continue
        if root_open and depth == 1 and delta < 0 and not root_has_gate:
            rendered.append(f"\t{field_name} = {{ always = no }} # M8 disables vanilla {kind}")
            root_has_gate = True
        if not (strip_unlocks and UNLOCK.match(code)):
            rendered.append(line)
        depth += delta
        if root_open and depth == 0:
            root_open = False
    if depth != 0:
        raise ValueError(f"unable to preserve brace structure in {path.name}")
    return "\n".join(rendered) + "\n"


def disabled_advance_content(path: Path) -> str:
    """Keep every vanilla advance key valid but make it permanently unavailable."""
    return neutralize_references(
        disabled_content(path, POTENTIAL, "potential", "advancement", True),
        remap_effects=True,
    )


def disabled_institution_content(path: Path) -> str:
    """Keep vanilla institution IDs for event links while preventing spawns."""
    return disabled_content(path, CAN_SPAWN, "can_spawn", "institution", False)


def installed_institution_keys(path: Path) -> tuple[str, ...]:
    """Read only top-level institution IDs from one installed age file."""
    result: list[str] = []
    depth = 0
    for line in path.read_text(encoding="utf-8-sig", errors="strict").splitlines():
        code = line.split("#", 1)[0]
        if depth == 0 and TOP_LEVEL.match(code):
            result.append(code.split("=", 1)[0].strip())
        depth += brace_delta(line)
    if depth != 0 or not result:
        raise ValueError(f"unable to inventory installed institutions in {path.name}")
    return tuple(result)


def legacy_institution_stubs(path: Path) -> str:
    """Remove installed IDs entirely; nullable-age records crash the Advances UI."""
    keys = installed_institution_keys(path)
    return (
        "# Generated by tools/m8_knowledge.py --write.\n"
        f"# Removed {len(keys)} post-antique institutions from {path.name}; "
        "all installed references are neutralized by generated exact-name overlays.\n"
    )


def empty_overrides(relative: str, destination: Path, label: str) -> dict[Path, str]:
    source = installed_dir(relative)
    if not source.is_dir():
        raise ValueError(f"installed {label} directory missing: {source}")
    outputs: dict[Path, str] = {}
    for path in sorted(source.glob("*.txt")):
        if path.name == "readme.txt":
            continue
        if label == "advance":
            outputs[destination / path.name] = disabled_advance_content(path)
        else:
            outputs[destination / path.name] = legacy_institution_stubs(path)
    if not outputs:
        raise ValueError(f"installed {label} manifest is empty")
    return outputs


def institution_eligibility_script() -> str:
    lines = [
        "# Generated by tools/m8_knowledge.py --write.",
        "# Root scope: receiving location. These gates constrain every spread channel.",
    ]
    for profile in INSTITUTION_PROFILES.values():
        lines.append(f"antq_institution_eligible_{profile.key} = {{")
        lines.extend(f"\t{line}" for line in profile.script)
        lines.extend(("}", ""))
    return "\n".join(lines)


def gated_value(field: str, base: str, profile: str) -> list[str]:
    return [
        f"\t{field} = {{",
        "\t\tvalue = 0",
        "\t\tif = {",
        f"\t\t\tlimit = {{ antq_institution_eligible_{profile} = yes }}",
        f"\t\t\tadd = {base}",
        "\t\t}",
        "\t}",
    ]


def institution_script() -> str:
    lines = [
        "# Generated by tools/m8_knowledge.py --write; M8 ancient institutions.",
        "# All dates are AntqDate-validated; every propagation channel is profile-gated.",
    ]
    for item in INSTITUTION_DATA:
        lines.extend((
            f"{item.key} = {{",
            f"\tage = {item.age}",
            f"\tlocation = {item.location}",
            "\tcan_spawn = {",
            f"\t\tcurrent_date >= {AntqDate.parse(item.earliest).engine()}",
            f"\t\tthis = location:{item.location}",
            f"\t\tantq_institution_eligible_{item.profile} = yes",
            "\t}",
        ))
        lines.extend(gated_value("promote_chance", "100", item.profile))
        lines.extend(gated_value(
            "spread_from_friendly_coast_border_location",
            f"institution_base_spread_from_friendly_neighbor_with_{item.spread_band}",
            item.profile,
        ))
        lines.extend(gated_value(
            "spread_from_any_coast_border_location",
            f"institution_base_spread_from_neighbor_with_{item.spread_band}",
            item.profile,
        ))
        for field in ("spread_from_any_import", "spread_from_any_export"):
            base = (
                f"institution_trade_spread_value_{item.spread_band}"
                if item.trade_spread else "0"
            )
            lines.extend(gated_value(field, base, item.profile))
        lines.extend(gated_value(
            "spread_embraced_to_capital",
            f"institution_total_embraced_to_capital_{item.spread_band}",
            item.profile,
        ))
        lines.extend(gated_value(
            "spread_scale_on_control_if_owner_embraced", "2", item.profile,
        ))
        lines.extend(gated_value(
            "spread_to_market_member",
            f"institution_spread_to_market_member_{item.spread_band}",
            item.profile,
        ))
        lines.extend(gated_value(
            "spread_to_market_center", "institution_spread_to_market_center", item.profile,
        ))
        lines.extend(("}", ""))
    return "\n".join(lines)


def institution_ledger() -> str:
    fields = (
        "key", "name", "age", "earliest", "birthplace", "start_active",
        "eligibility_profile", "eligibility_summary", "ordinary_trade_spread", "source",
    )
    rows = [",".join(fields)]
    for item in INSTITUTION_DATA:
        profile = INSTITUTION_PROFILES[item.profile]
        values = (
            item.key, item.name, item.age, AntqDate.parse(item.earliest).engine(),
            item.location, "yes" if item.start_active else "no", item.profile,
            profile.summary, "yes" if item.trade_spread else "no", item.source,
        )
        rows.append(",".join(f'"{value.replace(chr(34), chr(34) * 2)}"' for value in values))
    return "\n".join(rows) + "\n"


def installed_institution_ledger() -> str:
    source = installed_dir("in_game/common/institution")
    symbol_keys = set(json.loads(VANILLA_INSTITUTION_SYMBOLS.read_text(encoding="utf-8-sig")))
    rows: list[tuple[str, str, str]] = []
    for path in sorted(source.glob("age_*.txt")):
        for key in installed_institution_keys(path):
            rows.append((key, path.name, "removed_from_database"))
    installed_keys = {key for key, _path, _status in rows}
    if installed_keys != symbol_keys:
        raise ValueError(
            "installed institution inventory differs from harvested symbols: "
            f"missing={sorted(symbol_keys - installed_keys)}, "
            f"extra={sorted(installed_keys - symbol_keys)}"
        )
    lines = ["key,installed_file,mod_status"]
    lines.extend(",".join(row) for row in rows)
    return "\n".join(lines) + "\n"


def institution_birth_modifiers() -> str:
    lines = [
        "# Generated by tools/m8_knowledge.py --write; M8 institution-origin modifiers.",
        "# The installed institution manager resolves institution_birth at each birthplace.",
    ]
    for item in INSTITUTION_DATA:
        modifier, value = INSTITUTION_BIRTH_EFFECTS[item.key]
        lines.extend((
            f"{item.key}_birth = {{",
            "\tgame_data = {",
            "\t\tcategory = location",
            "\t}",
            f"\t{modifier} = {value}",
            "}",
            "",
        ))
    return "\n".join(lines)


def removed_institution_birth_modifiers() -> str:
    return (
        "# Generated by tools/m8_knowledge.py --write.\n"
        "# Exact-name override: birth modifiers for the 18 removed post-antique institutions.\n"
    )


def localization(records: tuple[Advance, ...], language: str) -> str:
    lines = [f"l_{language}:"]
    for record in records:
        lines.append(f' {record.key}: "{record.name}"')
        lines.append(f' {record.key}_desc: "{AGE_NAMES[record.age_index]} knowledge: {record.name}."')
    for item in INSTITUTION_DATA:
        lines.append(f' {item.key}: "{item.name}"')
        lines.append(f' {item.key}_desc: "{item.description}"')
        lines.append(
            f' STATIC_MODIFIER_NAME_{item.key}_birth: '
            f'"Birthplace of ${item.key}$"'
        )
        lines.append(
            f' STATIC_MODIFIER_DESC_{item.key}_birth: '
            f'"Historic origin of the {item.name} institution."'
        )
    return "\n".join(lines) + "\n"


def outputs(records: tuple[Advance, ...]) -> dict[Path, str]:
    rendered = {
        **empty_overrides("in_game/common/advances", ADVANCES, "advance"),
        ADVANCES / "00_antiquitas_m8_tree.txt": advance_script(records),
        **empty_overrides("in_game/common/institution", INSTITUTIONS, "institution"),
        INSTITUTIONS / "00_antiquitas_m8_institutions.txt": institution_script(),
        SCRIPTED_TRIGGERS / "00_antiquitas_m8_institution_spread.txt": institution_eligibility_script(),
        STATIC_MODIFIERS / "institutions.txt": removed_institution_birth_modifiers(),
        STATIC_MODIFIERS / "antq_m8_institution_birth.txt": institution_birth_modifiers(),
        INSTITUTION_LEDGER: institution_ledger(),
        INSTALLED_INSTITUTION_LEDGER: installed_institution_ledger(),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        rendered[LOC_ROOT / language / f"antq_m8_knowledge_l_{language}.yml"] = localization(records, language)
    return rendered


def expected_inventory(relative: str, destination: Path, custom: str) -> set[Path]:
    source = installed_dir(relative)
    installed = {
        destination / path.name
        for path in source.glob("*.txt")
        if path.name != "readme.txt"
    }
    if not installed:
        raise ValueError(f"installed inventory is empty: {relative}")
    return { *installed, destination / custom }


def write(records: tuple[Advance, ...]) -> None:
    for path, content in outputs(records).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
        print(f"m8_knowledge: wrote {path.relative_to(ROOT)}")


def check(records: tuple[Advance, ...]) -> bool:
    failures: list[str] = []
    expected = outputs(records)
    for path, content in expected.items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != content:
            failures.append(f"stale {path.relative_to(ROOT)}")
    advance_inventory = expected_inventory("in_game/common/advances", ADVANCES, "00_antiquitas_m8_tree.txt")
    permitted_advances = advance_inventory | {ADVANCES / "antq_age_scaffolds.txt"}
    actual_advances = set(ADVANCES.glob("*.txt"))
    for path in sorted(actual_advances - permitted_advances):
        failures.append(f"unexpected advance file {path.relative_to(ROOT)}")
    institution_inventory = expected_inventory("in_game/common/institution", INSTITUTIONS, "00_antiquitas_m8_institutions.txt")
    actual_institutions = set(INSTITUTIONS.glob("*.txt")) if INSTITUTIONS.is_dir() else set()
    for path in sorted(actual_institutions - institution_inventory):
        failures.append(f"unexpected institution file {path.relative_to(ROOT)}")
    for path in advance_inventory:
        text = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
        if UNLOCK.search(text):
            failures.append(f"unit or levy unlock survived in {path.relative_to(ROOT)}")
    for path in institution_inventory:
        text = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
        if "00_antiquitas_m8" not in path.name:
            if "post-antique institutions" not in text:
                failures.append(f"vanilla institution file is not an explicit empty override in {path.relative_to(ROOT)}")
            if any(TOP_LEVEL.match(line) for line in text.splitlines()):
                failures.append(f"legacy institution definition survives in {path.relative_to(ROOT)}")
            if legacy_references(text):
                failures.append(f"legacy institution reference survives in {path.relative_to(ROOT)}")
    custom_institutions = INSTITUTIONS / "00_antiquitas_m8_institutions.txt"
    if custom_institutions.is_file():
        text = custom_institutions.read_text(encoding="utf-8-sig")
        for item in INSTITUTION_DATA:
            marker = f"antq_institution_eligible_{item.profile}"
            if text.count(marker) != 10:
                failures.append(f"{item.key} does not gate all ten spawn/spread channels")
    custom_tree = ADVANCES / "00_antiquitas_m8_tree.txt"
    if custom_tree.is_file() and any(token in custom_tree.read_text(encoding="utf-8-sig").lower() for token in FORBIDDEN):
        failures.append("anachronistic token survived in the M8 tree")
    if failures:
        print("m8_knowledge: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    tiers = technology_tier_summary()
    print(
        "m8_knowledge: PASS "
        f"(250 advances; 9 ancient institutions; 18 legacy institutions removed; "
        f"starting tiers 1/2/3/4 = {'/'.join(map(str, tiers))}; no vanilla unlocks)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        records = advance_records()
        validate(records)
        if args.write:
            write(records)
            return 0
        return 0 if check(records) else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m8_knowledge: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

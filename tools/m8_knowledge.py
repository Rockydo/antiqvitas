#!/usr/bin/env python3
"""Render and validate ANTIQVITAS's complete M8 knowledge layer.

The installed database is deliberately replaced by exact filenames: continuing
to carry medieval and early-modern advances underneath an ancient tree would
make anachronisms reachable even when the new advances are sound.  This tool
keeps the source manifest tied to the locally pinned EU5 installation and
produces the five, continuous historical trees from the documented M8 design.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, M2_MIRROR_LANGUAGES

ROOT = Path(__file__).resolve().parents[1]
ADVANCES = ROOT / "in_game/common/advances"
INSTITUTIONS = ROOT / "in_game/common/institution"
STATIC_MODIFIERS = ROOT / "main_menu/common/static_modifiers"
LOC_ROOT = ROOT / "main_menu/localization"
ROSTER = ROOT / "docs/world_1ad/polities.csv"

AGE_KEYS = (
    "age_1_traditions", "age_2_renaissance", "age_3_discovery",
    "age_4_reformation", "age_5_absolutism",
)
AGE_NAMES = ("Principate", "High Empires", "Crisis", "Dominate", "Migrations")
ICONS = (
    "abacus_advance", "legalism_advance", "road_advance_1",
    "crown_power_advance_discovery", "expansionism",
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
    "antq_imperial_cult": (("unlock_law", "legal_code_law"),),
    "antq_provincial_census": (("unlock_law", "administrative_system"),),
    "antq_tax_registers": (("unlock_law", "distribution_of_power_law"),),
    "antq_road_milestones": (("unlock_law", "royal_court_customs_law"),),
    "antq_legal_petitions": (("unlock_law", "education_masses_law"),),
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
    "antq_supply_columns": (("unlock_law", "tribal_legal_basis_law"),),
    "antq_monsoon_navigation": (("unlock_law", "coin_laws"),),
    "antq_red_sea_piloting": (("unlock_law", "mining_law"),),
    "antq_caravan_accounting": (("unlock_law", "immigration_law"),),
    "antq_paper_precursors": (("unlock_law", "cultural_traditions_law"),),
    # Polygyny is a policy inside the religious marriage_law category; it is
    # not itself granted by a vanilla advance.  Unlock its parent category.
    "antq_civic_associations": (("unlock_law", "marriage_law"),),
}


# Five ten-step strands run continuously through all five ages.  Their names
# are the source-led historical statements; individual mechanical effects stay
# bounded to locally verified engine contracts in M9/M10 where needed.
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


INSTITUTION_DATA = (
    Institution("antq_hellenism", "Hellenism", "A living network of Greek civic, literary, and sacred institutions.", "age_1_traditions", "athens", True, "1.1.1", "early"),
    Institution("antq_roman_law_engineering", "Roman Law and Engineering", "Roman legal practice and public engineering circulate through imperial networks.", "age_1_traditions", "rome", True, "1.1.1", "early"),
    Institution("antq_han_bureaucratic_statecraft", "Han Bureaucratic Statecraft", "Written administration, registers, and examination-minded statecraft radiate from Han China.", "age_1_traditions", "jingzhao", True, "1.1.1", "early"),
    Institution("antq_buddhist_monasticism", "Buddhist Monasticism", "Buddhist monastic communities preserve learning and create durable religious networks.", "age_1_traditions", "anuradhapura", True, "1.1.1", "early"),
    Institution("antq_cataphract_warfare", "Cataphract Warfare", "Heavy armoured cavalry methods circulate from the Iranian and steppe worlds.", "age_2_renaissance", "merv", False, "96.1.1", "early"),
    Institution("antq_papermaking", "Papermaking", "Paper and its associated craft knowledge spread outward from Luoyang.", "age_2_renaissance", "luoyang", False, "105.1.1", "mid"),
    Institution("antq_christian_monasticism", "Christian Monasticism", "Egyptian ascetic communities establish a second monastic centre of gravity.", "age_3_discovery", "alexandria", False, "270.1.1", "mid"),
    Institution("antq_theological_orthodoxy", "Theological Orthodoxy", "Council-led doctrinal settlement shapes the late Roman religious world.", "age_4_reformation", "iznik", False, "325.1.1", "late"),
    Institution("antq_foederati_statecraft", "Foederati Statecraft", "Land-for-service settlements become a deliberate frontier and imperial practice.", "age_4_reformation", "edirne", False, "382.1.1", "late"),
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
        for age_index, group in enumerate(age_groups):
            # EU5 validates `requires` within one age only.  Each age thus has
            # five complete ten-step strands; the age transition itself is the
            # historical gate between their thematic continuations.
            previous: str | None = None
            if len(group) != 10:
                raise ValueError(f"{track} {AGE_NAMES[age_index]} must have exactly ten advances")
            for step, name in enumerate(group):
                key = f"antq_{name}"
                records.append(Advance(key, name.replace("_", " ").title(), AGE_KEYS[age_index], age_index, step, previous))
                previous = key
    return tuple(records)


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
    for age_index, age in enumerate(AGE_KEYS):
        age_records = [record for record in records if record.age == age]
        if len(age_records) != 50:
            failures.append(f"{age} has {len(age_records)}, not 50 advances")
        if any(record.depth not in range(10) for record in age_records):
            failures.append(f"{age} has a depth outside 0..9")
    roots = [record for record in records if record.requires is None]
    if len(roots) != 25:
        failures.append("the five strands in each age must have exactly 25 roots")
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
    if len(leaves) != 25:
        failures.append("the five strands in each age must have exactly 25 terminal advances")
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
    if sum(item.start_active for item in INSTITUTION_DATA) != 4:
        failures.append("M8 requires four active AD 1 institution origins")
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
    for record in records:
        lines.extend((f"{record.key} = {{", f"\tage = {record.age}", f"\ticon = {ICONS[record.age_index]}", f"\tdepth = {record.depth}", f"\tresearch_cost = {2 + record.age_index * 2 + record.depth * 0.5:.1f}"))
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
    return disabled_content(path, POTENTIAL, "potential", "advancement", True)


def disabled_institution_content(path: Path) -> str:
    """Keep vanilla institution IDs for event links while preventing spawns."""
    return disabled_content(path, CAN_SPAWN, "can_spawn", "institution", False)


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
            outputs[destination / path.name] = disabled_institution_content(path)
    if not outputs:
        raise ValueError(f"installed {label} manifest is empty")
    return outputs


def institution_script() -> str:
    lines = [
        "# Generated by tools/m8_knowledge.py --write; M8 ancient institutions.",
        "# Timed spawn thresholds are rendered only from AntqDate-validated values.",
    ]
    for item in INSTITUTION_DATA:
        lines.extend((f"{item.key} = {{", f"\tage = {item.age}", f"\tlocation = {item.location}", "\tcan_spawn = {", f"\t\tcurrent_date >= {AntqDate.parse(item.earliest).engine()}", f"\t\tthis = location:{item.location}", "\t}", "\tpromote_chance = { add = 100 }", f"\tspread_from_friendly_coast_border_location = institution_base_spread_from_friendly_neighbor_with_{item.spread_band}", f"\tspread_from_any_coast_border_location = institution_base_spread_from_neighbor_with_{item.spread_band}", f"\tspread_from_any_import = institution_trade_spread_value_{item.spread_band}", f"\tspread_from_any_export = institution_trade_spread_value_{item.spread_band}", f"\tspread_embraced_to_capital = institution_total_embraced_to_capital_{item.spread_band}", "\tspread_scale_on_control_if_owner_embraced = 2", "\tspread_to_market_member = institution_spread_to_market_member_early", "\tspread_to_market_center = institution_spread_to_market_center", "}", ""))
    return "\n".join(lines)


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
        STATIC_MODIFIERS / "antq_m8_institution_birth.txt": institution_birth_modifiers(),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        rendered[LOC_ROOT / language / f"antq_m8_knowledge_l_{language}.yml"] = localization(records, language)
    return rendered


def expected_inventory(relative: str, destination: Path, custom: str) -> set[Path]:
    return {*empty_overrides(relative, destination, relative).keys(), destination / custom}


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
        if "00_antiquitas_m8" not in path.name and "M8 disables vanilla institution" not in text:
            failures.append(f"vanilla institution remains spawnable in {path.relative_to(ROOT)}")
    custom_tree = ADVANCES / "00_antiquitas_m8_tree.txt"
    if custom_tree.is_file() and any(token in custom_tree.read_text(encoding="utf-8-sig").lower() for token in FORBIDDEN):
        failures.append("anachronistic token survived in the M8 tree")
    if failures:
        print("m8_knowledge: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    tiers = technology_tier_summary()
    print(f"m8_knowledge: PASS (250 advances; 9 institutions; starting tiers 1/2/3/4 = {'/'.join(map(str, tiers))}; no vanilla unlocks)")
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

#!/usr/bin/env python3
"""Render the first ANTIQVITAS M9 diplomatic contracts.

The AD 1 subject ledger remains the historical authority.  This generator owns
the engine adapters selected by that ledger, their localisation mirrors, and
the one date-gated contract.  Keeping the date here forces it through
``dates.AntqDate`` rather than letting an unvalidated literal reach script.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path

from dates import AntqDate, M2_MIRROR_LANGUAGES
from ownership_map import vanilla_owned_locations

ROOT = Path(__file__).resolve().parents[1]
SUBJECT_OUTPUT = ROOT / "in_game/common/subject_types/00_antiquitas_m9_subjects.txt"
SUBJECT_BALANCE_OUTPUT = ROOT / "docs/m9/subject_start_balance.csv"
SUBJECT_LEDGER = ROOT / "docs/world_1ad/subjects.csv"
CB_OUTPUT = ROOT / "in_game/common/casus_belli/00_antiquitas_m9.txt"
WARGOAL_OUTPUT = ROOT / "in_game/common/wargoals/00_antiquitas_m9.txt"
PEACE_OUTPUT = ROOT / "in_game/common/peace_treaties/00_antiquitas_m9.txt"
IO_OUTPUT = ROOT / "in_game/common/international_organizations/00_antiquitas_m9.txt"
HRE_MIRROR_OUTPUT = ROOT / "in_game/common/international_organizations/hre.txt"
BIAS_OUTPUT = ROOT / "in_game/common/biases/00_antiquitas_m9.txt"
IO_ACTION_OUTPUT = ROOT / "in_game/common/generic_actions/antq_m9_organization_actions.txt"
IO_AI_LIST_OUTPUT = ROOT / "in_game/common/generic_action_ai_lists/antq_m9_organization_actions_list.txt"
IO_AI_PULSE_OUTPUT = ROOT / "in_game/common/on_action/antq_m9_organization_ai_pulse.txt"
AI_TREASURY_RESERVE = 80
LOC_ROOT = ROOT / "main_menu/localization"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
REGIONS = ROOT / "docs/vanilla_symbols/regions.json"
LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
GEOGRAPHY_HIERARCHY = ROOT / "docs/vanilla_symbols/geography_hierarchy.json"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
ADVANCE_OUTPUT = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"

# The historical relations themselves and their citations are in
# docs/world_1ad/subjects.csv.  These adapters are deliberately keyed by the
# design tags used in that ledger, never the volatile engine-tag remapping.
START_ADAPTERS = {
    "ROM": "antq_client_kingdom",
    "PAR": "antq_satrapy",
    "HAN": "antq_tributary",
    "KNG": "antq_tributary",
}
FOEDERATI_UNLOCK = AntqDate.parse("382.1.1")
HOLY_SUPPRESSION_UNLOCK = AntqDate.parse("325.1.1")
CAMPAIGN_START = AntqDate.parse("1.1.1")

# The active CBs use the installed ``ai_will_do = { add = { ... } }``
# contract.  Values stay deliberately close to the local attack-threat
# baseline (10): eligibility supplies the historical guardrails, while the
# priority only stops valid opportunities being silently unavailable to AI.
ACTIVE_CB_AI_WEIGHTS = {
    "antq_punitive_expedition": 10,
    "antq_impose_client_king": 8,
    "antq_demand_tribute": 7,
    "antq_frontier_rectification": 16,
    "antq_loot_raid": 14,
    "antq_succession_intervention": 6,
    "antq_holy_suppression": 4,
}
DORMANT_CB_KEYS = {
    "antq_chinese_warlord_unification",
    "antq_sasanid_unification",
    "antq_gupta_digvijaya",
}
IO_ACTION_KEYS = (
    "antq_present_han_tribute",
    "antq_convene_kangju_route_council",
)


@dataclass(frozen=True)
class SubjectContract:
    key: str
    label: str
    description: str
    script: str
    loyalty_to_overlord: int
    strength_vs_overlord: str
    maritime_path_tolerance: str
    expected_start_min: int
    expected_start_max: int
    autonomy: str
    tribute: str
    war_duty: str
    integration: str


@dataclass(frozen=True)
class CasusBelli:
    key: str
    label: str
    description: str
    script: str


@dataclass(frozen=True)
class PeaceTreaty:
    key: str
    label: str
    description: str
    script: str


@dataclass(frozen=True)
class InternationalOrganization:
    key: str
    label: str
    description: str
    script: str


HRE_ENGINE_SENTINEL = """\thas_target = no
\tunique = yes
\texpel_members_who_are_targets_of_other_members = no
\tshow_on_diplomatic_map = no
\thas_leader_country = no
\tcreate_visible_trigger = { always = no }
\tinvite_visible_trigger = { always = no }
\tjoin_visible_trigger = { always = no }
\tjoin_enabled_trigger = { always = no }
\tcan_declare_war = { always = no }
\tcan_join_trigger = { always = no }
\tcan_leave_trigger = { always = no }
\tauto_leave_trigger = { always = no }
\tauto_disband_trigger = { always = no }
\tdisband_minimum_member_count = 0
\t# Disabled HRE interactions are still type-checked by the diplomacy UI.
\t# Implement the statuses they reference so the empty sentinel remains a
\t# valid HRE object without ever bestowing one on an AD 1 country.
\tspecial_statuses_implemented = {
\t\temperor
\t\telector
\t\tarchbishop_elector
\t\tfree_city
\t}
\ton_joined = {}
\ton_left = {}
\tvariables = {}
"""


# Discovery profiles encode the plan's bounded knowledge horizons.  Each is a
# set of installed region keys rather than a claim that every settlement,
# route, or polity within that region was equally well known.
ROMAN_OIKOUMENE = (
    "italy_region", "iberia_region", "france_region", "north_german_region",
    "south_german_region", "great_britain_region", "ireland_region",
    "scandinavian_region", "baltic_region", "balkan_region", "carpathia_region",
    "maghreb_region", "egypt_region", "nubia_region", "ethiopia_region",
    "somalia_region", "swahili_coast_region", "arabia_region", "crescent_region",
    "anatolia_region", "caucasus_region", "persia_region", "khorasan_region",
    "western_india_region", "central_india_region", "deccan_region",
    "hindustan_region", "bengal_region", "indian_ocean_region", "east_china_region",
)
HAN_HORIZON = (
    "north_china_region", "east_china_region", "south_china_region", "west_china_region",
    "xinjiang_region", "tibet_region", "mongolia_region", "manchuria_region",
    "korea_region", "steppes_region", "khorasan_region", "persia_region",
    "crescent_region", "anatolia_region",
)
INDIAN_OCEAN_HORIZON = (
    "arabia_region", "crescent_region", "persia_region", "khorasan_region",
    "western_india_region", "central_india_region", "deccan_region", "hindustan_region",
    "bengal_region", "indian_ocean_region", "indochina_region", "indonesia_region",
    "south_china_region", "east_china_region",
)
REGIONAL_DISCOVERY = {
    "Africa": ("maghreb_region", "sahel_region", "nubia_region", "ethiopia_region", "somalia_region"),
    "Anatolia": ("anatolia_region",),
    "Andes": ("andes_region",),
    "Arabia": ("arabia_region", "crescent_region", "persia_region", "indian_ocean_region"),
    "Balkans": ("balkan_region",),
    "Baltic": ("baltic_region",),
    "Britain": ("great_britain_region", "ireland_region"),
    "Caribbean-Amazon": ("caribbean_region", "brazil_region"),
    "Caucasus": ("caucasus_region", "anatolia_region", "persia_region"),
    "Central Asia": ("steppes_region", "xinjiang_region", "khorasan_region", "persia_region"),
    "China": ("north_china_region", "east_china_region", "south_china_region", "west_china_region"),
    "Danube": ("balkan_region", "carpathia_region"),
    "Eastern Europe": ("ruthenia_region", "russian_region"),
    "Finland": ("scandinavian_region",),
    "Germania": ("north_german_region", "south_german_region", "baltic_region"),
    "India": INDIAN_OCEAN_HORIZON,
    "Iran": ("persia_region", "khorasan_region", "caucasus_region", "crescent_region"),
    "Ireland": ("ireland_region", "great_britain_region"),
    "Japan": ("japan_region", "korea_region", "east_china_region"),
    "Korea": ("korea_region", "manchuria_region", "north_china_region"),
    "Lanka": INDIAN_OCEAN_HORIZON,
    "Levant": ("crescent_region", "anatolia_region", "arabia_region", "egypt_region"),
    "Mesoamerica": ("mesoamerica_region",),
    "Mesopotamia": ("crescent_region", "persia_region", "arabia_region"),
    "North America": ("alaska_region", "canada_region", "great_lakes_region", "great_plains_region", "east_coast_region", "west_coast_region"),
    "Northern Andes": ("colombia_region", "andes_region"),
    "Oceania": ("melanesia_region", "micronesia_region", "polynesia_region"),
    "Pontic": ("steppes_region", "caucasus_region", "balkan_region"),
    "Rome": ROMAN_OIKOUMENE,
    "Scandinavia": ("scandinavian_region", "baltic_region", "ireland_region"),
    "Southeast Asia": ("indochina_region", "indonesia_region", "south_china_region", "indian_ocean_region"),
    "Steppe": ("steppes_region", "mongolia_region", "xinjiang_region", "north_china_region", "manchuria_region"),
    "Tarim": ("xinjiang_region", "west_china_region", "north_china_region", "steppes_region", "khorasan_region"),
    "West Africa": ("sahel_region", "guinea_region", "maghreb_region"),
}


def standard_contract(
    *,
    subject_pays: str,
    color: str,
    level: int,
    capacity: str,
    loyalty_to_overlord: int,
    strength_vs_overlord: str,
    maritime_path_tolerance: str,
    external: str = "yes",
    annexable: str = "no",
    cancellation: str = "overlord",
    offensive: bool = False,
    modifiers: tuple[str, ...] = (),
    subject_modifiers: tuple[str, ...] = (),
) -> str:
    """Use only fields harvested from installed vanilla subject contracts."""
    lines = [
        f"\tsubject_pays = {subject_pays}",
        f"\tcolor = {color}",
        f"\tlevel = {level}",
        f"\tcounts_as_external = {external}",
        "\tvisible = { scope:target = { subject_type_is_not_locked = yes } }",
        "\tcreation_visible = { always = yes }",
        "\tjoin_defensive_wars_always = { always = yes }",
    ]
    if offensive:
        lines.append("\tjoin_offensive_wars_can_call = { scope:actor ?= { is_subject_of = scope:recipient } }")
    lines.extend((
        "\thas_overlords_ruler = no",
        "\twill_join_independence_wars = yes",
    ))
    if cancellation in {"subject", "both"}:
        lines.append("\tsubject_can_cancel = yes")
    if cancellation in {"overlord", "both"}:
        lines.append("\toverlord_can_cancel = yes")
    lines.extend((
        f"\tcan_be_annexed = {annexable}",
        "\thas_limited_diplomacy = no",
        "\tallow_declaring_wars = { always = yes }",
        "\tcan_change_rank = yes",
        "\tcan_change_heir_selection = yes",
        f"\tdiplomatic_capacity_cost_scale = {capacity}",
        f"\tstrength_vs_overlord = {strength_vs_overlord}",
        f"\tmaritime_path_tolerance = {maritime_path_tolerance}",
        *modifiers,
        "\tsubject_modifier = {",
        f"\t\tloyalty_to_overlord = {loyalty_to_overlord}",
        *(f"\t\t{item}" for item in subject_modifiers),
        "\t}",
    ))
    return "\n".join(lines)


def contracts() -> tuple[SubjectContract, ...]:
    knowledge_exchange = (
        "\tinstitution_spread_to_overlord = monthly_institution_spread_weak",
        "\tinstitution_spread_to_subject = monthly_institution_spread_weak",
        "\toverlord_modifier = { monthly_prestige = 0.01 }",
    )
    foederati_script = standard_contract(
        subject_pays="subject_pays_vassal",
        color="subject_vassal",
        level=1,
        capacity="0.30",
        external="no",
        offensive=True,
        subject_modifiers=("country_cabinet_efficiency = -0.05",),
        loyalty_to_overlord=40,
        strength_vs_overlord="-0.05",
        maritime_path_tolerance="-0.15",
    )
    unlock = FOEDERATI_UNLOCK.engine()
    foederati_script = foederati_script.replace(
        "\tvisible = { scope:target = { subject_type_is_not_locked = yes } }\n\tcreation_visible = { always = yes }",
        f"\tvisible = {{ current_date >= {unlock} scope:target = {{ subject_type_is_not_locked = yes }} }}\n"
        f"\tcreation_visible = {{ current_date >= {unlock} }}",
    )
    return (
        SubjectContract(
            "antq_client_kingdom",
            "Client Kingdom",
            "A locally governed kingdom bound to an imperial patron by treaty and protection.",
            standard_contract(
                subject_pays="subject_pays_vassal", color="subject_vassal", level=1, capacity="0.35", offensive=True,
                modifiers=knowledge_exchange,
                loyalty_to_overlord=50, strength_vs_overlord="-0.05", maritime_path_tolerance="-0.15",
            ),
            50, "-0.05", "-0.15", 50, 85,
            "Level 1; local ruler, own rank and diplomacy; patron protection",
            "Vassal-scale negotiated tribute",
            "Always defensive; callable for offensive war",
            "Not annexable",
        ),
        SubjectContract(
            "antq_satrapy",
            "Satrapy",
            "An autonomous subordinate realm within an Iranian imperial network.",
            standard_contract(
                subject_pays="subject_pays_vassal", color="subject_vassal", level=1, capacity="0.45", offensive=True,
                modifiers=knowledge_exchange,
                loyalty_to_overlord=45, strength_vs_overlord="-0.05", maritime_path_tolerance="-0.10",
            ),
            45, "-0.05", "-0.10", 45, 85,
            "Level 1; autonomous royal house and internal government",
            "Vassal-scale negotiated tribute",
            "Always defensive; callable for offensive war",
            "Not annexable",
        ),
        SubjectContract(
            "antq_tributary",
            "Tributary",
            "A polity linked by tribute, diplomacy, and frontier security rather than direct administration.",
            standard_contract(
                subject_pays="subject_pays_tributary", color="subject_tributary", level=0, capacity="0.20", cancellation="both",
                modifiers=("\toverlord_protects_external = no", *knowledge_exchange),
                loyalty_to_overlord=35, strength_vs_overlord="-0.05", maritime_path_tolerance="0.25",
            ),
            35, "-0.05", "0.25", 30, 75,
            "Level 0; independent diplomacy and wars; either party may cancel",
            "Tributary-scale payment",
            "Always defensive; no automatic offensive call",
            "Not annexable",
        ),
        SubjectContract(
            "antq_foederati",
            "Foederati",
            "A settled military partner bound by land, service, and treaty.",
            foederati_script,
            40, "-0.05", "-0.15", 45, 85,
            "Level 1; internal partner within the imperial sphere",
            "Vassal-scale service and payment",
            "Always defensive; callable for offensive war",
            "Not annexable",
        ),
        SubjectContract(
            "antq_autonomous_city",
            "Autonomous City",
            "A self-governing city owing limited obligations to a stronger protector.",
            standard_contract(
                subject_pays="subject_pays_tributary", color="subject_tributary", level=0, capacity="0.15", cancellation="both",
                loyalty_to_overlord=40, strength_vs_overlord="-0.05", maritime_path_tolerance="0.10",
            ),
            40, "-0.05", "0.10", 40, 80,
            "Level 0; self-governing city; either party may cancel",
            "Limited tributary-scale payment",
            "Always defensive; no automatic offensive call",
            "Not annexable",
        ),
    )


def subject_script(records: tuple[SubjectContract, ...]) -> str:
    blocks = [
        "# Generated by tools/m9_diplomacy.py --write; M9 ancient subject contracts.",
        "# M3's sourced dependency ledger selects the start adapters below.",
        "# Timed availability is rendered only from AntqDate-validated values.",
        "",
    ]
    for record in records:
        blocks.extend((f"{record.key} = {{", record.script, "}", ""))
    return "\n".join(blocks)


def _ai_disabled() -> str:
    """Keep a deliberately hidden, future historical CB unavailable to AI."""
    return "\tai_will_do = { value = -1 }"


def _ai_weight(value: int) -> str:
    """Render the locally harvested additive AI-CB priority contract."""
    if value < 0:
        raise ValueError("active casus-belli AI weights must be non-negative")
    return "\n".join((
        "\tai_will_do = {",
        "\t\tadd = {",
        "\t\t\tdesc = \"BASE\"",
        f"\t\t\tvalue = {value}",
        "\t\t}",
        "\t}",
    ))


def subject_cb(subject_type: str, treaty: str, war_goal: str, ai_weight: int) -> str:
    return "\n".join((
        "\tyears = 15",
        "\tcreate_visible = { scope:target = { subject_type_is_not_locked = yes } }",
        "\tcreate_enabled = {",
        "\t\tnot = { has_truce_with = scope:target }",
        "\t\tcountry_rank_level >= scope:target.country_rank_level",
        "\t\tscope:target = {",
        "\t\t\tcan_make_subject_of = {",
        "\t\t\t\ttarget = root",
        f"\t\t\t\ttype = subject_type:{subject_type}",
        "\t\t\t\tignore_war_limitation = yes",
        "\t\t\t}",
        "\t\t}",
        "\t\tpeace_treaty_war_score_cost = {",
        f"\t\t\tpeace_treaty = peace_treaty:{treaty}",
        "\t\t\tloser = scope:target",
        "\t\t\tvalue <= 100",
        "\t\t}",
        "\t}",
        f"\twar_goal_type = {war_goal}",
        _ai_weight(ai_weight),
    ))


def cb_records() -> tuple[CasusBelli, ...]:
    holy_date = HOLY_SUPPRESSION_UNLOCK.engine()
    return (
        CasusBelli(
            "antq_punitive_expedition", "Punitive Expedition",
            "Punish a neighbouring power without treating its frontier as a permanent conquest right.",
            "\n".join((
                "\tyears = 10",
                "\tcreate_visible = { scope:target = { is_neighbor_of = root } }",
                "\tcreate_enabled = { not = { has_truce_with = scope:target } }",
                "\twar_goal_type = antq_punitive_superiority",
                _ai_weight(ACTIVE_CB_AI_WEIGHTS["antq_punitive_expedition"]),
            )),
        ),
        CasusBelli(
            "antq_impose_client_king", "Impose Client King",
            "Compel a defeated court to accept a protected client-king relationship.",
            subject_cb("antq_client_kingdom", "antq_treaty_impose_client_king", "antq_client_capital", ACTIVE_CB_AI_WEIGHTS["antq_impose_client_king"]),
        ),
        CasusBelli(
            "antq_demand_tribute", "Demand Tribute",
            "Compel a defeated polity to enter a tributary relationship.",
            subject_cb("antq_tributary", "antq_treaty_demand_tribute", "antq_tribute_capital", ACTIVE_CB_AI_WEIGHTS["antq_demand_tribute"]),
        ),
        CasusBelli(
            "antq_frontier_rectification", "Frontier Rectification",
            "Recover a claimed frontier province without presenting it as a universal war of conquest.",
            "\n".join((
                "\tyears = 15",
                "\tcreate_visible = { scope:target = { any_owned_location = { is_core_of = root } } }",
                "\tcreate_enabled = { not = { has_truce_with = scope:target } }",
                "\tprovince = { any_location_in_province = { is_core_of = scope:actor } }",
                "\twar_goal_type = antq_frontier_recovery",
                _ai_weight(ACTIVE_CB_AI_WEIGHTS["antq_frontier_rectification"]),
            )),
        ),
        CasusBelli(
            "antq_loot_raid", "Loot Raid",
            "A limited frontier raid intended for tribal and steppe polities rather than territorial annexation.",
            "\n".join((
                "\tyears = 5",
                "\tcreate_visible = {",
                "\t\tOR = {",
                "\t\t\tgovernment_type = government_type:tribe",
                "\t\t\tgovernment_type = government_type:steppe_horde",
                "\t\t}",
                "\t\tscope:target = { is_neighbor_of = root }",
                "\t}",
                "\tcreate_enabled = { not = { has_truce_with = scope:target } }",
                "\twar_goal_type = antq_raid_superiority",
                _ai_weight(ACTIVE_CB_AI_WEIGHTS["antq_loot_raid"]),
            )),
        ),
        CasusBelli(
            "antq_succession_intervention", "Succession Intervention",
            "Intervene in a contested neighbouring monarchy without presupposing a particular claimant in AD 1.",
            "\n".join((
                "\tyears = 10",
                "\tcreate_visible = {",
                "\t\tgovernment_type = government_type:monarchy",
                "\t\tscope:target = { government_type = government_type:monarchy }",
                "\t}",
                "\tcreate_enabled = { not = { has_truce_with = scope:target } }",
                "\twar_goal_type = antq_succession_capital",
                _ai_weight(ACTIVE_CB_AI_WEIGHTS["antq_succession_intervention"]),
            )),
        ),
        CasusBelli(
            "antq_holy_suppression", "Holy Suppression",
            "A late-antique religious war justified as the suppression of a rival public cult.",
            "\n".join((
                "\tyears = 10",
                f"\tcreate_visible = {{ current_date >= {holy_date} religion != scope:target.religion }}",
                f"\tcreate_enabled = {{ current_date >= {holy_date} not = {{ has_truce_with = scope:target }} }}",
                "\twar_goal_type = antq_holy_superiority",
                _ai_weight(ACTIVE_CB_AI_WEIGHTS["antq_holy_suppression"]),
            )),
        ),
        CasusBelli(
            "antq_chinese_warlord_unification", "Chinese Warlord Unification",
            "Reserved for M10's source-led Chinese fragmentation and reunification situations.",
            "\n".join(("\tcreate_visible = { always = no }", "\tcreate_enabled = { always = no }", "\twar_goal_type = antq_unification_superiority", _ai_disabled())),
        ),
        CasusBelli(
            "antq_sasanid_unification", "Sasanid Unification",
            "Reserved for M10's source-led Arsacid collapse and Sasanid revolt sequence.",
            "\n".join(("\tcreate_visible = { always = no }", "\tcreate_enabled = { always = no }", "\twar_goal_type = antq_unification_superiority", _ai_disabled())),
        ),
        CasusBelli(
            "antq_gupta_digvijaya", "Gupta Digvijaya",
            "Reserved for M10's source-led Gupta expansion sequence rather than pre-scripting it into AD 1.",
            "\n".join(("\tcreate_visible = { always = no }", "\tcreate_enabled = { always = no }", "\twar_goal_type = antq_unification_superiority", _ai_disabled())),
        ),
    )


def cb_script(records: tuple[CasusBelli, ...]) -> str:
    blocks = [
        "# Generated by tools/m9_diplomacy.py --write; M9 ancient casus belli.",
        "# Fields are limited to local 1.3.1.1 CB contracts; dates use AntqDate.",
        "",
    ]
    for record in records:
        blocks.extend((f"{record.key} = {{", record.script, "}", ""))
    return "\n".join(blocks)


def wargoal_script() -> str:
    records = (
        ("antq_punitive_superiority", "superiority", "1", "1"),
        ("antq_raid_superiority", "superiority", "1.25", "1.25"),
        ("antq_frontier_recovery", "take_province", "0.60", "0.60"),
        ("antq_client_capital", "take_capital", "0.80", "0.25"),
        ("antq_tribute_capital", "take_capital", "1", "0.25"),
        ("antq_succession_capital", "take_capital", "1", "0.50"),
        ("antq_holy_superiority", "superiority", "1.10", "1.10"),
        ("antq_unification_superiority", "superiority", "0.75", "0.75"),
    )
    blocks = [
        "# Generated by tools/m9_diplomacy.py --write; M9 ancient wargoals.",
        "",
    ]
    for key, goal_type, conquer_cost, subjugate_cost in records:
        blocks.extend((
            f"{key} = {{",
            f"\ttype = {goal_type}",
            "\tattacker = {",
            f"\t\tconquer_cost = {conquer_cost}",
            f"\t\tsubjugate_cost = {subjugate_cost}",
            "\t}",
            "\tdefender = {",
            "\t}",
            "\tticking_war_score = 0.5",
            "}",
            "",
        ))
    return "\n".join(blocks)


def subject_treaty(key: str, subject_type: str, cb: str, cost: int) -> str:
    return "\n".join((
        "\tcost = {",
        f"\t\tvalue = {cost}",
        "\t}",
        "\tcategory = country",
        "\tpotential = {",
        f"\t\tscope:war = {{ casus_belli ?= casus_belli:{cb} }}",
        "\t\tscope:loser = {",
        "\t\t\tcan_make_subject_of = {",
        "\t\t\t\ttarget = scope:winner",
        f"\t\t\t\ttype = subject_type:{subject_type}",
        "\t\t\t\tignore_war_limitation = yes",
        "\t\t\t}",
        "\t\t}",
        "\t}",
        "\tallow = {",
        "\t}",
        "\teffect = {",
        "\t\tscope:loser = {",
        "\t\t\tmake_subject_of = {",
        "\t\t\t\ttarget = scope:winner",
        f"\t\t\t\ttype = subject_type:{subject_type}",
        "\t\t\t\twar = scope:war",
        "\t\t\t}",
        "\t\t}",
        "\t}",
        "\tai_desire = { value = 1000 }",
    ))


def peace_records() -> tuple[PeaceTreaty, ...]:
    return (
        PeaceTreaty("antq_treaty_impose_client_king", "Install Client King", "Install a protected client king in the defeated country.", subject_treaty("antq_treaty_impose_client_king", "antq_client_kingdom", "antq_impose_client_king", 45)),
        PeaceTreaty("antq_treaty_demand_tribute", "Enforce Tribute", "Bind the defeated country into a tributary relationship.", subject_treaty("antq_treaty_demand_tribute", "antq_tributary", "antq_demand_tribute", 35)),
        PeaceTreaty("antq_treaty_impose_satrapy", "Install Satrapy", "Install an autonomous subordinate realm within an Iranian imperial network.", subject_treaty("antq_treaty_impose_satrapy", "antq_satrapy", "antq_succession_intervention", 50)),
    )


def peace_script(records: tuple[PeaceTreaty, ...]) -> str:
    blocks = [
        "# Generated by tools/m9_diplomacy.py --write; M9 ancient peace treaties.",
        "",
    ]
    for record in records:
        blocks.extend((f"{record.key} = {{", record.script, "}", ""))
    return "\n".join(blocks)


def io_tag_trigger(design_tags: tuple[str, ...], indent: str) -> tuple[str, ...]:
    if not design_tags:
        return (f"{indent}always = no",)
    tags = engine_tag_map()
    return (
        f"{indent}OR = {{",
        *(f"{indent}\ttag = {tags[tag]}" for tag in design_tags),
        f"{indent}}}",
    )


def functional_io_lines(
    eligible: tuple[str, ...], *, leader_locked: bool
) -> tuple[str, ...]:
    """Verified join/leave, recurring obligation, and AI participation surface."""
    if not eligible:
        return (
            "\tinvite_visible_trigger = { always = no }",
            "\tcan_join_trigger = { always = no }",
            "\tcan_leave_trigger = { always = no }",
            "\tauto_leave_trigger = { always = no }",
            "\tauto_disband_trigger = { always = yes }",
            "\tvariables = {}",
        )
    leave = (
        "\tcan_leave_trigger = { NOT = { is_leader_of_international_organization = scope:recipient } }"
        if leader_locked else "\tcan_leave_trigger = { always = yes }"
    )
    return (
        "\tjoin_visible_trigger = { always = yes }",
        "\tjoin_enabled_trigger = { always = yes }",
        "\tinvite_visible_trigger = { always = yes }",
        "\tinvite_enabled_trigger = { always = yes }",
        "\tcan_join_trigger = {",
        *io_tag_trigger(eligible, "\t\t"),
        "\t\tis_rebel_country = no",
        "\t}",
        leave,
        "\tauto_leave_trigger = {",
        "\t\tNOT = {",
        *io_tag_trigger(eligible, "\t\t\t"),
        "\t\t}",
        "\t}",
        "\tauto_disband_trigger = { total_members < 2 }",
        "\tdisband_minimum_member_count = 1",
        "\ton_joined = { add_prestige = prestige_weak_bonus }",
        "\ton_left = { add_prestige = prestige_weak_penalty }",
        "\tmonthly_effect = {",
        "\t\trandom_list = {",
        "\t\t\t1 = {",
        "\t\t\t\tevery_international_organization_member = {",
        "\t\t\t\t\tadd_gold = { value = monthly_income_trade_and_tax multiply = -0.02 }",
        "\t\t\t\t}",
        "\t\t\t}",
        "\t\t\t59 = {}",
        "\t\t}",
        "\t}",
        "\tvariables = {",
        "\t\tantq_cohesion = {",
            "\t\t\tmonthly_change = 0.05",
        "\t\t\tstart = 50",
        "\t\t\tmin = 0",
        "\t\t\tmax = 100",
        "\t\t}",
        "\t}",
        "\tai_desire_to_join = { add = { desc = BASE_VALUE value = 25 } }",
        "\tai_desire_to_allow_new_member = { add = { desc = WE_WANT_THE_ORGANIZATION_TO_GROW value = 20 } }",
    )


def leader_io(
    *, map_visible: bool, leader_modifier: tuple[str, ...], eligible: tuple[str, ...]
) -> str:
    """A leader-country IO with bounded membership and active obligations."""
    lines = [
        "\thas_target = no",
        "\tunique = yes",
        "\texpel_members_who_are_targets_of_other_members = no",
        f"\tshow_on_diplomatic_map = {'yes' if map_visible else 'no'}",
        "\thas_leader_country = yes",
        "\tleader_type = country",
        "\tleader_color = define:NMapColors|INTERNATIONAL_ORGANIZATION_LEADER_COLOR",
        "\tcreate_visible_trigger = { always = no }",
        "\tcan_declare_war = { always = yes }",
        "\tmodifier = {",
        "\t\tmonthly_prestige = 0.01",
        "\t\tglobal_trade_through_owned_territory_efficiency = 0.01",
        "\t}",
        "\topinion_bonus = 5",
        *functional_io_lines(eligible, leader_locked=True),
    ]
    if leader_modifier:
        lines[9:9] = ("\tleader_modifier = {", *leader_modifier, "\t}")
    return "\n".join(lines)


def organization_records() -> tuple[InternationalOrganization, ...]:
    return (
        InternationalOrganization(
            "antq_han_tributary_system", "Han Tributary System",
            "An AD 1 network of tribute, recognition, and frontier diplomacy centred on the Han court.",
            "\n".join((
                leader_io(map_visible=True, leader_modifier=("\t\tmonthly_prestige = 0.05", "\t\tdiplomatic_capacity_modifier = 0.10"), eligible=("HAN", "KHT", "KUC", "KAS", "LOU", "TUR", "GMU", "QIM", "YQI", "SHC", "PUL", "FJS", "IWL", "DNH")),
                "\tonly_leader_country_joins_defensive_wars = yes",
                "\tjoin_defensive_wars_auto_call = {",
                "\t\tscope:target ?= { NOT = { is_member_of_international_organization = root } }",
                "\t}",
            )),
        ),
        InternationalOrganization(
            "antq_xiongnu_confederation", "Xiongnu Confederation",
            "The Chanyu's confederation is represented separately from the Xiongnu country to preserve its later shatter-and-reform path.",
            leader_io(map_visible=True, leader_modifier=("\t\tmonthly_prestige = 0.05", "\t\tmonthly_tribal_cohesion = 0.03"), eligible=()),
        ),
        InternationalOrganization(
            "antq_kangju_confederation", "Kangju Confederation",
            "A light AD 1 confederational layer linking the Kangju king with constituent Sogdian city polities without treating Sogdiana as a unitary annexed province.",
            leader_io(
                map_visible=True,
                leader_modifier=(
                    "\t\tmonthly_prestige = 0.03",
                    "\t\tglobal_trade_through_owned_territory_efficiency = 0.03",
                ),
                eligible=("KNG", "SOG"),
            ),
        ),
        InternationalOrganization(
            "antq_panhellenic_games", "Panhellenic Games",
            "A prestige institution maintained as a light, non-territorial organization until its late-antique sunset.",
            "\n".join((
                "\thas_target = no",
                "\tunique = yes",
                "\texpel_members_who_are_targets_of_other_members = no",
                "\tshow_on_diplomatic_map = no",
                "\thas_leader_country = no",
                "\tcreate_visible_trigger = { always = no }",
                "\tinvite_visible_trigger = { always = no }",
                "\tcan_declare_war = { always = yes }",
                "\tcan_join_trigger = { always = no }",
                "\tcan_leave_trigger = { always = no }",
                "\tauto_leave_trigger = { always = no }",
                "\tauto_disband_trigger = { always = no }",
                "\tmodifier = { monthly_prestige = 0.03 }",
                "\topinion_bonus = 10",
                "\ton_joined = {",
                "\t}",
                "\ton_left = {",
                "\t}",
                "\tvariables = {",
                "\t}",
            )),
        ),
        InternationalOrganization(
            "antq_germanic_frontier_exchanges", "Germanic Frontier Exchanges",
            "A hidden non-territorial UI adapter for bounded Roman, Rhine, Danube, and neighbouring-polity diplomacy; it is not a Germanic league or alliance.",
            "\n".join((
                "\thas_target = no",
                "\tunique = yes",
                "\texpel_members_who_are_targets_of_other_members = no",
                "\tshow_on_diplomatic_map = no",
                "\thas_leader_country = no",
                "\tcreate_visible_trigger = { always = no }",
                "\tcan_declare_war = { always = no }",
                "\tmodifier = { monthly_prestige = 0.02 global_trade_through_owned_territory_efficiency = 0.01 }",
                "\topinion_bonus = 8",
                *functional_io_lines(("ROM", "MCM", "CRU", "CHT", "FRI", "BTV", "LAN", "SEM", "HER", "QUA"), leader_locked=False),
            )),
        ),
        InternationalOrganization(
            "antq_northern_amber_assemblies", "Northern Amber and Assembly Contacts",
            "A hidden non-territorial UI adapter for plural coastal, river-portage, migration, and assembly contacts; it is not shared sovereignty or a Baltic state.",
            "\n".join((
                "\thas_target = no",
                "\tunique = yes",
                "\texpel_members_who_are_targets_of_other_members = no",
                "\tshow_on_diplomatic_map = no",
                "\thas_leader_country = no",
                "\tcreate_visible_trigger = { always = no }",
                "\tcan_declare_war = { always = no }",
                "\tmodifier = { global_trade_through_owned_territory_efficiency = 0.02 }",
                "\topinion_bonus = 6",
                *functional_io_lines(("FRI", "LAN", "SEM", "GUT", "SAX", "AES", "SUE"), leader_locked=False),
            )),
        ),
        InternationalOrganization(
            "antq_arabian_route_exchanges", "Arabian Route Exchanges",
            "A non-territorial AD 1 forum for safe-conducts, water works, route intelligence, and transit disputes among Arabian polities.",
            "\n".join((
                "\thas_target = no",
                "\tunique = yes",
                "\texpel_members_who_are_targets_of_other_members = no",
                "\tshow_on_diplomatic_map = no",
                "\thas_leader_country = no",
                "\tcreate_visible_trigger = { always = no }",
                "\tcan_declare_war = { always = no }",
                "\tmodifier = { global_trade_through_owned_territory_efficiency = 0.025 }",
                "\tgives_food_access_to_members = yes",
                "\topinion_bonus = 7",
                *functional_io_lines(("NAB", "SAB", "HIM", "QAT", "HAD", "KIN", "THM", "AGR", "GRH", "QTR", "OMN", "BED"), leader_locked=False),
            )),
        ),
        InternationalOrganization(
            "antq_christian_church", "Christian Church",
            "A dormant scaffold for the post-Nicaea council and orthodoxy system; it has no AD 1 instance.",
            "\n".join((
                "\thas_target = no",
                "\tunique = yes",
                "\texpel_members_who_are_targets_of_other_members = no",
                "\tshow_on_diplomatic_map = no",
                "\thas_leader_country = no",
                "\tcreate_visible_trigger = { always = no }",
                "\tinvite_visible_trigger = { always = no }",
                "\tcan_declare_war = { always = yes }",
                "\tcan_join_trigger = { always = no }",
                "\tcan_leave_trigger = { always = no }",
                "\tauto_leave_trigger = { always = no }",
                "\tauto_disband_trigger = { always = no }",
                "\ton_joined = {",
                "\t}",
                "\ton_left = {",
                "\t}",
                "\tvariables = {",
                "\t}",
            )),
        ),
    )


def organization_script(records: tuple[InternationalOrganization, ...]) -> str:
    blocks = [
        "# Generated by tools/m9_diplomacy.py --write; M9 ancient international organizations.",
        "# Start membership and all future dated activation are separate from these type contracts.",
        "# The empty hre sentinel satisfies a build-1.3.11 hardcoded lookup; it has no leader, members, map surface, or actions.",
        "",
        "hre = {",
        HRE_ENGINE_SENTINEL.rstrip(),
        "}",
        "",
    ]
    for record in records:
        blocks.extend((f"{record.key} = {{", record.script, "}", ""))
    return "\n".join(blocks)


def io_action_block(
    key: str, io_key: str, icon: str, cost: int, actor_effect: str,
) -> str:
    return f"""{key} = {{
\ticon = {icon}
\ttype = internationalorganization
\tpotential = {{
\t\texists = international_organization:{io_key}
\t\tscope:actor = {{ is_member_of_international_organization = international_organization:{io_key} }}
\t}}
\tselect_trigger = {{
\t\tlooking_for_a = international_organization
\t\tsource = actor
\t\ttarget_flag = recipient
\t\tname = "choose_international_organization"
\t\tcolumn = {{ data = name }}
\t\tinteraction_source_list = {{
\t\t\tinternational_organization:{io_key} = {{ add_to_list = source }}
\t\t}}
\t\tvisible = {{
\t\t\tinternational_organization_type = international_organization_type:{io_key}
\t\t\tscope:actor = {{ is_member_of_international_organization = root }}
\t\t}}
\t}}
\tallow = {{ scope:actor = {{ gold >= {cost} }} }}
\tcooldown = {{ type = {key} years = 3 }}
\teffect = {{
\t\tscope:actor = {{
\t\t\tadd_gold = -{cost}
\t\t\t{actor_effect}
\t\t}}
\t\tscope:recipient = {{ change_variable = {{ name = antq_cohesion add = 3 }} }}
\t}}
}}"""


def io_action_script() -> str:
    return "# Generated by tools/m9_diplomacy.py --write.\n\n" + "\n\n".join((
        io_action_block(
            "antq_present_han_tribute", "antq_han_tributary_system",
            "antq_exchange_route_intelligence", 15,
            "add_legitimacy = legitimacy_weak_bonus",
        ),
        io_action_block(
            "antq_convene_kangju_route_council", "antq_kangju_confederation",
            "antq_send_frontier_envoys", 12,
            "add_prestige = prestige_weak_bonus",
        ),
    )) + "\n"


def io_ai_list_script() -> str:
    return """# Generated by tools/m9_diplomacy.py --write.
# The build-1.3.11 generic-action AI cannot resolve international-organization
# selector targets and posts invalid perform_generic_action commands.  AI use
# is implemented by antq_m9_organization_ai_pulse instead.
antq_m9_organization_actions_list = {
\tpotential = { always = no }
\tactions = {
\t\tantq_present_han_tribute
\t\tantq_convene_kangju_route_council
\t}
}
"""


def io_ai_pulse_script() -> str:
    """Execute the two recurring organization choices without generic actions.

    EU5 1.3.11 does not expose a selected international-organization target to
    generic-action AI.  A country pulse can scope the exact organization
    directly, while expiring variables preserve the public action's three-year
    cooldown and the historical host/cost/calendar contract.
    """
    return f"""# Generated by tools/m9_diplomacy.py --write.
# Hooked from the installed monthly_country_pulse mirror generated by
# tools/m12_hardcoded_startup.py.

antq_m9_organization_ai_pulse = {{
\ttrigger = {{
\t\tis_ai = yes
\t\tOR = {{
\t\t\tAND = {{ tag = XAR current_month = 3 }}
\t\t\tAND = {{ tag = XCI current_month = 9 }}
\t\t}}
\t}}
\teffect = {{
\t\tif = {{
\t\t\tlimit = {{
\t\t\t\ttag = XAR
\t\t\t\tcurrent_month = 3
\t\t\t\tgold >= {AI_TREASURY_RESERVE}
\t\t\t\texists = international_organization:antq_han_tributary_system
\t\t\t\tis_member_of_international_organization = international_organization:antq_han_tributary_system
\t\t\t\tNOT = {{ has_variable = antq_m9_han_tribute_cooldown }}
\t\t\t}}
\t\t\tadd_gold = -15
\t\t\tadd_legitimacy = legitimacy_weak_bonus
\t\t\tset_variable = {{ name = antq_m9_han_tribute_cooldown value = yes years = 3 }}
\t\t\tinternational_organization:antq_han_tributary_system = {{
\t\t\t\tchange_variable = {{ name = antq_cohesion add = 3 }}
\t\t\t}}
\t\t}}
\t\tif = {{
\t\t\tlimit = {{
\t\t\t\ttag = XCI
\t\t\t\tcurrent_month = 9
\t\t\t\tgold >= {AI_TREASURY_RESERVE}
\t\t\t\texists = international_organization:antq_kangju_confederation
\t\t\t\tis_member_of_international_organization = international_organization:antq_kangju_confederation
\t\t\t\tNOT = {{ has_variable = antq_m9_kangju_council_cooldown }}
\t\t\t}}
\t\t\tadd_gold = -12
\t\t\tadd_prestige = prestige_weak_bonus
\t\t\tset_variable = {{ name = antq_m9_kangju_council_cooldown value = yes years = 3 }}
\t\t\tinternational_organization:antq_kangju_confederation = {{
\t\t\t\tchange_variable = {{ name = antq_cohesion add = 3 }}
\t\t\t}}
\t\t}}
\t}}
}}
"""


def io_bias_script(records: tuple[InternationalOrganization, ...]) -> str:
    values = {
        "antq_han_tributary_system": 5,
        "antq_xiongnu_confederation": 10,
        "antq_kangju_confederation": 7,
        "antq_panhellenic_games": 0,
        "antq_germanic_frontier_exchanges": 2,
        "antq_northern_amber_assemblies": 2,
        "antq_arabian_route_exchanges": 3,
        "antq_christian_church": 0,
    }
    blocks = [
        "# Generated by tools/m9_diplomacy.py --write; required IO member-opinion biases.",
        "",
    ]
    for record in records:
        blocks.extend((f"io_opinion_{record.key} = {{", f"\tvalue = {values[record.key]}", "}", ""))
    return "\n".join(blocks)


def engine_tag_map() -> dict[str, str]:
    return {
        entry["design_tag"]: entry["engine_tag"]
        for entry in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }


def subject_balance_rows(
    records: tuple[SubjectContract, ...],
) -> list[dict[str, str]]:
    contracts_by_key = {record.key: record for record in records}
    tags = engine_tag_map()
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        roster = {row["tag"]: row for row in csv.DictReader(handle)}
    with SUBJECT_LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    rows: list[dict[str, str]] = []
    for source in source_rows:
        contract_key = START_ADAPTERS[source["overlord"]]
        contract = contracts_by_key[contract_key]
        rows.append(
            {
                "overlord_design_tag": source["overlord"],
                "overlord_engine_tag": tags[source["overlord"]],
                "overlord_name": roster[source["overlord"]]["name"],
                "subject_design_tag": source["subject"],
                "subject_engine_tag": tags[source["subject"]],
                "subject_name": roster[source["subject"]]["name"],
                "start_capital": roster[source["subject"]]["map_capital"],
                "installed_start_ownable": "yes",
                "subject_type": contract_key,
                "base_loyalty_to_overlord": str(contract.loyalty_to_overlord),
                "strength_vs_overlord": contract.strength_vs_overlord,
                "maritime_path_tolerance": contract.maritime_path_tolerance,
                "expected_start_loyalty_min": str(contract.expected_start_min),
                "expected_start_loyalty_max": str(contract.expected_start_max),
                "autonomy": contract.autonomy,
                "tribute": contract.tribute,
                "war_duty": contract.war_duty,
                "relations": "Dynamic opinion; no forced cultural or court homogenization",
                "integration": contract.integration,
                "source": source["source"],
                "confidence": source["confidence"],
                "note": source["note"],
            }
        )
    return rows


def subject_balance_csv(records: tuple[SubjectContract, ...]) -> str:
    from io import StringIO

    rows = subject_balance_rows(records)
    output = StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=tuple(rows[0]),
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def international_organization_manager() -> str:
    """Render only source-bounded AD 1 IO instances.

    Xiongnu cohesion belongs to the Xiongnu country and its reform because the
    map has no evidence-led constituent sovereign tags; no one-member duplicate
    organization is created. The Games likewise remain provincial Roman civic
    life rather than a one-country international shell.
    Kangju and Sogdiana receive a separate confederational layer because the
    evidence supports Kangju predominance alongside constituent city polities.
    """
    tags = engine_tag_map()
    start = CAMPAIGN_START.engine()
    entries = (
        (
            "antq_han_tributary_system",
            ("HAN", "KHT", "KUC", "KAS", "LOU", "TUR", "GMU", "QIM", "YQI", "SHC", "PUL", "FJS", "IWL", "DNH"),
            "HAN",
            "hsv360 { 8 72 82 }",
        ),
        ("antq_kangju_confederation", ("KNG", "SOG"), "KNG", "hsv360 { 194 52 58 }"),
        (
            "antq_germanic_frontier_exchanges",
            ("ROM", "MCM", "CRU", "CHT", "FRI", "BTV", "LAN", "SEM", "HER", "QUA"),
            None,
            "hsv360 { 32 20 48 }",
        ),
        (
            "antq_northern_amber_assemblies",
            ("FRI", "LAN", "SEM", "GUT", "SAX", "AES", "SUE"),
            None,
            "hsv360 { 195 24 54 }",
        ),
        (
            "antq_arabian_route_exchanges",
            ("NAB", "SAB", "HIM", "QAT", "HAD", "KIN", "THM", "AGR", "GRH", "QTR", "OMN", "BED"),
            None,
            "hsv360 { 30 50 70 }",
        ),
    )
    blocks = [
        "# Generated by tools/m9_diplomacy.py through generate_start_mirror.py --write.",
        "# M9 AD 1 organizations; source limits and technical adapters: docs/m9/.",
        "international_organization_manager = {",
        "\t# Engine sentinel: the initializer unconditionally resolves the unique HRE instance.",
        "\t# It is deliberately empty, leaderless, hidden, and mechanically inert.",
        "\tadd_international_organization = {",
        "\t\ttype = hre",
        f"\t\tcreation_date = {start}",
        "\t\tmap_color = hsv360 { 0 0 0 }",
        "\t}",
        "",
    ]
    for io_type, members, leader, color in entries:
        blocks.extend((
            "\tadd_international_organization = {",
            f"\t\ttype = {io_type}",
            f"\t\tcreation_date = {start}",
            f"\t\tmap_color = {color}",
            f"\t\tmembers = {{ {' '.join(tags[tag] for tag in members)} }}",
        ))
        if leader:
            blocks.append(f"\t\tleader = {tags[leader]}")
        blocks.extend(("\t}", ""))
    blocks.append("}")
    return "\n".join(blocks) + "\n"


@lru_cache(maxsize=1)
def owned_regions_by_tag() -> dict[str, frozenset[str]]:
    """Return every engine region containing an opening polity's territory.

    Discovery is region-granular in EU5.  A country which owns a location in a
    region it has not discovered can make the movement pathfinder fall through
    to diplomatic map sharing and ask for a relation with itself.  Resolve the
    complete location -> province -> area -> region chain here so the bookmark
    generator cannot create that invalid state for any polity.
    """
    hierarchy = json.loads(GEOGRAPHY_HIERARCHY.read_text(encoding="utf-8-sig"))
    parents: dict[str, set[str]] = {}
    for container, children in hierarchy.items():
        for child in children:
            # A few installed provinces contain a same-named location.  Keep
            # every real parent edge and ignore only that self-loop.
            if child != container:
                parents.setdefault(child, set()).add(container)
    regions: dict[str, set[str]] = {}
    failures: list[str] = []
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(line for line in handle if not line.startswith("#"))
        for entry in rows:
            frontier = {entry["location"]}
            visited: set[str] = set()
            found: set[str] = set()
            for _ in range(8):
                frontier -= visited
                if not frontier:
                    break
                visited |= frontier
                next_frontier: set[str] = set()
                for node in frontier:
                    for parent in parents.get(node, set()):
                        if parent.endswith("_region"):
                            found.add(parent)
                        else:
                            next_frontier.add(parent)
                frontier = next_frontier
            if len(found) != 1:
                failures.append(f"{entry['tag']}:{entry['location']}")
                continue
            regions.setdefault(entry["tag"], set()).update(found)
    if failures:
        raise ValueError(
            "opening locations without a resolvable region: "
            + ", ".join(failures[:20])
        )
    return {tag: frozenset(values) for tag, values in regions.items()}


def discovery_regions(row: dict[str, str]) -> tuple[str, ...]:
    if row["tag"] == "ROM":
        base = ROMAN_OIKOUMENE
    elif row["tag"] == "HAN":
        base = HAN_HORIZON
    else:
        try:
            base = REGIONAL_DISCOVERY[row["region"]]
        except KeyError as exc:
            raise ValueError(
                f"no M9 discovery profile for {row['tag']} region {row['region']}"
            ) from exc
    # Retain the sourced knowledge horizon, then add only the engine regions
    # required to make every owned opening location genuinely discovered.
    required = owned_regions_by_tag().get(row["tag"], frozenset())
    return tuple(dict.fromkeys((*base, *sorted(required - set(base)))))


def validate_discovery() -> int:
    valid_regions = set(json.loads(REGIONS.read_text(encoding="utf-8-sig")))
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    failures: list[str] = []
    for row in rows:
        profile = discovery_regions(row)
        if not profile:
            failures.append(f"{row['tag']} has an empty discovery profile")
        unknown = sorted(set(profile) - valid_regions)
        if unknown:
            failures.append(f"{row['tag']} has unknown discovery regions {unknown}")
        missing_owned = sorted(owned_regions_by_tag().get(row["tag"], frozenset()) - set(profile))
        if missing_owned:
            failures.append(
                f"{row['tag']} does not discover owned regions {missing_owned}"
            )
        forbidden = {"north_atlantic_ocean_region", "north_pacific_ocean_region", "south_atlantic_region", "south_pacific_ocean_region"}
        if set(profile) & forbidden:
            failures.append(f"{row['tag']} crosses an ocean discovery boundary")
    if failures:
        raise ValueError("\n".join(failures))
    return len(rows)


def localization(
    subjects: tuple[SubjectContract, ...],
    cbs: tuple[CasusBelli, ...],
    treaties: tuple[PeaceTreaty, ...],
    organizations: tuple[InternationalOrganization, ...],
    language: str,
) -> str:
    entries: list[tuple[str, str]] = []
    # Installed war notifications concatenate ``$TYPE$ $SUBJECT$``.  Here
    # $TYPE$ is the diplomatic relationship and $SUBJECT$ is already the
    # country's styled long name, producing repetitions such as "Client
    # Kingdom Client Kingdom of Mauretania".  These exact-key adapters name
    # the styled country once; the notification title already establishes
    # that it concerns a subject.
    entries.extend((
        (
            "SUBJECT_JOINED_WAR_ATTACKER_DESC",
            "$MONARCHTITLE$, $SUBJECT$ has joined the $WAR$ against $ENEMY$ "
            "as an attacker without automatically involving us!",
        ),
        (
            "SUBJECT_JOINED_WAR_DEFENDER_DESC",
            "$MONARCHTITLE$, $SUBJECT$ has been attacked and joined the $WAR$ "
            "against $ENEMY$ as a defender without automatically involving us!",
        ),
    ))
    for record in subjects:
        entries.extend((
            (record.key, record.label),
            (f"{record.key}_desc", record.description),
            (f"AM_{record.key}", record.label),
            (f"LEAD_{record.key}", record.label),
            (f"OFFER_{record.key}_CATEGORY", "CATEGORY_SUBJECT_ACTIONS"),
            (f"REQUEST_{record.key}_CATEGORY", "CATEGORY_SUBJECT_ACTIONS"),
        ))
    for record in cbs:
        entries.extend(((record.key, record.label), (f"{record.key}_desc", record.description), (f"{record.key}_PROV", record.label)))
    for record in treaties:
        entries.extend((
            (record.key, record.label),
            (f"{record.key}_desc", record.description),
            (f"{record.key}_entry", record.label),
            (f"{record.key}_entry_short", record.label),
        ))
    for record in organizations:
        entries.extend((
            (record.key, record.label),
            (f"{record.key}_desc", record.description),
            (f"io_opinion_{record.key}", f"{record.label} Member Opinion"),
            (f"diplomatic_status_{record.key}_name", record.label),
            (f"diplomatic_status_{record.key}_tooltip", f"#T {record.label}#!\\nThis country is a member of the {record.label}."),
            (f"{record.key}_list_who_tt", f"$WHO$ is in the {record.label} with $LIST$"),
        ))
    entries.extend((
        ("antq_cohesion", "Organization Cohesion"),
        ("antq_cohesion_desc", "The accumulated capacity of this organization to coordinate shared obligations."),
        ("antq_present_han_tribute", "Present Court Tribute"),
        ("antq_present_han_tribute_desc", "Present a bounded embassy gift and register of obligations at the Han court."),
        ("antq_convene_kangju_route_council", "Convene Route Council"),
        ("antq_convene_kangju_route_council_desc", "Convene Kangju and Sogdian delegates over caravan passage and shared route obligations."),
    ))
    for action in IO_ACTION_KEYS:
        entries.extend((
            (f"PERFORM_{action}_ACTION_SETUP", f"When a member polity uses the ${action}$ action."),
            (f"PERFORM_{action}_ACTION_HEADER", "$MESSENGER$"),
            (f"PERFORM_{action}_ACTION_TITLE", f"[SCOPE.sCountry('actor').GetName] has ${action}$."),
            (f"PERFORM_{action}_ACTION_EFFECTS", "$EFFECT$"),
            (f"PERFORM_{action}_ACTION_LOG", f"$PERFORM_{action}_ACTION_TITLE$"),
            (f"PERFORM_{action}_ACTION_BTN1", "OK"),
            (f"PERFORM_{action}_ACTION_BTN2", "OK"),
            (f"PERFORM_{action}_ACTION_BTN3", "$common_string_go_to$"),
            (f"PERFORM_{action}_ACTION_MAP", ""),
        ))
    for key, label, description in (
        ("antq_punitive_superiority", "Win battles", "Win battles to demonstrate punitive superiority."),
        ("antq_raid_superiority", "Win raids", "Win battles while conducting a limited raid."),
        ("antq_frontier_recovery", "Recover the frontier", "Control the claimed frontier province."),
        ("antq_client_capital", "Take the capital", "Control the capital to impose a client king."),
        ("antq_tribute_capital", "Take the capital", "Control the capital to enforce tribute."),
        ("antq_succession_capital", "Take the capital", "Control the capital in a succession intervention."),
        ("antq_holy_superiority", "Win religious battles", "Win battles to suppress a rival public cult."),
        ("antq_unification_superiority", "Win the unification war", "Win battles to settle a historical unification struggle."),
    ):
        entries.extend(((f"war_goal_{key}", label), (f"war_goal_{key}_desc", description)))
    return "\n".join([f"l_{language}:", *(f' {key}: "{value}"' for key, value in entries), ""])


def outputs(subjects: tuple[SubjectContract, ...]) -> dict[Path, str]:
    cbs = cb_records()
    treaties = peace_records()
    organizations = organization_records()
    rendered = {
        SUBJECT_OUTPUT: subject_script(subjects),
        CB_OUTPUT: cb_script(cbs),
        WARGOAL_OUTPUT: wargoal_script(),
        PEACE_OUTPUT: peace_script(treaties),
        IO_OUTPUT: organization_script(organizations),
        HRE_MIRROR_OUTPUT: (
            "# Exact-name ANTIQVITAS mirror. The installed medieval HRE type is "
            "replaced by the inert hardcoded-key sentinel in "
            "00_antiquitas_m9.txt.\n"
        ),
        BIAS_OUTPUT: io_bias_script(organizations),
        IO_ACTION_OUTPUT: io_action_script(),
        IO_AI_LIST_OUTPUT: io_ai_list_script(),
        IO_AI_PULSE_OUTPUT: io_ai_pulse_script(),
        SUBJECT_BALANCE_OUTPUT: subject_balance_csv(subjects),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        rendered[LOC_ROOT / language / f"antq_m9_subjects_l_{language}.yml"] = localization(
            subjects, cbs, treaties, organizations, language
        )
    return rendered


def validate(records: tuple[SubjectContract, ...]) -> None:
    keys = [record.key for record in records]
    if len(keys) != len(set(keys)):
        raise ValueError("M9 subject contract keys must be unique")
    missing = sorted(set(START_ADAPTERS.values()) - set(keys))
    if missing:
        raise ValueError(f"start adapters lack M9 contract definitions: {', '.join(missing)}")
    knowledge = ADVANCE_OUTPUT.read_text(encoding="utf-8-sig")
    if "unlock_subject_type = antq_tributary" in knowledge:
        raise ValueError(
            "AD 1 tributaries must not require a research unlock from their subjects"
        )
    rendered_loc = localization(
        records, cb_records(), peace_records(), organization_records(), "english"
    )
    for key in (
        "SUBJECT_JOINED_WAR_ATTACKER_DESC",
        "SUBJECT_JOINED_WAR_DEFENDER_DESC",
    ):
        line = next(
            (line for line in rendered_loc.splitlines() if line.startswith(f" {key}:")),
            "",
        )
        if not line or "$SUBJECT$" not in line or "$TYPE$" in line:
            raise ValueError(
                f"{key} must name the styled subject once without composing $TYPE$"
            )
    for record in records:
        for prefix in ("OFFER", "REQUEST"):
            category = (
                f' {prefix}_{record.key}_CATEGORY: '
                '"CATEGORY_SUBJECT_ACTIONS"'
            )
            if category not in rendered_loc:
                raise ValueError(
                    f"{record.key} lacks the installed {prefix} subject-category alias"
                )
        if not 1 <= record.loyalty_to_overlord <= 50:
            raise ValueError(
                f"{record.key} loyalty_to_overlord must stay in installed 1-50 scale"
            )
        if not (
            0 < record.expected_start_min
            <= record.expected_start_max
            <= 100
        ):
            raise ValueError(f"{record.key} has invalid expected start-loyalty band")
        for field, value in (
            ("strength_vs_overlord", record.strength_vs_overlord),
            ("maritime_path_tolerance", record.maritime_path_tolerance),
        ):
            try:
                float(value)
            except ValueError as exc:
                raise ValueError(f"{record.key} has invalid {field}") from exc
    balance = subject_balance_rows(records)
    if len(balance) != 35:
        raise ValueError(f"expected 35 start dependencies, found {len(balance)}")
    if len({row["subject_engine_tag"] for row in balance}) != 35:
        raise ValueError("start dependency subjects must have unique engine tags")
    if {row["subject_type"] for row in balance} != set(START_ADAPTERS.values()):
        raise ValueError("start dependency balance ledger lacks a contract family")
    installed_locations = set(
        json.loads(LOCATIONS.read_text(encoding="utf-8-sig"))
    )
    installed_start_ownable = vanilla_owned_locations(installed_locations)
    invalid_subject_capitals = [
        f"{row['subject_design_tag']}={row['start_capital']}"
        for row in balance
        if row["start_capital"] not in installed_start_ownable
    ]
    if invalid_subject_capitals:
        raise ValueError(
            "start dependency subjects require installed-proven ownable capitals: "
            + ", ".join(invalid_subject_capitals)
        )
    if not (AntqDate(1, 1, 1) < FOEDERATI_UNLOCK <= AntqDate(476, 9, 4)):
        raise ValueError("foederati unlock is outside the playable campaign")
    if not (AntqDate(1, 1, 1) < HOLY_SUPPRESSION_UNLOCK <= AntqDate(476, 9, 4)):
        raise ValueError("holy-suppression unlock is outside the playable campaign")
    cb_keys = [record.key for record in cb_records()]
    if len(cb_keys) != len(set(cb_keys)):
        raise ValueError("M9 casus belli keys must be unique")
    cb_by_key = {record.key: record for record in cb_records()}
    expected_cb_keys = set(ACTIVE_CB_AI_WEIGHTS) | DORMANT_CB_KEYS
    if set(cb_by_key) != expected_cb_keys:
        raise ValueError("M9 CB AI registry is out of sync with rendered casus belli")
    for key, weight in ACTIVE_CB_AI_WEIGHTS.items():
        script = cb_by_key[key].script
        if _ai_weight(weight) not in script or "value = -1" in script:
            raise ValueError(f"active M9 CB {key} lacks its bounded AI priority")
    for key in DORMANT_CB_KEYS:
        script = cb_by_key[key].script
        if _ai_disabled() not in script or "create_visible = { always = no }" not in script:
            raise ValueError(f"dormant M9 CB {key} must remain unavailable")
    treaty_keys = [record.key for record in peace_records()]
    if len(treaty_keys) != len(set(treaty_keys)):
        raise ValueError("M9 peace-treaty keys must be unique")
    io_keys = [record.key for record in organization_records()]
    if len(io_keys) != len(set(io_keys)):
        raise ValueError("M9 international-organization keys must be unique")
    tags = engine_tag_map()
    required_start_tags = {
        "ROM", "HAN", "KHT", "KUC", "KAS", "LOU", "TUR", "XIO",
        "GMU", "QIM", "YQI", "SHC", "PUL", "FJS", "IWL", "DNH",
        "KNG", "SOG",
        "NAB", "SAB", "HIM", "QAT", "HAD", "KIN", "THM", "AGR",
        "GRH", "QTR", "OMN", "BED",
    }
    if missing := sorted(required_start_tags - set(tags)):
        raise ValueError(f"M9 IO start tags are absent from the tag map: {', '.join(missing)}")
    validate_discovery()


def write(records: tuple[SubjectContract, ...]) -> None:
    for path, content in outputs(records).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
        print(f"m9_diplomacy: wrote {path.relative_to(ROOT)}")


def check(records: tuple[SubjectContract, ...]) -> bool:
    failures = []
    for path, expected in outputs(records).items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != expected:
            failures.append(f"stale {path.relative_to(ROOT)}")
    io_rendered = outputs(records)[IO_OUTPUT]
    io_actions = outputs(records)[IO_ACTION_OUTPUT]
    io_ai_list = outputs(records)[IO_AI_LIST_OUTPUT]
    io_ai_pulse = outputs(records)[IO_AI_PULSE_OUTPUT]
    forbidden_ai_tokens = ("ai_tick", "automation_tick", "ai_prerequisite", "ai_will_do", "ai_interaction_source_list")
    if any(token in io_actions for token in forbidden_ai_tokens):
        failures.append("M9 organization actions still expose the targetless generic-action AI path")
    if "always = no" not in io_ai_list:
        failures.append("M9 organization generic-action AI list is not inert")
    for key in ("antq_present_han_tribute", "antq_convene_kangju_route_council"):
        if io_ai_list.count(key) != 1:
            failures.append(f"M9 organization generic action is not explicitly registered once: {key}")
    for token in (
        "is_ai = yes", "tag = XAR", "tag = XCI", "current_month = 3",
        "current_month = 9", f"gold >= {AI_TREASURY_RESERVE}",
        "antq_m9_han_tribute_cooldown", "antq_m9_kangju_council_cooldown",
        "years = 3", "international_organization:antq_han_tributary_system = {",
        "international_organization:antq_kangju_confederation = {",
    ):
        if token not in io_ai_pulse:
            failures.append(f"M9 organization AI pulse lacks {token}")
    if "opinion_trust" in io_rendered:
        failures.append("runtime-rejected opinion_trust survived in IO definitions")
    for token in (
        "hre = {",
        "show_on_diplomatic_map = no",
        "has_leader_country = no",
        "can_join_trigger = { always = no }",
        "auto_disband_trigger = { always = no }",
    ):
        if token not in io_rendered:
            failures.append(f"hardcoded HRE sentinel lacks {token}")
    start_rendered = international_organization_manager()
    hre_instance = start_rendered.split("type = hre", 1)[1].split("\n\t}", 1)[0]
    if start_rendered.count("type = hre") != 1 or "members = {" in hre_instance:
        failures.append("hardcoded HRE sentinel instance is missing or malformed")
    if failures:
        print("m9_diplomacy: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    print(
        f"m9_diplomacy: PASS ({len(records)} subject contracts; {len(cb_records())} casus belli; "
        f"{len(peace_records())} peace treaties; {len(organization_records())} IO types; "
        f"{validate_discovery()} discovery profiles; foederati unlock {FOEDERATI_UNLOCK.engine()})"
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
        records = contracts()
        validate(records)
    except (OSError, ValueError) as exc:
        print(f"m9_diplomacy: FAIL\n  - {exc}")
        return 1
    if args.write:
        write(records)
        return 0
    return 0 if check(records) else 1


if __name__ == "__main__":
    raise SystemExit(main())

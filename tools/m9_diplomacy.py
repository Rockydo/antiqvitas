#!/usr/bin/env python3
"""Render the first ANTIQVITAS M9 diplomatic contracts.

The AD 1 subject ledger remains the historical authority.  This generator owns
the engine adapters selected by that ledger, their localisation mirrors, and
the one date-gated contract.  Keeping the date here forces it through
``dates.AntqDate`` rather than letting an unvalidated literal reach script.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, M2_MIRROR_LANGUAGES

ROOT = Path(__file__).resolve().parents[1]
SUBJECT_OUTPUT = ROOT / "in_game/common/subject_types/00_antiquitas_m9_subjects.txt"
CB_OUTPUT = ROOT / "in_game/common/casus_belli/00_antiquitas_m9.txt"
WARGOAL_OUTPUT = ROOT / "in_game/common/wargoals/00_antiquitas_m9.txt"
PEACE_OUTPUT = ROOT / "in_game/common/peace_treaties/00_antiquitas_m9.txt"
LOC_ROOT = ROOT / "main_menu/localization"

# The historical relations themselves and their citations are in
# docs/world_1ad/subjects.csv.  These adapters are deliberately keyed by the
# design tags used in that ledger, never the volatile engine-tag remapping.
START_ADAPTERS = {
    "ROM": "antq_client_kingdom",
    "PAR": "antq_satrapy",
    "HAN": "antq_tributary",
}
FOEDERATI_UNLOCK = AntqDate.parse("382.1.1")
HOLY_SUPPRESSION_UNLOCK = AntqDate.parse("325.1.1")


@dataclass(frozen=True)
class SubjectContract:
    key: str
    label: str
    description: str
    script: str


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


def standard_contract(
    *,
    subject_pays: str,
    color: str,
    level: int,
    capacity: str,
    external: str = "yes",
    annexable: str = "no",
    cancellation: str = "overlord",
    offensive: bool = False,
    modifiers: tuple[str, ...] = (),
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
        *modifiers,
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
        modifiers=("\tsubject_modifier = { country_cabinet_efficiency = -0.05 }",),
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
            ),
        ),
        SubjectContract(
            "antq_satrapy",
            "Satrapy",
            "An autonomous subordinate realm within an Iranian imperial network.",
            standard_contract(
                subject_pays="subject_pays_vassal", color="subject_vassal", level=1, capacity="0.45", offensive=True,
                modifiers=knowledge_exchange,
            ),
        ),
        SubjectContract(
            "antq_tributary",
            "Tributary",
            "A polity linked by tribute, diplomacy, and frontier security rather than direct administration.",
            standard_contract(
                subject_pays="subject_pays_tributary", color="subject_tributary", level=0, capacity="0.20", cancellation="both",
                modifiers=("\toverlord_protects_external = no", *knowledge_exchange),
            ),
        ),
        SubjectContract(
            "antq_foederati",
            "Foederati",
            "A settled military partner bound by land, service, and treaty.",
            foederati_script,
        ),
        SubjectContract(
            "antq_autonomous_city",
            "Autonomous City",
            "A self-governing city owing limited obligations to a stronger protector.",
            standard_contract(
                subject_pays="subject_pays_tributary", color="subject_tributary", level=0, capacity="0.15", cancellation="both",
            ),
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
    """M10 historical situations will grant and weight these contextually."""
    return "\tai_will_do = { value = -1 }"


def subject_cb(key: str, subject_type: str, treaty: str, war_goal: str) -> str:
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
        _ai_disabled(),
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
                _ai_disabled(),
            )),
        ),
        CasusBelli(
            "antq_impose_client_king", "Impose Client King",
            "Compel a defeated court to accept a protected client-king relationship.",
            subject_cb("antq_impose_client_king", "antq_client_kingdom", "antq_treaty_impose_client_king", "antq_client_capital"),
        ),
        CasusBelli(
            "antq_demand_tribute", "Demand Tribute",
            "Compel a defeated polity to enter a tributary relationship.",
            subject_cb("antq_demand_tribute", "antq_tributary", "antq_treaty_demand_tribute", "antq_tribute_capital"),
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
                _ai_disabled(),
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
                _ai_disabled(),
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
                _ai_disabled(),
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
                _ai_disabled(),
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


def localization(
    subjects: tuple[SubjectContract, ...],
    cbs: tuple[CasusBelli, ...],
    treaties: tuple[PeaceTreaty, ...],
    language: str,
) -> str:
    entries: list[tuple[str, str]] = []
    for record in subjects:
        entries.extend((
            (record.key, record.label),
            (f"{record.key}_desc", record.description),
            (f"AM_{record.key}", record.label),
            (f"LEAD_{record.key}", record.label),
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
    rendered = {
        SUBJECT_OUTPUT: subject_script(subjects),
        CB_OUTPUT: cb_script(cbs),
        WARGOAL_OUTPUT: wargoal_script(),
        PEACE_OUTPUT: peace_script(treaties),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        rendered[LOC_ROOT / language / f"antq_m9_subjects_l_{language}.yml"] = localization(subjects, cbs, treaties, language)
    return rendered


def validate(records: tuple[SubjectContract, ...]) -> None:
    keys = [record.key for record in records]
    if len(keys) != len(set(keys)):
        raise ValueError("M9 subject contract keys must be unique")
    missing = sorted(set(START_ADAPTERS.values()) - set(keys))
    if missing:
        raise ValueError(f"start adapters lack M9 contract definitions: {', '.join(missing)}")
    if not (AntqDate(1, 1, 1) < FOEDERATI_UNLOCK <= AntqDate(476, 9, 4)):
        raise ValueError("foederati unlock is outside the playable campaign")
    if not (AntqDate(1, 1, 1) < HOLY_SUPPRESSION_UNLOCK <= AntqDate(476, 9, 4)):
        raise ValueError("holy-suppression unlock is outside the playable campaign")
    cb_keys = [record.key for record in cb_records()]
    if len(cb_keys) != len(set(cb_keys)):
        raise ValueError("M9 casus belli keys must be unique")
    treaty_keys = [record.key for record in peace_records()]
    if len(treaty_keys) != len(set(treaty_keys)):
        raise ValueError("M9 peace-treaty keys must be unique")


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
    if failures:
        print("m9_diplomacy: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    print(
        f"m9_diplomacy: PASS ({len(records)} subject contracts; {len(cb_records())} casus belli; "
        f"{len(peace_records())} peace treaties; foederati unlock {FOEDERATI_UNLOCK.engine()})"
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

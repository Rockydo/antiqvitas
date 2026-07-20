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


@dataclass(frozen=True)
class SubjectContract:
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


def localization(records: tuple[SubjectContract, ...], language: str) -> str:
    entries: list[tuple[str, str]] = []
    for record in records:
        entries.extend((
            (record.key, record.label),
            (f"{record.key}_desc", record.description),
            (f"AM_{record.key}", record.label),
            (f"LEAD_{record.key}", record.label),
        ))
    return "\n".join([f"l_{language}:", *(f' {key}: "{value}"' for key, value in entries), ""])


def outputs(records: tuple[SubjectContract, ...]) -> dict[Path, str]:
    rendered = {SUBJECT_OUTPUT: subject_script(records)}
    for language in ("english", *M2_MIRROR_LANGUAGES):
        rendered[LOC_ROOT / language / f"antq_m9_subjects_l_{language}.yml"] = localization(records, language)
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
    print(f"m9_diplomacy: PASS ({len(records)} ancient subject contracts; foederati unlock {FOEDERATI_UNLOCK.engine()})")
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

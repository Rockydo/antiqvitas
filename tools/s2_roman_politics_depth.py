#!/usr/bin/env python3
"""Permanent focused regression for Rome's deep early/late political arc."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLITICS = ROOT / "docs/m6/ancient_politics_content.csv"
POLITICS_ART = ROOT / "docs/m6/ancient_politics_art.csv"
PRIVILEGES = ROOT / "docs/m6/estate_order_privileges.csv"
PRIVILEGE_ART = ROOT / "docs/m6/estate_order_art.csv"
REFORM_PATHS = ROOT / "docs/m6/alternative_reform_paths.csv"
REFORM_SCRIPT = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "docs/m8/advances.csv"

EARLY_REFORMS = {
    "antq_principate",
    "antq_augustan_dyarchy",
    "antq_provincial_principate",
    "antq_flavian_imperial_settlement",
    "antq_antonine_provincial_principate",
    "antq_severan_military_principate",
}
LATE_REFORMS = {
    "antq_dominate",
    "antq_tetrarchic_collegium",
    "antq_constantinian_consistory",
    "antq_late_imperial_twin_courts",
}
SUCCESSOR_AGES = {
    "antq_flavian_imperial_settlement": ("0", "age_1_traditions"),
    "antq_antonine_provincial_principate": ("1", "age_2_renaissance"),
    "antq_severan_military_principate": ("2", "age_3_discovery"),
    "antq_tetrarchic_collegium": ("3", "age_4_reformation"),
    "antq_constantinian_consistory": ("3", "age_4_reformation"),
    "antq_late_imperial_twin_courts": ("4", "age_5_absolutism"),
}
NEW_ROMAN_PRIVILEGES = {
    "antq_roman_senatorial_provincial_commissions",
    "antq_roman_imperial_legatine_inspections",
    "antq_roman_equestrian_procuratorial_careers",
    "antq_roman_municipal_decurion_obligations",
    "antq_roman_veteran_allotment_guarantees",
    "antq_roman_provincial_petition_safeguards",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def block(script: str, key: str) -> str:
    start = script.find(f"{key} = {{")
    if start < 0:
        raise ValueError(f"missing generated reform block: {key}")
    depth = 0
    opened = False
    for index in range(start, len(script)):
        if script[index] == "{":
            depth += 1
            opened = True
        elif script[index] == "}":
            depth -= 1
            if opened and depth == 0:
                return script[start:index + 1]
    raise ValueError(f"unterminated generated reform block: {key}")


def main() -> int:
    failures: list[str] = []
    politics = rows(POLITICS)
    profile_counts = Counter(
        (row["profile"], row["category"])
        for row in politics
        if row["profile"] in {"roman", "late_roman"}
    )
    expected_counts = {
        ("roman", "parliament_type"): 1,
        ("roman", "cabinet_action"): 11,
        ("roman", "parliament_issue"): 9,
        ("roman", "parliament_agenda"): 9,
        ("late_roman", "parliament_type"): 1,
        ("late_roman", "cabinet_action"): 5,
        ("late_roman", "parliament_issue"): 3,
        ("late_roman", "parliament_agenda"): 3,
    }
    if profile_counts != expected_counts:
        failures.append(f"Roman council breadth differs: {dict(profile_counts)}")

    paths = {row["reform"]: row for row in rows(REFORM_PATHS)}
    for reform, (age_index, _age_key) in SUCCESSOR_AGES.items():
        row = paths.get(reform)
        if row is None or row["age_index"] != age_index:
            failures.append(f"wrong or missing successor age contract: {reform}")

    reform_script = REFORM_SCRIPT.read_text(encoding="utf-8-sig")
    for reform in EARLY_REFORMS:
        if "set_parliament_type = parliament_type:antq_roman_senate" not in block(
            reform_script, reform
        ):
            failures.append(f"early Roman reform lost Senate activation: {reform}")
    for reform in LATE_REFORMS:
        if "set_parliament_type = parliament_type:antq_imperial_consistory" not in block(
            reform_script, reform
        ):
            failures.append(f"late Roman reform lost Consistory activation: {reform}")

    advances = rows(ADVANCES)
    for reform, (_age_index, age_key) in SUCCESSOR_AGES.items():
        token = f"unlock_government_reform={reform}"
        matches = [row for row in advances if token in row["unlocks"].split(";")]
        if len(matches) != 1 or matches[0]["age"] != age_key:
            failures.append(
                f"successor unlock is not unique and age-correct: {reform}"
            )

    privilege_rows = {row["key"]: row for row in rows(PRIVILEGES)}
    for left, right in (
        (
            "antq_roman_senatorial_provincial_commissions",
            "antq_roman_imperial_legatine_inspections",
        ),
        (
            "antq_roman_equestrian_procuratorial_careers",
            "antq_roman_municipal_decurion_obligations",
        ),
        (
            "antq_roman_veteran_allotment_guarantees",
            "antq_roman_provincial_petition_safeguards",
        ),
    ):
        if (
            privilege_rows.get(left, {}).get("potential_tags") != "XAA"
            or privilege_rows.get(right, {}).get("potential_tags") != "XAA"
            or privilege_rows.get(left, {}).get("exclusive_with") != right
            or privilege_rows.get(right, {}).get("exclusive_with") != left
        ):
            failures.append(f"Roman privilege choice pair is not exact-tag/exclusive: {left}")

    politics_art = {row["key"] for row in rows(POLITICS_ART)}
    required_politics_art = {
        row["key"]
        for row in politics
        if row["category"] in {"parliament_type", "cabinet_action"}
        and row["profile"] in {"roman", "late_roman"}
    }
    if not required_politics_art.issubset(politics_art):
        failures.append("Roman council/state-office direct art is incomplete")

    privilege_art = {row["key"] for row in rows(PRIVILEGE_ART)}
    late_privileges = {
        row["key"]
        for row in privilege_rows.values()
        if row["potential_reforms"]
        and set(row["potential_reforms"].split("|")) == LATE_REFORMS
    }
    if len(late_privileges) != 6:
        failures.append(f"late Roman profile privilege count differs: {len(late_privileges)}")
    if not (NEW_ROMAN_PRIVILEGES | late_privileges).issubset(privilege_art):
        failures.append("new Roman privilege direct art is incomplete")

    if failures:
        print("s2_roman_politics_depth: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s2_roman_politics_depth: PASS "
        "(11 early + 5 late programmes; 9 + 3 debates/agendas; "
        "6 successor reforms; 12 new direct-art privileges)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

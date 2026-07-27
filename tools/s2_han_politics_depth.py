#!/usr/bin/env python3
"""Permanent focused regression for Han's Western/Eastern political arc."""

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

WESTERN_REFORMS = {
    "antq_han_imperial_bureaucracy",
    "antq_memorialist_han_court",
    "antq_commandery_supervision",
    "antq_xin_state_reorganization",
}
EASTERN_REFORMS = {
    "antq_guangwu_restoration_court",
    "antq_eastern_han_secretariat",
    "antq_affinal_regency_court",
    "antq_provincial_inspectorate_commands",
    "antq_three_kingdoms_chancellery",
    "antq_jin_reunification_court",
}
SUCCESSOR_AGES = {
    "antq_xin_state_reorganization": ("0", "age_1_traditions"),
    "antq_guangwu_restoration_court": ("0", "age_1_traditions"),
    "antq_eastern_han_secretariat": ("1", "age_2_renaissance"),
    "antq_affinal_regency_court": ("1", "age_2_renaissance"),
    "antq_provincial_inspectorate_commands": ("2", "age_3_discovery"),
    "antq_three_kingdoms_chancellery": ("2", "age_3_discovery"),
    "antq_jin_reunification_court": ("3", "age_4_reformation"),
}
NEW_HAN_PRIVILEGES = {
    "antq_han_three_excellencies_nomination_review",
    "antq_han_secretariat_appointment_channel",
    "antq_han_regional_inspector_circuits",
    "antq_han_commandery_administrator_tenure",
    "antq_han_state_salt_iron_workshops",
    "antq_han_local_market_workshop_compacts",
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
        if row["profile"] in {"han", "late_han"}
    )
    expected_counts = {
        ("han", "parliament_type"): 1,
        ("han", "cabinet_action"): 11,
        ("han", "parliament_issue"): 9,
        ("han", "parliament_agenda"): 9,
        ("late_han", "parliament_type"): 1,
        ("late_han", "cabinet_action"): 5,
        ("late_han", "parliament_issue"): 3,
        ("late_han", "parliament_agenda"): 3,
    }
    if profile_counts != expected_counts:
        failures.append(f"Han council breadth differs: {dict(profile_counts)}")

    paths = {row["reform"]: row for row in rows(REFORM_PATHS)}
    for reform, (age_index, _age_key) in SUCCESSOR_AGES.items():
        row = paths.get(reform)
        if row is None or row["age_index"] != age_index:
            failures.append(f"wrong or missing successor age contract: {reform}")

    reform_script = REFORM_SCRIPT.read_text(encoding="utf-8-sig")
    for reform in WESTERN_REFORMS:
        if "set_parliament_type = parliament_type:antq_han_court_conference" not in block(
            reform_script, reform
        ):
            failures.append(f"Western Han reform lost court activation: {reform}")
    for reform in EASTERN_REFORMS:
        if (
            "set_parliament_type = parliament_type:antq_eastern_han_imperial_secretariat"
            not in block(reform_script, reform)
        ):
            failures.append(f"Eastern Han reform lost Secretariat activation: {reform}")

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
            "antq_han_three_excellencies_nomination_review",
            "antq_han_secretariat_appointment_channel",
        ),
        (
            "antq_han_regional_inspector_circuits",
            "antq_han_commandery_administrator_tenure",
        ),
        (
            "antq_han_state_salt_iron_workshops",
            "antq_han_local_market_workshop_compacts",
        ),
    ):
        if (
            privilege_rows.get(left, {}).get("potential_tags") != "XAR"
            or privilege_rows.get(right, {}).get("potential_tags") != "XAR"
            or privilege_rows.get(left, {}).get("exclusive_with") != right
            or privilege_rows.get(right, {}).get("exclusive_with") != left
        ):
            failures.append(f"Han privilege choice pair is not exact-tag/exclusive: {left}")

    politics_art = {row["key"] for row in rows(POLITICS_ART)}
    required_politics_art = {
        row["key"]
        for row in politics
        if row["category"] in {"parliament_type", "cabinet_action"}
        and row["profile"] in {"han", "late_han"}
    }
    if not required_politics_art.issubset(politics_art):
        failures.append("Han council/state-office direct art is incomplete")

    privilege_art = {row["key"] for row in rows(PRIVILEGE_ART)}
    late_privileges = {
        row["key"]
        for row in privilege_rows.values()
        if row["potential_reforms"]
        and set(row["potential_reforms"].split("|")) == EASTERN_REFORMS
    }
    if len(late_privileges) != 6:
        failures.append(f"late Han profile privilege count differs: {len(late_privileges)}")
    if not (NEW_HAN_PRIVILEGES | late_privileges).issubset(privilege_art):
        failures.append("new Han privilege direct art is incomplete")

    if failures:
        print("s2_han_politics_depth: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s2_han_politics_depth: PASS "
        "(11 Western + 5 Eastern programmes; 9 + 3 debates/agendas; "
        "7 successor reforms; 12 new direct-art privileges)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

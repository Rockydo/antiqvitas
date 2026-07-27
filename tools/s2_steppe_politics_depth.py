#!/usr/bin/env python3
"""Permanent focused regression for Xiongnu and Xianbei political depth."""

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

XIONGNU_REFORMS = {
    "antq_steppe_confederation",
    "antq_xiongnu_dual_wing_command",
    "antq_xiongnu_gift_circuit",
    "antq_xiongnu_southern_frontier_court",
    "antq_xiongnu_northern_western_confederacy",
    "antq_southern_xiongnu_commandery_settlement",
    "antq_xiongnu_five_divisions_order",
    "antq_han_zhao_chanyu_court",
}
XIANBEI_REFORMS = {
    "antq_xianbei_eastern_confederacy",
    "antq_tanshihuai_three_divisions",
    "antq_xianbei_successor_federations",
    "antq_murong_frontier_court",
    "antq_tuoba_dai_confederacy",
    "antq_rouran_khaganate",
}
SUCCESSOR_AGES = {
    "antq_xiongnu_southern_frontier_court": ("0", "age_1_traditions"),
    "antq_xiongnu_northern_western_confederacy": ("0", "age_1_traditions"),
    "antq_southern_xiongnu_commandery_settlement": ("0", "age_1_traditions"),
    "antq_xiongnu_five_divisions_order": ("2", "age_3_discovery"),
    "antq_han_zhao_chanyu_court": ("3", "age_4_reformation"),
    "antq_tanshihuai_three_divisions": ("1", "age_2_renaissance"),
    "antq_xianbei_successor_federations": ("1", "age_2_renaissance"),
    "antq_murong_frontier_court": ("3", "age_4_reformation"),
    "antq_tuoba_dai_confederacy": ("3", "age_4_reformation"),
    "antq_rouran_khaganate": ("5", "age_6_revolutions"),
}
XIONGNU_EXACT_PRIVILEGES = {
    "antq_xiongnu_chanyu_lineage_nomination",
    "antq_xiongnu_wing_commander_acclamation",
    "antq_xiongnu_han_frontier_stipend_treaty",
    "antq_xiongnu_independent_western_tribute_circuit",
    "antq_xiongnu_chanyu_gift_redistribution",
    "antq_xiongnu_lineage_gift_retention_quotas",
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
        if row["profile"] in {"xiongnu", "xianbei"}
    )
    expected_counts = {
        ("xiongnu", "parliament_type"): 1,
        ("xiongnu", "cabinet_action"): 11,
        ("xiongnu", "parliament_issue"): 9,
        ("xiongnu", "parliament_agenda"): 9,
        ("xianbei", "parliament_type"): 1,
        ("xianbei", "cabinet_action"): 5,
        ("xianbei", "parliament_issue"): 3,
        ("xianbei", "parliament_agenda"): 3,
    }
    if profile_counts != expected_counts:
        failures.append(f"steppe council breadth differs: {dict(profile_counts)}")

    paths = {row["reform"]: row for row in rows(REFORM_PATHS)}
    for reform, (age_index, _age_key) in SUCCESSOR_AGES.items():
        row = paths.get(reform)
        if row is None or row["age_index"] != age_index:
            failures.append(f"wrong or missing successor age contract: {reform}")

    reform_script = REFORM_SCRIPT.read_text(encoding="utf-8-sig")
    for reform in XIONGNU_REFORMS:
        if "set_parliament_type = parliament_type:antq_xiongnu_wing_council" not in block(
            reform_script, reform
        ):
            failures.append(f"Xiongnu reform lost wing-council activation: {reform}")
    for reform in XIANBEI_REFORMS:
        if "set_parliament_type = parliament_type:antq_xianbei_chiefly_assembly" not in block(
            reform_script, reform
        ):
            failures.append(f"Xianbei reform lost chiefly-assembly activation: {reform}")

    advances = rows(ADVANCES)
    for reform, (_age_index, age_key) in SUCCESSOR_AGES.items():
        token = f"unlock_government_reform={reform}"
        matches = [row for row in advances if token in row["unlocks"].split(";")]
        if len(matches) != 1 or matches[0]["age"] != age_key:
            failures.append(f"successor unlock is not unique and age-correct: {reform}")

    privilege_rows = {row["key"]: row for row in rows(PRIVILEGES)}
    for left, right in (
        (
            "antq_xiongnu_chanyu_lineage_nomination",
            "antq_xiongnu_wing_commander_acclamation",
        ),
        (
            "antq_xiongnu_han_frontier_stipend_treaty",
            "antq_xiongnu_independent_western_tribute_circuit",
        ),
        (
            "antq_xiongnu_chanyu_gift_redistribution",
            "antq_xiongnu_lineage_gift_retention_quotas",
        ),
    ):
        if (
            privilege_rows.get(left, {}).get("potential_tags") != "XIO"
            or privilege_rows.get(right, {}).get("potential_tags") != "XIO"
            or privilege_rows.get(left, {}).get("exclusive_with") != right
            or privilege_rows.get(right, {}).get("exclusive_with") != left
        ):
            failures.append(
                f"Xiongnu privilege choice pair is not exact-tag/exclusive: {left}"
            )

    xianbei_privileges = {
        row["key"]
        for row in privilege_rows.values()
        if row["potential_reforms"]
        and set(row["potential_reforms"].split("|")) == XIANBEI_REFORMS
    }
    if len(xianbei_privileges) != 6:
        failures.append(f"Xianbei profile privilege count differs: {len(xianbei_privileges)}")

    politics_art = {row["key"] for row in rows(POLITICS_ART)}
    required_politics_art = {
        row["key"]
        for row in politics
        if row["category"] in {"parliament_type", "cabinet_action"}
        and row["profile"] in {"xiongnu", "xianbei"}
    }
    if not required_politics_art.issubset(politics_art):
        failures.append("Xiongnu/Xianbei council and state-office direct art is incomplete")

    privilege_art = {row["key"] for row in rows(PRIVILEGE_ART)}
    if not (XIONGNU_EXACT_PRIVILEGES | xianbei_privileges).issubset(privilege_art):
        failures.append("new Xiongnu/Xianbei privilege direct art is incomplete")

    if failures:
        print("s2_steppe_politics_depth: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s2_steppe_politics_depth: PASS "
        "(11 Xiongnu + 5 Xianbei programmes; 9 + 3 debates/agendas; "
        "10 dated successors; 12 new direct-art privileges)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

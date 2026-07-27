#!/usr/bin/env python3
"""Permanent focused regression for the Arsacid-to-Sasanian political arc."""

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

ARSACID_REFORMS = {
    "antq_parthian_king_of_kings",
    "antq_parthian_subkingdom",
    "antq_indo_scythian_kingship",
    "antq_iranian_great_house_reform",
    "antq_iranian_royal_domain",
    "antq_vologasid_dynastic_settlement",
    "antq_arsacid_dual_court_compact",
    "antq_late_arsacid_house_mobilization",
}
SASANIAN_REFORMS = {
    "antq_sassanid_centralized_monarchy",
    "antq_ardashir_unification_court",
    "antq_shapur_imperial_settlement",
    "antq_sasanian_shahrdar_marzban_order",
    "antq_yazdegerd_concordat_court",
    "antq_bahram_great_house_settlement",
}
SUCCESSOR_AGES = {
    "antq_vologasid_dynastic_settlement": ("0", "age_1_traditions"),
    "antq_arsacid_dual_court_compact": ("1", "age_2_renaissance"),
    "antq_late_arsacid_house_mobilization": ("2", "age_3_discovery"),
    "antq_ardashir_unification_court": ("2", "age_3_discovery"),
    "antq_shapur_imperial_settlement": ("2", "age_3_discovery"),
    "antq_sasanian_shahrdar_marzban_order": ("3", "age_4_reformation"),
    "antq_yazdegerd_concordat_court": ("5", "age_6_revolutions"),
    "antq_bahram_great_house_settlement": ("5", "age_6_revolutions"),
}
NEW_ARSACID_PRIVILEGES = {
    "antq_iranian_great_house_succession_acclamation",
    "antq_iranian_royal_dynastic_nomination",
    "antq_iranian_subkingdom_tribute_autonomy",
    "antq_iranian_royal_domain_assessment",
    "antq_iranian_noble_mounted_host_exemptions",
    "antq_iranian_standing_royal_garrisons",
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
        if row["profile"] in {"iranian", "sasanian"}
    )
    expected_counts = {
        ("iranian", "parliament_type"): 1,
        ("iranian", "cabinet_action"): 11,
        ("iranian", "parliament_issue"): 9,
        ("iranian", "parliament_agenda"): 9,
        ("sasanian", "parliament_type"): 1,
        ("sasanian", "cabinet_action"): 5,
        ("sasanian", "parliament_issue"): 3,
        ("sasanian", "parliament_agenda"): 3,
    }
    if profile_counts != expected_counts:
        failures.append(f"Iranian council breadth differs: {dict(profile_counts)}")

    paths = {row["reform"]: row for row in rows(REFORM_PATHS)}
    for reform, (age_index, _age_key) in SUCCESSOR_AGES.items():
        row = paths.get(reform)
        if row is None or row["age_index"] != age_index:
            failures.append(f"wrong or missing successor age contract: {reform}")

    reform_script = REFORM_SCRIPT.read_text(encoding="utf-8-sig")
    for reform in ARSACID_REFORMS:
        if "set_parliament_type = parliament_type:antq_iranian_great_council" not in block(
            reform_script, reform
        ):
            failures.append(f"Arsacid reform lost great-house council activation: {reform}")
    for reform in SASANIAN_REFORMS:
        if "set_parliament_type = parliament_type:antq_sasanian_royal_council" not in block(
            reform_script, reform
        ):
            failures.append(f"Sasanian reform lost royal-council activation: {reform}")

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
            "antq_iranian_great_house_succession_acclamation",
            "antq_iranian_royal_dynastic_nomination",
        ),
        (
            "antq_iranian_subkingdom_tribute_autonomy",
            "antq_iranian_royal_domain_assessment",
        ),
        (
            "antq_iranian_noble_mounted_host_exemptions",
            "antq_iranian_standing_royal_garrisons",
        ),
    ):
        if (
            privilege_rows.get(left, {}).get("potential_tags") != "XAH"
            or privilege_rows.get(right, {}).get("potential_tags") != "XAH"
            or privilege_rows.get(left, {}).get("exclusive_with") != right
            or privilege_rows.get(right, {}).get("exclusive_with") != left
        ):
            failures.append(
                f"Arsacid privilege choice pair is not exact-tag/exclusive: {left}"
            )

    politics_art = {row["key"] for row in rows(POLITICS_ART)}
    required_politics_art = {
        row["key"]
        for row in politics
        if row["category"] in {"parliament_type", "cabinet_action"}
        and row["profile"] in {"iranian", "sasanian"}
    }
    if not required_politics_art.issubset(politics_art):
        failures.append("Arsacid/Sasanian council and state-office direct art is incomplete")

    privilege_art = {row["key"] for row in rows(PRIVILEGE_ART)}
    sasanian_privileges = {
        row["key"]
        for row in privilege_rows.values()
        if row["potential_reforms"]
        and set(row["potential_reforms"].split("|")) == SASANIAN_REFORMS
    }
    if len(sasanian_privileges) != 6:
        failures.append(
            f"Sasanian profile privilege count differs: {len(sasanian_privileges)}"
        )
    if not (NEW_ARSACID_PRIVILEGES | sasanian_privileges).issubset(privilege_art):
        failures.append("new Arsacid/Sasanian privilege direct art is incomplete")

    if failures:
        print("s2_iranian_politics_depth: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s2_iranian_politics_depth: PASS "
        "(11 Arsacid + 5 Sasanian programmes; 9 + 3 debates/agendas; "
        "8 successor reforms; 12 new direct-art privileges)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

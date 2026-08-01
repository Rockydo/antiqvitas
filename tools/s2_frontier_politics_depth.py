#!/usr/bin/env python3
"""Focused regression for four distinct frontier political profiles."""

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
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
ADVANCES = ROOT / "docs/m8/advances.csv"

PROFILES = {
    "aestian": {
        "tag": "AES",
        "council": "antq_aestian_amber_coast_gathering",
        "base": "antq_aestian_amber_coast_order",
        "start_privilege": "antq_aestian_leading_household_hearings",
        "alternatives": {
            "antq_aestian_shore_exchange_compact",
            "antq_aestian_woodland_assembly",
        },
    },
    "frisian": {
        "tag": "FRI",
        "council": "antq_frisian_terp_assembly",
        "base": "antq_frisian_terp_community_order",
        "start_privilege": "antq_frisian_leading_terp_hearings",
        "alternatives": {
            "antq_frisian_tidal_compact",
            "antq_frisian_frontier_council",
        },
    },
    "dacian": {
        "tag": "DAC",
        "council": "antq_dacian_hillfort_council",
        "base": "antq_dacian_divided_kingships",
        "start_privilege": "antq_dacian_hillfort_house_hearings",
        "alternatives": {
            "antq_dacian_hillfort_compact",
            "antq_dacian_mountain_court",
        },
    },
    "garamantian": {
        "tag": "GAR",
        "council": "antq_garamantian_oasis_council",
        "base": "antq_garamantian_oasis_state",
        "start_privilege": "antq_garamantian_leading_oasis_hearings",
        "alternatives": {
            "antq_garamantian_irrigation_court",
            "antq_garamantian_caravan_compact",
        },
    },
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
    counts = Counter(
        (row["profile"], row["category"])
        for row in politics
        if row["profile"] in PROFILES
    )
    expected = {
        (profile, category): count
        for profile in PROFILES
        for category, count in (
            ("parliament_type", 1),
            ("cabinet_action", 5),
            ("parliament_issue", 3),
            ("parliament_agenda", 3),
        )
    }
    if counts != expected:
        failures.append(f"frontier council breadth differs: {dict(counts)}")

    reform_script = REFORM_SCRIPT.read_text(encoding="utf-8-sig")
    path_rows = {row["reform"]: row for row in rows(REFORM_PATHS)}
    advances = rows(ADVANCES)
    governments = {row["design_tag"]: row for row in rows(GOVERNMENTS)}
    privilege_rows = rows(PRIVILEGES)
    profile_privileges: set[str] = set()

    for profile, contract in PROFILES.items():
        reform_set = {contract["base"], *contract["alternatives"]}
        council_effect = (
            f"set_parliament_type = parliament_type:{contract['council']}"
        )
        for reform in reform_set:
            if council_effect not in block(reform_script, reform):
                failures.append(f"{profile} reform lost council activation: {reform}")

        for reform in contract["alternatives"]:
            row = path_rows.get(reform)
            if row is None or row["profile"] != profile or row["age_index"] != "0":
                failures.append(f"wrong or missing Age-I alternative: {reform}")
            token = f"unlock_government_reform={reform}"
            matches = [row for row in advances if token in row["unlocks"].split(";")]
            profiles = [row["eligibility"] for row in matches]
            if (
                not matches
                or any(row["age"] != "age_1_traditions" for row in matches)
                or len(profiles) != len(set(profiles))
                or "Practices transferable" in " ".join(profiles)
            ):
                failures.append(
                    f"alternative unlock is not profile-distinct and Age-I: {reform}"
                )

        base_token = f"unlock_government_reform={contract['base']}"
        base_matches = [
            row for row in advances if base_token in row["unlocks"].split(";")
        ]
        if base_matches:
            failures.append(f"opening reform leaked into research: {contract['base']}")

        government = governments.get(contract["tag"], {})
        if (
            government.get("reform") != contract["base"]
            or contract["start_privilege"]
            not in government.get("privileges", "").split("|")
        ):
            failures.append(f"{contract['tag']} opening political setup differs")

        matching_privileges = {
            row["key"]
            for row in privilege_rows
            if row["potential_reforms"]
            and set(row["potential_reforms"].split("|")) == reform_set
        }
        if len(matching_privileges) != 6:
            failures.append(
                f"{profile} profile privilege count differs: {len(matching_privileges)}"
            )
        profile_privileges.update(matching_privileges)

    politics_art = {row["key"] for row in rows(POLITICS_ART)}
    required_politics_art = {
        row["key"]
        for row in politics
        if row["category"] in {"parliament_type", "cabinet_action"}
        and row["profile"] in PROFILES
    }
    if not required_politics_art.issubset(politics_art):
        failures.append("frontier council and state-office direct art is incomplete")

    privilege_art = {row["key"] for row in rows(PRIVILEGE_ART)}
    if not profile_privileges.issubset(privilege_art):
        failures.append("frontier profile privilege direct art is incomplete")

    if failures:
        print("s2_frontier_politics_depth: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s2_frontier_politics_depth: PASS "
        "(4 councils; 20 programmes; 12 debates/agendas; "
        "12 reforms; 24 direct-art profile privileges)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

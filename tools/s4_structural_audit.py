#!/usr/bin/env python3
"""Regression guard for the advanced structural-audit remediation."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M10_SITUATIONS = tuple(sorted((ROOT / "in_game/common/situations").glob("antq_m10_*.txt")))
M10_DISASTERS = tuple(sorted((ROOT / "in_game/common/disasters").glob("antq_m10_*.txt")))
S2_SITUATIONS = (ROOT / "in_game/common/situations/antq_s2_germania_dynamics.txt",)
IO_TYPES = ROOT / "in_game/common/international_organizations/00_antiquitas_m9.txt"
IO_START = ROOT / "main_menu/setup/start/15_international_organizations.txt"
ACTION_FILES = (
    ROOT / "in_game/common/generic_actions/antq_m9_organization_actions.txt",
    ROOT / "in_game/common/generic_actions/antq_s2_germania_actions.txt",
    ROOT / "in_game/common/generic_actions/antq_s2_arabian_route_actions.txt",
)
AI_LIST_ROOT = ROOT / "in_game/common/generic_action_ai_lists"
ACTIVE_IOS = {
    "antq_han_tributary_system",
    "antq_kangju_confederation",
    "antq_germanic_frontier_exchanges",
    "antq_northern_amber_assemblies",
    "antq_arabian_route_exchanges",
}


def blocks(text: str, prefix: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for match in re.finditer(rf"(?m)^({re.escape(prefix)}[a-z0-9_]*)\s*=\s*\{{", text):
        depth = 0
        for index in range(match.end() - 1, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    result[match.group(1)] = text[match.start(): index + 1]
                    break
    return result


def main() -> int:
    failures: list[str] = []
    managers: dict[str, str] = {}
    for path in (*M10_SITUATIONS, *M10_DISASTERS, *S2_SITUATIONS):
        managers.update(blocks(path.read_text(encoding="utf-8-sig"), "antq_"))
    if len(managers) < 35:
        failures.append(f"historical manager inventory unexpectedly shallow: {len(managers)}")
    for key, block in managers.items():
        variable = f"{key}_resolution_progress"
        required = (
            "can_end = {",
            f"var:{variable} >= 100",
            f"set_variable = {{ name = {variable} value = 0 }}",
            "on_monthly = {",
            f"change_variable = {{ name = {variable}",
            "stability >= 20 at_war = no",
            "stability >= 0 at_war = yes",
            f"remove_variable = {variable}",
        )
        for token in required:
            if token not in block:
                failures.append(f"{key} lacks staged-current token: {token}")
        if "current_date >=" not in block:
            failures.append(f"{key} lacks a sourced safety-bound date")
        if key.startswith("antq_m10_"):
            for token in ("add_manpower", "monthly_income_trade_and_tax", "change_province_food_percentage"):
                if token not in block:
                    failures.append(f"{key} lacks recurring material pressure: {token}")

    disaster_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in M10_DISASTERS)
    for disease in ("antq_m10_second_antonine_plague", "antq_m10_third_cyprian_plague"):
        block = managers.get(disease, "")
        for token in (
            "global_population_growth = -0.003",
            "global_manpower_modifier = -0.12",
            "global_monthly_food_modifier = -0.10",
            "tax_income_efficiency = small_tax_income_efficiency_penalty",
        ):
            if token not in block:
                failures.append(f"{disease} lacks epidemic trajectory modifier: {token}")
    cyprian = managers.get("antq_m10_third_cyprian_plague", "")
    if "has_any_active_disaster = no" in cyprian:
        failures.append("Cyprian trajectory cannot overlap the third-century crisis")
    if "monthly_gold_income" in disaster_text:
        failures.append("historical managers revived invalid monthly_gold_income")

    start_text = IO_START.read_text(encoding="utf-8-sig")
    start_blocks = re.findall(r"add_international_organization\s*=\s*\{(.*?)\n\t\}", start_text, re.S)
    start_types: dict[str, int] = {}
    for block in start_blocks:
        type_match = re.search(r"\btype\s*=\s*([a-z0-9_]+)", block)
        member_match = re.search(r"\bmembers\s*=\s*\{([^}]*)\}", block)
        if type_match and member_match:
            start_types[type_match.group(1)] = len(member_match.group(1).split())
    if set(start_types) != ACTIVE_IOS:
        failures.append(f"opening IO inventory mismatch: {sorted(start_types)}")
    for key, count in start_types.items():
        if count < 2:
            failures.append(f"opening one-member IO shell: {key}={count}")

    type_blocks = blocks(IO_TYPES.read_text(encoding="utf-8-sig"), "antq_")
    for key in ACTIVE_IOS:
        block = type_blocks.get(key, "")
        for token in (
            "join_visible_trigger = { always = yes }",
            "can_join_trigger = {",
            "can_leave_trigger = {",
            "monthly_effect = {",
            "antq_cohesion = {",
            "ai_desire_to_join = {",
            "ai_desire_to_allow_new_member = {",
        ):
            if token not in block:
                failures.append(f"active IO {key} lacks functional token: {token}")
        if "can_join_trigger = { always = no }" in block:
            failures.append(f"active IO {key} still disables joining")

    actions: set[str] = set()
    for path in ACTION_FILES:
        text = path.read_text(encoding="utf-8-sig")
        action_blocks = blocks(text, "antq_")
        actions.update(action_blocks)
        for key, block in action_blocks.items():
            for forbidden in ("ai_tick = never", "automation_tick = never", "add = -1000"):
                if forbidden in block:
                    failures.append(f"organization action {key} retains {forbidden}")
            for token in ("ai_tick = monthly", "automation_tick = monthly", "ai_will_do = {"):
                if token not in block:
                    failures.append(f"organization action {key} lacks {token}")
    ai_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in AI_LIST_ROOT.glob("*.txt"))
    for key in actions:
        if len(re.findall(rf"(?m)^\s*{re.escape(key)}\s*$", ai_text)) != 1:
            failures.append(f"organization action AI registry is not exactly once: {key}")

    if failures:
        print("s4_structural_audit: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        f"s4_structural_audit: PASS ({len(managers)} staged currents; "
        f"{len(ACTIVE_IOS)} active IOs; {len(actions)} AI organization actions)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

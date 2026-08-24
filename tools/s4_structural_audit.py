#!/usr/bin/env python3
"""Regression guard for the advanced structural-audit remediation."""

from __future__ import annotations

import re
from pathlib import Path

from m10_situation_actions import action_key, load_situations, responses

ROOT = Path(__file__).resolve().parents[1]
M10_SITUATIONS = tuple(sorted((ROOT / "in_game/common/situations").glob("antq_m10_*.txt")))
M10_DISASTERS = tuple(sorted((ROOT / "in_game/common/disasters").glob("antq_m10_*.txt")))
S2_SITUATIONS = (ROOT / "in_game/common/situations/antq_s2_germania_dynamics.txt",)
IO_TYPES = ROOT / "in_game/common/international_organizations/00_antiquitas_m9.txt"
IO_START = ROOT / "main_menu/setup/start/15_international_organizations.txt"
M9_ACTION_FILE = ROOT / "in_game/common/generic_actions/antq_m9_organization_actions.txt"
M9_AI_PULSE = ROOT / "in_game/common/on_action/antq_m9_organization_ai_pulse.txt"
M10_AI_PULSE = ROOT / "in_game/common/on_action/antq_m10_situation_ai_pulse.txt"
GERMANIA_AI_PULSE = ROOT / "in_game/common/on_action/antq_s2_germania_ai_pulse.txt"
ARABIA_AI_PULSE = ROOT / "in_game/common/on_action/antq_s2_arabian_route_ai_pulse.txt"
ACTION_FILES = (
    M9_ACTION_FILE,
    ROOT / "in_game/common/generic_actions/antq_s2_germania_actions.txt",
    ROOT / "in_game/common/generic_actions/antq_s2_arabian_route_actions.txt",
)
AI_LIST_ROOT = ROOT / "in_game/common/generic_action_ai_lists"
SITUATION_ACTION_FILE = ROOT / "in_game/common/generic_actions/antq_m10_situation_actions.txt"
SITUATION_PANEL_ROOT = ROOT / "in_game/gui/panels/situation"
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


def nested_block(text: str, label: str) -> str:
    """Return the first balanced named script block, or an empty string."""
    match = re.search(rf"(?m)^\s*{re.escape(label)}\s*=\s*\{{", text)
    if not match:
        return ""
    depth = 0
    for index in range(match.end() - 1, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[match.start(): index + 1]
    return ""


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

    situation_managers: dict[str, str] = {}
    for path in (*M10_SITUATIONS, *S2_SITUATIONS):
        situation_managers.update(blocks(path.read_text(encoding="utf-8-sig"), "antq_"))
    try:
        situation_actions = SITUATION_ACTION_FILE.read_text(encoding="utf-8-sig")
    except OSError:
        situation_actions = ""
        failures.append("missing generated ancient situation actions")
    situation_action_blocks = blocks(situation_actions, "antq_")
    ai_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in AI_LIST_ROOT.glob("*.txt"))
    authored_responses = {
        record.key: tuple(action_key(record, response) for response in responses(record))
        for record in load_situations()
    }
    for key in situation_managers:
        panel = SITUATION_PANEL_ROOT / f"{key}.gui"
        if not panel.is_file():
            failures.append(f"situation {key} lacks its readable panel layout")
        else:
            panel_text = panel.read_text(encoding="utf-8-sig")
            for token in ("TooltipRequirementsList", f"{key}_tooltip", f"{key}_resolution_progress", "situation_disaster_progressbar_with_thresholds"):
                if token not in panel_text:
                    failures.append(f"situation {key} panel lacks {token}")
        presentation = (
            "tooltip = {",
            f'custom_tooltip = "{key}_tooltip"',
            "is_data_map = yes",
            "map_color = {",
            "value = owner.country_color",
            "legend_key = {",
            f'desc = "{key}_legend"',
            "color = define:NMapColors|MAP_COLOR_HIGH",
        )
        for token in presentation:
            if token not in situation_managers[key]:
                failures.append(f"situation {key} lacks panel/map presentation token: {token}")
        progress = f"{key}_resolution_progress"
        actions = authored_responses.get(key, ())
        if len(actions) != 3:
            failures.append(
                f"situation {key} has {len(actions)} authored actions instead of three"
            )
        for action in actions:
            action_block = situation_action_blocks.get(action, "")
            required = (
                f"{action} = {{",
                "type = situation",
                f"situation:{key} = this",
                f"name = {progress}",
            )
            for token in required:
                if token not in action_block:
                    failures.append(f"situation action {action} lacks {token}")
            for forbidden in (
                "ai_tick", "automation_tick", "ai_prerequisite",
                "ai_will_do", "ai_interaction_source_list",
            ):
                if forbidden in action_block:
                    failures.append(
                        f"situation action {action} exposes unsafe generic-action AI token: {forbidden}"
                    )
            registry_path_count = len(
                re.findall(rf"(?m)^\s*{re.escape(action)}\s*$", ai_text)
            )
            if registry_path_count != 1:
                failures.append(
                    "situation action AI candidate index is not exactly once "
                    f"(found {registry_path_count}): {action}"
                )

    m10_pulse = M10_AI_PULSE.read_text(encoding="utf-8-sig")
    expected_response_count = sum(len(actions) for actions in authored_responses.values())
    if m10_pulse.count("\t\tif = {") != expected_response_count:
        failures.append(
            "safe M10 situation AI pulse does not contain one branch per authored response"
        )
    for token in (
        "antq_m10_situation_ai_pulse = {", "is_ai = yes", "gold >= 80",
        "situation_is_active = yes", "_ai_cooldown", "years = 2",
    ):
        if token not in m10_pulse:
            failures.append(f"safe M10 situation AI pulse lacks {token}")
    for key, actions in authored_responses.items():
        for action in actions:
            if f"name = {action}_ai_cooldown" not in m10_pulse:
                failures.append(f"safe M10 situation AI pulse lacks cooldown for {action}")

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
            for forbidden in (
                "ai_tick", "automation_tick", "ai_prerequisite",
                "ai_will_do", "ai_interaction_source_list",
            ):
                if forbidden in block:
                    failures.append(
                        f"organization action {key} exposes unsafe generic-action AI token: {forbidden}"
                    )
            if "add_opinion" in block:
                target_allow = nested_block(nested_block(block, "allow"), "scope:target")
                if "this != scope:actor" not in target_allow:
                    failures.append(f"organization action {key} permits an AI self-target")
                target_effect = nested_block(nested_block(block, "effect"), "scope:target")
                if "limit = { this != scope:actor }" not in target_effect:
                    failures.append(f"organization action {key} can execute a self-target effect")
    for key in actions:
        if len(re.findall(rf"(?m)^\s*{re.escape(key)}\s*$", ai_text)) != 1:
            failures.append(f"organization action AI registry is not exactly once: {key}")

    m9_pulse = M9_AI_PULSE.read_text(encoding="utf-8-sig")
    for token in (
        "antq_m9_organization_ai_pulse = {", "is_ai = yes",
        "tag = XAR", "current_month = 3", "tag = XCI", "current_month = 9",
        "gold >= 80", "antq_m9_han_tribute_cooldown",
        "antq_m9_kangju_council_cooldown", "years = 3",
        "international_organization:antq_han_tributary_system = {",
        "international_organization:antq_kangju_confederation = {",
    ):
        if token not in m9_pulse:
            failures.append(f"safe M9 organization AI pulse lacks {token}")

    for pulse_path, pulse_key, branch_count, cooldown_years in (
        (GERMANIA_AI_PULSE, "antq_s2_germania_ai_pulse", 12, 5),
        (ARABIA_AI_PULSE, "antq_s2_arabian_route_ai_pulse", 4, 3),
    ):
        pulse = pulse_path.read_text(encoding="utf-8-sig")
        if pulse.count("\t\tif = {") != branch_count:
            failures.append(f"{pulse_key} branch inventory mismatch")
        for token in (
            f"{pulse_key} = {{", "is_ai = yes", "gold >= 80",
            "random_international_organization_member = {", "this != scope:",
            "_ai_cooldown", f"years = {cooldown_years}",
        ):
            if token not in pulse:
                failures.append(f"safe organization AI pulse {pulse_key} lacks {token}")

    if failures:
        print("s4_structural_audit: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        f"s4_structural_audit: PASS ({len(managers)} staged currents; "
        f"{len(ACTIVE_IOS)} active IOs; {len(actions)} registered organization actions)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

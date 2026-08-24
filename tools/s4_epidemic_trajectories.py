#!/usr/bin/env python3
"""Prove that major epidemic currents drive native mortality and material loss."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SECOND_EVENTS = ROOT / "in_game/events/antq_m10_second_century.txt"
THIRD_EVENTS = ROOT / "in_game/events/antq_m10_third_century.txt"
SECOND_DISASTERS = ROOT / "in_game/common/disasters/antq_m10_second_century.txt"
THIRD_DISASTERS = ROOT / "in_game/common/disasters/antq_m10_third_century.txt"
CONFIG = ROOT / "config/local_paths.json"


def block(text: str, key: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*\{{", text)
    if not match:
        raise ValueError(f"missing definition {key}")
    depth = 0
    quoted = False
    escaped = False
    for index in range(match.end() - 1, len(text)):
        char = text[index]
        if escaped:
            escaped = False
        elif quoted and char == "\\":
            escaped = True
        elif char == '"':
            quoted = not quoted
        elif not quoted and char == "{":
            depth += 1
        elif not quoted and char == "}":
            depth -= 1
            if depth == 0:
                return text[match.start(): index + 1]
    raise ValueError(f"unclosed definition {key}")


def main() -> int:
    failures: list[str] = []
    second_events = SECOND_EVENTS.read_text(encoding="utf-8-sig")
    third_events = THIRD_EVENTS.read_text(encoding="utf-8-sig")
    antonine_event = block(second_events, "antq_m10_second.2013")
    crisis_event = block(third_events, "antq_m10_third.3005")
    cyprian_event = block(third_events, "antq_m10_third.3008")

    anchors = (
        (antonine_event, "location:antioch", "value = 0.35"),
        (antonine_event, "location:luoyang", "value = 0.20"),
        (cyprian_event, "location:tunis", "value = 0.30"),
    )
    for event, location, strength in anchors:
        for token in (location, "spawn_disease = {", "disease = disease:smallpox", strength):
            if token not in event:
                failures.append(f"epidemic anchor {location} lacks {token}")
    for label, event in (("Antonine", antonine_event), ("Cyprian", cyprian_event)):
        for token in (
            "add_manpower = { value =",
            "add_gold = { value =",
            "change_province_food_percentage",
        ):
            if token not in event:
                failures.append(f"{label} opening event lacks material effect {token}")
        if "original_outbreak" in event or "every_country" in event or "every_location" in event:
            failures.append(f"{label} event depends on an existing or deterministic global outbreak")
    if "spawn_disease" in crisis_event or "set_disease_presence" in crisis_event:
        failures.append("generic third-century crisis still injects a disease outbreak")

    disasters = (
        (
            "Antonine",
            block(SECOND_DISASTERS.read_text(encoding="utf-8-sig"), "antq_m10_second_antonine_plague"),
        ),
        (
            "Cyprian",
            block(THIRD_DISASTERS.read_text(encoding="utf-8-sig"), "antq_m10_third_cyprian_plague"),
        ),
    )
    for label, disaster in disasters:
        for token in (
            "global_population_growth = -0.003",
            "global_manpower_modifier = -0.12",
            "global_monthly_food_modifier = -0.10",
            "tax_income_efficiency = small_tax_income_efficiency_penalty",
            "add_manpower = { value = monthly_manpower multiply = -0.5 }",
            "add_gold = { value = monthly_income_trade_and_tax multiply = -0.25 }",
            "change_province_food_percentage = -0.01",
            "_resolution_progress >= 100",
            "remove_variable = antq_",
        ):
            if token not in disaster:
                failures.append(f"{label} trajectory lacks {token}")
        if disaster.count("current_date >=") != 2:
            failures.append(f"{label} trajectory does not retain one start and one safety-bound date")

    game_dir = Path(json.loads(CONFIG.read_text(encoding="utf-8-sig"))["game_dir"])
    installed_disease_root = game_dir / "game/in_game/common/diseases"
    mod_disease_root = ROOT / "in_game/common/diseases"
    readme = (installed_disease_root / "readme.txt").read_text(encoding="utf-8-sig")
    smallpox = (mod_disease_root / "smallpox.txt").read_text(encoding="utf-8-sig")
    for token in (
        "pop deaths",
        "mortality_rate:",
        "percentage_to_meet_their_fate_on_calc",
        "location_spread_threshold",
    ):
        if token not in readme:
            failures.append(f"installed disease contract lacks {token}")
    for token in (
        "percentage_to_meet_their_fate_on_calc = {",
        "mortality_rate = {",
        "location_spread_threshold = {",
        "on_spread_to_country = {",
        'value = "distance_to_squared(scope:disease.origin)"',
        "sub_unit_stagnation_chance = { value = 0.65 }",
    ):
        if token not in smallpox:
            failures.append(f"mod smallpox proxy lacks {token}")
    for path in sorted(mod_disease_root.glob("*.txt")):
        if path.stem == "malaria":
            continue
        epidemic = path.read_text(encoding="utf-8-sig")
        if epidemic.count('value = "distance_to_squared(scope:disease.origin)"') != 2:
            failures.append(f"{path.name} does not distance-bound both outbreak phases")
        for token in (
            "location_rank ?= location_rank:rural_settlement",
            "num_roads = 0",
            "sub_unit_stagnation_chance = { value = 0.65 }",
        ):
            if token not in epidemic:
                failures.append(f"{path.name} lacks ancient-mobility bound {token}")

    if failures:
        print("s4_epidemic_trajectories: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s4_epidemic_trajectories: PASS "
        "(3 bounded outbreak anchors; native mortality/spread; 2 material trajectories)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

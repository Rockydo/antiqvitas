#!/usr/bin/env python3
"""Audit the Round 7 Teutoburg campaign gate and counterfactual paths."""

from __future__ import annotations

import argparse
import csv
import io
from dataclasses import dataclass
from pathlib import Path

import m10_history


ROOT = Path(__file__).resolve().parents[1]
TRIGGER = ROOT / "in_game/common/scripted_triggers/antq_s7_teutoburg.txt"
M10_EVENTS = ROOT / "in_game/events/antq_m10_first_century.txt"
M11_EVENTS = ROOT / "in_game/events/antq_m11_flavor_phases.txt"
BOOTSTRAP = ROOT / "in_game/common/on_action/antq_m6_character_bootstrap.txt"
CSV_OUTPUT = ROOT / "docs/m10/teutoburg_scenario_matrix.csv"
REPORT_OUTPUT = ROOT / "docs/m10/TEUTOBURG_FRONTIER_CHAIN.md"


@dataclass(frozen=True)
class Scenario:
    name: str
    varus: bool
    eligible_actor_exists: bool
    eligible_war: bool
    other_war: bool = False
    truce_or_alliance: bool = False
    east_rhine_ownership: bool = False
    roman_controlled_germania: bool = False
    battle_already_resolved: bool = False
    policy_already_resolved: bool = False
    expected_battle: bool = False
    expected_policy: bool = True
    note: str = ""


SCENARIOS = (
    Scenario("Rome at peace", True, True, False, expected_battle=False, expected_policy=True, note="Peace cannot manufacture a battle."),
    Scenario("Eligible Germanic war", True, True, True, expected_battle=True, expected_policy=False, note="The campaign may culminate from 9.8.8."),
    Scenario("War elsewhere", True, True, False, other_war=True, expected_battle=False, expected_policy=True, note="An unrelated war is insufficient."),
    Scenario("Frontier truce or alliance", True, True, False, truce_or_alliance=True, expected_battle=False, expected_policy=True, note="Diplomatic contact is not combat."),
    Scenario("East-of-Rhine occupation", True, True, False, east_rhine_ownership=True, expected_battle=False, expected_policy=True, note="Ownership alone cannot fire a battle."),
    Scenario("Conquered Germania at peace", True, False, False, roman_controlled_germania=True, expected_battle=False, expected_policy=True, note="Annexation removes the eligible opponent and suppresses the battle."),
    Scenario("Varus dead or missing", False, True, True, expected_battle=False, expected_policy=True, note="Invalid character scope falls back safely."),
    Scenario("Germanic actors missing", True, False, False, expected_battle=False, expected_policy=True, note="No surviving eligible opponent means no battle."),
    Scenario("AI Rome in eligible war", True, True, True, expected_battle=True, expected_policy=False, note="The trigger does not distinguish AI and player."),
    Scenario("Player Rome in eligible war", True, True, True, expected_battle=True, expected_policy=False, note="The player receives the same contingent choices."),
    Scenario("Save reload before battle", True, True, True, expected_battle=True, expected_policy=False, note="Country and character variables persist across saves."),
    Scenario("Save reload after battle", True, True, True, battle_already_resolved=True, expected_battle=False, expected_policy=False, note="The resolved variable prevents duplicate battle and policy events."),
    Scenario("Save reload after policy", True, True, False, policy_already_resolved=True, expected_battle=False, expected_policy=False, note="The policy-resolved variable prevents duplicate fallback events."),
)


def evaluate(scenario: Scenario) -> tuple[bool, bool]:
    campaign_ready = scenario.varus and scenario.eligible_actor_exists and scenario.eligible_war
    battle = campaign_ready and not scenario.battle_already_resolved
    policy = (
        not scenario.battle_already_resolved
        and not scenario.policy_already_resolved
        and not battle
    )
    return battle, policy


def rows() -> tuple[dict[str, str], ...]:
    result: list[dict[str, str]] = []
    for scenario in SCENARIOS:
        battle, policy = evaluate(scenario)
        result.append({
            "scenario": scenario.name,
            "living_varus": str(scenario.varus).lower(),
            "eligible_actor_exists": str(scenario.eligible_actor_exists).lower(),
            "eligible_war": str(scenario.eligible_war).lower(),
            "unrelated_war": str(scenario.other_war).lower(),
            "truce_or_alliance": str(scenario.truce_or_alliance).lower(),
            "east_rhine_ownership": str(scenario.east_rhine_ownership).lower(),
            "conquered_germania": str(scenario.roman_controlled_germania).lower(),
            "battle_already_resolved": str(scenario.battle_already_resolved).lower(),
            "policy_already_resolved": str(scenario.policy_already_resolved).lower(),
            "battle_fires": str(battle).lower(),
            "policy_fires": str(policy).lower(),
            "expected_battle": str(scenario.expected_battle).lower(),
            "expected_policy": str(scenario.expected_policy).lower(),
            "result": "PASS" if (battle, policy) == (scenario.expected_battle, scenario.expected_policy) else "FAIL",
            "note": scenario.note,
        })
    return tuple(result)


def csv_text(data: tuple[dict[str, str], ...]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=tuple(data[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(data)
    return buffer.getvalue()


def report(data: tuple[dict[str, str], ...]) -> str:
    opponents = ", ".join(m10_history.TEUTOBURG_OPPONENTS)
    return f"""# Conditional Teutoburg frontier chain

Static result: **PASS** ({len(data)} reviewed scenarios; zero modeled phantom battles or duplicate resolutions).

The AD 9 defeat is no longer an unconditional calendar event. Its battle window begins on 9.8.8 and requires a living Varus reference plus a real Roman war with one of the reviewed Germanic frontier polities: {opponents}. Peace, unrelated wars, truces, alliances, east-of-Rhine ownership, or conquered Germania do not substitute for that war.

If the qualifying campaign never occurs, the sourced window expires without a defeat. Rome instead receives *The Germania Frontier Policy* in the following derived window, with consolidation, continued forward occupation, and negotiated-compacts choices. This fallback never declares a battle or silently starts a war.

Preparation, pressure, and contested-corridor phase notices share the same campaign trigger. The first qualifying opponent is persisted as a participant scope; the battle choices apply different manpower, treasury, war-exhaustion, tradition, and opponent consequences rather than cosmetic prestige variants. The aftermath requires the persisted battle-resolution variable. The living Varus scope, opponent scope, active-chain marker, battle resolution, aftermath marker, and policy resolution are country variables, providing save/reload continuity and one-shot suppression.

This is a structural scenario proof, not runtime completion. Fresh player and observer/AI runs must still verify event timing, character survival, war scopes, annexations, deaths, choice effects, and save/reload behavior in the engine.
"""


def validate(data: tuple[dict[str, str], ...]) -> None:
    failures = [row["scenario"] for row in data if row["result"] != "PASS"]
    if failures:
        raise ValueError(f"scenario expectations failed: {failures}")
    trigger = TRIGGER.read_text(encoding="utf-8-sig")
    m10 = M10_EVENTS.read_text(encoding="utf-8-sig")
    m11 = M11_EVENTS.read_text(encoding="utf-8-sig")
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8-sig")
    mapped = m10_history.engine_tags()
    for design_tag in m10_history.TEUTOBURG_OPPONENTS:
        engine_tag = mapped[design_tag]
        for token in (f"country_exists = c:{engine_tag}", f"is_at_war_with = c:{engine_tag}"):
            if trigger.count(token) != 1:
                raise ValueError(f"campaign trigger does not contain exactly one {token!r}")
    for token in (
        "trigger_if = {",
        "limit = { has_variable = antq_teutoburg_varus }",
        "var:antq_teutoburg_varus = { is_alive = yes }",
        "trigger_else = { always = no }",
        "from = 9.8.8",
        "antq_teutoburg_campaign_ready_trigger = yes",
        "set_variable = antq_teutoburg_battle_resolved",
        "antq_m10.1099",
        "NOT = { has_variable = antq_teutoburg_battle_resolved }",
        "set_variable = antq_teutoburg_policy_resolved",
        "set_variable = { name = antq_teutoburg_opponent value = scope:antq_teutoburg_selected_opponent }",
        "var:antq_teutoburg_opponent ?= {",
        "add_war_exhaustion = war_exhaustion_severe_bonus",
        "add_army_tradition = army_tradition_mild_bonus",
        f"remove_character_modifier = {m10_history.TEUTOBURG_LIFESPAN_GUARD}",
        "save_scope_as = antq_teutoburg_departing_varus",
        "kill_character_silently = scope:antq_teutoburg_departing_varus",
        "remove_variable = antq_teutoburg_varus",
    ):
        if token not in trigger + m10:
            raise ValueError(f"Teutoburg contract lost {token!r}")
    if m11.count("antq_teutoburg_campaign_ready_trigger = yes") != 3:
        raise ValueError("exactly three pre-battle Teutoburg phases must share the campaign gate")
    if m11.count("\n\t\thas_variable = antq_teutoburg_battle_resolved\n") != 1:
        raise ValueError("the Teutoburg aftermath must uniquely require positive battle resolution")
    if m11.count("NOT = { has_variable = antq_teutoburg_battle_resolved }") != 3:
        raise ValueError("all three pre-battle Teutoburg phases must suppress resolved battles")
    for token in (
        "first_name = antq_publius_quinctilius_varus",
        "age = { 40 55 }",
        "save_scope_as = antq_m6_living_publius_quinctilius_varus",
        "set_variable = { name = antq_teutoburg_varus value = scope:antq_m6_living_publius_quinctilius_varus }",
    ):
        if token not in bootstrap:
            raise ValueError(f"Varus bootstrap lost {token!r}")
    guard_anchor = (
        "scope:antq_m6_living_publius_quinctilius_varus = {\n"
        "\t\t\t\tadd_character_modifier = { modifier = "
        f"{m10_history.TEUTOBURG_LIFESPAN_GUARD} years = -1"
    )
    if guard_anchor not in bootstrap:
        raise ValueError("Varus lacks sourced lifespan protection through AD 9")
    if trigger.startswith(
        "antq_teutoburg_campaign_ready_trigger = {\n\thas_variable"
    ):
        raise ValueError("Varus readiness dereferences outside a conditional trigger")


def outputs(data: tuple[dict[str, str], ...]) -> dict[Path, str]:
    return {CSV_OUTPUT: csv_text(data), REPORT_OUTPUT: report(data)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    data = rows()
    validate(data)
    rendered = outputs(data)
    if args.write:
        for path, content in rendered.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8-sig", newline="\n")
    else:
        stale = [path for path, content in rendered.items() if not path.is_file() or path.read_text(encoding="utf-8-sig") != content]
        if stale:
            raise ValueError(f"stale Teutoburg audit outputs: {[str(path.relative_to(ROOT)) for path in stale]}")
    print(f"s7_teutoburg_scenarios: PASS ({len(data)} scenarios; contingent battle and policy fallback)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

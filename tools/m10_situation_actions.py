#!/usr/bin/env python3
"""Render distinct, visible response surfaces for every ancient situation."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, replace
from pathlib import Path

from dates import M2_MIRROR_LANGUAGES


ROOT = Path(__file__).resolve().parents[1]
SITUATION_FILES = tuple(sorted((ROOT / "in_game/common/situations").glob("antq_m10_*.txt"))) + (
    ROOT / "in_game/common/situations/antq_s2_germania_dynamics.txt",
)
ACTION_OUTPUT = ROOT / "in_game/common/generic_actions/antq_m10_situation_actions.txt"
AI_LIST_OUTPUT = ROOT / "in_game/common/generic_action_ai_lists/antq_m10_situation_actions_list.txt"
AI_PULSE_OUTPUT = ROOT / "in_game/common/on_action/antq_m10_situation_ai_pulse.txt"
LOC_ROOT = ROOT / "main_menu/localization"
LANGUAGES = ("english", *M2_MIRROR_LANGUAGES)
EXPECTED_SITUATIONS = 43
AI_TREASURY_RESERVE = 80


@dataclass(frozen=True)
class Situation:
    key: str
    anchor: str
    theme: str
    actors: tuple[str, ...]
    label: str

    @property
    def progress(self) -> str:
        return f"{self.key}_resolution_progress"


@dataclass(frozen=True)
class Response:
    key: str
    title: str
    description: str
    cost: int
    progress: int
    stability: str | None = None
    prestige: str | None = None
    legitimacy: str | None = None
    manpower_months: float = 0


THEME_RESPONSES: dict[str, tuple[Response, ...]] = {
    "diplomacy": (
        Response("embassy", "Exchange Embassies and Hostages", "Bind the rival courts to a public diplomatic process.", 14, 14, stability="stability_weak_bonus"),
        Response("client", "Subsidize a Client Settlement", "Spend reserves to make a durable compromise attractive to every claimant.", 26, 25, legitimacy="legitimacy_mild_bonus"),
        Response("ultimatum", "Back the Ultimatum with Troops", "Concentrate troops behind the negotiations and accept the domestic strain of coercion.", 22, 32, stability="stability_weak_penalty", manpower_months=1.0),
    ),
    "rebellion": (
        Response("amnesty", "Proclaim a Conditional Amnesty", "Separate negotiable communities from irreconcilable leaders through pardons and guarantees.", 12, 13, stability="stability_weak_bonus"),
        Response("redress", "Redress Levies and Local Abuses", "Fund restitution, replace compromised officials, and address the grievances feeding resistance.", 24, 24, prestige="prestige_mild_penalty"),
        Response("suppression", "Concentrate the Field Army", "Force a rapid decision with a costly concentration of soldiers and supplies.", 20, 33, stability="stability_weak_penalty", manpower_months=1.5),
    ),
    "campaign": (
        Response("depots", "Establish Forward Supply Depots", "Build the transport and provisioning network needed to sustain operations.", 18, 17),
        Response("allies", "Bind the Border Allies", "Use payments, honors, and guarantees to bring local powers into the campaign system.", 25, 24, legitimacy="legitimacy_mild_bonus"),
        Response("offensive", "Order a Decisive Offensive", "Risk manpower and internal calm to seek a military decision before the enemy can recover.", 28, 34, stability="stability_weak_penalty", manpower_months=2.0),
    ),
    "migration": (
        Response("settlement", "Survey Lands for Settlement", "Identify defensible land and distribute newcomers without dissolving local obligations.", 20, 23, stability="stability_weak_bonus"),
        Response("provisions", "Issue Grain and Travel Provisions", "Keep migrating communities supplied while negotiators establish terms.", 15, 16),
        Response("barrier", "Fortify the Crossing Points", "Channel movement with fortified corridors, patrols, and a costly show of force.", 25, 31, stability="stability_weak_penalty", manpower_months=1.0),
    ),
    "civil_war": (
        Response("conference", "Convene the Rival Courts", "Offer guarantees and a neutral conference before political rivalry becomes irreversible.", 17, 17, stability="stability_weak_bonus"),
        Response("recognition", "Recognize a Constitutional Settlement", "Spend authority and wealth to assemble a workable coalition around one settlement.", 25, 25, legitimacy="legitimacy_mild_bonus"),
        Response("army", "Secure the Armies' Allegiance", "Commit pay, reinforcements, and political capital to force a swift conclusion.", 30, 34, stability="stability_weak_penalty", manpower_months=1.5),
    ),
    "statecraft": (
        Response("census", "Commission a Census and Survey", "Give administrators the information needed to turn ambition into durable institutions.", 18, 18),
        Response("compact", "Forge an Elite Compact", "Distribute honors and offices to bind regional elites to the new order.", 24, 25, legitimacy="legitimacy_mild_bonus"),
        Response("decree", "Impose the New Order by Decree", "Accelerate institutional change at the price of disruption and resistance.", 27, 32, stability="stability_weak_penalty"),
    ),
    "exchange": (
        Response("patronage", "Endow Scholars and Sanctuaries", "Sponsor the people and institutions carrying ideas across political frontiers.", 19, 20, prestige="prestige_mild_bonus"),
        Response("routes", "Protect Pilgrims and Caravans", "Fund escorts, hostels, and safe-conducts along the routes of exchange.", 15, 17, stability="stability_weak_bonus"),
        Response("court", "Admit the New Learning at Court", "Commit the ruling elite to the movement and absorb the resulting controversy.", 25, 30, legitimacy="legitimacy_mild_bonus", stability="stability_weak_penalty"),
    ),
    "frontier": (
        Response("envoys", "Summon a Frontier Congress", "Bring chiefs, governors, and merchants together to settle obligations and boundaries.", 15, 16, stability="stability_weak_bonus"),
        Response("subsidies", "Renew Gifts and Subsidies", "Purchase time and cooperation with regular payments to frontier partners.", 23, 24, prestige="prestige_mild_penalty"),
        Response("garrisons", "Reinforce the Frontier Garrisons", "Spend manpower and treasure to impose order from defended strongpoints.", 24, 32, stability="stability_weak_penalty", manpower_months=1.0),
    ),
}


THEME_BY_KEY = {
    "antq_m10_gaius_eastern_settlement": "diplomacy",
    "antq_m10_armenian_war": "diplomacy",
    "antq_m10_second_trajan_parthia": "diplomacy",
    "antq_m10_second_verus_parthia": "diplomacy",
    "antq_m10_fourth_shapur_julian": "diplomacy",
    "antq_m10_batavian_revolt": "rebellion",
    "antq_m10_boudica_revolt": "rebellion",
    "antq_m10_great_jewish_revolt": "rebellion",
    "antq_m10_illyrian_revolt": "rebellion",
    "antq_m10_mauretania_annexation": "rebellion",
    "antq_m10_second_bar_kokhba": "rebellion",
    "antq_m10_second_yellow_turbans": "rebellion",
    "antq_m10_tacfarinas_war": "rebellion",
    "antq_m10_trung_sisters": "rebellion",
    "antq_m10_wang_mang_xin": "rebellion",
    "antq_m10_claudian_britain": "campaign",
    "antq_m10_dacian_wars": "campaign",
    "antq_m10_final_attila": "campaign",
    "antq_m10_final_hephthalites": "campaign",
    "antq_m10_final_radagaisus_rhine": "campaign",
    "antq_m10_final_vandal_africa": "campaign",
    "antq_m10_fourth_aksum_meroe": "campaign",
    "antq_m10_fourth_fei_river": "campaign",
    "antq_m10_han_xianbei": "campaign",
    "antq_m10_immensum_bellum": "campaign",
    "antq_m10_second_marcomannic_wars": "campaign",
    "antq_m10_second_trajan_dacia": "campaign",
    "antq_m10_final_adventus_saxonum": "migration",
    "antq_m10_final_britain_abandoned": "migration",
    "antq_m10_fourth_gothic_refugees": "migration",
    "antq_m10_second_gothic_migration": "migration",
    "antq_m10_fourth_constantine_civil_wars": "civil_war",
    "antq_m10_second_five_emperors": "civil_war",
    "antq_m10_third_eight_princes": "civil_war",
    "antq_m10_third_three_kingdoms": "civil_war",
    "antq_m10_fourth_gwanggaeto": "statecraft",
    "antq_m10_second_kanishka_apogee": "statecraft",
    "antq_m10_third_diocletian_dominate": "statecraft",
    "antq_s2_alemannic_formation": "statecraft",
    "antq_s2_frankish_formation": "statecraft",
    "antq_m10_fourth_faxian_gupta": "exchange",
    "antq_s2_aestian_amber_shore": "exchange",
    "antq_s2_maroboduus_rivalry": "frontier",
}


ACTOR_OVERRIDES = {
    # Rome, Armenia, and Parthia were all principals. Rome must not receive an
    # inert panel owned only by the Armenian anchor.
    "antq_m10_gaius_eastern_settlement": ("XAA", "XAO", "XAH"),
    "antq_m10_armenian_war": ("XAA", "XAO", "XAH"),
    "antq_m10_fourth_shapur_julian": ("XAA", "XAH"),
    "antq_m10_second_trajan_parthia": ("XAA", "XAH"),
    "antq_m10_second_verus_parthia": ("XAA", "XAH"),
    "antq_m10_batavian_revolt": ("BTV", "XAA"),
    "antq_m10_boudica_revolt": ("XBX", "XAA"),
    "antq_m10_great_jewish_revolt": ("JUD", "XAA"),
    "antq_m10_mauretania_annexation": ("MAU", "XAA"),
    "antq_m10_claudian_britain": ("XAA", "XBX"),
}


def localized_situation_labels() -> dict[str, str]:
    labels: dict[str, str] = {}
    pattern = re.compile(r'^\s*(antq_(?:m10|s2)_[a-z0-9_]+):\s*"([^"]+)"')
    for path in sorted((LOC_ROOT / "english").glob("*.yml")):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = pattern.match(line)
            if match:
                labels[match.group(1)] = match.group(2)
    return labels


def block_at(text: str, open_brace: int) -> str:
    depth = 0
    for index, char in enumerate(text[open_brace:], open_brace):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace:index + 1]
    raise ValueError("unterminated Paradox block")


def load_situations() -> tuple[Situation, ...]:
    records: list[Situation] = []
    labels = localized_situation_labels()
    for path in SITUATION_FILES:
        if not path.is_file():
            raise ValueError(f"missing situation source: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8-sig")
        for match in re.finditer(r"(?m)^(antq_(?:m10|s2)_[a-z0-9_]+)\s*=\s*\{", text):
            key = match.group(1)
            block = block_at(text, match.end() - 1)
            content = re.search(r"\bcontent_trigger\s*=\s*\{(.*?)\}", block, re.S)
            if content is None:
                raise ValueError(f"{key} has no content trigger")
            anchor = re.search(r"\btag\s*=\s*([A-Z0-9]{3})\b", content.group(1))
            if anchor is None:
                raise ValueError(f"{key} has no exact anchor tag")
            theme = THEME_BY_KEY.get(key)
            if theme is None:
                raise ValueError(f"ancient situation has no authored response theme: {key}")
            label = labels.get(key)
            if not label:
                raise ValueError(f"ancient situation has no player-facing label: {key}")
            anchor_tag = anchor.group(1)
            records.append(Situation(
                key, anchor_tag, theme, ACTOR_OVERRIDES.get(key, (anchor_tag,)), label
            ))
    records.sort(key=lambda item: item.key)
    if len(records) != EXPECTED_SITUATIONS:
        raise ValueError(f"ancient situation inventory is {len(records)}, expected {EXPECTED_SITUATIONS}")
    if len({record.key for record in records}) != len(records):
        raise ValueError("ancient situation inventory has duplicate keys")
    return tuple(records)


def responses(record: Situation) -> tuple[Response, ...]:
    rank = sorted(THEME_BY_KEY).index(record.key)
    extras = (
        {"legitimacy": "legitimacy_weak_bonus"},
        {"prestige": "prestige_weak_bonus"},
        {"stability": "stability_weak_bonus"},
        {"manpower_months": 0.5},
    )[rank % 4]
    authored = {
        "embassy": (
            f"Open a witnessed embassy and hostage exchange for {record.label}",
            f"Name envoys, hostages, and a public timetable so {record.label} becomes a negotiated process rather than a rumor of force.",
        ),
        "client": (
            f"Fund a client compact in {record.label}",
            f"Spend reserves to make a durable compromise attractive to every claimant involved in {record.label}.",
        ),
        "ultimatum": (
            f"Back the ultimatum in {record.label}",
            f"Concentrate troops behind the talks and accept the domestic strain of coercing a settlement of {record.label}.",
        ),
        "amnesty": (
            f"Proclaim a conditional amnesty in {record.label}",
            f"Separate negotiable communities from irreconcilable leaders during {record.label} through pardons and guarantees.",
        ),
        "redress": (
            f"Redress levies and abuses behind {record.label}",
            f"Fund restitution and replace compromised officials so the grievances feeding {record.label} lose their local fuel.",
        ),
        "suppression": (
            f"Concentrate the field army for {record.label}",
            f"Force a rapid military decision in {record.label} with a costly concentration of soldiers and supplies.",
        ),
        "depots": (
            f"Establish forward depots for {record.label}",
            f"Build the transport and provisioning network needed to sustain operations throughout {record.label}.",
        ),
        "allies": (
            f"Bind the border allies of {record.label}",
            f"Use payments, honors, and guarantees to bring local powers into the campaign system of {record.label}.",
        ),
        "offensive": (
            f"Order a decisive offensive in {record.label}",
            f"Risk manpower and internal calm to seek a military decision in {record.label} before the enemy recovers.",
        ),
        "settlement": (
            f"Survey lands for the people of {record.label}",
            f"Identify defensible land and distribute newcomers of {record.label} without dissolving local obligations.",
        ),
        "provisions": (
            f"Issue grain and travel stores for {record.label}",
            f"Keep the communities moving through {record.label} supplied while negotiators establish terms.",
        ),
        "barrier": (
            f"Fortify the crossings of {record.label}",
            f"Channel movement in {record.label} with fortified corridors, patrols, and a costly show of force.",
        ),
        "conference": (
            f"Convene the rival courts of {record.label}",
            f"Offer guarantees and a neutral conference before {record.label} becomes an irreversible civil rupture.",
        ),
        "recognition": (
            f"Recognize a constitutional settlement of {record.label}",
            f"Spend authority and wealth to assemble a workable coalition around one settlement of {record.label}.",
        ),
        "army": (
            f"Secure army allegiance in {record.label}",
            f"Commit pay, reinforcements, and political capital to force a swift conclusion of {record.label}.",
        ),
        "census": (
            f"Commission a census for {record.label}",
            f"Give administrators the household, land, and office information needed to make {record.label} durable.",
        ),
        "compact": (
            f"Forge an elite compact around {record.label}",
            f"Distribute honors and offices to bind regional elites to the new order of {record.label}.",
        ),
        "decree": (
            f"Impose {record.label} by decree",
            f"Accelerate institutional change in {record.label} at the price of disruption and resistance.",
        ),
        "patronage": (
            f"Endow the carriers of {record.label}",
            f"Sponsor the scholars, sanctuaries, and workshops carrying {record.label} across political frontiers.",
        ),
        "routes": (
            f"Protect the routes of {record.label}",
            f"Fund escorts, hostels, and safe-conducts along the roads and sea-lanes of {record.label}.",
        ),
        "court": (
            f"Admit {record.label} at court",
            f"Commit the ruling elite to {record.label} and absorb the controversy of a public court adoption.",
        ),
        "envoys": (
            f"Summon a frontier congress for {record.label}",
            f"Bring chiefs, governors, and merchants together to settle obligations opened by {record.label}.",
        ),
        "subsidies": (
            f"Renew gifts along {record.label}",
            f"Purchase time and cooperation with regular payments to the frontier partners of {record.label}.",
        ),
        "garrisons": (
            f"Reinforce garrisons during {record.label}",
            f"Spend manpower and treasure to impose order from defended strongpoints throughout {record.label}.",
        ),
    }
    tuned: list[Response] = []
    for offset, response in enumerate(THEME_RESPONSES[record.theme]):
        title, description = authored[response.key]
        payload = {
            "title": title,
            "description": description,
            "cost": response.cost + rank,
            "progress": response.progress + (rank % 8) + offset,
        }
        if offset == 1:
            payload.update(extras)
        tuned.append(replace(response, **payload))
    return tuple(tuned)


def action_key(record: Situation, response: Response) -> str:
    return f"{record.key}_{response.key}"


def actor_trigger(record: Situation) -> str:
    if len(record.actors) == 1:
        return f"tag = {record.actors[0]}"
    return "OR = { " + " ".join(f"tag = {tag}" for tag in record.actors) + " }"


def action_block(record: Situation, response: Response) -> str:
    key = action_key(record, response)
    actor = actor_trigger(record)
    country_effects = [f"\t\t\tadd_gold = -{response.cost}"]
    if response.stability:
        country_effects.append(f"\t\t\tadd_stability = {response.stability}")
    if response.prestige:
        country_effects.append(f"\t\t\tadd_prestige = {response.prestige}")
    if response.legitimacy:
        country_effects.append(f"\t\t\tadd_legitimacy = {response.legitimacy}")
    if response.manpower_months:
        country_effects.append(
            "\t\t\tadd_manpower = { value = monthly_manpower "
            f"multiply = -{response.manpower_months:g} }}"
        )
    effects = "\n".join(country_effects)
    return f'''# Generated ancient-current response. The selector keeps this action inside its own situation panel.
{key} = {{
\ttype = situation
\tshow_message = no
\tpotential = {{
\t\t# The engine evaluates situation-action potential once without an actor
\t\t# while building the global action registry.  Use the same optional
\t\t# actor scope contract as the vanilla situation actions so that registry
\t\t# discovery is silent; the country restriction is enforced whenever an
\t\t# actor is present and repeated in the target selector below.
\t\tscope:actor ?= {{
\t\t\t{actor}
\t\t\tcan_see_situation = situation:{record.key}
\t\t}}
\t}}
\tallow = {{
\t\tscope:actor = {{ gold >= {response.cost} }}
\t\tscope:recipient = {{ situation_is_active = yes }}
\t}}
\tcooldown = {{ type = {key} years = 2 }}
\tselect_trigger = {{
\t\tlooking_for_a = situation
\t\tinteraction_source_list = {{
\t\t\tsituation:{record.key} = {{ add_to_list = source }}
\t\t}}
\t\ttarget_flag = recipient
\t\tname = "choose_situation"
\t\tcolumn = {{ data = name }}
\t\tvisible = {{
\t\t\tsituation:{record.key} = this
\t\t\tsituation_is_active = yes
\t\t\tscope:actor = {{ {actor} }}
\t\t}}
\t}}
\teffect = {{
\t\tscope:actor = {{
{effects}
\t\t}}
\t\tscope:recipient = {{ change_variable = {{ name = {record.progress} add = {response.progress} }} }}
\t}}
}}'''


def action_script(records: tuple[Situation, ...]) -> str:
    chunks = [
        "# Generated by tools/m10_situation_actions.py --write.",
        "# Three themed, material, AI-usable responses for each active ancient situation.",
        "",
    ]
    for record in records:
        for response in responses(record):
            chunks.extend((action_block(record, response), ""))
    return "\n".join(chunks)


def ai_list_script(records: tuple[Situation, ...]) -> str:
    chunks = [
        "# Generated by tools/m10_situation_actions.py --write.",
        "# Registry-only lists for player-facing situation actions. Native generic-action",
        "# AI target selection posts invalid commands after situations activate, so AI",
        "# execution is handled by antq_m10_situation_ai_pulse instead.",
        "",
    ]
    for record in records:
        actions = "\n".join(
            f"\t\t{action_key(record, response)}" for response in responses(record)
        )
        chunks.extend((
            f"{record.key}_response_ai_list = {{",
            "\tpotential = { always = no }",
            "\tactions = {",
            actions,
            "\t}",
            "}",
            "",
            ))
    return "\n".join(chunks)


def ai_effect_lines(response: Response, indent: str = "\t\t\t") -> list[str]:
    lines = [f"{indent}add_gold = -{response.cost}"]
    if response.stability:
        lines.append(f"{indent}add_stability = {response.stability}")
    if response.prestige:
        lines.append(f"{indent}add_prestige = {response.prestige}")
    if response.legitimacy:
        lines.append(f"{indent}add_legitimacy = {response.legitimacy}")
    if response.manpower_months:
        lines.append(
            f"{indent}add_manpower = {{ value = monthly_manpower "
            f"multiply = -{response.manpower_months:g} }}"
        )
    return lines


def ai_pulse_script(records: tuple[Situation, ...]) -> str:
    actor_tags = sorted({tag for record in records for tag in record.actors})
    lines = [
        "# Generated by tools/m10_situation_actions.py --write.",
        "# Direct AI execution avoids the engine's invalid situation-target generic-action queue.",
        "",
        "antq_m10_situation_ai_pulse = {",
        "\ttrigger = {",
        "\t\tis_ai = yes",
        "\t\tOR = { " + " ".join(f"tag = {tag}" for tag in actor_tags) + " }",
        "\t}",
        "\teffect = {",
    ]
    for record in records:
        for month, response in zip((1, 5, 9), responses(record), strict=True):
            key = action_key(record, response)
            cooldown = f"{key}_ai_cooldown"
            lines.extend((
                "\t\tif = {",
                "\t\t\tlimit = {",
                f"\t\t\t\t{actor_trigger(record)}",
                f"\t\t\t\tcurrent_month = {month}",
                f"\t\t\t\tgold >= {AI_TREASURY_RESERVE}",
                f"\t\t\t\tcan_see_situation = situation:{record.key}",
                f"\t\t\t\tsituation:{record.key} = {{ situation_is_active = yes }}",
                f"\t\t\t\tNOT = {{ has_variable = {cooldown} }}",
                "\t\t\t}",
                *ai_effect_lines(response),
                f"\t\t\tset_variable = {{ name = {cooldown} value = yes years = 2 }}",
                f"\t\t\tsituation:{record.key} = {{",
                f"\t\t\t\tchange_variable = {{ name = {record.progress} add = {response.progress} }}",
                "\t\t\t}",
                "\t\t}",
            ))
    lines.extend(("\t}", "}", ""))
    return "\n".join(lines)


def progress_command(record: Situation) -> str:
    return (
        f"[GetSituationByKey('{record.key}').MakeScope."
        f"GetVariable('{record.progress}').GetValue]"
    )


def localization(records: tuple[Situation, ...], language: str) -> str:
    lines = [f"l_{language}:"]
    for record in records:
        for response in responses(record):
            key = action_key(record, response)
            progress = progress_command(record)
            lines.extend((
                f' {key}: "{response.title}"',
                f' {key}_desc: "{response.description} Spend {response.cost} [gold|e] to add #G {response.progress}#! resolution progress. Current progress: #Y {progress}/100#!."',
                f' {key}_tt: "Add #G {response.progress}#! resolution progress (currently #Y {progress}/100#!)."',
            ))
    return "\n".join(lines) + "\n"


def outputs(records: tuple[Situation, ...]) -> dict[Path, str]:
    rendered = {
        ACTION_OUTPUT: action_script(records),
        AI_LIST_OUTPUT: ai_list_script(records),
        AI_PULSE_OUTPUT: ai_pulse_script(records),
    }
    for language in LANGUAGES:
        rendered[LOC_ROOT / language / f"antq_m10_situation_actions_l_{language}.yml"] = localization(records, language)
    return rendered


def validate(records: tuple[Situation, ...]) -> list[str]:
    failures: list[str] = []
    rendered = outputs(records)
    for path, expected in rendered.items():
        if not path.is_file():
            failures.append(f"missing generated output: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != expected:
            failures.append(f"stale generated output: {path.relative_to(ROOT)}")
    action_text = rendered[ACTION_OUTPUT]
    loc_text = rendered[LOC_ROOT / "english" / "antq_m10_situation_actions_l_english.yml"]
    if "Fund Relief and Negotiation" in loc_text or "Mobilize a Coordinated Response" in loc_text:
        failures.append("cloned legacy response text survives")
    localized_titles = [
        response.title for record in records for response in responses(record)
    ]
    if len(localized_titles) != len(records) * 3 or len(set(localized_titles)) != len(localized_titles):
        failures.append("situation response titles are missing or cloned")
    for forbidden in (
        "ai_tick", "automation_tick", "ai_prerequisite", "ai_will_do",
        "ai_interaction_source_list",
    ):
        if forbidden in action_text:
            failures.append(f"situation responses expose unsafe generic-action AI token: {forbidden}")
    if action_text.count("can_see_situation = situation:") != len(records) * 3:
        failures.append("situation response potentials lack exact visibility gating")
    if action_text.count("scope:actor ?= {") != len(records) * 3:
        failures.append("situation response potentials do not use the actor-optional registry contract")
    ai_list_text = rendered[AI_LIST_OUTPUT]
    if ai_list_text.count("potential = { always = no }") != len(records):
        failures.append("ancient situation response AI registries are not hard-disabled")
    list_definitions = re.findall(
        r"(?m)^(antq_[a-z0-9_]+_response_ai_list)\s*=\s*\{", ai_list_text
    )
    if len(list_definitions) != len(records) or len(set(list_definitions)) != len(records):
        failures.append(
            "situation response AI candidate index does not contain one unique list per situation"
        )
    for record in records:
        if len(responses(record)) != 3:
            failures.append(f"{record.key} does not have three authored responses")
        list_key = f"{record.key}_response_ai_list"
        list_match = re.search(rf"(?m)^{re.escape(list_key)}\s*=\s*\{{", ai_list_text)
        if list_match is None:
            failures.append(f"missing situation response AI candidate list: {list_key}")
            list_block = ""
        else:
            list_block = block_at(ai_list_text, list_match.end() - 1)
        for token in ("potential = { always = no }", "actions = {"):
            if token not in list_block:
                failures.append(f"{list_key} lacks candidate-index contract: {token}")
        for response in responses(record):
            key = action_key(record, response)
            if len(re.findall(rf"(?m)^\s*{re.escape(key)}\s*$", ai_list_text)) != 1:
                failures.append(f"{key} is not indexed exactly once for native AI evaluation")
            action_match = re.search(rf"(?m)^{re.escape(key)}\s*=\s*\{{", action_text)
            if action_match is None:
                failures.append(f"missing generated situation response: {key}")
                continue
            action = block_at(action_text, action_match.end() - 1)
            visibility = f"can_see_situation = situation:{record.key}"
            if action.count(visibility) != 1:
                failures.append(f"{key} is not exactly gated in actor potential")
            for token in (
                f"situation:{record.key} = this",
                f"name = {record.progress}", "type = situation",
            ):
                if token not in action:
                    failures.append(f"{key} lacks panel/action contract: {token}")
    pulse_text = rendered[AI_PULSE_OUTPUT]
    if pulse_text.count("\t\tif = {") != len(records) * 3:
        failures.append("situation AI pulse does not contain one branch per authored response")
    for token in (
        "antq_m10_situation_ai_pulse = {", "is_ai = yes",
        f"gold >= {AI_TREASURY_RESERVE}", "years = 2",
        "situation_is_active = yes", "_ai_cooldown",
    ):
        if token not in pulse_text:
            failures.append(f"situation AI pulse lacks {token}")
    for record in records:
        for month, response in zip((1, 5, 9), responses(record), strict=True):
            key = action_key(record, response)
            for token in (
                f"current_month = {month}",
                f"can_see_situation = situation:{record.key}",
                f"name = {key}_ai_cooldown",
                f"name = {record.progress} add = {response.progress}",
            ):
                if token not in pulse_text:
                    failures.append(f"safe situation AI pulse lacks {key} contract: {token}")
    gaius = next(record for record in records if record.key == "antq_m10_gaius_eastern_settlement")
    if gaius.actors != ("XAA", "XAO", "XAH"):
        failures.append("Gaius settlement must be actionable by Rome, Armenia, and Parthia")
    titles: dict[str, str] = {}
    signatures: dict[tuple[object, ...], str] = {}
    for record in records:
        for response in responses(record):
            key = action_key(record, response)
            title_key = response.title.casefold()
            if title_key in titles:
                failures.append(f"cloned situation response title: {titles[title_key]} and {key}")
            titles[title_key] = key
            if len(response.description) < 70:
                failures.append(f"{key} description is too shallow")
            signature = (
                response.cost, response.progress, response.stability,
                response.prestige, response.legitimacy, response.manpower_months,
            )
            prior = signatures.get(signature)
            if prior:
                failures.append(f"{key} reuses response signature of {prior}")
            signatures[signature] = key
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        records = load_situations()
        if args.write:
            for path, content in outputs(records).items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8-sig", newline="\n")
        failures = validate(records)
    except (OSError, ValueError) as exc:
        failures = [str(exc)]
    if failures:
        print("m10_situation_actions: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print(f"m10_situation_actions: PASS ({len(records)} situations; {len(records) * 3} themed response actions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

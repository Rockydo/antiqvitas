#!/usr/bin/env python3
"""Render the M11 source-labelled own-country decision layer.

The game exposes player decisions through ``common/generic_actions`` rather
than a separate decision database.  This generator deliberately limits each
action to reviewed AD 1 tags, uses only locally documented country effects,
and makes every historical statement reviewable in the CSV ledger.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/m11/decisions.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
OUTPUT = ROOT / "in_game/common/generic_actions/antq_m11_decisions.txt"
MESSAGE_TYPES = ROOT / "main_menu/gui/antq_m11_messagetypes.txt"
LOC_ROOT = ROOT / "main_menu/localization"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)
EXPECTED_COUNT = 40
EFFECTS = {"prestige", "legitimacy", "stability"}


@dataclass(frozen=True)
class Decision:
    identifier: str
    arc: str
    tags: tuple[str, ...]
    gold: int
    cooldown: int
    effect: str
    title: str
    description: str
    source: str
    confidence: str
    note: str


def esc(value: str) -> str:
    return value.replace('"', "'")


def load_tag_maps() -> tuple[dict[str, str], set[str]]:
    mapping = json.loads(TAG_MAP.read_text(encoding="utf-8"))
    engines = {entry["design_tag"]: entry["engine_tag"] for entry in mapping["entries"]}
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        roster = {row["tag"].strip() for row in csv.DictReader(handle)}
    return engines, roster


def load_decisions() -> list[Decision]:
    required = (
        "id", "arc", "tags", "gold", "cooldown", "effect", "title",
        "desc", "source", "confidence", "note",
    )
    with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    decisions: list[Decision] = []
    seen: set[str] = set()
    for index, row in enumerate(rows, start=2):
        missing = [field for field in required if not row.get(field, "").strip()]
        if missing:
            raise ValueError(f"{LEDGER.relative_to(ROOT)}:{index}: blank {', '.join(missing)}")
        identifier = row["id"].strip()
        if identifier in seen:
            raise ValueError(f"{LEDGER.relative_to(ROOT)}:{index}: duplicate id {identifier}")
        seen.add(identifier)
        tags = tuple(tag.strip() for tag in row["tags"].split(";") if tag.strip())
        try:
            gold, cooldown = int(row["gold"]), int(row["cooldown"])
        except ValueError as exc:
            raise ValueError(f"{LEDGER.relative_to(ROOT)}:{index}: gold and cooldown must be integers") from exc
        decision = Decision(
            identifier, row["arc"].strip(), tags, gold, cooldown,
            row["effect"].strip(), row["title"].strip(), row["desc"].strip(),
            row["source"].strip(), row["confidence"].strip(), row["note"].strip(),
        )
        decisions.append(decision)
    return decisions


def validate(decisions: list[Decision], engines: dict[str, str], roster: set[str]) -> None:
    if len(decisions) != EXPECTED_COUNT:
        raise ValueError(f"expected exactly {EXPECTED_COUNT} M11 decisions, found {len(decisions)}")
    for decision in decisions:
        if not decision.identifier.startswith(("endow_", "fund_", "consult_", "audit_", "repair_", "renew_", "receive_", "dedicate_", "review_", "inspect_", "open_", "dispatch_", "sponsor_", "scrutinize_", "honor_", "remit_", "convene_", "safeguard_", "mint_", "hold_", "invite_", "patronize_", "maintain_", "recognize_", "protect_", "give_", "settle_", "support_")):
            raise ValueError(f"decision id must use a readable verb: {decision.identifier}")
        if not decision.tags:
            raise ValueError(f"{decision.identifier}: no design tags")
        unknown = sorted(set(decision.tags) - roster)
        if unknown:
            raise ValueError(f"{decision.identifier}: tags absent from roster: {', '.join(unknown)}")
        unmapped = sorted(set(decision.tags) - engines.keys())
        if unmapped:
            raise ValueError(f"{decision.identifier}: tags absent from tag map: {', '.join(unmapped)}")
        if decision.effect not in EFFECTS:
            raise ValueError(f"{decision.identifier}: unsupported effect {decision.effect}")
        if not 5 <= decision.gold <= 30:
            raise ValueError(f"{decision.identifier}: gold must be 5..30")
        if not 3 <= decision.cooldown <= 8:
            raise ValueError(f"{decision.identifier}: cooldown must be 3..8 years")
        if decision.confidence not in {"secure", "contested"}:
            raise ValueError(f"{decision.identifier}: confidence must be secure or contested")


def render_action(decision: Decision, engines: dict[str, str]) -> str:
    tag_lines = "\n".join(f"\t\t\t\ttag = {engines[tag]}" for tag in decision.tags)
    return f'''# {decision.identifier}: {decision.source} [{decision.confidence}]\n# {decision.note}\nantq_{decision.identifier} = {{\n\ttype = owncountry\n\n\tai_tick = never\n\tautomation_tick = never\n\n\tpotential = {{\n\t\tscope:actor = {{\n\t\t\tOR = {{\n{tag_lines}\n\t\t\t}}\n\t\t}}\n\t}}\n\n\tallow = {{\n\t\tscope:actor = {{ gold >= {decision.gold} }}\n\t}}\n\n\tcooldown = {{\n\t\ttype = antq_{decision.identifier}\n\t\tyears = {decision.cooldown}\n\t}}\n\n\teffect = {{\n\t\tscope:actor = {{\n\t\t\tadd_gold = -{decision.gold}\n\t\t\tadd_{decision.effect} = {decision.effect}_weak_bonus\n\t\t}}\n\t}}\n\n\tai_will_do = {{\n\t\tadd = -1000\n\t}}\n}}\n'''


def render_loc(decisions: list[Decision], language: str) -> str:
    lines = [f"l_{language}:"]
    for decision in decisions:
        key = f"antq_{decision.identifier}"
        lines.append(f' {key}: "{esc(decision.title)}"')
        lines.append(f' {key}_desc: "{esc(decision.description)}"')
    return "\n".join(lines) + "\n"


def render_messages(decisions: list[Decision], language: str) -> str:
    """Supply the engine's mandatory generic-action message bundle.

    The installed message handler synthesizes ``PERFORM_<action>_ACTION`` for
    every action, even if the action is player-only.  Keeping the notification
    terse avoids an invented narrative while retaining a useful ledger entry.
    """
    lines = [f"l_{language}:"]
    for decision in decisions:
        action = f"antq_{decision.identifier}"
        message = f"PERFORM_{action}_ACTION"
        lines.extend((
            f' {message}_SETUP: "When a [country|e] uses the ${action}$ action."',
            f' {message}_HEADER: "$MESSENGER$"',
            f' {message}_TITLE: "[SCOPE.sCountry(\'actor\').GetName] has ${action}$."',
            f' {message}_EFFECTS: "$EFFECT$"',
            f' {message}_LOG: "${message}_TITLE$"',
            f' {message}_BTN1: "OK"',
            f' {message}_BTN2: "OK"',
            f' {message}_BTN3: "$common_string_go_to$"',
            f' {message}_MAP: ""',
        ))
    return "\n".join(lines) + "\n"


def render_message_types(decisions: list[Decision]) -> str:
    """Render the installed GUI message-type contract for each action.

    The generic-action loader registers a ``PERFORM_<action>_ACTION`` event
    at database load, so a localization bundle alone is insufficient.  The
    local ``main_menu/gui/messagetypes.txt`` establishes this compact schema.
    """
    blocks = ["# Generated by tools/m11_decisions.py from docs/m11/decisions.csv.\n"]
    for decision in decisions:
        blocks.append(
            f'''PERFORM_antq_{decision.identifier}_ACTION={{\nlog=yes\nonmap=no\npopup=yes\nidle=no\noption=yes\npausepopup=no\nmessage_category = government\n}}\n'''
        )
    return "\n".join(blocks)


def write(decisions: list[Decision], engines: dict[str, str]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = "# Generated by tools/m11_decisions.py from docs/m11/decisions.csv.\n\n"
    rendered += "\n".join(render_action(decision, engines) for decision in decisions)
    OUTPUT.write_text(rendered, encoding="utf-8-sig")
    MESSAGE_TYPES.parent.mkdir(parents=True, exist_ok=True)
    MESSAGE_TYPES.write_text(render_message_types(decisions), encoding="utf-8-sig")
    for language in LANGUAGES:
        path = LOC_ROOT / language / f"antq_m11_decisions_l_{language}.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_loc(decisions, language), encoding="utf-8-sig")
        messages = LOC_ROOT / language / f"antq_m11_decision_messages_l_{language}.yml"
        messages.write_text(render_messages(decisions, language), encoding="utf-8-sig")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write generated game files")
    args = parser.parse_args()
    engines, roster = load_tag_maps()
    decisions = load_decisions()
    validate(decisions, engines, roster)
    counts = Counter(decision.arc for decision in decisions)
    print(f"validated {len(decisions)} decisions across " + ", ".join(f"{arc}={count}" for arc, count in sorted(counts.items())))
    if args.write:
        write(decisions, engines)
        print(f"wrote {OUTPUT.relative_to(ROOT)}, {MESSAGE_TYPES.relative_to(ROOT)}, and {len(LANGUAGES)} localization/message mirrors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

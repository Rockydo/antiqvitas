#!/usr/bin/env python3
"""Ancientize every mounted expansion/survey/sea-raiding localization surface.

EU5's Geopolitics window is an always-available engine UI.  ANTIQVITAS keeps
its useful settlement, map-survey, and sanctioned-raiding mechanics, but the
stock labels describe them with early-modern vocabulary.  This generator
harvests the complete base+DLC English localization union and emits one late
mod layer for every supported client.  A game patch that adds or changes a
matching key makes ``--check`` fail until this layer is regenerated and
reviewed.

Script expressions and concept links are protected byte-for-byte.  Only the
player-rendered prose around them is rewritten.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from dates import M2_MIRROR_LANGUAGES


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
LANGUAGES = ("english", *M2_MIRROR_LANGUAGES)
OUTPUT_STEM = "zzzz_antq_ancient_expansion"

ENTRY = re.compile(
    r'^(?P<indent>\s*)(?P<key>[^:#\s][^:]*):(?P<version>\d+)?\s+'
    r'"(?P<value>(?:\\.|[^"\\])*)"\s*(?:#.*)?$'
)
KEY_MATCH = re.compile(
    r"(?:colon|privateer|explor|explo(?:_|$)|conquistador|geopolit)", re.IGNORECASE
)
PROSE_MATCH = re.compile(
    r"\b(?:colonial|colonies|colony|colonist|colonization|colonize|colonized|"
    r"privateer|privateers|privateering|explorer|explorers|exploration|"
    r"explorations|exploring|explored|explore|conquistador|conquistadors)\b",
    re.IGNORECASE,
)

# These are the shared engine-system families reachable from the Geopolitics,
# economy, automation, alert, message, modifier, and outliner surfaces.  Event,
# mission, flavor, and historical-description files are intentionally excluded:
# their definitions are separately quarantined and copying their prose into a
# late global overlay would turn inactive content into localization ownership.
SYSTEM_SOURCES = frozenset(
    {
        "actions_l_english.yml",
        "alerts_l_english.yml",
        "area_preferences_l_english.yml",
        "auto_modifiers_l_english.yml",
        "character_l_english.yml",
        "colonisation_l_english.yml",
        "common_used_strings_l_english.yml",
        "economy_l_english.yml",
        "effects_l_english.yml",
        "game_concepts_l_english.yml",
        "game_rules_l_english.yml",
        "general_tooltips_l_english.yml",
        "interfaces_l_english.yml",
        "lists_l_english.yml",
        "messages_l_english.yml",
        "modifier_types_l_english.yml",
        "outliner_l_english.yml",
        "privateers_l_english.yml",
        "scripted_effects_l_english.yml",
        "scripted_lists_l_english.yml",
        "static_modifiers_l_english.yml",
        "tooltip_structs_l_english.yml",
        "triggers_l_english.yml",
        "tutorial_l_english.yml",
    }
)
GENERIC_SYSTEM_KEYS = frozenset(
    {
        "ABANDON_BUTTON",
        "AREA_IS_ACCESSIBLE_OPEN_SEA",
        "AREA_IS_NOT_ADJANCENT",
        "AREA_OPEN_SEA_NO_ADVANCE",
        "AUTOMATION_FILTER_EXPANSION_DESC",
        "PRIVATE_POWER_TT",
        "SORT_CHARTER_MAINTENANCE",
        "SORT_CHARTER_MIGRATION",
        "SORT_CHARTER_NAME",
        "SORT_CHARTER_PROGRESS",
        "TERRA_INCOGNITA_TOOLTIP",
        "game_concept_fleet_basing_rights_desc",
        "game_concept_trade_range_desc",
    }
)

# Localization commands, concept links, icons, and substitutions may contain
# technical identifiers which the engine requires. They are never rendered
# literally and therefore must not be renamed. Rich-text wrappers are split
# into their non-rendered opener/closer: the prose *inside* ``#T ... #!`` is
# visible and must still be rewritten and audited.
TOKEN = re.compile(
    r"\[[^\]]*\]|\$[^$]*\$|@[A-Za-z0-9_]+!|"
    r"#TOOLTIP:[^,\n]+,|#[A-Za-z0-9_]+\s*|#!"
)

# Longest/specific phrases precede their components.  These substitutions are
# intentionally restrained and work for both title case and sentence prose.
REPLACEMENTS = (
    (r"\bColonial Charters\b", "Settlement Charters"),
    (r"\bcolonial charters\b", "settlement charters"),
    (r"\bColonial Charter\b", "Settlement Charter"),
    (r"\bcolonial charter\b", "settlement charter"),
    (r"\bColonial Migration\b", "Settlement Migration"),
    (r"\bcolonial migration\b", "settlement migration"),
    (r"\bColonial Maintenance\b", "Settlement Upkeep"),
    (r"\bcolonial maintenance\b", "settlement upkeep"),
    (r"\bColonial Range\b", "Settlement Range"),
    (r"\bcolonial range\b", "settlement range"),
    (r"\bColonial Progress\b", "Settlement Progress"),
    (r"\bcolonial progress\b", "settlement progress"),
    (r"\bCost of Colonies\b", "Settlement Upkeep"),
    (r"\bcost of colonies\b", "settlement upkeep"),
    (r"\bPrivateering\b", "Commissioned Sea Raiding"),
    (r"\bprivateering\b", "commissioned sea raiding"),
    (r"\bPrivateers\b", "Commissioned Raiders"),
    (r"\bprivateers\b", "commissioned raiders"),
    (r"\bPrivateer\b", "Commissioned Raider"),
    (r"\bprivateer\b", "commissioned raider"),
    (r"\bExploration Progress\b", "Survey Progress"),
    (r"\bexploration progress\b", "survey progress"),
    (r"\bExploration Cost\b", "Survey Cost"),
    (r"\bexploration cost\b", "survey cost"),
    (r"\bExploration Time\b", "Survey Time"),
    (r"\bexploration time\b", "survey time"),
    (r"\bExplorations\b", "Survey Expeditions"),
    (r"\bexplorations\b", "survey expeditions"),
    (r"\bExploration\b", "Survey Expedition"),
    (r"\bexploration\b", "survey expedition"),
    (r"\bExploring\b", "Surveying"),
    (r"\bexploring\b", "surveying"),
    (r"\bExplored\b", "Surveyed"),
    (r"\bexplored\b", "surveyed"),
    (r"\bExplore\b", "Survey"),
    (r"\bexplore\b", "survey"),
    (r"\bExplorers\b", "Survey Leaders"),
    (r"\bexplorers\b", "survey leaders"),
    (r"\bExplorer\b", "Survey Leader"),
    (r"\bexplorer\b", "survey leader"),
    (r"\bColonization\b", "Settlement Founding"),
    (r"\bcolonization\b", "settlement founding"),
    (r"\bColonized\b", "Settled"),
    (r"\bcolonized\b", "settled"),
    (r"\bColonize\b", "Settle"),
    (r"\bcolonize\b", "settle"),
    (r"\bColonizers\b", "Settlers"),
    (r"\bcolonizers\b", "settlers"),
    (r"\bColonists\b", "Settlers"),
    (r"\bcolonists\b", "settlers"),
    (r"\bColonist\b", "Settler"),
    (r"\bcolonist\b", "settler"),
    (r"\bColonies\b", "Settlements"),
    (r"\bcolonies\b", "settlements"),
    (r"\bColony\b", "Settlement"),
    (r"\bcolony\b", "settlement"),
    (r"\bColonial\b", "Settlement"),
    (r"\bcolonial\b", "settlement"),
    (r"\bConquistadors\b", "Expedition Commanders"),
    (r"\bconquistadors\b", "expedition commanders"),
    (r"\bConquistador\b", "Expedition Commander"),
    (r"\bconquistador\b", "expedition commander"),
    (r"\bNew World\b", "distant regions"),
    (r"\bnew world\b", "distant regions"),
    (r"\bMother Country\b", "Sponsoring State"),
    (r"\bmother country\b", "sponsoring state"),
    (r"\bCannons\b", "Shipboard Artillery"),
    (r"\bcannons\b", "shipboard artillery"),
    (r"\bCannon\b", "Artillery"),
    (r"\bcannon\b", "artillery"),
    (r"\bModern\b", "Contemporary"),
    (r"\bmodern\b", "contemporary"),
    (r"\bGeopolitics\b", "Frontiers and Sea Lanes"),
    (r"\bgeopolitics\b", "frontiers and sea lanes"),
    (r"\bGeopolitical\b", "Strategic"),
    (r"\bgeopolitical\b", "strategic"),
)

# Deliberate labels for the most prominent always-rendered controls.  These are
# applied after the general ancientization pass.
EXACT = {
    "GEOPOLITICS_TITLE": "Frontiers and Sea Lanes",
    "TAB_TOOLTIP_GEOPOLTICS_TITLE": "Frontiers and Sea Lanes",
    "TAB_TOOLTIP_GEOPOLTICS_LEFT_CLICK": "Open Frontiers and Sea Lanes Panel",
    "TAB_TOOLTIP_GEOPOLTICS_RIGHT_CLICK": "Toggle Frontier and Sea-Lane Queues",
    "OPEN_GEOPOLITICS_MAP_MODES": "Open Frontier and Sea-Lane Map Modes",
    "GEOPOLITICS_MESSAGE_CATEGORY": "Frontier and Sea-Lane Messages",
    "MESSAGE_GEOPOLITICS_SETTINGS": "Frontier and Sea-Lane Message Settings",
    "COLONIAL_TAB": "Settlements",
    "MARITIME_SUBTAB_PRIVATEERS": "Commissioned Raiders",
    "RECRUIT_EXPLORER": "Recruit Survey Leader",
    "recruit_explorer": "Recruit Survey Leader",
    "CURRENT_PRIVATEERS": "Possible Commissioned Raiders",
    "game_concept_colonial_charter": "Settlement Charter",
    "game_concept_colonial_charters": "Settlement Charters",
    "game_concept_colonial_migration": "Settlement Migration",
    "game_concept_colonial_maintenance": "Settlement Upkeep",
    "game_concept_colonial_range": "Settlement Range",
    "game_concept_colony": "Settlement",
    "game_concept_colonies": "Settlements",
    "game_concept_colonization": "Settlement Founding",
    "game_concept_colonize": "Settle",
    "game_concept_colonized": "Settled",
    "game_concept_exploration": "Survey Expedition",
    "game_concept_explorations": "Survey Expeditions",
    "game_concept_exploring": "Surveying",
    "game_concept_exploration_progress": "Survey Progress",
    "game_concept_exploration_expense": "Survey Cost",
    "game_concept_explorer": "Survey Leader",
    "game_concept_explorers": "Survey Leaders",
    "game_concept_privateer": "Commissioned Raider",
    "game_concept_privateers": "Commissioned Raiders",
    "game_concept_privateer_maintenance": "Raider Support",
    "game_concept_privateer_durability": "Raider Durability",
}


def game_root() -> Path:
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    return Path(str(config["game_dir"])) / "game"


def output_path(language: str) -> Path:
    return (
        ROOT / "main_menu/localization" / language
        / f"{OUTPUT_STEM}_l_{language}.yml"
    )


def mounted_english_files() -> dict[str, Path]:
    game = game_root()
    roots = [game / "main_menu/localization/english"]
    roots.extend(
        package / "main_menu/localization/english"
        for package in sorted((game / "dlc").glob("*"))
        if package.is_dir()
    )
    mounted: dict[str, Path] = {}
    for directory in roots:
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.yml")):
            mounted[path.relative_to(directory).as_posix()] = path
    if not mounted:
        raise ValueError("installed English localization union is empty")
    return mounted


def existing_mod_keys() -> set[str]:
    keys: set[str] = set()
    own = output_path("english").resolve()
    directory = ROOT / "main_menu/localization/english"
    for path in sorted(directory.glob("*.yml")):
        if path.resolve() == own:
            continue
        for line in path.read_text(encoding="utf-8-sig").splitlines()[1:]:
            match = ENTRY.match(line)
            if match:
                keys.add(match.group("key"))
    return keys


def protected_prose(value: str) -> str:
    return TOKEN.sub(" ", value)


def rewrite_prose(value: str) -> str:
    parts: list[str] = []
    cursor = 0
    for token in TOKEN.finditer(value):
        prose = value[cursor:token.start()]
        for pattern, replacement in REPLACEMENTS:
            prose = re.sub(pattern, replacement, prose)
        parts.extend((prose, token.group(0)))
        cursor = token.end()
    prose = value[cursor:]
    for pattern, replacement in REPLACEMENTS:
        prose = re.sub(pattern, replacement, prose)
    parts.append(prose)
    return "".join(parts)


def selected_entries() -> tuple[dict[str, str], tuple[str, ...]]:
    blocked = existing_mod_keys()
    selected: dict[str, str] = {}
    owners: dict[str, str] = {}
    contributing: set[str] = set()
    for relative, path in mounted_english_files().items():
        if relative not in SYSTEM_SOURCES:
            continue
        for number, line in enumerate(
            path.read_text(encoding="utf-8-sig").splitlines()[1:], start=2
        ):
            match = ENTRY.match(line)
            if not match:
                continue
            key = match.group("key")
            value = match.group("value")
            if key in blocked:
                continue
            if key not in EXACT and key not in GENERIC_SYSTEM_KEYS and not KEY_MATCH.search(key):
                continue
            rewritten = EXACT.get(key, rewrite_prose(value))
            previous = selected.get(key)
            if previous is not None and previous != rewritten:
                raise ValueError(
                    f"conflicting installed localization key {key!r}: "
                    f"{owners[key]} vs {relative}:{number}"
                )
            selected[key] = rewritten
            owners[key] = f"{relative}:{number}"
            contributing.add(relative)
    if not selected:
        raise ValueError("no expansion localization entries selected")
    required = set(EXACT) | set(GENERIC_SYSTEM_KEYS)
    missing_required = sorted(key for key in required if key not in selected and key not in blocked)
    if missing_required:
        raise ValueError(f"installed high-visibility key drift: {missing_required}")
    leaked = {}
    for key, value in selected.items():
        match = PROSE_MATCH.search(protected_prose(value))
        if match:
            leaked[key] = match.group(0)
    if leaked:
        sample = list(sorted(leaked.items()))[:20]
        raise ValueError(f"unsanitized expansion prose remains: {sample}")
    return selected, tuple(sorted(contributing))


def render(language: str) -> str:
    entries, sources = selected_entries()
    lines = [
        "\ufeff" + f"l_{language}:",
        " # Generated complete base+DLC ancient expansion presentation layer.",
        f" # {len(entries)} entries from {len(sources)} mounted source files; do not hand-edit.",
    ]
    for key in sorted(entries, key=str.casefold):
        lines.append(f' {key}: "{entries[key]}"')
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        entries, sources = selected_entries()
        mismatches: list[Path] = []
        for language in LANGUAGES:
            path = output_path(language)
            expected = render(language).encode("utf-8")
            if args.check:
                if not path.is_file() or path.read_bytes() != expected:
                    mismatches.append(path)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(expected)
        if mismatches:
            raise ValueError(
                "regenerate " + ", ".join(str(path.relative_to(ROOT)) for path in mismatches)
            )
    except (OSError, ValueError) as exc:
        print(f"m12_ancient_expansion_loc: FAIL\n  - {exc}")
        return 1
    action = "verified" if args.check else "generated"
    print(
        f"m12_ancient_expansion_loc: PASS ({action} {len(entries)} entries "
        f"from {len(sources)} mounted sources across {len(LANGUAGES)} clients)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

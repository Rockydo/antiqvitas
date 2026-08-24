#!/usr/bin/env python3
"""Ancientize the complete mounted dynastic-marriage UI vocabulary.

Dynastic marriage is a valid ancient diplomatic and succession mechanic, but
EU5's shared character and diplomacy widgets call every such union a "Royal
Marriage" even for Rome and republics.  Harvest the complete base+DLC English
systemic localization union and publish one late exact-key layer for every
supported client.  Flavor and event prose is deliberately excluded because
those definitions are quarantined by their own contracts.
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
OUTPUT_STEM = "zzzz_antq_ancient_marriage"

ENTRY = re.compile(
    r'^(?P<indent>\s*)(?P<key>[^:#\s][^:]*):(?P<version>\d+)?\s+'
    r'"(?P<value>(?:\\.|[^"\\])*)"\s*(?:#.*)?$'
)
TOKEN = re.compile(r"\[[^\]]*\]|\$[^$]*\$|@[A-Za-z0-9_]+!|#[^#\n]*#!")
KEY_MATCH = re.compile(r"royal_marriag|marry_noble|marriage_finder", re.I)
PROSE_MATCH = re.compile(r"\broyal (?:marriage|marriages|bond|bonds)\b", re.I)

SYSTEM_SOURCES = frozenset(
    {
        "actions_l_english.yml",
        "alerts_l_english.yml",
        "character_interactions_l_english.yml",
        "common_used_strings_l_english.yml",
        "country_interactions_l_english.yml",
        "diplomacy_l_english.yml",
        "diplomatic_status_l_english.yml",
        "effects_l_english.yml",
        "game_concepts_l_english.yml",
        "general_tooltips_l_english.yml",
        "government_names_l_english.yml",
        "hints_l_english.yml",
        "interfaces_l_english.yml",
        "lists_l_english.yml",
        "messages_l_english.yml",
        "opinions_l_english.yml",
        "scripted_effects_l_english.yml",
        "tooltip_structs_l_english.yml",
        "triggers_l_english.yml",
        "tutorial_l_english.yml",
    }
)

REPLACEMENTS = (
    (r"\bRoyal Marriages\b", "Dynastic Marriages"),
    (r"\broyal marriages\b", "dynastic marriages"),
    (r"\bRoyal Marriage\b", "Dynastic Marriage"),
    (r"\broyal marriage\b", "dynastic marriage"),
    (r"\bRoyal Bonds\b", "Dynastic Bonds"),
    (r"\broyal bonds\b", "dynastic bonds"),
    (r"\bRoyal Bond\b", "Dynastic Bond"),
    (r"\broyal bond\b", "dynastic bond"),
)
EXACT = {
    "MARRIAGE_FINDER": "Arrange a Dynastic Marriage",
    "marry_noble": "Marry a Local Aristocrat",
    "marry_noble_act": "$marry_noble$",
    "marry_noble_select_title": "Select a Local Aristocrat to Marry",
    "marry_noble_desc_specific": (
        "[SCOPE.sCharacter('recipient').GetName] will marry a local aristocrat."
    ),
    "marry_noble_desc": (
        "The [character|e] will marry a local aristocrat."
    ),
    "marry_noble_past": (
        "[SCOPE.sCharacter('recipient').GetName] has married a local aristocrat!"
    ),
    "marry_noble_act_past": (
        "A local aristocratic marriage for "
        "[SCOPE.sCharacter('recipient').GetName] strengthens the succession "
        "without creating a foreign diplomatic bond."
    ),
}


def game_root() -> Path:
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    return Path(str(config["game_dir"])) / "game"


def output_path(language: str) -> Path:
    return (
        ROOT
        / "main_menu/localization"
        / language
        / f"{OUTPUT_STEM}_l_{language}.yml"
    )


def existing_mod_keys() -> set[str]:
    """Respect exact localization owned by other ANTIQVITAS generators."""
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


def protected_prose(value: str) -> str:
    return TOKEN.sub(" ", value)


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
            if not KEY_MATCH.search(key) and not PROSE_MATCH.search(
                protected_prose(value)
            ):
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
    missing = sorted(set(EXACT) - set(selected) - blocked)
    if missing:
        raise ValueError(f"installed high-visibility key drift: {missing}")
    leaked = {
        key: PROSE_MATCH.search(protected_prose(value)).group(0)
        for key, value in selected.items()
        if PROSE_MATCH.search(protected_prose(value))
    }
    if leaked:
        raise ValueError(
            "unsanitized dynastic-marriage prose remains: "
            f"{list(sorted(leaked.items()))[:20]}"
        )
    return selected, tuple(sorted(contributing))


def render(language: str) -> str:
    entries, sources = selected_entries()
    lines = [
        "\ufeff" + f"l_{language}:",
        " # Generated complete base+DLC ancient marriage presentation layer.",
        f" # {len(entries)} entries from {len(sources)} mounted source files; do not hand-edit.",
    ]
    lines.extend(
        f' {key}: "{entries[key]}"' for key in sorted(entries, key=str.casefold)
    )
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
                "regenerate "
                + ", ".join(str(path.relative_to(ROOT)) for path in mismatches)
            )
    except (OSError, ValueError) as exc:
        print(f"m12_ancient_marriage_loc: FAIL\n  - {exc}")
        return 1
    action = "verified" if args.check else "generated"
    print(
        f"m12_ancient_marriage_loc: PASS ({action} {len(entries)} entries "
        f"from {len(sources)} mounted sources across {len(LANGUAGES)} clients)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify the complete AD 1 political-map contract for M3.

The generated start mirror is the loader-facing proof that the vanilla 1337
snapshot cannot remain underneath ANTIQVITAS.  This focused check joins the
reviewed roster, collision-safe runtime tags, country definitions, capitals,
and ownership ledger into one explicit M3 acceptance census.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
START_DIR = ROOT / "main_menu/setup/start"
COUNTRIES = ROOT / "in_game/setup/countries/antq_00_world.txt"

COUNTRY_HEADER = re.compile(r"(?m)^\t\t(?P<tag>[A-Z0-9]{3}) = \{ #")
COUNTRY_BLOCK = re.compile(
    r"(?ms)^\t\t(?P<tag>[A-Z0-9]{3}) = \{ #.*?^\t\t\}\n"
)
DEFINITION_HEADER = re.compile(r"(?m)^(?P<tag>[A-Z0-9]{3}) = \{ #")
CAPITAL = re.compile(r"(?m)^\t\t\tcapital = (?P<capital>[a-z0-9_]+)$")


def fail(failures: list[str], message: str) -> None:
    failures.append(message)


def read_roster() -> list[dict[str, str]]:
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("political roster is empty")
    return rows


def read_tag_map() -> dict[str, str]:
    payload = json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise ValueError("tag map has no entries list")
    mapping = {entry["design_tag"]: entry["engine_tag"] for entry in entries}
    if len(mapping) != len(entries):
        raise ValueError("tag map repeats a design tag")
    if len(set(mapping.values())) != len(mapping):
        raise ValueError("tag map repeats an engine tag")
    return mapping


def read_ownership() -> dict[str, set[str]]:
    by_tag: dict[str, set[str]] = defaultdict(set)
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(line for line in handle if not line.startswith("#")):
            by_tag[row["tag"]].add(row["location"])
    return by_tag


def main() -> int:
    failures: list[str] = []
    try:
        roster = read_roster()
        tag_map = read_tag_map()
        ownership = read_ownership()
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"m3_political_map: FAIL\n  - {exc}")
        return 1

    roster_tags = {row["tag"] for row in roster}
    expected_engine_tags = {tag_map.get(tag, "") for tag in roster_tags}
    if len(roster_tags) != len(roster):
        fail(failures, "political roster repeats a design tag")
    if "" in expected_engine_tags:
        missing = sorted(tag for tag in roster_tags if tag not in tag_map)
        fail(failures, "roster tags absent from engine tag map: " + ", ".join(missing))
    if set(tag_map) != roster_tags:
        extras = sorted(set(tag_map) - roster_tags)
        if extras:
            fail(failures, "engine tag map has non-roster tags: " + ", ".join(extras))

    installed_dir = Path(config["game_dir"]) / "game/main_menu/setup/start"
    installed_names = {path.name for path in installed_dir.glob("*.txt")}
    mod_names = {path.name for path in START_DIR.glob("*.txt")}
    if mod_names != installed_names:
        missing = sorted(installed_names - mod_names)
        extra = sorted(mod_names - installed_names)
        if missing:
            fail(failures, "start mirror lacks installed manager files: " + ", ".join(missing))
        if extra:
            fail(failures, "start mirror has unmirrored manager files: " + ", ".join(extra))

    try:
        start_text = (START_DIR / "10_countries.txt").read_text(encoding="utf-8")
        definition_text = COUNTRIES.read_text(encoding="utf-8-sig")
    except FileNotFoundError as exc:
        print(f"m3_political_map: FAIL\n  - {exc}")
        return 1

    current_tags = COUNTRY_HEADER.findall(start_text)
    current_set = set(current_tags)
    if len(current_tags) != len(current_set):
        duplicates = sorted(tag for tag, count in Counter(current_tags).items() if count > 1)
        fail(failures, "duplicate country starts: " + ", ".join(duplicates))
    missing_starts = sorted(expected_engine_tags - current_set)
    extra_starts = sorted(current_set - expected_engine_tags)
    if missing_starts:
        fail(failures, "roster polities missing from AD 1 start: " + ", ".join(missing_starts))
    if extra_starts:
        fail(failures, "non-ANTIQVITAS country starts survived: " + ", ".join(extra_starts))

    actual_capitals: dict[str, str] = {}
    for block in COUNTRY_BLOCK.finditer(start_text):
        match = CAPITAL.search(block.group(0))
        if match is None:
            fail(failures, f"{block['tag']}: no AD 1 capital")
        else:
            actual_capitals[block["tag"]] = match["capital"]
    expected_capitals = {tag_map[row["tag"]]: row["map_capital"] for row in roster}
    wrong_capitals = sorted(
        tag for tag, capital in expected_capitals.items() if actual_capitals.get(tag) != capital
    )
    if wrong_capitals:
        preview = ", ".join(
            f"{tag}={actual_capitals.get(tag, '<missing>')} (expected {expected_capitals[tag]})"
            for tag in wrong_capitals[:12]
        )
        suffix = " ..." if len(wrong_capitals) > 12 else ""
        fail(failures, "start capitals differ from roster: " + preview + suffix)

    definition_tags = DEFINITION_HEADER.findall(definition_text)
    definition_set = set(definition_tags)
    if len(definition_tags) != len(definition_set):
        duplicates = sorted(tag for tag, count in Counter(definition_tags).items() if count > 1)
        fail(failures, "duplicate country definitions: " + ", ".join(duplicates))
    missing_definitions = sorted(expected_engine_tags - definition_set)
    extra_definitions = sorted(definition_set - expected_engine_tags)
    if missing_definitions:
        fail(failures, "roster polities missing country definitions: " + ", ".join(missing_definitions))
    if extra_definitions:
        fail(failures, "non-ANTIQVITAS country definitions: " + ", ".join(extra_definitions))

    for row in roster:
        locations = ownership.get(row["tag"], set())
        if not locations:
            fail(failures, f"{row['tag']}: no sourced owned locations")
        elif row["map_capital"] not in locations:
            fail(failures, f"{row['tag']}: capital {row['map_capital']} is not owned")

    if failures:
        print("m3_political_map: FAIL")
        for message in failures:
            print(f"  - {message}")
        return 1
    print(
        "m3_political_map: PASS "
        f"({len(roster)} roster polities; {len(current_set)} AD 1 starts; "
        f"{len(definition_set)} country definitions; {len(mod_names)} exact start managers; "
        f"{sum(len(locations) for locations in ownership.values())} sourced controlled locations)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

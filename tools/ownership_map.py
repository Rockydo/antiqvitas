#!/usr/bin/env python3
"""Resolve sourced AD 1 ownership geography into engine location lists.

The historical source files name EU5 geography hierarchy keys rather than
unreviewable thousands-of-location blobs.  This tool expands those keys using
the locally harvested map definition, then retains only locations demonstrably
ownable in the installed vanilla start manager.  A generated, reviewable CSV is
the sole input to the M3 country-manager generator.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from io import StringIO
from pathlib import Path

from extract_vanilla import tokenize

ROOT = Path(__file__).resolve().parents[1]
AREAS = ROOT / "docs/world_1ad/ownership_areas.csv"
DIRECT = ROOT / "docs/world_1ad/ownership_locations.csv"
OUTPUT = ROOT / "docs/world_1ad/ownership_resolved.csv"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
HIERARCHY = ROOT / "docs/vanilla_symbols/geography_hierarchy.json"
LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
CONFIG = ROOT / "config/local_paths.json"

AREA_FIELDS = ("tag", "geography", "tenure", "source", "confidence", "note")
DIRECT_FIELDS = ("tag", "location", "tenure", "source", "confidence", "note")
OUTPUT_FIELDS = ("tag", "engine_tag", "location", "tenure", "source", "confidence", "note")
TENURES = {"own_control_core", "own_control_integrated", "own_control_conquered"}
CONFIDENCE = {"secure", "contested"}


def read_rows(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"missing {path.relative_to(ROOT)}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(fields):
            raise ValueError(
                f"{path.relative_to(ROOT)} header must be " + ",".join(fields)
            )
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} must contain at least one row")
    return rows


def vanilla_owned_locations(locations: set[str]) -> set[str]:
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    source = Path(config["game_dir"]) / "game/main_menu/setup/start/10_countries.txt"
    tokens = list(tokenize(source.read_bytes().decode("utf-8-sig", errors="replace")))
    owned: set[str] = set()
    index = 0
    while index + 2 < len(tokens):
        key = tokens[index].value
        if (
            key in TENURES
            and tokens[index + 1].value == "="
            and tokens[index + 2].value == "{"
        ):
            depth = 1
            index += 3
            while index < len(tokens) and depth:
                value = tokens[index].value
                if value == "{":
                    depth += 1
                elif value == "}":
                    depth -= 1
                elif value in locations:
                    owned.add(value)
                index += 1
            continue
        index += 1
    if not owned:
        raise ValueError("could not parse any ownable locations from installed start manager")
    return owned


def descendants(key: str, hierarchy: dict[str, list[str]], locations: set[str]) -> set[str]:
    if key in locations:
        return {key}
    if key not in hierarchy:
        raise KeyError(f"unknown EU5 geography key {key}")
    result: set[str] = set()
    pending = list(hierarchy[key])
    seen = {key}
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        if current in locations:
            result.add(current)
        else:
            pending.extend(hierarchy.get(current, []))
    return result


def source_rows() -> tuple[list[dict[str, str]], dict[str, str], set[str], dict[str, list[str]], set[str]]:
    area_rows = read_rows(AREAS, AREA_FIELDS)
    direct_rows = read_rows(DIRECT, DIRECT_FIELDS)
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        roster = list(csv.DictReader(handle))
    capital_by_tag = {row["tag"]: row["map_capital"] for row in roster}
    tag_map = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    hierarchy = json.loads(HIERARCHY.read_text(encoding="utf-8-sig"))
    locations = set(json.loads(LOCATIONS.read_text(encoding="utf-8-sig")))
    return area_rows + direct_rows, capital_by_tag, locations, hierarchy, set(tag_map)


def render() -> tuple[str, int, int]:
    area_rows = read_rows(AREAS, AREA_FIELDS)
    direct_rows = read_rows(DIRECT, DIRECT_FIELDS)
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        roster = list(csv.DictReader(handle))
    capitals = {row["tag"]: row["map_capital"] for row in roster}
    tag_map = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    hierarchy = json.loads(HIERARCHY.read_text(encoding="utf-8-sig"))
    locations = set(json.loads(LOCATIONS.read_text(encoding="utf-8-sig")))
    vanilla_owned = vanilla_owned_locations(locations)
    errors: list[str] = []
    assignments: dict[tuple[str, str], dict[str, str]] = {}

    def add(tag: str, location: str, tenure: str, source: str, confidence: str, note: str) -> None:
        if tag not in tag_map:
            errors.append(f"unknown roster tag {tag}")
            return
        if capitals.get(tag) == "TBD":
            errors.append(f"{tag} has ownership but no verified map capital")
        if tenure not in TENURES:
            errors.append(f"{tag}/{location}: invalid tenure {tenure}")
        if confidence not in CONFIDENCE:
            errors.append(f"{tag}/{location}: invalid confidence {confidence}")
        if not source or not note:
            errors.append(f"{tag}/{location}: source and note are required")
        previous = next((value for (other, loc), value in assignments.items() if loc == location and other != tag), None)
        if previous:
            errors.append(f"{location} assigned to both {previous['tag']} and {tag}")
            return
        key = (tag, location)
        current = assignments.get(key)
        if current and current["tenure"] != tenure:
            errors.append(f"{tag}/{location}: conflicting tenures {current['tenure']} and {tenure}")
            return
        if current:
            current["source"] = ";".join(dict.fromkeys((current["source"] + ";" + source).split(";")))
            return
        assignments[key] = {
            "tag": tag,
            "engine_tag": tag_map[tag],
            "location": location,
            "tenure": tenure,
            "source": source,
            "confidence": confidence,
            "note": note,
        }

    for row in area_rows:
        try:
            expanded = descendants(row["geography"], hierarchy, locations) & vanilla_owned
        except KeyError as exc:
            errors.append(f"{row['tag']}/{row['geography']}: {exc}")
            continue
        if not expanded:
            errors.append(f"{row['tag']}/{row['geography']}: no vanilla-ownable locations")
        for location in sorted(expanded):
            add(row["tag"], location, row["tenure"], row["source"], row["confidence"], row["note"])
    for row in direct_rows:
        location = row["location"]
        if location not in locations:
            errors.append(f"{row['tag']}/{location}: unknown location")
            continue
        # A directly reviewed local key can legitimately be unowned in 1337
        # (for example, an ancient archaeological site). Broad geography is
        # filtered through the vanilla ownership surface; exact reviewed keys
        # are instead proved by the real-game smoke gate.
        add(row["tag"], location, row["tenure"], row["source"], row["confidence"], row["note"])
    if errors:
        raise ValueError("\n".join(sorted(set(errors))))

    stream = StringIO(newline="")
    stream.write("# Generated by tools/ownership_map.py --write; do not edit.\n")
    writer = csv.DictWriter(stream, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(sorted(assignments.values(), key=lambda row: (row["tag"], row["location"])))
    return stream.getvalue(), len(assignments), len({row["tag"] for row in assignments.values()})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        content, locations, tags = render()
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"ownership_map: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.write_text(content, encoding="utf-8-sig", newline="")
        print(f"ownership_map: wrote {OUTPUT.relative_to(ROOT)} ({locations} locations; {tags} tags)")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != content:
        print("ownership_map: FAIL\n  - stale or missing ownership_resolved.csv; run --write")
        return 1
    print(f"ownership_map: PASS ({locations} locations; {tags} tags)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

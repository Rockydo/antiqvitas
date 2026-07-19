#!/usr/bin/env python3
"""Create stable collision-free engine tags for the AD 1 design roster."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
OUTPUT = ROOT / "docs/world_1ad/tag_map.json"
TAG_LINE = re.compile(r"^([A-Z0-9]{3})\s*=\s*\{")
ENGINE_TAG = re.compile(r"^[A-Z0-9]{3}$")
# Verified by smoke on build 24187685: XAD hashes to the unrelated localization
# key name_li3.mandarin_language.  The engine only reports the collision after
# it hashes both keys, so reserve observed unsafe values in addition to exact
# localization spelling collisions.
HASH_COLLISION_TAGS = {"XAD"}


def game_dir() -> Path:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    return Path(config["game_dir"])


def vanilla_tags() -> set[str]:
    tags: set[str] = set()
    source = game_dir() / "game/in_game/setup/countries"
    for path in source.glob("*.txt"):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = TAG_LINE.match(line)
            if match:
                tags.add(match.group(1))
    return tags


def localization_keys() -> set[str]:
    """Tags are localization keys too, so they must not collide with any key.

    The country database reports these as hash collisions during load, even if
    the conflicting key belongs to an unrelated system.
    """
    source = ROOT / "docs/vanilla_symbols/localization_key.json"
    return {
        key
        for key in json.loads(source.read_text(encoding="utf-8-sig"))
        if ENGINE_TAG.fullmatch(key)
    }


def generated_tags() -> list[str]:
    for second in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        for third in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            yield f"X{second}{third}"


def prior_engine_tags() -> dict[str, str]:
    """Retain valid previous allocations when the roster grows.

    Design tags are deliberately allowed to collide with vanilla and
    localization namespaces.  A sequential fresh allocation would therefore
    renumber every later collision when a new row is inserted midway through
    the historical roster.  Those internal tag changes are needless save and
    tooling churn, so preserve any prior allocation that remains safe against
    the current build's reserved namespaces.
    """
    raw: str | None = None
    try:
        # Prefer the committed map.  During a roster-edit working tree the
        # generated output may already contain a provisional allocation, while
        # HEAD is the last accepted stable allocation.
        completed = subprocess.run(
            ["git", "show", "HEAD:docs/world_1ad/tag_map.json"],
            cwd=ROOT,
            capture_output=True,
            check=False,
            text=True,
        )
        if completed.returncode == 0:
            raw = completed.stdout
    except OSError:
        pass
    if raw is None and OUTPUT.is_file():
        try:
            raw = OUTPUT.read_text(encoding="utf-8")
        except OSError:
            return {}
    if raw is None:
        return {}
    try:
        payload = json.loads(raw)
        entries = payload.get("entries", [])
    except json.JSONDecodeError:
        return {}
    result: dict[str, str] = {}
    for entry in entries:
        design = entry.get("design_tag")
        engine = entry.get("engine_tag")
        if isinstance(design, str) and isinstance(engine, str) and ENGINE_TAG.fullmatch(engine):
            result[design] = engine
    return result


def build_map() -> dict[str, object]:
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        roster = list(csv.DictReader(handle))
    vanilla = vanilla_tags()
    loc_keys = localization_keys()
    blocked = set(vanilla) | loc_keys | HASH_COLLISION_TAGS
    prior = prior_engine_tags()
    reserved = blocked | set(prior.values())
    allocated = set(blocked)
    replacement = generated_tags()
    entries: list[dict[str, object]] = []
    for row in roster:
        design = row["tag"]
        vanilla_collision = design in vanilla
        localization_collision = design in loc_keys
        previous = prior.get(design)
        if previous and previous not in blocked and previous not in allocated:
            engine = previous
        elif design not in reserved and design not in allocated:
            engine = design
        else:
            engine = next(
                candidate
                for candidate in replacement
                if candidate not in reserved and candidate not in allocated
            )
        allocated.add(engine)
        entries.append(
            {
                "design_tag": design,
                "engine_tag": engine,
                "vanilla_collision": vanilla_collision,
                "localization_collision": localization_collision,
                "name": row["name"],
            }
        )
    return {
        "game_build": json.loads(
            (ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig")
        )["game_build_id"],
        "entry_count": len(entries),
        "collision_count": sum(1 for entry in entries if entry["vanilla_collision"]),
        "localization_collision_count": sum(
            1 for entry in entries if entry["localization_collision"]
        ),
        "reserved_hash_collision_tags": sorted(HASH_COLLISION_TAGS),
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    expected = json.dumps(build_map(), indent=2) + "\n"
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8", newline="\n")
        print(f"tag_map: wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file():
        print("tag_map: FAIL (missing generated tag map)", file=sys.stderr)
        return 1
    actual = OUTPUT.read_text(encoding="utf-8")
    if actual != expected:
        print("tag_map: FAIL (map is stale; run tools/generate_tag_map.py --write)", file=sys.stderr)
        return 1
    payload = json.loads(actual)
    print(
        f"tag_map: PASS ({payload['entry_count']} entries; "
        f"{payload['collision_count']} vanilla and "
        f"{payload['localization_collision_count']} localization collisions remapped)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

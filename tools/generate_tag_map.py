#!/usr/bin/env python3
"""Create stable collision-free engine tags for the AD 1 design roster."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
OUTPUT = ROOT / "docs/world_1ad/tag_map.json"
TAG_LINE = re.compile(r"^([A-Z0-9]{3})\s*=\s*\{")


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


def generated_tags() -> list[str]:
    for second in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        for third in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            yield f"X{second}{third}"


def build_map() -> dict[str, object]:
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        roster = list(csv.DictReader(handle))
    vanilla = vanilla_tags()
    used = set(vanilla)
    replacement = generated_tags()
    entries: list[dict[str, object]] = []
    for row in roster:
        design = row["tag"]
        if design not in used:
            engine = design
            collision = False
        else:
            engine = next(candidate for candidate in replacement if candidate not in used)
            collision = True
        used.add(engine)
        entries.append(
            {
                "design_tag": design,
                "engine_tag": engine,
                "vanilla_collision": collision,
                "name": row["name"],
            }
        )
    return {
        "game_build": json.loads(
            (ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig")
        )["game_build_id"],
        "entry_count": len(entries),
        "collision_count": sum(1 for entry in entries if entry["vanilla_collision"]),
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
        f"{payload['collision_count']} vanilla collisions remapped)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

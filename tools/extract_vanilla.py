#!/usr/bin/env python3
"""Harvest the installed EU5 build into deterministic symbol and inventory JSON."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYMBOL_DIRS = {
    "advance": "advances",
    "age": "age",
    "building": "building_types",
    "casus_belli": "casus_belli",
    "country_rank": "country_ranks",
    "culture_group": "culture_groups",
    "culture": "cultures",
    "disaster": "disasters",
    "disease": "diseases",
    "estate": "estates",
    "estate_privilege": "estate_privileges",
    "good": "goods",
    "government_reform": "government_reforms",
    "government_type": "government_types",
    "institution": "institution",
    "international_organization": "international_organizations",
    "language": "languages",
    "law": "laws",
    "location_rank": "location_ranks",
    "peace_treaty": "peace_treaties",
    "policy": "policies",
    "pop_type": "pop_types",
    "religion_group": "religion_groups",
    "religion": "religions",
    "road_type": "road_types",
    "situation": "situations",
    "societal_value": "societal_values",
    "subject_type": "subject_types",
    "town_setup": "town_setups",
    "trait": "traits",
    "unit_category": "unit_categories",
    "unit_type": "unit_types",
    "wargoal": "wargoals",
}
TEXT_SUFFIXES = {".txt", ".gui", ".gfx", ".yml", ".csv", ".json", ".info", ".map"}


@dataclass(frozen=True)
class Token:
    value: str
    quoted: bool = False


def tokenize(text: str):
    """Yield Clausewitz tokens while tolerating comments, operators, and RGB values."""
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if char == "#":
            newline = text.find("\n", index)
            index = length if newline < 0 else newline + 1
            continue
        if char in "{}=":
            yield Token(char)
            index += 1
            continue
        if char == '"':
            index += 1
            value = []
            while index < length:
                char = text[index]
                if char == "\\" and index + 1 < length:
                    value.append(text[index + 1])
                    index += 2
                elif char == '"':
                    index += 1
                    break
                else:
                    value.append(char)
                    index += 1
            yield Token("".join(value), quoted=True)
            continue
        end = index
        while end < length and not text[end].isspace() and text[end] not in '{}="#':
            end += 1
        yield Token(text[index:end])
        index = end


def top_level_keys(text: str) -> set[str]:
    tokens = iter(tokenize(text))
    keys: set[str] = set()
    depth = 0
    previous: Token | None = None
    for token in tokens:
        if token.value == "{":
            depth += 1
        elif token.value == "}":
            depth = max(depth - 1, 0)
        elif token.value == "=" and depth == 0 and previous:
            if re.fullmatch(r"[A-Za-z0-9_:.@-]+", previous.value):
                keys.add(previous.value)
        previous = token
    return keys


def detect_encoding(raw: bytes) -> tuple[str, bool]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            raw.decode(encoding)
            return encoding, bom
        except UnicodeDecodeError:
            continue
    return "binary", bom


def read_script(path: Path) -> str:
    return path.read_bytes().decode("utf-8-sig", errors="replace")


def geography(game: Path) -> dict[str, object]:
    path = game / "in_game/map_data/definitions.txt"
    text = read_script(path)
    hierarchy: dict[str, list[str]] = defaultdict(list)
    locations: set[str] = set()
    stack: list[str] = []
    tokens = list(tokenize(text))
    index = 0
    pending: str | None = None
    while index < len(tokens):
        value = tokens[index].value
        if value == "=" and index and index + 1 < len(tokens) and tokens[index + 1].value == "{":
            pending = tokens[index - 1].value
            stack.append(pending)
            if len(stack) >= 2:
                hierarchy[stack[-2]].append(pending)
            index += 2
            continue
        if value == "}":
            if stack:
                stack.pop()
        elif value not in {"{", "="} and len(stack) == 5:
            locations.add(value)
            hierarchy[stack[-1]].append(value)
        index += 1
    by_level = {
        "continents": sorted(key for key in hierarchy if key in set(hierarchy.keys()) and key in {
            token.value for token in tokens[:0]
        }),
        "locations": sorted(locations),
    }
    # Depth-aware key extraction is clearer in a second lightweight pass.
    levels: dict[int, set[str]] = defaultdict(set)
    depth = 0
    for index, token in enumerate(tokens):
        if token.value == "=" and index and index + 1 < len(tokens) and tokens[index + 1].value == "{":
            levels[depth].add(tokens[index - 1].value)
        elif token.value == "{":
            depth += 1
        elif token.value == "}":
            depth = max(depth - 1, 0)
    by_level.update(
        {
            "continents": sorted(levels[0]),
            "subcontinents": sorted(levels[1]),
            "regions": sorted(levels[2]),
            "areas": sorted(levels[3]),
            "provinces": sorted(levels[4]),
            "hierarchy": {key: sorted(set(value)) for key, value in sorted(hierarchy.items())},
        }
    )
    return by_level


def inventory(game: Path) -> dict[str, object]:
    files = []
    folders: dict[str, int] = defaultdict(int)
    for path in game.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(game).as_posix()
        folders[str(Path(relative).parent).replace("\\", "/")] += 1
        item: dict[str, object] = {"path": relative, "size": path.stat().st_size}
        if path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size <= 16 * 1024**2:
            raw = path.read_bytes()
            encoding, bom = detect_encoding(raw)
            item.update({"encoding": encoding, "utf8_bom": bom})
        files.append(item)
    return {
        "file_count": len(files),
        "files": files,
        "folder_file_counts": dict(sorted(folders.items())),
    }


def setup_inventory(game: Path) -> dict[str, list[str]]:
    result = {}
    for root_name in ("main_menu/setup", "in_game/setup"):
        root = game / root_name
        if root.exists():
            result[root_name] = sorted(
                path.relative_to(game).as_posix() for path in root.rglob("*") if path.is_file()
            )
    for name in ("in_game/events", "in_game/common/situations", "in_game/common/disasters"):
        root = game / name
        result[name] = (
            sorted(path.relative_to(game).as_posix() for path in root.rglob("*") if path.is_file())
            if root.exists()
            else []
        )
    dlc = game / "dlc"
    if dlc.exists():
        for package in sorted(path for path in dlc.iterdir() if path.is_dir()):
            result[f"dlc/{package.name}"] = sorted(
                path.relative_to(game).as_posix()
                for path in package.rglob("*")
                if path.is_file()
            )
    return result


def localization_keys(game: Path) -> set[str]:
    keys: set[str] = set()
    pattern = re.compile(r"^\s*([A-Za-z0-9_.:@-]+):(?:\d+)?\s", re.MULTILINE)
    for path in game.rglob("*_l_english.yml"):
        keys.update(pattern.findall(read_script(path)))
    return keys


def event_ids(game: Path) -> set[str]:
    ids: set[str] = set()
    pattern = re.compile(r"^\s*id\s*=\s*([A-Za-z0-9_.:-]+)", re.MULTILINE)
    root = game / "in_game/events"
    for path in root.rglob("*.txt"):
        text = read_script(path)
        ids.update(pattern.findall(text))
        ids.update(
            key
            for key in top_level_keys(text)
            if "." in key and re.fullmatch(r"[A-Za-z0-9_.:-]+", key)
        )
    return ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "config/local_paths.json")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/vanilla_symbols")
    parser.add_argument("--skip-inventory", action="store_true")
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text(encoding="utf-8-sig"))
    game = Path(cfg["game_dir"]) / "game"
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    common = game / "in_game/common"
    summary: dict[str, int] = {}
    for symbol, folder in SYMBOL_DIRS.items():
        symbols: set[str] = set()
        root = common / folder
        if root.exists():
            for path in root.rglob("*.txt"):
                symbols.update(top_level_keys(read_script(path)))
        values = sorted(value for value in symbols if value not in {"replace", "include"})
        (output / f"{symbol}.json").write_text(
            json.dumps(values, indent=2) + "\n", encoding="utf-8"
        )
        summary[symbol] = len(values)
    geo = geography(game)
    for key in ("locations", "provinces", "areas", "regions", "subcontinents", "continents"):
        (output / f"{key}.json").write_text(
            json.dumps(geo[key], indent=2) + "\n", encoding="utf-8"
        )
        summary[key] = len(geo[key])
    (output / "geography_hierarchy.json").write_text(
        json.dumps(geo["hierarchy"], indent=2) + "\n", encoding="utf-8"
    )
    loc = sorted(localization_keys(game))
    events = sorted(event_ids(game))
    (output / "localization_key.json").write_text(
        json.dumps(loc, indent=2) + "\n", encoding="utf-8"
    )
    (output / "event_id.json").write_text(
        json.dumps(events, indent=2) + "\n", encoding="utf-8"
    )
    summary["localization_key"] = len(loc)
    summary["event_id"] = len(events)
    (output / "content_inventory.json").write_text(
        json.dumps(setup_inventory(game), indent=2) + "\n", encoding="utf-8"
    )
    if not args.skip_inventory:
        (output / "file_inventory.json").write_text(
            json.dumps(inventory(game), indent=2) + "\n", encoding="utf-8"
        )
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Exact-name quarantine for installed buildings outside the AD 1 active set."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
RELATIVE = Path("in_game/common/building_types")
TARGET = ROOT / RELATIVE
MANIFEST = ROOT / "docs/m5/building_quarantine_manifest.json"
CUSTOM_SOURCES = {
    "00_antiquitas_adapter_replacements.txt",
    "00_antiquitas_regional_buildings.txt",
    "00_antiquitas_roman_buildings.txt",
}
DEFINITION = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\s*=\s*\{\s*(?:#.*)?$")
DIRECT_SETUP = re.compile(
    r"(?m)^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*\{\s*tag\s*="
)
TOWN_SETUP = re.compile(
    r"(?m)^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*[0-9]+\s*(?:#.*)?$"
)
UNLOCK = re.compile(r"(?m)^\s*unlock_building\s*=\s*([A-Za-z0-9_]+)")
GATE = re.compile(r"^\s*(country_potential|location_potential|allow)\s*=\s*\{")
HAS_VARIABLE = re.compile(
    r"\bhas_variable\s*=\s*(?!\{)([A-Za-z][A-Za-z0-9_]*)"
)
STRUCTURED_VARIABLE = re.compile(
    r"\bhas_variable\s*=\s*\{[^{}]*?\bname\s*=\s*"
    r"([A-Za-z][A-Za-z0-9_]*)",
    re.DOTALL,
)
UNLOCK_READER = re.compile(
    r"\bhas_unlocked_(building|advance)_trigger\s*=\s*\{[^{}]*?"
    r"\btype\s*=\s*([A-Za-z][A-Za-z0-9_]*)",
    re.DOTALL,
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean_text(text: str) -> str:
    """Normalize inherited source whitespace without changing script tokens."""
    return "\n".join(line.rstrip(" \t") for line in text.splitlines()).rstrip("\n") + "\n"


def game_root() -> Path:
    data = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    return Path(data["game_dir"]) / "game"


def installed_sources() -> dict[str, Path]:
    game = game_root()
    roots = [game / RELATIVE]
    roots.extend(
        package / RELATIVE
        for package in sorted((game / "dlc").glob("*"))
        if package.is_dir()
    )
    mounted: dict[str, Path] = {}
    for directory in roots:
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.txt")):
            mounted[path.relative_to(directory).as_posix()] = path
    if not mounted:
        raise ValueError("installed building source union is empty")
    return mounted


def definition_keys(path: Path) -> list[str]:
    return [
        match.group(1)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if (match := DEFINITION.match(line))
    ]


def custom_keys() -> set[str]:
    keys: set[str] = set()
    for name in CUSTOM_SOURCES:
        path = TARGET / name
        if not path.is_file():
            raise ValueError(f"missing custom building source: {path}")
        keys.update(definition_keys(path))
    return keys


def active_adapters(installed: set[str]) -> set[str]:
    used: set[str] = set()
    for path in sorted((ROOT / "main_menu/setup/start").glob("*.txt")):
        used.update(DIRECT_SETUP.findall(path.read_text(encoding="utf-8-sig")))
    for path in sorted((ROOT / "in_game/common/town_setups").glob("*.txt")):
        used.update(TOWN_SETUP.findall(path.read_text(encoding="utf-8-sig")))
    tree = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
    if tree.is_file():
        used.update(UNLOCK.findall(tree.read_text(encoding="utf-8-sig")))
    adapters = used.intersection(installed)
    missing = sorted(used - installed - custom_keys())
    if missing:
        raise ValueError(f"active setup/unlock building keys are undefined: {missing}")
    return adapters


def compatibility_variables(text: str) -> set[str]:
    """Recover inert variable readers from one installed definition.

    The engine warns when an event-set variable loses its last loaded reader.
    Quarantined definitions must therefore keep the variable contract without
    retaining unsafe or player-visible availability logic.
    """
    names = set(HAS_VARIABLE.findall(text))
    names.update(STRUCTURED_VARIABLE.findall(text))
    for kind, key in UNLOCK_READER.findall(text):
        names.add(f"unlocked_{kind}_{key}")
    return names


def definition_compatibility(lines: list[str]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    depth = 0
    key: str | None = None
    block: list[str] = []
    for line in lines:
        match = DEFINITION.match(line.rstrip("\r\n")) if depth == 0 else None
        if match:
            key = match.group(1)
            block = [line]
        elif key is not None:
            block.append(line)
        depth += line.count("{") - line.count("}")
        if key is not None and depth == 0:
            result[key] = compatibility_variables("".join(block))
            key = None
            block = []
    if depth != 0:
        raise ValueError("unbalanced building source while collecting compatibility")
    return result


def marker(variables: set[str]) -> str:
    lines = [
        "\t# ANTIQVITAS installed-building quarantine: definition retained only "
        "for engine/script references.",
        "\tcountry_potential = {",
        "\t\talways = no",
    ]
    if variables:
        lines.append("\t\t# Preserve load-time event-variable contracts without legacy gates.")
        lines.extend(f"\t\thas_variable = {name}" for name in sorted(variables))
    lines.extend(("\t}", "\tallow = { always = no }"))
    return "\n".join(lines) + "\n"


def strip_top_level_gate(
    lines: list[str], start: int, initial_depth: int
) -> tuple[int, int]:
    """Skip one top-level trigger block, returning next index and new depth."""
    depth = initial_depth
    index = start
    while index < len(lines):
        line = lines[index]
        depth += line.count("{") - line.count("}")
        index += 1
        if depth == 1:
            return index, depth
    raise ValueError("unterminated building availability block")


def quarantine(source: Path, adapters: set[str]) -> tuple[bytes, list[str]]:
    lines = source.read_text(encoding="utf-8-sig").splitlines(keepends=True)
    compatibility = definition_compatibility(lines)
    output: list[str] = []
    keys: list[str] = []
    depth = 0
    active = False
    index = 0
    while index < len(lines):
        line = lines[index]
        match = DEFINITION.match(line.rstrip("\r\n")) if depth == 0 else None
        if match:
            key = match.group(1)
            keys.append(key)
            active = key in adapters
            output.append(line)
            depth += line.count("{") - line.count("}")
            index += 1
            if not active:
                output.append(marker(compatibility.get(key, set())))
            continue
        if not active and depth == 1 and GATE.match(line):
            index, depth = strip_top_level_gate(lines, index, depth)
            continue
        output.append(line)
        depth += line.count("{") - line.count("}")
        index += 1
        if depth == 0:
            active = False
    if depth != 0:
        raise ValueError(f"unbalanced building source: {source}")
    rendered = clean_text("".join(output))
    return b"\xef\xbb\xbf" + rendered.encode("utf-8"), keys


def inventory() -> dict[str, object]:
    sources = installed_sources()
    installed: set[str] = set()
    for source in sources.values():
        installed.update(definition_keys(source))
    adapters = active_adapters(installed)
    custom = custom_keys()
    overlap = sorted(installed.intersection(custom))
    if overlap:
        raise ValueError(f"custom building keys collide with installed keys: {overlap}")
    files: list[dict[str, object]] = []
    for relative, source in sorted(sources.items()):
        rendered, keys = quarantine(source, adapters)
        files.append(
            {
                "relative": relative,
                "source": str(source),
                "source_sha256": sha256(source.read_bytes()),
                "rendered_sha256": sha256(rendered),
                "definitions": keys,
                "target": (RELATIVE / relative).as_posix(),
            }
        )
    return {
        "game_version": "1.3.11",
        "installed_file_count": len(files),
        "installed_definition_count": len(installed),
        "quarantined_definition_count": len(installed - adapters),
        "engine_adapter_definition_count": len(adapters),
        "engine_adapter_definitions": sorted(adapters),
        "active_custom_definition_count": len(custom),
        "active_custom_definitions": sorted(custom),
        "files": files,
    }


def canonical(value: dict[str, object]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write() -> None:
    value = inventory()
    sources = installed_sources()
    adapters = set(value["engine_adapter_definitions"])
    for relative, source in sorted(sources.items()):
        rendered, _ = quarantine(source, adapters)
        target = TARGET / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(rendered)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_bytes(canonical(value))
    print(
        "m5_building_quarantine: wrote "
        f"{value['installed_file_count']} exact-name sources; "
        f"{value['quarantined_definition_count']} hidden legacy definitions; "
        f"{value['engine_adapter_definition_count']} active AD 1 adapters"
    )


def check() -> bool:
    failures: list[str] = []
    try:
        value = inventory()
        sources = installed_sources()
        adapters = set(value["engine_adapter_definitions"])
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"m5_building_quarantine: FAIL\n  - {exc}")
        return False
    if not MANIFEST.is_file() or MANIFEST.read_bytes() != canonical(value):
        failures.append(f"stale or missing {MANIFEST.relative_to(ROOT)}")
    for relative, source in sorted(sources.items()):
        expected, keys = quarantine(source, adapters)
        target = TARGET / relative
        if not target.is_file() or target.read_bytes() != expected:
            failures.append(f"stale or missing exact-name building shell: {target}")
            continue
        text = target.read_text(encoding="utf-8-sig")
        expected_markers = len(set(keys) - adapters)
        if text.count("ANTIQVITAS installed-building quarantine") != expected_markers:
            failures.append(f"incomplete quarantine markers: {target}")
    if failures:
        print("m5_building_quarantine: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return False
    print(
        "m5_building_quarantine: PASS "
        f"({value['quarantined_definition_count']} hidden legacy; "
        f"{value['engine_adapter_definition_count']} active adapters; "
        f"{value['active_custom_definition_count']} active custom)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            write()
            return 0
        return 0 if check() else 1
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"m5_building_quarantine: FAIL\n  - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

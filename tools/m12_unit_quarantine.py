#!/usr/bin/env python3
"""Exact-name quarantine for every installed legacy unit-type source."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
RELATIVE = Path("in_game/common/unit_types")
TARGET = ROOT / RELATIVE
CUSTOM = TARGET / "00_antiquitas_m7_units.txt"
MANIFEST = ROOT / "docs/m12/unit_quarantine_manifest.json"
DEFINITION = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\s*=\s*\{\s*(?:#.*)?$")
UPGRADE = re.compile(r"^\s*upgrades_to(?:_only)?\s*=")
VISIBILITY = re.compile(r"^\s*(?:hide|buildable)\s*=")
DEFAULT = re.compile(r"^\s*default\s*=")
COPY_FROM = re.compile(r"(?m)^\s*copy_from\s*=\s*([A-Za-z0-9_]+)")
MARKER = "\t# ANTIQVITAS installed-unit quarantine.\n\thide = yes\n\tbuildable = no\n"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
        raise ValueError("installed unit-type source union is empty")
    return mounted


def copy_graph(sources: dict[str, Path]) -> dict[str, str]:
    graph: dict[str, str] = {}
    for source in sources.values():
        depth = 0
        current: str | None = None
        body: list[str] = []
        for line in source.read_text(encoding="utf-8-sig").splitlines():
            match = DEFINITION.match(line) if depth == 0 else None
            if match:
                current = match.group(1)
                body = [line]
            elif current is not None:
                body.append(line)
            depth += line.count("{") - line.count("}")
            if current is not None and depth == 0:
                joined = "\n".join(body)
                parent = COPY_FROM.search(joined)
                if parent:
                    graph[current] = parent.group(1)
                current = None
                body = []
    return graph


def adapter_keys(sources: dict[str, Path]) -> set[str]:
    custom = CUSTOM.read_text(encoding="utf-8-sig")
    direct = set(COPY_FROM.findall(custom))
    graph = copy_graph(sources)
    installed = {
        match.group(1)
        for source in sources.values()
        for line in source.read_text(encoding="utf-8-sig").splitlines()
        if (match := DEFINITION.match(line))
    }
    missing = sorted(direct - installed)
    if missing:
        raise ValueError(f"custom copy parents missing from installed union: {missing}")
    adapters = set(direct)
    frontier = list(direct)
    while frontier:
        key = frontier.pop()
        parent = graph.get(key)
        if parent and parent not in adapters:
            adapters.add(parent)
            frontier.append(parent)
    return adapters


def quarantine(source: Path, adapters: set[str]) -> tuple[bytes, list[str]]:
    text = source.read_text(encoding="utf-8-sig")
    output: list[str] = []
    keys: list[str] = []
    depth = 0
    adapter = False
    for line in text.splitlines(keepends=True):
        match = DEFINITION.match(line.rstrip("\r\n")) if depth == 0 else None
        if match:
            keys.append(match.group(1))
            adapter = match.group(1) in adapters
        # A hidden/non-buildable compatibility shell cannot legally upgrade or
        # restate visibility. Ancient units own their own graph. Preserve the
        # exact installed parent chain used by custom units: those definitions
        # are already technical hidden/non-buildable templates.
        if not adapter and (
            UPGRADE.match(line) or VISIBILITY.match(line) or DEFAULT.match(line)
        ):
            continue
        output.append(line)
        if match and not adapter:
            output.append(MARKER)
        depth += line.count("{") - line.count("}")
        if depth == 0:
            adapter = False
    rendered = "".join(output)
    if text.endswith(("\n", "\r")) and not rendered.endswith("\n"):
        rendered += "\n"
    return b"\xef\xbb\xbf" + rendered.encode("utf-8"), keys


def inventory() -> dict[str, object]:
    sources = installed_sources()
    adapters = adapter_keys(sources)
    files: list[dict[str, object]] = []
    installed_keys: set[str] = set()
    for relative, source in sorted(sources.items()):
        rendered, keys = quarantine(source, adapters)
        installed_keys.update(keys)
        files.append(
            {
                "relative": relative,
                "source": "<GAME_ROOT>/" + source.relative_to(game_root()).as_posix(),
                "source_sha256": sha256(source.read_bytes()),
                "rendered_sha256": sha256(rendered),
                "definitions": keys,
                "target": (RELATIVE / relative).as_posix(),
            }
        )
    custom_text = CUSTOM.read_text(encoding="utf-8-sig")
    custom_keys = sorted(
        match.group(1)
        for line in custom_text.splitlines()
        if (match := DEFINITION.match(line))
    )
    overlap = sorted(installed_keys.intersection(custom_keys))
    if overlap:
        raise ValueError(f"custom unit keys collide with installed keys: {overlap}")
    return {
        "game_version": "1.3.11",
        "installed_file_count": len(files),
        "installed_definition_count": len(installed_keys),
        "quarantined_definition_count": len(installed_keys - adapters),
        "engine_adapter_definition_count": len(adapters),
        "engine_adapter_definitions": sorted(adapters),
        "active_custom_definition_count": len(custom_keys),
        "active_custom_definitions": custom_keys,
        "files": files,
    }


def canonical(value: dict[str, object]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write() -> None:
    value = inventory()
    sources = installed_sources()
    adapters = adapter_keys(sources)
    for relative, source in sorted(sources.items()):
        rendered, _ = quarantine(source, adapters)
        target = TARGET / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(rendered)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_bytes(canonical(value))
    print(
        "m12_unit_quarantine: wrote "
        f"{value['installed_file_count']} exact-name sources / "
        f"{value['installed_definition_count']} legacy shells"
    )


def check() -> bool:
    failures: list[str] = []
    try:
        value = inventory()
        sources = installed_sources()
        adapters = adapter_keys(sources)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"m12_unit_quarantine: FAIL\n  - {exc}")
        return False
    if not MANIFEST.is_file() or MANIFEST.read_bytes() != canonical(value):
        failures.append(f"stale or missing {MANIFEST.relative_to(ROOT)}")
    for relative, source in sorted(sources.items()):
        expected, keys = quarantine(source, adapters)
        target = TARGET / relative
        if not target.is_file() or target.read_bytes() != expected:
            failures.append(f"stale or missing exact-name unit shell: {target}")
            continue
        text = target.read_text(encoding="utf-8-sig")
        expected_markers = len(set(keys) - adapters)
        if (
            text.count("ANTIQVITAS installed-unit quarantine")
            != expected_markers
        ):
            failures.append(f"incomplete quarantine markers: {target}")
        for match in re.finditer(
            r"(?ms)^([A-Za-z][A-Za-z0-9_]*)\s*=\s*\{.*?(?=^[A-Za-z][A-Za-z0-9_]*\s*=\s*\{|\Z)",
            text,
        ):
            key, body = match.group(1), match.group(0)
            if key not in adapters and re.search(r"(?m)^\s*default\s*=\s*yes", body):
                failures.append(f"quarantined legacy default remains: {key}")
    if failures:
        print("m12_unit_quarantine: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return False
    print(
        "m12_unit_quarantine: PASS "
        f"({value['quarantined_definition_count']} legacy hidden/non-buildable; "
        f"{value['engine_adapter_definition_count']} copy-chain adapters; "
        f"{value['active_custom_definition_count']} active ancient)"
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
        print(f"m12_unit_quarantine: FAIL\n  - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

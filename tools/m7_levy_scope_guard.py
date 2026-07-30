#!/usr/bin/env python3
"""Independently guard the complete ANTIQVITAS levy-registry replacement."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
RELATIVE_DIR = Path("in_game/common/levies")
TARGET_DIR = ROOT / RELATIVE_DIR
ACTIVE_FILE = "05_traditions_levies.txt"
ACTIVE_KEYS = {
    "antq_levy_district_spear_muster",
    "antq_levy_seasonal_skirmishers",
}
ACTIVE_UNITS = {
    "antq_district_spear_muster",
    "antq_seasonal_skirmishers",
}
ROOT_KEY_RE = re.compile(r"^([a-z0-9_]+)\s*=\s*\{", re.MULTILINE)
UNIT_RE = re.compile(r"^\s*unit\s*=\s*([a-z0-9_]+)\s*$", re.MULTILINE)


def installed_dir() -> Path:
    data = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    path = Path(data["game_dir"]) / "game" / RELATIVE_DIR
    if not path.is_dir():
        raise ValueError(f"installed levy registry is missing: {path}")
    return path


def registry_files(directory: Path) -> dict[str, Path]:
    return {
        path.name: path
        for path in sorted(directory.glob("*.txt"))
        if path.name[:1].isdigit()
    }


def check() -> bool:
    failures: list[str] = []
    installed = registry_files(installed_dir())
    targets = registry_files(TARGET_DIR)
    if set(targets) != set(installed):
        missing = sorted(set(installed) - set(targets))
        extra = sorted(set(targets) - set(installed))
        if missing:
            failures.append(f"missing exact levy mirrors: {', '.join(missing)}")
        if extra:
            failures.append(f"unexpected levy mirrors: {', '.join(extra)}")

    installed_keys: set[str] = set()
    for path in installed.values():
        installed_keys.update(ROOT_KEY_RE.findall(path.read_text(encoding="utf-8-sig")))

    active_keys: set[str] = set()
    active_units: set[str] = set()
    for name, path in targets.items():
        text = path.read_text(encoding="utf-8-sig")
        keys = set(ROOT_KEY_RE.findall(text))
        units = set(UNIT_RE.findall(text))
        if name == ACTIVE_FILE:
            active_keys.update(keys)
            active_units.update(units)
            continue
        if keys or units:
            failures.append(f"quarantined levy source remains active: {name}")
        if "installed levy registry quarantined" not in text:
            failures.append(f"quarantine marker missing: {name}")

    if active_keys != ACTIVE_KEYS:
        failures.append(
            "active levy keys differ from the two reviewed ancient adapters"
        )
    if active_units != ACTIVE_UNITS:
        failures.append(
            "active levy unit links differ from the two reviewed ancient units"
        )
    leaked = sorted(installed_keys & active_keys)
    if leaked:
        failures.append(f"installed levy definitions remain active: {', '.join(leaked)}")

    if failures:
        print("m7_levy_scope_guard: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return False
    print(
        "m7_levy_scope_guard: PASS "
        f"({len(targets)} exact mirrors; {len(installed_keys)} installed definitions "
        "quarantined; 2 ancient levy adapters active)"
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
            print(
                "m7_levy_scope_guard: levy files are owned by tools/m7_war.py; "
                "checking generated output"
            )
        return 0 if check() else 1
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"m7_levy_scope_guard: FAIL\n  - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Guard the one installed flag predicate that dereferences an absent capital."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
SOURCE_RELATIVE = Path("game/main_menu/common/flag_definitions/00_flag_definitions.txt")
OUTPUT = ROOT / "main_menu/common/flag_definitions/00_flag_definitions.txt"
TARGET = re.compile(
    r"^(?P<indent>\s*)capital\s*=\s*location:sitges(?P<suffix>\s*(?:#.*)?(?:\r?\n)?)$"
)


def source_path() -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        source = Path(str(config["game_dir"])) / SOURCE_RELATIVE
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed flag-definition source: {exc}") from exc
    if not source.is_file():
        raise ValueError(f"installed flag-definition source is missing: {source}")
    return source


def render() -> bytes:
    source = source_path()
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    rendered: list[str] = []
    replacements = 0
    for line in raw.decode("utf-8-sig").splitlines(keepends=True):
        target = TARGET.match(line)
        if target is None:
            rendered.append(line)
            continue
        rendered.append(
            f"{target.group('indent')}capital ?= location:sitges"
            f"{target.group('suffix')}"
        )
        replacements += 1
    if replacements != 1:
        raise ValueError(
            f"expected one Catalan Sitges-capital predicate, found {replacements}"
        )
    result = "".join(rendered).encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + result


def write() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(render())
    print(f"m12_flag_capital_guard: wrote {OUTPUT.relative_to(ROOT)}")


def check() -> bool:
    try:
        expected = render()
    except (OSError, ValueError) as exc:
        print(f"m12_flag_capital_guard: FAIL\n  - {exc}")
        return False
    if not OUTPUT.is_file() or OUTPUT.read_bytes() != expected:
        print(f"m12_flag_capital_guard: FAIL\n  - stale or missing {OUTPUT.relative_to(ROOT)}")
        return False
    print(
        "m12_flag_capital_guard: PASS "
        "(one optional Catalan Sitges-capital flag predicate)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        try:
            write()
        except (OSError, ValueError) as exc:
            print(f"m12_flag_capital_guard: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())

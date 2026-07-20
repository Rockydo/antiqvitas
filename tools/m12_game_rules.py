#!/usr/bin/env python3
"""Render the exact installed game-rule file with observer country change enabled.

The game driver must enter Observer through the country-change surface. The
installed default prohibits that transition, so this guarded exact-name overlay
preserves every local rule and changes only the one default used by the
automated test playset. Re-rendering from the installed file makes a game patch
or contract drift fail validation rather than silently carrying an old copy.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
OUTPUT = ROOT / "main_menu/common/game_rules/00_game_rules.txt"
COUNTRY_CHANGE = re.compile(r"^\s*country_change\s*=\s*\{\s*(?:#.*)?$")
PROHIBITED_DEFAULT = re.compile(
    r"^(?P<prefix>\s*default\s*=\s*)country_change_prohibited(?P<suffix>\s*(?:#.*)?(?:\r?\n)?)$"
)


def source_file() -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        path = Path(config["game_dir"]) / "game/main_menu/common/game_rules/00_game_rules.txt"
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed game-rule file: {exc}") from exc
    if not path.is_file():
        raise ValueError(f"installed game-rule file is missing: {path}")
    return path


def brace_delta(line: str) -> int:
    code = line.split("#", 1)[0]
    return code.count("{") - code.count("}")


def render() -> bytes:
    source = source_file()
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    rendered: list[str] = []
    depth = 0
    in_country_change = False
    replacements = 0
    blocks = 0
    for line in lines:
        code = line.split("#", 1)[0]
        if depth == 0 and COUNTRY_CHANGE.match(code):
            in_country_change = True
            blocks += 1
        match = PROHIBITED_DEFAULT.match(line) if in_country_change and depth == 1 else None
        if match:
            newline = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
            line = f"{match.group('prefix')}country_change_allowed # ANTIQVITAS enables autonomous observer{newline}"
            replacements += 1
        rendered.append(line)
        depth += brace_delta(code)
        if depth < 0:
            raise ValueError(f"{source.name}: brace depth became negative")
        if in_country_change and depth == 0:
            in_country_change = False
    if depth != 0:
        raise ValueError(f"{source.name}: brace depth ends at {depth}")
    if blocks != 1:
        raise ValueError(f"{source.name}: expected one country_change rule, found {blocks}")
    if replacements != 1:
        raise ValueError(f"{source.name}: expected one prohibited country-change default, found {replacements}")
    result = "".join(rendered).encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + result


def write() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(render())
    print(f"m12_game_rules: wrote {OUTPUT.relative_to(ROOT)}")


def check() -> bool:
    try:
        expected = render()
    except (OSError, ValueError) as exc:
        print(f"m12_game_rules: FAIL\n  - {exc}")
        return False
    if not OUTPUT.is_file():
        print(f"m12_game_rules: FAIL\n  - missing {OUTPUT.relative_to(ROOT)}")
        return False
    if OUTPUT.read_bytes() != expected:
        print(f"m12_game_rules: FAIL\n  - stale {OUTPUT.relative_to(ROOT)}")
        return False
    print("m12_game_rules: PASS (exact installed rules; country-change default enabled for observer)")
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
            print(f"m12_game_rules: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())

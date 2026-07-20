#!/usr/bin/env python3
"""Hide post-antique vanilla scriptable hints through a guarded exact-name overlay.

Generic instructional hints remain useful to an AD 1 campaign. The selected
definitions instead name post-476 crises, states, or dynasties that cannot be
honestly surfaced during ANTIQVITAS's date range. The installed source is
re-read at every check so a game update cannot silently change this override.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
SOURCE_RELATIVE = Path("game/in_game/common/scriptable_hints/scripted_hints.txt")
OUTPUT = ROOT / "in_game/common/scriptable_hints/scripted_hints.txt"
EXPECTED_TARGET_COUNT = 33
TARGETS = (
    "hint_coup_attempt",
    "hint_crisis_of_the_chinese_dynasty",
    "hint_fall_of_delhi",
    "hint_black_death",
    "hint_rise_of_the_ottomans",
    "hint_golden_age_of_piracy",
    "hint_hundred_years_war",
    "hint_hussite_wars",
    "hint_italian_wars",
    "hint_little_ice_age",
    "hint_the_revolution",
    "hint_treaty_of_tordesillas",
    "hint_great_pestilence",
    "hint_columbian_exchange",
    "hint_western_schism",
    "hint_reformation",
    "hint_council_of_trent",
    "hint_war_of_religions",
    "hint_guelphs_and_ghibellines",
    "hint_colonial_revolution",
    "hint_red_turban_rebellions",
    "hint_rise_of_timur",
    "hint_sengoku",
    "hint_nanbokuchou",
    "hint_turmoil_in_brandenburg",
    "hint_holland",
    "hint_hungary",
    "hint_norway",
    "hint_naples",
    "hint_castile",
    "hint_ottomans",
    "hint_hre",
    "hint_eastern_roman_empire",
)
TARGET_SET = frozenset(TARGETS)
HEADER = re.compile(r"^(?P<indent>\s*)(?P<name>hint_[A-Za-z0-9_]+)\s*=\s*\{")
PRIORITY = re.compile(r"^(?P<indent>\s*)priority\s*=\s*\{")


def source_path() -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        source = Path(str(config["game_dir"])) / SOURCE_RELATIVE
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed scriptable hints: {exc}") from exc
    if not source.is_file():
        raise ValueError(f"installed scriptable hints are missing: {source}")
    return source


def brace_delta(line: str) -> int:
    code = line.split("#", 1)[0]
    return code.count("{") - code.count("}")


def render() -> bytes:
    source = source_path()
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    rendered: list[str] = []
    depth = 0
    current: str | None = None
    seen: set[str] = set()
    disabled: set[str] = set()
    for line in lines:
        code = line.split("#", 1)[0]
        header = HEADER.match(code) if depth == 0 else None
        if header is not None:
            name = header.group("name")
            current = name if name in TARGET_SET else None
            if current is not None:
                seen.add(current)
        priority = PRIORITY.match(code) if current is not None and depth == 1 else None
        rendered.append(line)
        if priority is not None:
            if brace_delta(code) != 1:
                raise ValueError(f"{current}: priority contract is not a multiline block")
            newline = "\r\n" if line.endswith("\r\n") else "\n"
            rendered.append(
                f"{priority.group('indent')}\talways = no # M12 disables post-antique vanilla hint{newline}"
            )
            disabled.add(current)
        depth += brace_delta(line)
        if depth < 0:
            raise ValueError("scriptable hints brace depth became negative")
        if depth == 0:
            current = None
    if depth != 0:
        raise ValueError(f"scriptable hints brace depth ends at {depth}")
    if len(TARGETS) != EXPECTED_TARGET_COUNT:
        raise ValueError(f"target inventory drift: expected {EXPECTED_TARGET_COUNT}, found {len(TARGETS)}")
    if seen != TARGET_SET:
        raise ValueError(f"target definitions drift: missing={sorted(TARGET_SET - seen)}")
    if disabled != TARGET_SET:
        raise ValueError(f"target priority gates drift: missing={sorted(TARGET_SET - disabled)}")
    result = "".join(rendered).encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + result


def write() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(render())
    print(f"m12_disable_historical_hints: wrote {OUTPUT.relative_to(ROOT)}")


def check() -> bool:
    try:
        expected = render()
    except (OSError, ValueError) as exc:
        print(f"m12_disable_historical_hints: FAIL\n  - {exc}")
        return False
    if not OUTPUT.is_file() or OUTPUT.read_bytes() != expected:
        print(f"m12_disable_historical_hints: FAIL\n  - stale or missing {OUTPUT.relative_to(ROOT)}")
        return False
    print(
        "m12_disable_historical_hints: PASS "
        f"({EXPECTED_TARGET_COUNT} exact-name post-antique hint gates)"
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
            print(f"m12_disable_historical_hints: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())

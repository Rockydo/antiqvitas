#!/usr/bin/env python3
"""Exact overlays for installed market links unsafe during AD 1 initialization."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
EXPECTED = {
    "in_game/common/generic_actions/languages.txt": 2,
    "in_game/common/generic_actions/markets.txt": 1,
    "in_game/common/generic_actions/religious_factions.txt": 1,
    "in_game/common/peace_treaties/sound_toll_exemption.txt": 1,
    "in_game/common/scripted_triggers/situation_triggers.txt": 2,
}
UNSAFE = re.compile(r"(?m)^(?P<indent>[ \t]+)market\s*=\s*\{")


def clean_text(text: str) -> str:
    return "\n".join(line.rstrip(" \t") for line in text.splitlines()).rstrip("\n") + "\n"


def game_root() -> Path:
    data = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    return Path(data["game_dir"]) / "game"


def render(relative: str, expected_count: int) -> bytes:
    source = game_root() / relative
    raw = source.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    text, count = UNSAFE.subn(r"\g<indent>market ?= {", text)
    if count != expected_count:
        raise ValueError(
            f"{relative}: expected {expected_count} unsafe market links, found {count}"
        )
    text = clean_text(text)
    encoded = text.encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + encoded


def outputs() -> dict[Path, bytes]:
    return {
        ROOT / relative: render(relative, count)
        for relative, count in EXPECTED.items()
    }


def write() -> None:
    for path, content in outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        print(f"m5_market_scope_guard: wrote {path.relative_to(ROOT)}")


def check() -> bool:
    expected = outputs()
    stale = [
        path.relative_to(ROOT)
        for path, content in expected.items()
        if not path.is_file() or path.read_bytes() != content
    ]
    if stale:
        print(
            "m5_market_scope_guard: FAIL\n  - stale or missing "
            + ", ".join(map(str, stale))
        )
        return False
    digest = hashlib.sha256(b"".join(expected.values())).hexdigest()[:12]
    print(
        "m5_market_scope_guard: PASS "
        f"({sum(EXPECTED.values())} optional links across {len(EXPECTED)} exact sources; {digest})"
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
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"m5_market_scope_guard: FAIL\n  - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

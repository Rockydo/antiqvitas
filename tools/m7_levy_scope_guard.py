#!/usr/bin/env python3
"""Guard the installed tribal-cavalry levy against an unset AD 1 market."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
RELATIVE = Path("in_game/common/levies/06_tribal_levies.txt")
TARGET = ROOT / RELATIVE
UNSAFE = "\t\t\tmarket = {\n"
SAFE = "\t\t\tmarket ?= {\n"


def source() -> Path:
    data = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    path = Path(data["game_dir"]) / "game" / RELATIVE
    if not path.is_file():
        raise ValueError(f"installed tribal levy source is missing: {path}")
    return path


def rendered() -> bytes:
    path = source()
    content = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    if content.count(UNSAFE) != 1:
        raise ValueError(
            "installed tribal levy drift: expected exactly one unsafe market link"
        )
    content = content.replace(UNSAFE, SAFE)
    content = "\n".join(line.rstrip(" \t") for line in content.splitlines()).rstrip("\n") + "\n"
    return b"\xef\xbb\xbf" + content.encode("utf-8")


def check() -> bool:
    expected = rendered()
    if not TARGET.is_file() or TARGET.read_bytes() != expected:
        print(f"m7_levy_scope_guard: FAIL\n  - stale or missing {TARGET.relative_to(ROOT)}")
        return False
    text = TARGET.read_text(encoding="utf-8-sig")
    if text.count("market ?= {") != 1 or UNSAFE in text:
        print("m7_levy_scope_guard: FAIL\n  - optional market guard is not exact")
        return False
    print(
        "m7_levy_scope_guard: PASS "
        f"(source {hashlib.sha256(source().read_bytes()).hexdigest()[:12]}; "
        "tribal cavalry retains horse-market semantics)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        expected = rendered()
        if args.write:
            TARGET.parent.mkdir(parents=True, exist_ok=True)
            TARGET.write_bytes(expected)
            print(f"m7_levy_scope_guard: wrote {TARGET.relative_to(ROOT)}")
            return 0
        return 0 if check() else 1
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"m7_levy_scope_guard: FAIL\n  - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Guard the one absent legacy-country scope in customizable country names."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
SOURCE_RELATIVE = Path("game/in_game/common/customizable_localization/countries.txt")
OUTPUT = ROOT / "in_game/common/customizable_localization/countries.txt"
TARGET_LINE = 140
COMPARISON = re.compile(
    r"^(?P<indent>\s*)government_type\s*=\s*government_type:(?P<kind>steppe_horde)"
    r"(?P<suffix>\s*(?:#.*)?(?:\r?\n)?)$"
)


def source_path() -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        source = Path(str(config["game_dir"])) / SOURCE_RELATIVE
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed country-localization source: {exc}") from exc
    if not source.is_file():
        raise ValueError(f"installed country-localization source is missing: {source}")
    return source


def render() -> bytes:
    raw = source_path().read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    if len(lines) < TARGET_LINE:
        raise ValueError(f"country-localization source has only {len(lines)} lines")
    comparison = COMPARISON.match(lines[TARGET_LINE - 1])
    if comparison is None:
        raise ValueError(f"expected steppe-horde comparison at source line {TARGET_LINE}")
    lines[TARGET_LINE - 1] = (
        f"{comparison.group('indent')}government_type ?= government_type:steppe_horde"
        f"{comparison.group('suffix')}"
    )
    result = "".join(lines).encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + result


def write() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(render())
    print(f"m12_country_loc_scope_guard: wrote {OUTPUT.relative_to(ROOT)}")


def check() -> bool:
    try:
        expected = render()
    except (OSError, ValueError) as exc:
        print(f"m12_country_loc_scope_guard: FAIL\n  - {exc}")
        return False
    if not OUTPUT.is_file() or OUTPUT.read_bytes() != expected:
        print(f"m12_country_loc_scope_guard: FAIL\n  - stale or missing {OUTPUT.relative_to(ROOT)}")
        return False
    print("m12_country_loc_scope_guard: PASS (one optional legacy-horde comparison)")
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
            print(f"m12_country_loc_scope_guard: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())

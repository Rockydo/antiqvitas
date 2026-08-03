#!/usr/bin/env python3
"""Exact-name overlays for installed scripts that query removed institutions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from dates import AntqDate, END
from legacy_institutions import legacy_references, neutralize_references


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
RELATIVES = (
    "in_game/common/bureaucracies/generic.txt",
    "in_game/common/customizable_localization/character_title.txt",
    "in_game/common/disasters/revolution_disaster.txt",
    "in_game/common/movements/calvinism_movement.txt",
    "in_game/common/movements/lutheranism_movement.txt",
    "in_game/common/religious_focuses/nahuatl.txt",
    "in_game/common/scripted_effects/___test_effects.txt",
    "in_game/common/scripted_triggers/institution_triggers.txt",
    "in_game/common/tests/age_of_discovery_tests.txt",
    "main_menu/common/achievements/standard_achievements.txt",
    "main_menu/gfx/portraits/portrait_modifiers/01_headwear_special.txt",
)
# The two installed legacy situations are owned by r5_visible_unions.py, which
# applies the stronger exact-quarantine contract after institution replacement.
EMPTY_RELATIVES = frozenset((
    "in_game/common/scripted_effects/___test_effects.txt",
    "in_game/common/tests/age_of_discovery_tests.txt",
))
NAHUATL_GUARD = re.compile(
    r"(?P<indent>\s*)limit\s*=\s*\{\s*"
    r"NOT\s*=\s*\{\s*"
    r"has_embraced_institution\s*=\s*institution:legalism\s*"
    r"\}\s*\}",
    re.MULTILINE,
)
DATE = re.compile(r"(?<![0-9])-?[0-9]{1,4}\.[0-9]{1,2}\.[0-9]{1,2}(?![0-9])")
INSTITUTION_MARKET = re.compile(r"(?m)^(?P<indent>[ \t]+)market\s*=\s*\{")


def sanitize_date(match: re.Match[str]) -> str:
    value = match.group(0)
    if value.startswith("-"):
        return value
    year = int(value.split(".", 1)[0])
    return AntqDate(*END).engine() if year > END[0] else value


def game_root() -> Path:
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    root = Path(config["game_dir"]) / "game"
    if not root.is_dir():
        raise ValueError(f"installed game root is missing: {root}")
    return root


def render(relative: str) -> bytes:
    source = game_root() / relative
    raw = source.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    if relative in EMPTY_RELATIVES:
        label = "test content"
        text = f"# ANTIQVITAS disables installed {label}; no post-antique institution references.\n"
    else:
        text = raw.decode("utf-8-sig")
        if not legacy_references(text):
            raise ValueError(f"{relative}: installed source no longer references legacy institutions")
        if relative.endswith("/nahuatl.txt"):
            text, count = NAHUATL_GUARD.subn(
                lambda match: f"{match.group('indent')}limit = {{ always = no }} "
                "# ANTIQVITAS removes the Legalism propagation branch",
                text,
            )
            if count != 1:
                raise ValueError(f"{relative}: expected one Nahuatl Legalism effect guard, found {count}")
        text = neutralize_references(text, remap_effects=True)
        text = DATE.sub(sanitize_date, text)
        if relative.endswith("/scripted_triggers/institution_triggers.txt"):
            text, count = INSTITUTION_MARKET.subn(
                r"\g<indent>market ?= {",
                text,
            )
            if count != 1:
                raise ValueError(
                    f"{relative}: expected one optional market guard, found {count}"
                )
    encoded = text.encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + encoded


def outputs() -> dict[Path, bytes]:
    return {ROOT / relative: render(relative) for relative in RELATIVES}


def write() -> None:
    for path, content in outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        print(f"m8_legacy_institution_purge: wrote {path.relative_to(ROOT)}")


def check() -> bool:
    try:
        expected = outputs()
    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"m8_legacy_institution_purge: FAIL\n  - {exc}")
        return False
    stale = [
        path.relative_to(ROOT)
        for path, content in expected.items()
        if not path.is_file() or path.read_bytes() != content
    ]
    if stale:
        print("m8_legacy_institution_purge: FAIL\n  - stale or missing " + ", ".join(map(str, stale)))
        return False
    print(f"m8_legacy_institution_purge: PASS ({len(expected)} exact-name overlays)")
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
        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"m8_legacy_institution_purge: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())

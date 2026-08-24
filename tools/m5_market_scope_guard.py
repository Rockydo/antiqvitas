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
    "in_game/common/scripted_triggers/situation_triggers.txt": 2,
}
UNSAFE = re.compile(r"(?m)^(?P<indent>[ \t]+)market\s*=\s*\{")
MARKET_CENTER_TEST = "\t\t\tnot = { this = market.location }"
MARKET_TREATY_TEST = (
    "\t\t\tnot = {\n"
    "\t\t\t\tmarket ?= {\n"
    "\t\t\t\t\towner = {\n"
    "\t\t\t\t\t\thas_trade_treaty_with = scope:actor\n"
    "\t\t\t\t\t}\n"
    "\t\t\t\t}\n"
    "\t\t\t}"
)
MARKET_EMBARGO_TEST = (
    "\t\t\t\tscope:actor = {\n"
    "\t\t\t\t\tnot = { is_embargoed_by = root.owner }\n"
    "\t\t\t\t}"
)
MARKET_EMBARGO_GUARD = (
    "\t\t\t\tAND = {\n"
    "\t\t\t\t\towner != scope:actor\n"
    "\t\t\t\t\tscope:actor = {\n"
    "\t\t\t\t\t\tnot = { is_embargoed_by = root.owner }\n"
    "\t\t\t\t\t}\n"
    "\t\t\t\t}"
)
MARKET_ISOLATION_TEST = (
    "\t\t\t\troot.owner = {\n"
    "\t\t\t\t\tor = {\n"
    "\t\t\t\t\t\tmodifier:trade_isolation = no\n"
    "\t\t\t\t\t\tgives_isolation_exemption_to = scope:actor\n"
    "\t\t\t\t\t}\n"
    "\t\t\t\t}"
)
MARKET_ISOLATION_GUARD = (
    "\t\t\t\tAND = {\n"
    "\t\t\t\t\towner != scope:actor\n"
    "\t\t\t\t\troot.owner = {\n"
    "\t\t\t\t\t\tor = {\n"
    "\t\t\t\t\t\t\tmodifier:trade_isolation = no\n"
    "\t\t\t\t\t\t\tgives_isolation_exemption_to = scope:actor\n"
    "\t\t\t\t\t\t}\n"
    "\t\t\t\t\t}\n"
    "\t\t\t\t}"
)


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
    if relative == "in_game/common/generic_actions/languages.txt":
        text, ai_count = re.subn(
            r"(?m)^(?P<indent>[ \t]*)(?P<field>ai_tick|automation_tick)\s*=\s*monthly(?P<tail>[ \t]*)$",
            r"\g<indent>\g<field> = never\g<tail>",
            text,
        )
        if ai_count != 4:
            raise ValueError(
                f"{relative}: expected four unsafe multi-target language scheduler ticks, "
                f"found {ai_count}"
            )
    if relative == "in_game/common/generic_actions/markets.txt":
        if text.count(MARKET_CENTER_TEST) != 1:
            raise ValueError(
                f"{relative}: installed create-market center-test contract changed"
            )
        if text.count(MARKET_TREATY_TEST) != 1:
            raise ValueError(
                f"{relative}: installed create-market treaty-test contract changed"
            )
        if text.count(MARKET_EMBARGO_TEST) != 2:
            raise ValueError(
                f"{relative}: installed create-trade self-embargo contract changed"
            )
        if text.count(MARKET_ISOLATION_TEST) != 1:
            raise ValueError(
                f"{relative}: installed create-trade isolation-exemption contract changed"
            )
        text = text.replace(
            MARKET_CENTER_TEST,
            "\t\t\tNOT = { market ?= { location = prev } }",
            1,
        )
        text = text.replace(
            MARKET_TREATY_TEST,
            # Asking the existing market owner whether it has a treaty with
            # the actor asserts when both scopes are the same country. The
            # actual invalid target is already covered by direct ownership.
            "\t\t\tNOT = { market ?= { owner = { this = scope:actor } } }",
            1,
        )
        # Both source- and destination-market selectors otherwise ask a
        # market owner whether it embargoes itself.  Script OR branches are
        # evaluated for candidate scoring even when the direct-owner branch
        # already succeeds, so the explicit inequality is required.
        text = text.replace(MARKET_EMBARGO_TEST, MARKET_EMBARGO_GUARD, 2)
        # Han begins with four owned markets under trade isolation. Candidate
        # scoring evaluates this branch even though direct ownership already
        # admits those markets, making the native exemption lookup ask Han for
        # its diplomatic relation with itself. Foreign markets still use the
        # installed isolation/exemption contract unchanged.
        text = text.replace(MARKET_ISOLATION_TEST, MARKET_ISOLATION_GUARD, 1)
        marker = "\ncreate_market = {"
        if text.count(marker) != 1:
            raise ValueError(f"{relative}: create_market action inventory changed")
        text = text.replace(
            marker,
            "\n# ANTIQVITAS: safe center, owner, and optional-market tests for seeded AD 1 markets.\n"
            "# These prevent unset location lookups and country self-relations.\n"
            + marker,
            1,
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

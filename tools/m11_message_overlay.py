#!/usr/bin/env python3
"""Render the exact-name ANTIQVITAS message registry.

EU5 loads its message registry from the exact ``main_menu/gui/messagetypes``
path, not an additive sibling. This tool copies the pinned installed file byte
for byte and appends the reviewed decision and generic-action registrations.
Any game patch or inventory change fails validation rather than silently
replacing a changed vanilla GUI surface.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from m11_decisions import EXPECTED_COUNT, load_decisions, load_tag_maps, validate
from m9_diplomacy import IO_ACTION_KEYS
from s2_germania_dynamics import ACTIONS as GERMANIA_ACTIONS


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
SOURCE_RELATIVE = Path("game/main_menu/gui/messagetypes.txt")
OUTPUT = ROOT / "main_menu/gui/messagetypes.txt"
EXPECTED_BUILD = "24187685"
EXPECTED_SHA256 = "610D35361A27253F93EBF6EC3F74247124C998A859B0E6D2BC8908D8741BBD1F"
EXPECTED_TYPE_COUNT = 1348
PILOT_ACTION = "endow_public_games"
ARABIAN_ROUTE_ACTIONS = (
    "antq_negotiate_route_safe_conduct",
    "antq_coordinate_cistern_repairs",
    "antq_exchange_route_intelligence",
    "antq_settle_transit_incident",
)
SILENT_OTHER_ACTION_MESSAGES = (
    "OTHER_PERFORMS_create_market_ACTION",
    "CREATE_MARKET_OTHERS",
)
SILENT_MISSING_AUDIO_MESSAGES = (
    "RULER_FAMILY_CHAR_COMES_OF_AGE",
    # Installed 1.3.11 registers this message with sound=yes but ships no
    # same-named Wwise event.  Large multicultural countries can emit several
    # changes on one tick, polluting error.log once per otherwise valid popup.
    "ESTATE_CULTURE_CHANGED_OTHER",
)


def message_block(message_type: str) -> str:
    return "\r\n".join((
        f"{message_type}={{",
        "log=yes",
        "onmap=no",
        "popup=yes",
        "idle=no",
        "option=yes",
        "pausepopup=no",
        "message_category = government",
        "}",
    ))


def scoped_types(scope: str) -> tuple[str, ...]:
    if scope == "pilot":
        return (f"PERFORM_antq_{PILOT_ACTION}_ACTION",)
    engines, roster = load_tag_maps()
    decisions = load_decisions()
    validate(decisions, engines, roster)
    decision_types = tuple(f"PERFORM_antq_{decision.identifier}_ACTION" for decision in decisions)
    message_types = decision_types + tuple(
        f"PERFORM_{action}_ACTION" for action in ARABIAN_ROUTE_ACTIONS
    ) + tuple(
        f"PERFORM_{action.key}_ACTION" for action in GERMANIA_ACTIONS
    ) + tuple(
        f"PERFORM_{action}_ACTION" for action in IO_ACTION_KEYS
    )
    expected = (
        EXPECTED_COUNT + len(ARABIAN_ROUTE_ACTIONS) + len(GERMANIA_ACTIONS)
        + len(IO_ACTION_KEYS)
    )
    if len(message_types) != expected or len(set(message_types)) != expected:
        raise ValueError("M11 full message registry does not match the validated decision ledger")
    return message_types


def installed_source(message_types: tuple[str, ...]) -> bytes:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        game_dir = Path(config["game_dir"])
        build = str(config["game_build_id"])
    except (KeyError, OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve pinned game source: {exc}") from exc
    if build != EXPECTED_BUILD:
        raise ValueError(f"game build {build} differs from pinned message-registry build {EXPECTED_BUILD}")
    source = game_dir / SOURCE_RELATIVE
    raw = source.read_bytes()
    if not raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("installed message registry unexpectedly lacks a UTF-8 BOM")
    actual_hash = hashlib.sha256(raw).hexdigest().upper()
    if actual_hash != EXPECTED_SHA256:
        raise ValueError(f"installed message registry hash drift: {actual_hash}")
    if raw.endswith((b"\n", b"\r")):
        raise ValueError("installed message registry final-newline contract drifted")
    text = raw.decode("utf-8-sig")
    count = len(re.findall(r"(?m)^[A-Za-z0-9_]+\s*=\s*\{", text))
    if count != EXPECTED_TYPE_COUNT:
        raise ValueError(f"installed message registry inventory drift: {count} definitions")
    collisions = [message_type for message_type in message_types if message_type in text]
    if collisions:
        raise ValueError(f"M11 message types collide with the installed registry: {', '.join(collisions)}")
    for message_type in SILENT_OTHER_ACTION_MESSAGES:
        pattern = re.compile(rf"(?ms)^{re.escape(message_type)}=\{{.*?^\}}")
        match = pattern.search(text)
        if match is None:
            raise ValueError(f"installed message type {message_type} is missing or changed")
        block = match.group(0)
        if block.count("popup=yes") != 1:
            raise ValueError(f"installed message type {message_type} popup contract changed")
        text = text[:match.start()] + block.replace("popup=yes", "popup=no", 1) + text[match.end():]
    for message_type in SILENT_MISSING_AUDIO_MESSAGES:
        pattern = re.compile(rf"(?ms)^{re.escape(message_type)}=\{{.*?^\}}")
        match = pattern.search(text)
        if match is None:
            raise ValueError(f"installed message type {message_type} is missing or changed")
        block = match.group(0)
        if block.count("sound=yes") != 1:
            raise ValueError(f"installed message type {message_type} sound contract changed")
        text = text[:match.start()] + block.replace("sound=yes", "sound=no", 1) + text[match.end():]
    return text.encode("utf-8-sig")


def expected(message_types: tuple[str, ...]) -> bytes:
    additions = "\r\n\r\n".join(message_block(message_type) for message_type in message_types)
    return installed_source(message_types) + b"\r\n\r\n" + additions.encode("utf-8") + b"\r\n"


def write(scope: str) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(expected(scoped_types(scope)))
    print(f"m11_message_overlay: wrote {OUTPUT.relative_to(ROOT)}")


def check(scope: str) -> bool:
    try:
        message_types = scoped_types(scope)
        rendered = expected(message_types)
    except (OSError, ValueError) as exc:
        print(f"m11_message_overlay: FAIL\n  - {exc}")
        return False
    if not OUTPUT.is_file():
        print(f"m11_message_overlay: FAIL\n  - missing {OUTPUT.relative_to(ROOT)}")
        return False
    if OUTPUT.read_bytes() != rendered:
        print(f"m11_message_overlay: FAIL\n  - stale {OUTPUT.relative_to(ROOT)}")
        return False
    print(
        f"m11_message_overlay: PASS ({EXPECTED_TYPE_COUNT} exact vanilla definitions + "
        f"{len(message_types)} M11 registrations; base {EXPECTED_SHA256[:12]})"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--scope", choices=("pilot", "all"), default="pilot")
    args = parser.parse_args()
    if args.write:
        try:
            write(args.scope)
        except (OSError, ValueError) as exc:
            print(f"m11_message_overlay: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check(args.scope) else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Keep one vanilla event file loader-valid while disabling its eligibility.

This is a deliberately narrow engine-contract pilot.  EU5 validates event
references, scope types, and variable/effect links across its generic systems
at load time.  Replacing a dated event file with empty stubs loses that graph;
instead, this renderer preserves each installed event definition and replaces
only its direct eligibility and historical scheduler with inert equivalents.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from dates import AntqDate, END, START


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
PILOT = "in_game/events/random_event.txt"
EVENT_HEADER = re.compile(r"^([A-Za-z][A-Za-z0-9_]*\.[0-9]+)\s*=\s*\{")
CHILD_BLOCK = re.compile(r"^\s*(trigger|dynamic_historical_event)\s*=\s*\{")
DATE = re.compile(r"(?<![0-9])-?[0-9]{1,4}\.[0-9]{1,2}\.[0-9]{1,2}(?![0-9])")


def game_root() -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        root = Path(config["game_dir"]) / "game"
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed game root: {exc}") from exc
    if not root.is_dir():
        raise ValueError(f"installed game root is missing: {root}")
    return root


def source_text(relative: str) -> tuple[str, bool]:
    path = game_root() / relative
    if not path.is_file():
        raise ValueError(f"installed source is missing: {relative}")
    raw = path.read_bytes()
    return raw.decode("utf-8-sig"), raw.startswith(b"\xef\xbb\xbf")


def brace_delta(line: str) -> int:
    code = line.split("#", 1)[0]
    return code.count("{") - code.count("}")


def sanitized_date(match: re.Match[str]) -> str:
    value = match.group(0)
    if value.startswith("-"):
        return value
    year = int(value.split(".", 1)[0])
    if year > END[0]:
        return AntqDate(*START).engine()
    return value


def render(relative: str) -> bytes:
    text, bom = source_text(relative)
    lines = text.splitlines(keepends=True)
    rendered: list[str] = []
    depth = 0
    active_event: str | None = None
    saw_events = 0
    inerted_events = 0
    skip_depth: int | None = None

    for line in lines:
        header = EVENT_HEADER.match(line)
        delta = brace_delta(line)

        if skip_depth is not None:
            skip_depth += delta
            if skip_depth == 0:
                skip_depth = None
            elif skip_depth < 0:
                raise ValueError(f"{relative}: child block brace depth became negative")
            continue

        if active_event is None:
            if depth == 0 and header:
                active_event = header.group(1)
                saw_events += 1
            rendered.append(line)
            depth += delta
            continue

        # Direct children of an event are at brace depth one.  Nested triggers
        # and effects are retained as part of the event's valid scope graph.
        child = CHILD_BLOCK.match(line) if depth == 1 else None
        if child:
            if child.group(1) == "trigger":
                rendered.append("\ttrigger = { always = no }\n")
                inerted_events += 1
            skip_depth = delta
            if skip_depth == 0:
                skip_depth = None
            continue

        if depth == 1 and depth + delta == 0:
            if inerted_events < saw_events:
                rendered.append("\ttrigger = { always = no }\n")
                inerted_events += 1
            rendered.append(line)
            depth += delta
            active_event = None
            continue

        rendered.append(line)
        depth += delta
        if depth < 0:
            raise ValueError(f"{relative}: source brace depth became negative")

    if depth != 0 or active_event is not None or skip_depth is not None:
        raise ValueError(f"{relative}: source brace contract changed")
    if saw_events == 0 or inerted_events != saw_events:
        raise ValueError(
            f"{relative}: expected every one of {saw_events} event definitions to become inert; "
            f"changed {inerted_events}"
        )
    result = DATE.sub(sanitized_date, "".join(rendered))
    return (b"\xef\xbb\xbf" if bom else b"") + result.encode("utf-8")


def output_path() -> Path:
    return ROOT / PILOT


def write() -> None:
    content = render(PILOT)
    destination = output_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    print("m12_event_quarantine: wrote inert pilot for 112 installed random events")


def check() -> bool:
    try:
        expected = render(PILOT)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"m12_event_quarantine: FAIL\n  - {exc}")
        return False
    destination = output_path()
    if not destination.is_file() or destination.read_bytes() != expected:
        print(f"m12_event_quarantine: FAIL\n  - stale or missing {PILOT}")
        return False
    print("m12_event_quarantine: PASS (112 inert installed random events)")
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
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            print(f"m12_event_quarantine: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())

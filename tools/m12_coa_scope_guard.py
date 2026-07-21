#!/usr/bin/env python3
"""Make absent vanilla government and HRE scopes evaluate false in CoA triggers.

The installed template registries evaluate their generic CoA predicates for
legacy country definitions that have no active government in ANTIQVITAS's AD 1
start. The local engine supports the ?= comparison form for a possibly absent
government type and uses an existence guard before HRE special-status queries
elsewhere in its own scripts. This exact-name renderer applies only those
locally evidenced defensive contracts.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
SOURCE_RELATIVE = Path("game/main_menu/common/scripted_triggers/00_coa_triggers.txt")
OUTPUT = ROOT / "main_menu/common/scripted_triggers/00_coa_triggers.txt"
GOVERNMENT = re.compile(
    r"^(?P<indent>\s*)government_type\s*=\s*government_type:(?P<kind>monarchy|republic|theocracy)"
    r"(?P<suffix>\s*(?:#.*)?(?:\r?\n)?)$"
)
HRE_HEADERS = frozenset((
    "coa_def_hre_free_imperial_city_trigger",
    "coa_def_hre_elector_trigger",
    "coa_def_hre_archbishop_elector_trigger",
))
HEADER = re.compile(r"^(?P<indent>\s*)(?P<name>coa_def_[A-Za-z0-9_]+_trigger)\s*=\s*\{\s*(?:#.*)?$")
ACTOR = re.compile(r"^(?P<indent>\s*)scope:actor\s*\?=\s*\{\s*(?:#.*)?$")
EXPECTED_GOVERNMENTS = Counter({"monarchy": 2, "republic": 1, "theocracy": 1})


def source_path() -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        source = Path(str(config["game_dir"])) / SOURCE_RELATIVE
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed CoA trigger source: {exc}") from exc
    if not source.is_file():
        raise ValueError(f"installed CoA trigger source is missing: {source}")
    return source


def brace_delta(line: str) -> int:
    code = line.split("#", 1)[0]
    return code.count("{") - code.count("}")


def newline_for(line: str) -> str:
    return "\r\n" if line.endswith("\r\n") else "\n"


def render() -> bytes:
    source = source_path()
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    rendered: list[str] = []
    depth = 0
    active_hre: str | None = None
    government_guards: Counter[str] = Counter()
    hre_guards: set[str] = set()

    for line in lines:
        code = line.split("#", 1)[0]
        header = HEADER.match(code) if depth == 0 else None
        if header is not None:
            active_hre = header.group("name") if header.group("name") in HRE_HEADERS else None

        government = GOVERNMENT.match(line)
        actor = ACTOR.match(code) if active_hre is not None and depth == 1 else None
        if government is not None:
            kind = government.group("kind")
            rendered.append(
                f"{government.group('indent')}government_type ?= government_type:{kind}"
                f"{government.group('suffix')}"
            )
            government_guards[kind] += 1
        else:
            rendered.append(line)
            if actor is not None:
                newline = newline_for(line)
                rendered.append(
                    f"{actor.group('indent')}\texists = international_organization:hre "
                    "# ANTIQVITAS has no HRE instance\n"
                )
                hre_guards.add(active_hre)

        depth += brace_delta(code)
        if depth < 0:
            raise ValueError("CoA trigger source brace depth became negative")
        if depth == 0:
            active_hre = None

    if depth != 0:
        raise ValueError(f"CoA trigger source brace depth ends at {depth}")
    if government_guards != EXPECTED_GOVERNMENTS:
        raise ValueError(
            f"government trigger inventory drift: expected={dict(EXPECTED_GOVERNMENTS)} "
            f"found={dict(government_guards)}"
        )
    if hre_guards != HRE_HEADERS:
        raise ValueError(
            f"HRE status-trigger inventory drift: expected={sorted(HRE_HEADERS)} "
            f"found={sorted(hre_guards)}"
        )
    result = "".join(rendered).encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + result


def write() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(render())
    print(f"m12_coa_scope_guard: wrote {OUTPUT.relative_to(ROOT)}")


def check() -> bool:
    try:
        expected = render()
    except (OSError, ValueError) as exc:
        print(f"m12_coa_scope_guard: FAIL\n  - {exc}")
        return False
    if not OUTPUT.is_file() or OUTPUT.read_bytes() != expected:
        print(f"m12_coa_scope_guard: FAIL\n  - stale or missing {OUTPUT.relative_to(ROOT)}")
        return False
    print(
        "m12_coa_scope_guard: PASS "
        "(4 optional-government comparisons; 3 guarded HRE status predicates)"
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
            print(f"m12_coa_scope_guard: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())

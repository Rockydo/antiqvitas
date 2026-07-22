#!/usr/bin/env python3
"""Guard obsolete startup branches and apply generated AD 1 raw-material effects.

EU5's generic hardcoded startup handler retains several country-specific 1337
initializers and assumes that Catholic and Shinto IO instances always exist.
ANTIQVITAS replaces the start managers and deliberately has neither instance
at AD 1.  This renderer preserves the installed source byte-for-byte except
for safe-scope operators on those absent IO lookups and dynamic post-campaign
date gates around the dated country setup blocks.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from dates import AntqDate, END
from generate_rgo_remap import rendered as rendered_rgo_remap
from generate_rgo_remap import runtime_worker_seeds


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
SOURCE_RELATIVE = Path("game/in_game/common/on_action/_hardcoded.txt")
OUTPUT = ROOT / "in_game/common/on_action/_hardcoded.txt"
START_HEADER = re.compile(r"^\s*on_game_start\s*=\s*\{\s*(?:#.*)?$")
COUNTRY_HEADER = re.compile(r"^(?P<indent>\s*)c:(?P<tag>[A-Z]{3})\s*=\s*\{\s*(?:#.*)?$")
SAFE_SCOPE = re.compile(
    r"^(?P<indent>\s*)(?P<scope>religion:catholic|"
    r"international_organization:catholic_church|"
    r"international_organization:shinto)\s*=\s*\{"
)
RGO_SETUP_ANCHOR = re.compile(r"^\s*setup_area_preferences\s*=\s*yes\s*(?:#.*)?$")
EXPECTED_COUNTRY_GATES = Counter({
    "CHI": 1,
    "MAJ": 1,
    "JAP": 1,
    "BYZ": 2,
    "VER": 1,
    "TEU": 1,
    "BUL": 1,
})
EXPECTED_SAFE_SCOPES = Counter({
    "religion:catholic": 1,
    "international_organization:catholic_church": 2,
    "international_organization:shinto": 2,
})
EXPECTED_RGO_CHANGE_COUNT = 328
EXPECTED_CUSTOM_RGO_GOODS = frozenset({
    "antq_camels",
    "antq_jade",
    "antq_naphtha",
    "antq_papyrus",
    "antq_silphium",
})
EXPECTED_ANNONA_SEED_LOCATIONS = frozenset({"cagliari", "faiyum", "sousse", "syracuse"})


def source_path() -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        source = Path(str(config["game_dir"])) / SOURCE_RELATIVE
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed hardcoded startup handler: {exc}") from exc
    if not source.is_file():
        raise ValueError(f"installed hardcoded startup handler is missing: {source}")
    return source


def brace_delta(line: str) -> int:
    code = line.split("#", 1)[0]
    return code.count("{") - code.count("}")


def newline_for(line: str) -> str:
    return "\r\n" if line.endswith("\r\n") else "\n"


def runtime_rgo_effects(newline: str) -> list[str]:
    """Render the M5 ledger as effects at the one proven runtime surface.

    Location-template files are parsed but not instantiated by the installed
    build at bookmark creation.  ``change_raw_material`` is locally documented
    and console-proven against a vanilla good, while ``on_game_start`` is the
    earliest source-pinned effect context after AD 1 locations exist.
    """
    _, _, changes = rendered_rgo_remap()
    if len(changes) != EXPECTED_RGO_CHANGE_COUNT:
        raise ValueError(
            "runtime RGO inventory drift: "
            f"expected {EXPECTED_RGO_CHANGE_COUNT}, found {len(changes)}"
        )
    locations = [location for location, _, _, _, _ in changes]
    if len(locations) != len(set(locations)):
        raise ValueError("runtime RGO ledger contains duplicate location effects")
    custom_goods = {replacement_good for _, _, _, _, replacement_good in changes if replacement_good.startswith("antq_")}
    if custom_goods != EXPECTED_CUSTOM_RGO_GOODS:
        raise ValueError(
            "runtime custom-good inventory drift: "
            f"expected {sorted(EXPECTED_CUSTOM_RGO_GOODS)}, found {sorted(custom_goods)}"
        )
    annona_seeds = runtime_worker_seeds()
    if {location for location, *_ in annona_seeds} != EXPECTED_ANNONA_SEED_LOCATIONS:
        raise ValueError(
            "runtime annona-seed inventory drift: "
            f"expected {sorted(EXPECTED_ANNONA_SEED_LOCATIONS)}, "
            f"found {sorted(location for location, *_ in annona_seeds)}"
        )
    effects = [
        f"\t\t# ANTIQVITAS M5 runtime RGO remap; generated from docs/m5 source ledgers.{newline}",
    ]
    for location, _region, _operation, _source_good, replacement_good in sorted(changes):
        if replacement_good.startswith("antq_"):
            effects.extend(
                (
                    f"\t\tlocation:{location} = {{{newline}",
                    f"\t\t\tchange_raw_material = goods:{replacement_good}{newline}",
                    "\t\t\tchange_max_raw_material_workers = 1 "
                    f"# Seed one localized RGO level for a runtime-added good.{newline}",
                    f"\t\t}}{newline}",
                )
            )
        else:
            effects.append(
                f"\t\tlocation:{location} = {{ change_raw_material = goods:{replacement_good} }}{newline}"
            )
    effects.append(f"\t\t# ANTIQVITAS M5 annona grain capacity seeds; source ledger: docs/m5/annona_grain_anchors.csv.{newline}")
    for location, good, workers, _source, _confidence, _note in annona_seeds:
        effects.extend(
            (
                f"\t\tlocation:{location} = {{{newline}",
                f"\t\t\tchange_raw_material = goods:{good}{newline}",
                f"\t\t\tchange_max_raw_material_workers = {workers}{newline}",
                f"\t\t}}{newline}",
            )
        )
    return effects


def render() -> bytes:
    source = source_path()
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    rendered: list[str] = []
    depth = 0
    in_start = False
    gated_depth: int | None = None
    country_gates: Counter[str] = Counter()
    safe_scopes: Counter[str] = Counter()
    out_of_campaign = AntqDate(*END).engine()
    rgo_injected = False

    for line in lines:
        code = line.split("#", 1)[0]
        if depth == 0 and START_HEADER.match(code):
            in_start = True

        country = COUNTRY_HEADER.match(code) if in_start and gated_depth is None else None
        safe = SAFE_SCOPE.match(code) if in_start and gated_depth is None else None

        if in_start and not rgo_injected and RGO_SETUP_ANCHOR.match(code):
            rendered.append(line)
            rendered.extend(runtime_rgo_effects(newline_for(line)))
            rgo_injected = True
            depth += brace_delta(code)
            continue

        if country is not None and country.group("tag") in EXPECTED_COUNTRY_GATES:
            indent = country.group("indent")
            rendered.append(line)
            depth += brace_delta(code)
            gated_depth = depth
            newline = newline_for(line)
            rendered.append(f"{indent}\tif = {{{newline}")
            rendered.append(
                f"{indent}\t\tlimit = {{ current_date > {out_of_campaign} }} "
                "# ANTIQVITAS guards dated vanilla startup\n"
            )
            country_gates[country.group("tag")] += 1
            continue

        if safe is not None:
            scope = safe.group("scope")
            rendered.append(line.replace(" =", " ?=", 1))
            safe_scopes[scope] += 1
            depth += brace_delta(code)
        elif gated_depth is not None and depth == gated_depth and code.strip() == "}":
            indent = line[: len(line) - len(line.lstrip())]
            rendered.append(f"{indent}\t}}{newline_for(line)}")
            rendered.append(line)
            depth += brace_delta(code)
            gated_depth = None
        elif gated_depth is not None:
            rendered.append(f"\t{line}" if line.strip() else line)
            depth += brace_delta(code)
        else:
            rendered.append(line)
            depth += brace_delta(code)

        if depth < 0:
            raise ValueError("hardcoded startup handler brace depth became negative")
        if in_start and depth == 0:
            in_start = False

    if depth != 0:
        raise ValueError(f"hardcoded startup handler brace depth ends at {depth}")
    if gated_depth is not None:
        raise ValueError("dated country setup block did not close")
    if not rgo_injected:
        raise ValueError("installed startup handler is missing the runtime RGO insertion anchor")
    if country_gates != EXPECTED_COUNTRY_GATES:
        raise ValueError(
            f"dated startup-country inventory drift: expected={dict(EXPECTED_COUNTRY_GATES)} "
            f"found={dict(country_gates)}"
        )
    if safe_scopes != EXPECTED_SAFE_SCOPES:
        raise ValueError(
            f"startup IO scope inventory drift: expected={dict(EXPECTED_SAFE_SCOPES)} "
            f"found={dict(safe_scopes)}"
        )
    result = "".join(rendered).encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + result


def write() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(render())
    print(f"m12_hardcoded_startup: wrote {OUTPUT.relative_to(ROOT)}")


def check() -> bool:
    try:
        expected = render()
    except (OSError, ValueError) as exc:
        print(f"m12_hardcoded_startup: FAIL\n  - {exc}")
        return False
    if not OUTPUT.is_file() or OUTPUT.read_bytes() != expected:
        print(f"m12_hardcoded_startup: FAIL\n  - stale or missing {OUTPUT.relative_to(ROOT)}")
        return False
    print(
        "m12_hardcoded_startup: PASS "
        f"(5 safe absent-IO scopes; 8 dated country-startup gates; {EXPECTED_RGO_CHANGE_COUNT} runtime RGO corrections)"
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
            print(f"m12_hardcoded_startup: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())

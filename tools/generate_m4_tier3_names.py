#!/usr/bin/env python3
"""Generate the provisional Tier-3 coverage ledger for populated AD 1 fields.

Tier 3 deliberately does not claim that an installed display label is an
ancient toponym.  It makes the fallback explicit, culture-bound, and
replaceable: direct and Tier-2 evidence always take precedence, while every
remaining populated map field receives a recorded retained-label adapter.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from io import StringIO
from pathlib import Path

from generate_m4_tier2_names import capital_locations, pop_cultures

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "docs/m4/dynamic_location_name_overrides.csv"
TIER2 = ROOT / "docs/m4/tier2_location_name_overrides.csv"
OUTPUT = ROOT / "docs/m4/tier3_location_name_overrides.csv"
MAP_OUTPUT = ROOT / "docs/m4/tier3_map_name_fallbacks.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
ENGINE_LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
PATHS = ROOT / "config/local_paths.json"
VANILLA_LOCATION_NAMES = Path("game/main_menu/localization/english/location_names/location_names_l_english.yml")
HEADER = ("location", "culture", "historical_name", "source", "confidence", "note")
MAP_HEADER = ("location", "historical_name", "source", "confidence", "note")
LOC_LINE = re.compile(r'^\s*([\w.-]+):\s*"([^"]+)"')


def ledger_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != HEADER:
            raise ValueError(f"{path.relative_to(ROOT)} must use header {','.join(HEADER)}")
        return list(reader)


def installed_names() -> dict[str, str]:
    game_dir = Path(json.loads(PATHS.read_text(encoding="utf-8-sig"))["game_dir"])
    path = game_dir / VANILLA_LOCATION_NAMES
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if match := LOC_LINE.match(line):
            result[match.group(1)] = match.group(2).strip()
    if not result:
        raise ValueError(f"no installed English location names read from {path}")
    return result


def render_population() -> str:
    cultures = {row["key"] for row in csv.DictReader(CULTURES.open(encoding="utf-8-sig", newline=""))}
    installed = set(json.loads(ENGINE_LOCATIONS.read_text(encoding="utf-8-sig")))
    names = installed_names()
    excluded = capital_locations()
    excluded.update(row["location"].strip() for row in ledger_rows(CURATED))
    excluded.update(row["location"].strip() for row in ledger_rows(TIER2))
    rows: list[dict[str, str]] = []
    for location, culture in sorted(pop_cultures().items()):
        name = names.get(location, "").strip()
        if location in excluded or location not in installed or not name:
            continue
        if culture not in cultures:
            raise ValueError(f"{location} uses unknown M4 culture {culture}")
        rows.append(
            {
                "location": location,
                "culture": culture,
                "historical_name": name,
                "source": "VANILLA:location_names_l_english;T3",
                "confidence": "tier3",
                "note": "Tier-3 retained installed label; no automatic historical identity claim.",
            }
        )
    if not rows:
        raise ValueError("Tier-3 selector produced no populated field adapters")
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=HEADER, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def render_map() -> str:
    installed = set(json.loads(ENGINE_LOCATIONS.read_text(encoding="utf-8-sig")))
    names = installed_names()
    rows = []
    for location in sorted(installed):
        retained = names.get(location, "").strip()
        rows.append(
            {
                "location": location,
                "historical_name": retained or location.replace("_", " ").title(),
                "source": "VANILLA:location_names_l_english;T3" if retained else "ENGINE:location-key;T3",
                "confidence": "tier3",
                "note": (
                    "Tier-3 retained installed root label; no automatic historical identity claim."
                    if retained
                    else "Tier-3 mechanical map-key fallback; no historical identity claim."
                ),
            }
        )
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=MAP_HEADER, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def outputs() -> dict[Path, str]:
    return {OUTPUT: render_population(), MAP_OUTPUT: render_map()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        expected = outputs()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m4_tier3_names: FAIL\n  - {exc}")
        return 1
    if args.write:
        for path, content in expected.items():
            path.write_text(content, encoding="utf-8-sig", newline="")
            print(f"m4_tier3_names: wrote {path.relative_to(ROOT)}")
        return 0
    stale = [path.relative_to(ROOT) for path, content in expected.items() if not path.is_file() or path.read_text(encoding="utf-8-sig") != content]
    if stale:
        print("m4_tier3_names: FAIL\n  - stale or missing " + ", ".join(str(path) for path in stale))
        return 1
    population_count = max(0, len(expected[OUTPUT].splitlines()) - 1)
    map_count = max(0, len(expected[MAP_OUTPUT].splitlines()) - 1)
    print(f"m4_tier3_names: PASS ({population_count} populated adapters; {map_count} explicit root fallbacks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

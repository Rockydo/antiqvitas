#!/usr/bin/env python3
"""Generate explicit, synthetic Tier-3 forms for the remaining map fields.

Tier 3 deliberately does not claim an attested ancient toponym.  It produces
a deterministic culture-shaped display proxy, marked as synthetic and
replaceable; direct and Tier-2 evidence always take precedence.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from io import StringIO
from pathlib import Path

from generate_m4_tier2_names import capital_locations, pop_cultures

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "docs/m4/dynamic_location_name_overrides.csv"
QUALIFIED = ROOT / "docs/m4/qualified_location_name_overrides.csv"
TIER2 = ROOT / "docs/m4/tier2_location_name_overrides.csv"
TIER2_WIDE = ROOT / "docs/m4/tier2_wide_location_name_overrides.csv"
TIER2_REMOTE = ROOT / "docs/m4/tier2_remote_location_name_overrides.csv"
TIER2_FAR = ROOT / "docs/m4/tier2_far_location_name_overrides.csv"
TIER2_ULTRA = ROOT / "docs/m4/tier2_ultra_location_name_overrides.csv"
OUTPUT = ROOT / "docs/m4/tier3_location_name_overrides.csv"
MAP_OUTPUT = ROOT / "docs/m4/tier3_map_name_fallbacks.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
ENGINE_LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
PATHS = ROOT / "config/local_paths.json"
VANILLA_LOCATION_NAMES = Path("game/main_menu/localization/english/location_names/location_names_l_english.yml")
HEADER = ("location", "culture", "historical_name", "source", "confidence", "note")
MAP_HEADER = ("location", "historical_name", "source", "confidence", "note")
LOC_LINE = re.compile(r'^\s*([\w.-]+):\s*"([^"]+)"')

# These are display morphology adapters, not linguistic reconstructions.  They
# deliberately make unsourced modern labels visibly provisional while keeping
# every generated label stable and culture-bound until a reviewed name replaces
# it.  The group field is the only identity input, so this cannot imply a town,
# boundary, language community, or historical polity at the map-field level.
GROUP_ENDINGS = {
    "antq_american_group": "can",
    "antq_andean_group": "marka",
    "antq_anatolian_group": "on",
    "antq_austronesian_group": "nagara",
    "antq_balkan_group": "on",
    "antq_baltic_group": "ava",
    "antq_berber_group": "a",
    "antq_caucasian_group": "a",
    "antq_celtic_group": "dun",
    "antq_germanic_group": "haim",
    "antq_hellenic_group": "on",
    "antq_iberian_group": "dun",
    "antq_indian_group": "pura",
    "antq_iranian_group": "kan",
    "antq_italic_group": "um",
    "antq_japonic_group": "mura",
    "antq_korean_group": "seong",
    "antq_mesoamerican_group": "can",
    "antq_nile_group": "a",
    "antq_oceanic_group": "nagara",
    "antq_semitic_group": "a",
    "antq_sinitic_group": "cheng",
    "antq_slavic_group": "ava",
    "antq_southeast_asian_group": "nagara",
    "antq_steppe_group": "kan",
    "antq_subsaharan_group": "koro",
    "antq_tibetan_group": "ling",
    "antq_uralic_group": "ava",
}


def synthetic_stem(label: str) -> str:
    """Return a stable ASCII-like display stem without asserting etymology."""
    decomposed = unicodedata.normalize("NFKD", label)
    letters = "".join(char for char in decomposed if not unicodedata.combining(char))
    stem = re.sub(r"[^A-Za-z]+", "", letters).strip()
    return (stem or "Topos").title()


def synthetic_name(label: str, group: str) -> str:
    """Make an explicit, non-attested Tier-3 culture display proxy."""
    ending = GROUP_ENDINGS.get(group, "on")
    stem = synthetic_stem(label)
    # A doubled ending makes the mechanical nature harder to read and is not
    # useful as a reconstruction; use a neutral alternate marker instead.
    if stem.lower().endswith(ending):
        ending = "ar"
    return f"{stem}{ending}"


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


def culture_groups() -> dict[str, str]:
    rows = csv.DictReader(CULTURES.open(encoding="utf-8-sig", newline=""))
    result = {row["key"]: row["group"] for row in rows}
    if not result:
        raise ValueError("no M4 cultures loaded")
    unknown = sorted(set(result.values()) - set(GROUP_ENDINGS))
    if unknown:
        raise ValueError(f"Tier-3 morphology lacks groups: {', '.join(unknown)}")
    return result


def render_population() -> str:
    cultures = culture_groups()
    installed = set(json.loads(ENGINE_LOCATIONS.read_text(encoding="utf-8-sig")))
    names = installed_names()
    excluded = capital_locations()
    excluded.update(row["location"].strip() for row in ledger_rows(CURATED))
    excluded.update(row["location"].strip() for row in ledger_rows(QUALIFIED))
    excluded.update(row["location"].strip() for row in ledger_rows(TIER2))
    excluded.update(row["location"].strip() for row in ledger_rows(TIER2_WIDE))
    excluded.update(row["location"].strip() for row in ledger_rows(TIER2_REMOTE))
    excluded.update(row["location"].strip() for row in ledger_rows(TIER2_FAR))
    excluded.update(row["location"].strip() for row in ledger_rows(TIER2_ULTRA))
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
                "historical_name": synthetic_name(name, cultures[culture]),
                "source": "T3M:installed-label+M4-culture",
                "confidence": "tier3",
                "note": "Synthetic culture-shaped Tier-3 display proxy; no attested toponym or historical identity claim.",
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
        seed = retained or location.replace("_", " ").replace("-", " ")
        rows.append(
            {
                "location": location,
                "historical_name": synthetic_name(seed, "map_fallback"),
                "source": "T3M:installed-label" if retained else "T3M:location-key",
                "confidence": "tier3",
                "note": "Synthetic neutral Tier-3 root display proxy; no attested toponym or historical identity claim.",
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

#!/usr/bin/env python3
"""Generate bounded, explicitly lower-confidence AD 1 Pleiades name adapters.

Tier 2 is intentionally separate from the reviewed direct-name ledger.  It
uses only precise, AD 1-active settlement records already present in the local
Pleiades queue, accepts a much shorter map-projection radius, and records both
the source ID and the proxy caveat on every generated row.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "docs/m4/pleiades_name_candidates.csv"
OUTPUT = ROOT / "docs/m4/tier2_location_name_overrides.csv"
CURATED = ROOT / "docs/m4/dynamic_location_name_overrides.csv"
QUALIFIED = ROOT / "docs/m4/qualified_location_name_overrides.csv"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
COORDINATES = ROOT / "docs/world_1ad/capital_coordinates.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
POPS = ROOT / "main_menu/setup/start/06_pops.txt"
ENGINE_LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"

MAX_OFFSET_PX = 1.50
HEADER = ("location", "culture", "historical_name", "source", "confidence", "note")
ARCHAEOLOGICAL_PREFIXES = (
    "tell ", "tel ", "khirbet ", "hirbet ", "qalat ", "qalaat ", "tumulus ",
)
BAD_NAME_CHARACTERS = "?*/[]()0123456789"
# Pleiades is an archaeological gazetteer as well as a historical one. A row
# classified as a settlement can nevertheless expose a modern feature label;
# those are useful research records but never safe player-facing toponyms.
ARCHAEOLOGICAL_FEATURE_RE = re.compile(
    r"\b(?:archaeological|bridge|camp|castrum|cemetery|church|excavation|fort(?:ress)?|"
    r"fortifications?|gate|harbo(?:u)?r|hillfort|mausoleum|medieval|mine|monastery|mosque|"
    r"prehistoric|quarry|road|roman|temple|theat(?:er|re)|tomb|tower|villa|wall)\b",
    re.IGNORECASE,
)


def csv_rows(path: Path, *, comments: bool = False) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        lines = (line for line in handle if not comments or not line.startswith("#"))
        return list(csv.DictReader(lines))


def direct_locations() -> set[str]:
    rows = csv_rows(CURATED)
    if tuple(rows[0]) != HEADER if rows else True:
        raise ValueError(f"{CURATED.relative_to(ROOT)} must use header {','.join(HEADER)}")
    locations = {row["location"].strip() for row in rows if row["location"].strip()}
    qualified = csv_rows(QUALIFIED)
    if tuple(qualified[0]) != HEADER if qualified else True:
        raise ValueError(f"{QUALIFIED.relative_to(ROOT)} must use header {','.join(HEADER)}")
    for row in qualified:
        if row["confidence"] != "tier2":
            raise ValueError(f"{QUALIFIED.relative_to(ROOT)} only permits tier2 rows")
        locations.add(row["location"].strip())
    return locations


def capital_locations() -> set[str]:
    roster = {row["tag"]: row for row in csv_rows(ROSTER)}
    result: set[str] = set()
    for row in csv_rows(COORDINATES):
        polity = roster.get(row["tag"])
        if not polity:
            raise ValueError(f"capital coordinate references unknown tag {row['tag']}")
        if row["confidence"] == "secure" and polity["kind"] != "sop":
            result.add(polity["map_capital"])
    return result


def pop_cultures() -> dict[str, str]:
    """Return the first declared pop culture for every installed location block."""
    found: dict[str, str] = {}
    current: str | None = None
    location_start = re.compile(r"^\t([a-z0-9_]+)\s*=\s*\{\s*$")
    culture = re.compile(r"\bculture\s*=\s*([a-z0-9_]+)\b")
    for raw_line in POPS.read_text(encoding="utf-8-sig").splitlines():
        if match := location_start.match(raw_line):
            current = match.group(1)
            continue
        if current and raw_line == "\t}":
            current = None
            continue
        if current and current not in found and (match := culture.search(raw_line)):
            found[current] = match.group(1)
    return found


def usable_title(value: str) -> bool:
    title = value.strip()
    folded = title.casefold()
    return (
        2 <= len(title) <= 72
        and not any(character in title for character in BAD_NAME_CHARACTERS)
        and not folded.startswith(ARCHAEOLOGICAL_PREFIXES)
        and not folded.startswith(("untitled", "unknown"))
        and not ARCHAEOLOGICAL_FEATURE_RE.search(title)
    )


def render() -> str:
    queue = csv_rows(QUEUE, comments=True)
    cultures = {row["key"] for row in csv_rows(CULTURES)}
    installed = set(json.loads(ENGINE_LOCATIONS.read_text(encoding="utf-8-sig")))
    excluded = direct_locations() | capital_locations()
    population_cultures = pop_cultures()
    candidates: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in queue:
        location = row["location"].strip()
        title = row["pleiades_title"].strip()
        try:
            offset = float(row["offset_px"])
        except ValueError as exc:
            raise ValueError(f"invalid Pleiades offset for {location}: {row['offset_px']}") from exc
        if (
            location not in installed
            or location in excluded
            or offset > MAX_OFFSET_PX
            or not usable_title(title)
        ):
            continue
        culture = population_cultures.get(location)
        if not culture or culture not in cultures:
            continue
        candidates[location].append(row)

    output: list[dict[str, str]] = []
    for location, rows in candidates.items():
        row = min(rows, key=lambda item: (float(item["offset_px"]), item["pleiades_id"]))
        output.append(
            {
                "location": location,
                "culture": population_cultures[location],
                "historical_name": row["pleiades_title"].strip(),
                "source": f"PLE:{row['pleiades_id']};T2",
                "confidence": "tier2",
                "note": (
                    "Tier-2 AD 1 Pleiades settlement adapter; nearest installed city field "
                    f"at {float(row['offset_px']):.2f}px; lower-confidence map proxy."
                ),
            }
        )
    output.sort(key=lambda row: row["location"])
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=HEADER, lineterminator="\n")
    writer.writeheader()
    writer.writerows(output)
    return stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        expected = render()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m4_tier2_names: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8-sig", newline="")
        print(f"m4_tier2_names: wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != expected:
        print(f"m4_tier2_names: FAIL\n  - stale or missing {OUTPUT.relative_to(ROOT)}")
        return 1
    count = max(0, len(expected.splitlines()) - 1)
    print(f"m4_tier2_names: PASS ({count} bounded lower-confidence AD 1 adapters)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

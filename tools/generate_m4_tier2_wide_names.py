#!/usr/bin/env python3
"""Generate wider, explicitly non-secure Pleiades AD 1 name adapters.

This is the fast coverage tier between direct research and retained-label Tier
3.  It never changes the direct ledger, uses only the already checked precise
AD 1 settlement queue, and records the wider projection caveat on every row.
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

from generate_m4_tier2_names import (
    CURATED,
    CULTURES,
    ENGINE_LOCATIONS,
    HEADER,
    QUEUE,
    capital_locations,
    csv_rows,
    pop_cultures,
    usable_title,
)

ROOT = Path(__file__).resolve().parents[1]
TIER2 = ROOT / "docs/m4/tier2_location_name_overrides.csv"
OUTPUT = ROOT / "docs/m4/tier2_wide_location_name_overrides.csv"
MIN_OFFSET_PX = 1.50
MAX_OFFSET_PX = 3.25


def ledger_locations(path: Path) -> set[str]:
    rows = csv_rows(path)
    if not rows or tuple(rows[0]) != HEADER:
        raise ValueError(f"{path.relative_to(ROOT)} must use header {','.join(HEADER)}")
    return {row["location"].strip() for row in rows}


def wide_title(value: str) -> bool:
    """Reject obvious modern archaeological/site labels from a light pass."""
    if not usable_title(value):
        return False
    folded = value.casefold()
    modern_terms = (
        "casa ", "castello", "château", "church", "fort ", "henchir", "monte ",
        "oued ", "santa ", "saint ", "sidi ", "site ", "tepe", "terra", "villa ",
    )
    modern_joiners = r"\b(?:de|del|des|di|do|du|el|la|le|les|saint|santa|sidi)\b"
    return "-" not in value and not any(term in folded for term in modern_terms) and not re.search(modern_joiners, folded)


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def render() -> str:
    queue = csv_rows(QUEUE, comments=True)
    cultures = {row["key"] for row in csv_rows(CULTURES)}
    installed = set(json.loads(ENGINE_LOCATIONS.read_text(encoding="utf-8-sig")))
    excluded = capital_locations() | ledger_locations(CURATED) | ledger_locations(TIER2)
    population_cultures = pop_cultures()
    candidates: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in queue:
        location, title = row["location"].strip(), row["pleiades_title"].strip()
        try:
            offset = float(row["offset_px"])
        except ValueError as exc:
            raise ValueError(f"invalid Pleiades offset for {location}: {row['offset_px']}") from exc
        if (
            location not in installed
            or location in excluded
            or not MIN_OFFSET_PX < offset <= MAX_OFFSET_PX
            or not wide_title(title)
            or normalized(title) == normalized(row["vanilla_name"])
        ):
            continue
        culture = population_cultures.get(location)
        if culture in cultures:
            candidates[location].append(row)

    output = []
    for location, rows in candidates.items():
        row = min(rows, key=lambda item: (float(item["offset_px"]), item["pleiades_id"]))
        output.append(
            {
                "location": location,
                "culture": population_cultures[location],
                "historical_name": row["pleiades_title"].strip(),
                "source": f"PLE:{row['pleiades_id']};T2W",
                "confidence": "tier2",
                "note": (
                    "Wide Tier-2 AD 1 Pleiades settlement adapter; nearest installed city field "
                    f"at {float(row['offset_px']):.2f}px; lower-confidence map proxy."
                ),
            }
        )
    output.sort(key=lambda row: row["location"])
    if not output:
        raise ValueError("wide Tier-2 selector produced no adapters")
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
        print(f"m4_tier2_wide_names: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8-sig", newline="")
        print(f"m4_tier2_wide_names: wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != expected:
        print(f"m4_tier2_wide_names: FAIL\n  - stale or missing {OUTPUT.relative_to(ROOT)}")
        return 1
    print(f"m4_tier2_wide_names: PASS ({max(0, len(expected.splitlines()) - 1)} wide lower-confidence adapters)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

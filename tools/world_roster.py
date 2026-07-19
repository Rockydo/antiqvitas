#!/usr/bin/env python3
"""Validate the sourced AD 1 polity roster before setup generation."""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
REQUIRED = (
    "tag",
    "name",
    "tier",
    "kind",
    "region",
    "historical_capital",
    "map_capital",
    "source",
    "confidence",
    "status",
)
TAG = re.compile(r"[A-Z0-9]{3}$")
TIERS = {"1", "2", "3"}
KINDS = {"country", "subject", "sop"}
CONFIDENCE = {"secure", "contested"}
STATUSES = {"researched", "mapped", "implemented"}


def main() -> int:
    failures: list[str] = []
    if not ROSTER.is_file():
        print("world_roster: FAIL\n  - missing docs/world_1ad/polities.csv")
        return 1
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(REQUIRED):
            failures.append("roster header does not match required field order")
        rows = list(reader)
    locations = set(json.loads(LOCATIONS.read_text(encoding="utf-8-sig")))
    seen: set[str] = set()
    mapped = 0
    for number, row in enumerate(rows, start=2):
        prefix = f"row {number}"
        for key in REQUIRED:
            if not row.get(key, "").strip():
                failures.append(f"{prefix}: missing {key}")
        tag = row.get("tag", "")
        if not TAG.fullmatch(tag):
            failures.append(f"{prefix}: invalid tag {tag!r}")
        elif tag in seen:
            failures.append(f"{prefix}: duplicate tag {tag}")
        seen.add(tag)
        if row.get("tier") not in TIERS:
            failures.append(f"{prefix}: invalid tier {row.get('tier')!r}")
        if row.get("kind") not in KINDS:
            failures.append(f"{prefix}: invalid kind {row.get('kind')!r}")
        if row.get("confidence") not in CONFIDENCE:
            failures.append(f"{prefix}: invalid confidence {row.get('confidence')!r}")
        if row.get("status") not in STATUSES:
            failures.append(f"{prefix}: invalid status {row.get('status')!r}")
        map_capital = row.get("map_capital", "")
        if map_capital and map_capital != "TBD":
            mapped += 1
            if map_capital not in locations:
                failures.append(f"{prefix}: unknown map capital {map_capital}")
    if failures:
        print("world_roster: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    counts = Counter(row["region"] for row in rows)
    tiers = Counter(row["tier"] for row in rows)
    print(
        "world_roster: PASS "
        f"({len(rows)} polities; {mapped} mapped capitals; tiers "
        + ", ".join(f"{tier}={tiers[tier]}" for tier in sorted(tiers))
        + ")"
    )
    print("  regions: " + ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

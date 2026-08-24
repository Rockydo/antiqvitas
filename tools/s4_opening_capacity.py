#!/usr/bin/env python3
"""Guard the engine-proven AD 1 carrying-capacity adapters."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import m12_hardcoded_startup as startup


ROOT = Path(__file__).resolve().parents[1]
ON_START = ROOT / "in_game/common/on_action/_hardcoded.txt"
STATIC = ROOT / "main_menu/common/static_modifiers/antq_opening_capacity.txt"


def main() -> int:
    failures: list[str] = []
    rows = startup.opening_capacity_rows()
    expected = {
        row["location"]: int(row["capacity_bonus_thousands"])
        for row in rows
    }
    on_start = ON_START.read_text(encoding="utf-8-sig")
    assignments = re.findall(
        r"location:([a-z0-9_]+)\s*=\s*\{\s*add_location_modifier\s*=\s*\{\s*"
        r"modifier\s*=\s*antq_opening_capacity_([0-9]{3})\s*"
        r"years\s*=\s*-1\s*mode\s*=\s*add_and_extend",
        on_start,
        re.S,
    )
    found = {location: int(tier) for location, tier in assignments}
    if len(assignments) != len(found):
        failures.append("opening-capacity startup assignments are duplicated")
    if found != expected:
        missing = sorted(set(expected) - set(found))
        extra = sorted(set(found) - set(expected))
        wrong = sorted(key for key in set(found) & set(expected) if found[key] != expected[key])
        failures.append(
            f"startup/ledger mismatch: missing={missing[:5]}, extra={extra[:5]}, wrong={wrong[:5]}"
        )

    static = STATIC.read_text(encoding="utf-8-sig")
    definitions = {
        int(tier): int(value)
        for tier, value in re.findall(
            r"(?m)^antq_opening_capacity_([0-9]{3})\s*=\s*\{.*?"
            r"local_population_capacity\s*=\s*([0-9]+)\s*\n\}",
            static,
            re.S,
        )
    }
    expected_tiers = set(expected.values())
    if set(definitions) != expected_tiers or any(key != value for key, value in definitions.items()):
        failures.append(f"capacity tier definitions drifted: {definitions}")
    forbidden = (
        "local_population_growth",
        "local_population_capacity_modifier",
        "global_population",
        "monthly_gold_income",
        "local_tax",
    )
    for token in forbidden:
        if token in static:
            failures.append(f"capacity adapters carry unrelated effect {token}")

    excess = sum(int(row["engine_excess_people"]) for row in rows)
    granted = sum(int(row["capacity_bonus_thousands"]) * 1000 for row in rows)
    tier_counts = Counter(expected.values())
    if granted < excess * 1.10:
        failures.append("aggregate capacity headroom is below ten percent")
    if max(expected.values()) > 400 or tier_counts[400] != 1 or tier_counts[300] != 1:
        failures.append(f"large-capacity anchors drifted: {dict(tier_counts)}")

    if failures:
        print("s4_opening_capacity: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s4_opening_capacity: PASS "
        f"({len(rows)} engine-proven locations; {excess:,} observed excess; "
        f"{granted:,} bounded capacity; no growth/economic bonus)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

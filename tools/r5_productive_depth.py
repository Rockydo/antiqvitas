#!/usr/bin/env python3
"""Cross-system Round 5 audit for authored productive-building method depth."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGIONAL = ROOT / "docs/m5/regional_production_methods.csv"
TRIBAL = ROOT / "docs/m5/tribal_buildings.csv"
CULTIVATORS = ROOT / "docs/m5/cultivator_production_methods.csv"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    failures: list[str] = []
    regional = read(REGIONAL)
    tribal = read(TRIBAL)
    cultivators = read(CULTIVATORS)
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")

    methods: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in regional:
        methods[row["building"]].append(row)

    productive_tribal = {row["key"] for row in tribal if row["produced"]}
    productive_non_cultivator = set(methods) | productive_tribal
    deep = {building for building, rows in methods.items() if len(rows) >= 3}
    ratio = len(deep) / len(productive_non_cultivator) if productive_non_cultivator else 0.0
    if ratio < 0.60:
        failures.append(
            f"only {len(deep)}/{len(productive_non_cultivator)} productive non-Cultivator families "
            f"have 3+ methods ({ratio:.1%}; requires >=60%)"
        )

    seen: set[str] = set()
    for building, rows in sorted(methods.items()):
        if len(rows) != 3:
            failures.append(f"{building}: expected exactly three regional methods, found {len(rows)}")
            continue
        order = {"maintenance": 0, "organized": 1, "intensive": 2}
        if {row["tier"] for row in rows} != set(order):
            failures.append(f"{building}: incomplete maintenance/organized/intensive ladder")
            continue
        rows.sort(key=lambda row: order[row["tier"]])
        outputs = [float(row["output_multiplier"]) for row in rows]
        inputs = [float(row["input_multiplier"]) for row in rows]
        if not (outputs[0] < outputs[1] < outputs[2]):
            failures.append(f"{building}: output does not increase by tier")
        if not (inputs[0] <= inputs[1] <= inputs[2]):
            failures.append(f"{building}: input intensity regresses by tier")
        efficiencies = [output / input for output, input in zip(outputs, inputs)]
        if not (efficiencies[0] < efficiencies[1] < efficiencies[2]):
            failures.append(f"{building}: later methods are economically dominated")
        for row in rows:
            key = row["key"]
            if key in seen:
                failures.append(f"duplicate method key {key}")
            seen.add(key)
            expected = 0 if row["unlock_age"] == "opening" else 1
            actual = advance_text.count(f"unlock_production_method = {key}")
            if actual != expected:
                failures.append(f"{key}: expected {expected} advance unlocks, found {actual}")

    cultivator_buildings = {row["building"] for row in cultivators}
    overlap = cultivator_buildings & productive_non_cultivator
    if overlap:
        failures.append(f"Cultivators leaked into non-Cultivator denominator: {sorted(overlap)}")

    if failures:
        print("r5_productive_depth: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "r5_productive_depth: PASS "
        f"({len(deep)}/{len(productive_non_cultivator)} = {ratio:.1%} productive "
        f"non-Cultivator families have 3+ methods; {len(seen)} regional methods audited)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

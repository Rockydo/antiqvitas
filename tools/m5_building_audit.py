#!/usr/bin/env python3
"""Enforce ANTIQVITAS's placed-building production and scale budget.

The audit deliberately counts every mod-seeded M5/M7 building placement, not
just the reusable regional families. Named civic sites and frontier forts are
valid one-level exceptions; the broad empire-building layer must nevertheless
remain predominantly scalable and materially productive.
"""

from __future__ import annotations

import csv
from pathlib import Path

from m5_regional_buildings import PRODUCTION_RECIPES


ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "docs/m5/regional_building_seeds.csv"
SPECIALS = ROOT / "docs/m5/special_buildings.csv"
FORTS = ROOT / "docs/m7/forts.csv"


def rows(path: Path) -> list[dict[str, str]]:
	with path.open(encoding="utf-8-sig", newline="") as handle:
		return list(csv.DictReader(handle))


def main() -> int:
	seeds, specials, forts = rows(SEEDS), rows(SPECIALS), rows(FORTS)
	productive = sum(row.get("family") in PRODUCTION_RECIPES for row in seeds)
	scalable = len(seeds)  # Regional definitions are is_special=no with guild_max_level.
	total = len(seeds) + len(specials) + len(forts)
	if not total:
		print("m5_building_audit: FAIL (no mod-seeded building placements)")
		return 1
	productive_ratio, scalable_ratio = productive / total, scalable / total
	failures = []
	if not 0.50 <= productive_ratio <= 0.80:
		failures.append(f"productive placement ratio {productive_ratio:.1%} must stay within 50%-80%")
	if scalable_ratio < 0.80:
		failures.append(f"scalable placement ratio {scalable_ratio:.1%} must be at least 80%")
	if failures:
		print("m5_building_audit: FAIL\n  - " + "\n  - ".join(failures))
		return 1
	print(
		"m5_building_audit: PASS "
		f"({total} placements: {productive} productive / {total - productive} civic-service-or-fort; "
		f"{scalable} scalable / {total - scalable} named-or-fort; "
		f"ratios productive={productive_ratio:.1%}, scalable={scalable_ratio:.1%})"
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

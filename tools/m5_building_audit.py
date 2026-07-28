#!/usr/bin/env python3
"""Enforce ANTIQVITAS's placed-building production and scale budget.

The audit deliberately counts every mod-seeded M5/M7 building placement, not
just the reusable regional families. Named civic sites and frontier forts are
valid one-level exceptions; the broad empire-building layer must nevertheless
remain predominantly scalable and materially productive.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from m5_regional_buildings import PRODUCTION_RECIPES, expanded_seed_rows


ROOT = Path(__file__).resolve().parents[1]
SPECIALS = ROOT / "docs/m5/special_buildings.csv"
FORTS = ROOT / "docs/m7/forts.csv"
SETTLEMENT_AUDIT = ROOT / "docs/m5/global_settlement_audit.csv"
ROMAN_PROFILES = ROOT / "docs/m5/roman_economy_profiles.csv"


def rows(path: Path) -> list[dict[str, str]]:
	with path.open(encoding="utf-8-sig", newline="") as handle:
		return list(csv.DictReader(handle))


def main() -> int:
	seeds, specials, forts = expanded_seed_rows(), rows(SPECIALS), rows(FORTS)
	settlement_audit = rows(SETTLEMENT_AUDIT)
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
	location_counts = Counter(row["location"] for row in seeds)
	roman_profile_locations = {
		location
		for row in rows(ROMAN_PROFILES)
		for location in row["locations"].split(";")
		if location
	}
	if len(location_counts) < 1200:
		failures.append(
			f"regional economy reaches only {len(location_counts)} distinct locations; "
			"at least 1200 are required"
		)
	ordinary_outliers = {
		location: count for location, count in location_counts.items()
		if location not in roman_profile_locations and count > 6
	}
	if ordinary_outliers:
		failures.append(f"ordinary locations exceed the six-building cap: {ordinary_outliers}")
	roman_outliers = {
		location: count for location, count in location_counts.items()
		if location in roman_profile_locations and count > 32
	}
	if roman_outliers:
		failures.append(f"reviewed Roman metropolitan locations exceed 32 buildings: {roman_outliers}")
	top_ten_ratio = sum(count for _location, count in location_counts.most_common(10)) / max(len(seeds), 1)
	if top_ten_ratio > 0.10:
		failures.append(
			f"top-ten locations hold {top_ten_ratio:.1%} of regional placements; "
			"the reviewed-metropolis concentration cap is 10%"
		)
	if len(settlement_audit) != 293:
		failures.append(
			f"global settlement audit has {len(settlement_audit)} polities; expected 293"
		)
	for row in settlement_audit:
		if int(row["placements"]) < 1:
			failures.append(f"{row['tag']} has no opening settlement economy")
		if int(row["productive_placements"]) < 1:
			failures.append(f"{row['tag']} has no productive opening building")
	if failures:
		print("m5_building_audit: FAIL\n  - " + "\n  - ".join(failures))
		return 1
	print(
		"m5_building_audit: PASS "
		f"({total} placements: {productive} productive / {total - productive} civic-service-or-fort; "
		f"{scalable} scalable / {total - scalable} named-or-fort; "
		f"{len(location_counts)} distinct regional locations / {len(settlement_audit)} polities; "
		f"top-ten concentration={top_ten_ratio:.1%}; "
		f"ratios productive={productive_ratio:.1%}, scalable={scalable_ratio:.1%})"
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

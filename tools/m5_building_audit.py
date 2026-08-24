#!/usr/bin/env python3
"""Enforce ANTIQVITAS's complete AD 1 building-instance budget."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from m5_regional_buildings import PRODUCTION_RECIPES, expanded_seed_rows


ROOT = Path(__file__).resolve().parents[1]
SPECIALS = ROOT / "docs/m5/special_buildings.csv"
OPENING_SPECIALS = ROOT / "docs/m5/opening_special_buildings.txt"
FORTS = ROOT / "docs/m7/forts.csv"
TRIBAL_SEEDS = ROOT / "docs/m5/tribal_building_seeds.csv"
TRIBAL_BUILDINGS = ROOT / "docs/m5/tribal_buildings.csv"
SETTLED_SEEDS = ROOT / "docs/m5/settled_opening_floor.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
SETTLEMENT_AUDIT = ROOT / "docs/m5/global_settlement_audit.csv"
ROMAN_PROFILES = ROOT / "docs/m5/roman_economy_profiles.csv"
MARKETS = ROOT / "docs/m5/markets.csv"
ROSTER = ROOT / "docs/world_1ad/polities.csv"


def rows(path: Path) -> list[dict[str, str]]:
	with path.open(encoding="utf-8-sig", newline="") as handle:
		return list(csv.DictReader(line for line in handle if not line.startswith("#")))


def main() -> int:
	seeds, all_specials, forts = expanded_seed_rows(), rows(SPECIALS), rows(FORTS)
	opening_special_keys = {
		line.strip()
		for line in OPENING_SPECIALS.read_text(encoding="utf-8-sig").splitlines()
		if line.strip() and not line.lstrip().startswith("#")
	}
	specials = [row for row in all_specials if row["key"] in opening_special_keys]
	tribal, settled = rows(TRIBAL_SEEDS), rows(SETTLED_SEEDS)
	settlement_audit = rows(SETTLEMENT_AUDIT)
	tribal_productive = {
		row["key"] for row in rows(TRIBAL_BUILDINGS) if row.get("produced", "").strip()
	}
	productive = (
		sum(row.get("family") in PRODUCTION_RECIPES for row in seeds)
		+ sum(row["building"] in tribal_productive for row in tribal)
		+ sum(row["building"] in PRODUCTION_RECIPES for row in settled)
	)
	scalable = len(seeds) + len(tribal) + len(settled)
	all_placements = [
		*((row["location"], row["family"], "regional") for row in seeds),
		*((row["location"], row["building"], "special") for row in specials),
		*((row["location"], row["building"], "tribal") for row in tribal),
		*((row["location"], row["building"], "settled") for row in settled),
		*((row["location"], row["building"], "fort") for row in forts),
	]
	total = len(all_placements)
	if not total:
		print("m5_building_audit: FAIL (no mod-seeded building placements)")
		return 1
	productive_ratio, scalable_ratio = productive / total, scalable / total
	failures = []
	if total > 3500:
		failures.append(f"opening building instances {total} exceed the 3500 global cap")
	if not 0.50 <= productive_ratio <= 0.80:
		failures.append(f"productive placement ratio {productive_ratio:.1%} must stay within 50%-80%")
	if scalable_ratio < 0.80:
		failures.append(f"scalable placement ratio {scalable_ratio:.1%} must be at least 80%")
	location_counts = Counter(location for location, _building, _layer in all_placements)
	if len(location_counts) < 1800:
		failures.append(
			f"opening economy reaches only {len(location_counts)} distinct locations; "
			"at least 1800 are required"
		)
	ordinary_outliers = {
		location: count for location, count in location_counts.items()
		if location != "rome" and count > 16
	}
	if ordinary_outliers:
		failures.append(f"non-Roma locations exceed the 16-building cap: {ordinary_outliers}")
	if location_counts.get("rome", 0) > 32:
		failures.append(f"Roma exceeds the 32-building cap: {location_counts['rome']}")
	top_ten_ratio = sum(count for _location, count in location_counts.most_common(10)) / total
	if top_ten_ratio > 0.10:
		failures.append(
			f"top-ten locations hold {top_ten_ratio:.1%} of regional placements; "
			"the reviewed-metropolis concentration cap is 10%"
		)
	roster = rows(ROSTER)
	roster_count = len(roster)
	if len(settlement_audit) != roster_count:
		failures.append(
			f"global settlement audit has {len(settlement_audit)} polities; "
			f"expected roster count {roster_count}"
		)
	owner = {row["location"]: row["tag"] for row in rows(OWNERSHIP)}
	placements_by_tag = Counter(owner.get(location, "") for location, _building, _layer in all_placements)
	tribal_by_tag = Counter(row["tag"] for row in tribal)
	for polity in roster:
		tag = polity["tag"]
		if polity["kind"] == "sop":
			if tribal_by_tag[tag] != 4:
				failures.append(f"{tag} has {tribal_by_tag[tag]} tribal opening buildings; expected 4")
		elif tag != "ROM" and placements_by_tag[tag] < 4:
			failures.append(f"{tag} has only {placements_by_tag[tag]} opening buildings; expected >=4")
	if failures:
		print("m5_building_audit: FAIL\n  - " + "\n  - ".join(failures))
		return 1
	print(
		"m5_building_audit: PASS "
		f"({total} placements: {productive} productive / {total - productive} civic-service-or-fort; "
		f"{scalable} scalable / {total - scalable} named-or-fort; "
		f"{len(location_counts)} distinct locations / {len(settlement_audit)} polities; "
		f"top-ten concentration={top_ten_ratio:.1%}; "
		f"ratios productive={productive_ratio:.1%}, scalable={scalable_ratio:.1%})"
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

#!/usr/bin/env python3
"""Generate a dispersed, capacity-bounded AD 1 settlement economy.

Location placements are regional capacity proxies, not claims for named
excavated workshops. Secure named sites stay in the special-building ledger.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path

from m5_regional_buildings import (
    CITY_ONLY_FAMILIES,
    PRODUCTION_RECIPES,
    ROMAN_ECONOMY_FAMILIES,
    WATER_OR_PORT_FAMILIES,
)


ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ROOT / "docs/m5/regional_building_families.csv"
SEEDS = ROOT / "docs/m5/regional_building_seeds.csv"
BUNDLES = ROOT / "docs/m5/s2_britain_ireland_building_seeds.csv"
URBAN_NODES = ROOT / "docs/m5/urban_nodes.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
POLITIES = ROOT / "docs/world_1ad/polities.csv"
RGO_AUDIT = ROOT / "docs/m5/global_rgo_audit.csv"
POPS = ROOT / "main_menu/setup/start/06_pops.txt"
AUDIT = ROOT / "docs/m5/global_settlement_audit.csv"
ROMAN_PROFILES = ROOT / "docs/m5/roman_economy_profiles.csv"

SEED_FIELDS = ("key", "family", "location", "macro", "source", "confidence", "note")
AUDIT_FIELDS = (
    "tag", "name", "region", "capital", "controlled_locations",
    "seeded_locations", "placements", "productive_placements",
    "civic_service_placements", "max_location_placements",
    "source", "confidence", "note",
)
REGION_MACRO = {
    **{region: "Europe" for region in (
        "Rome", "Britain", "Ireland", "Germania", "Balkans", "Danube",
        "Eastern Europe", "Baltic", "Finland", "Scandinavia", "Pontic",
    )},
    "Africa": "North Africa",
    **{region: "Middle East" for region in (
        "Anatolia", "Levant", "Mesopotamia", "Iran", "Arabia", "Caucasus",
    )},
    **{region: "Central Asia" for region in ("Steppe", "Central Asia", "Tarim")},
    **{region: "South Asia" for region in ("India", "Lanka")},
    "Southeast Asia": "Southeast Asia",
    **{region: "East Asia" for region in ("China", "Korea", "Japan")},
    "West Africa": "West Africa",
    **{region: "Americas" for region in (
        "Andes", "Northern Andes", "Mesoamerica", "North America",
        "Caribbean-Amazon",
    )},
    "Oceania": "Oceania",
}
LOCATION_MACRO_OVERRIDES = {
    "alexandria": "North Africa",
    "tunis": "North Africa",
    "annaba": "North Africa",
    "bizerte": "North Africa",
    "gabes": "North Africa",
    "sousse": "North Africa",
    "antioch": "Middle East",
    "baghdad": "Middle East",
    "ayasuluk": "Middle East",
    "shoubak": "Middle East",
    "homs": "Middle East",
    "sidon": "Middle East",
}

# Ubiquitous workshop inputs must not make a family look locally specific.
COMMON_INPUTS = {
    "tools", "lumber", "pottery", "cloth", "leather", "dyes", "fiber_crops",
    "coal", "tar", "sand", "goods_gold",
}
GOOD_ALIASES = {
    "barley": {"wheat"},
    "legumes": {"wheat"},
    "maize": {"millet", "wheat"},
    "potatoes": {"millet", "wheat"},
    "cassava": {"millet", "wheat"},
    "wild_game": {"livestock"},
    "horses": {"livestock"},
    "dates": {"fruit"},
    "citrus": {"fruit"},
    "spices": {"pepper", "incense"},
    "tea": {"incense"},
    "cocoa": {"fruit"},
    "coffee": {"fruit"},
}
CROP_GOODS = {
    "wheat", "barley", "millet", "rice", "maize", "legumes", "potatoes",
    "cassava", "fruit", "dates", "citrus",
}
ARID_CLIMATES = {"arid", "cold_arid", "hot_arid", "desert"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(line for line in handle if not line.startswith("#"))
        ]


def population_totals() -> dict[str, float]:
    result: dict[str, float] = {}
    current = ""
    for line in POPS.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"^\t([a-z0-9_]+) = \{$", line)
        if match:
            current = match.group(1)
            result.setdefault(current, 0.0)
            continue
        if current:
            result[current] += sum(
                float(value)
                for value in re.findall(r"\bsize = ([0-9]+(?:\.[0-9]+)?)", line)
            )
            if line == "\t}":
                current = ""
    return result


def expanded_bundle_rows() -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for bundle in read_rows(BUNDLES):
        for index, family in enumerate(bundle["families"].split("|"), start=1):
            result.append({
                "key": f"reg_{bundle['key']}_{index}",
                "family": family,
                "location": bundle["location"],
                "macro": bundle["macro"],
                "source": bundle["source"],
                "confidence": bundle["confidence"],
                "note": bundle["note"],
            })
    return result


def candidate_score(
    family: str,
    good: str,
    owner_region: str,
    harbor: float,
    urban_profile: str,
    climate: str,
    signatures: dict[str, set[str]],
    usage: Counter[str],
) -> tuple[float, str]:
    if family in ROMAN_ECONOMY_FAMILIES and owner_region != "Rome":
        return (-10_000.0, family)
    if family in CITY_ONLY_FAMILIES and urban_profile != "city":
        return (-10_000.0, family)
    if family in WATER_OR_PORT_FAMILIES and harbor <= 0:
        return (-10_000.0, family)

    matches = {good, *GOOD_ALIASES.get(good, set())}
    score = 70.0 if matches & signatures[family] else 0.0
    if good in CROP_GOODS and any(token in family for token in ("granary", "mill", "bread", "brew")):
        score += 35.0
    if good == "rice" and "rice" in family:
        score += 50.0
    if good != "rice" and "rice" in family:
        score -= 90.0
    if good != "millet" and "millet" in family:
        score -= 70.0
    if good not in {"wheat", "barley", "legumes"} and "wheat" in family:
        score -= 50.0
    if climate in ARID_CLIMATES and any(token in family for token in ("cistern", "caravan", "pack_animal")):
        score += 18.0
    if harbor > 0 and family in WATER_OR_PORT_FAMILIES:
        score += 14.0
    if urban_profile == "city" and family in CITY_ONLY_FAMILIES:
        score += 10.0
    score -= min(usage[family], 40) * 0.8
    return (score, family)


def generate() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    families = read_rows(FAMILIES)
    family_keys = [row["key"] for row in families]
    signatures = {
        row["key"]: {
            good for good in row["goods"].split(";")
            if good and good not in COMMON_INPUTS
        }
        for row in families
    }
    polities = {row["tag"]: row for row in read_rows(POLITIES)}
    ownership_rows = read_rows(OWNERSHIP)
    rgo = {row["location"]: row for row in read_rows(RGO_AUDIT)}
    populations = population_totals()
    urban = {row["location"]: row["profile"] for row in read_rows(URBAN_NODES)}

    locations_by_tag: dict[str, list[str]] = defaultdict(list)
    owner_by_location: dict[str, str] = {}
    for row in ownership_rows:
        locations_by_tag[row["tag"]].append(row["location"])
        owner_by_location[row["location"]] = row["tag"]

    bundle_rows = expanded_bundle_rows()
    rows: list[dict[str, str]] = []
    used_pairs = {(row["location"], row["family"]) for row in bundle_rows}
    usage: Counter[str] = Counter(row["family"] for row in bundle_rows)
    per_location: Counter[str] = Counter(row["location"] for row in bundle_rows)

    def details(location: str) -> tuple[str, str, float, str, str]:
        tag = owner_by_location[location]
        region = polities[tag]["region"]
        data = rgo[location]
        try:
            harbor = float(data["natural_harbor_suitability"] or 0)
        except ValueError:
            harbor = 0.0
        return tag, region, harbor, urban.get(location, ""), data["ad1_good"]

    def choose_family(location: str) -> str:
        _tag, region, harbor, urban_profile, good = details(location)
        candidates = [
            family for family in family_keys
            if family in PRODUCTION_RECIPES and (location, family) not in used_pairs
        ]
        return max(
            candidates,
            key=lambda family: candidate_score(
                family, good, region, harbor, urban_profile,
                rgo[location]["climate"], signatures, usage,
            ),
        )

    def add(
        location: str,
        family: str,
        reason: str,
        *,
        key: str = "",
        source: str = "P12.1;P12.3;P13;PER",
        confidence: str = "contested",
        note: str = "",
        cap: int = 6,
    ) -> bool:
        pair = (location, family)
        if pair in used_pairs or per_location[location] >= cap:
            return False
        tag, region, _harbor, _urban_profile, good = details(location)
        index = len(rows) + 1
        rows.append({
            "key": key or f"reg_world_{index:04d}_{location}",
            "family": family,
            "location": location,
            "macro": LOCATION_MACRO_OVERRIDES.get(location, REGION_MACRO[region]),
            "source": source,
            "confidence": confidence,
            "note": note or (
                f"AD 1 {reason} capacity proxy for {polities[tag]['name']}; "
                f"the {good} resource, generated population, settlement rank, "
                "and controlled hinterland guide placement, not a claim for a "
                "named excavated workshop in this engine polygon."
            ),
        })
        used_pairs.add(pair)
        usage[family] += 1
        per_location[location] += 1
        return True

    selected_locations: set[str] = set()
    # Preserve the deeply differentiated, source-reviewed Roman provincial
    # packages as metropolitan exceptions. Ordinary sites remain capped at six.
    roman_slugs = {family.removeprefix("antq_reg_") for family in ROMAN_ECONOMY_FAMILIES}
    for profile in read_rows(ROMAN_PROFILES):
        selected = (
            roman_slugs
            if profile["families"] == "all"
            else set(profile["families"].split(";"))
        )
        for location in profile["locations"].split(";"):
            if not location:
                continue
            selected_locations.add(location)
            for slug in sorted(selected):
                family = f"antq_reg_{slug}"
                if urban.get(location) == "town" and family in CITY_ONLY_FAMILIES:
                    continue
                add(
                    location,
                    family,
                    "reviewed Roman provincial",
                    key=f"reg_roman_economy_{profile['profile']}_{location}_{slug}",
                    source=profile["source"],
                    confidence=profile["confidence"],
                    note=profile["note"],
                    cap=32,
                )

    for tag in sorted(polities):
        controlled = locations_by_tag[tag]
        if not controlled:
            continue
        capital = polities[tag]["map_capital"]
        ordered = sorted(
            controlled,
            key=lambda location: (
                location != capital,
                -populations.get(location, 0.0),
                location,
            ),
        )
        quota = min(len(ordered), max(2, min(18, round(math.sqrt(len(ordered))))))
        chosen: list[str] = []
        seen_goods: set[str] = set()
        for location in ordered:
            good = rgo[location]["ad1_good"]
            if location == capital or good not in seen_goods:
                chosen.append(location)
                seen_goods.add(good)
            if len(chosen) == quota:
                break
        if len(chosen) < quota:
            chosen.extend(location for location in ordered if location not in chosen)
            chosen = chosen[:quota]
        for location in chosen:
            selected_locations.add(location)
            add(location, choose_family(location), "settlement-and-hinterland economic")
        if capital in controlled:
            add(capital, choose_family(capital), "capital-market")

    for location in sorted(urban):
        if location not in owner_by_location:
            continue
        selected_locations.add(location)
        add(location, choose_family(location), "urban-service and craft")

    for family in family_keys:
        if usage[family]:
            continue
        candidates: list[tuple[float, float, str]] = []
        for location in selected_locations:
            _tag, region, harbor, urban_profile, good = details(location)
            score, _ = candidate_score(
                family, good, region, harbor, urban_profile,
                rgo[location]["climate"], signatures, usage,
            )
            if score > -10_000 and per_location[location] < 6:
                candidates.append((score, populations.get(location, 0.0), location))
        if not candidates:
            raise ValueError(f"no valid global settlement candidate for {family}")
        _score, _population, location = max(candidates)
        add(location, family, "specialized regional craft")

    # A settlement system also needs storage, water, transport, exchange, and
    # civic capacity. Bring ordinary regional placements to a 75% productive
    # target, dispersed over the same reviewed settlement sample.
    def choose_service(location: str) -> str:
        _tag, region, harbor, urban_profile, good = details(location)
        candidates = [
            family for family in family_keys
            if family not in PRODUCTION_RECIPES and (location, family) not in used_pairs
        ]
        return max(
            candidates,
            key=lambda family: candidate_score(
                family, good, region, harbor, urban_profile,
                rgo[location]["climate"], signatures, usage,
            ),
        )

    productive_count = sum(
        row["family"] in PRODUCTION_RECIPES for row in rows + bundle_rows
    )
    service_count = len(rows) + len(bundle_rows) - productive_count
    service_target = math.ceil(productive_count / 3)
    service_locations = sorted(
        selected_locations,
        key=lambda location: (-populations.get(location, 0.0), location),
    )
    cursor = 0
    while service_count < service_target:
        location = service_locations[cursor % len(service_locations)]
        cursor += 1
        if per_location[location] >= 6:
            continue
        family = choose_service(location)
        score, _ = candidate_score(
            family,
            rgo[location]["ad1_good"],
            polities[owner_by_location[location]]["region"],
            details(location)[2],
            urban.get(location, ""),
            rgo[location]["climate"],
            signatures,
            usage,
        )
        if score <= -10_000:
            continue
        if add(location, family, "storage, exchange, transport, or civic-service"):
            service_count += 1

    all_rows = rows + bundle_rows
    placements_by_tag: Counter[str] = Counter()
    productive_by_tag: Counter[str] = Counter()
    locations_per_tag: dict[str, set[str]] = defaultdict(set)
    location_counts_by_tag: dict[str, Counter[str]] = defaultdict(Counter)
    for row in all_rows:
        tag = owner_by_location[row["location"]]
        placements_by_tag[tag] += 1
        productive_by_tag[tag] += row["family"] in PRODUCTION_RECIPES
        locations_per_tag[tag].add(row["location"])
        location_counts_by_tag[tag][row["location"]] += 1

    audit_rows: list[dict[str, str]] = []
    for tag, polity in sorted(polities.items()):
        total = placements_by_tag[tag]
        productive = productive_by_tag[tag]
        audit_rows.append({
            "tag": tag,
            "name": polity["name"],
            "region": polity["region"],
            "capital": polity["map_capital"],
            "controlled_locations": str(len(locations_by_tag[tag])),
            "seeded_locations": str(len(locations_per_tag[tag])),
            "placements": str(total),
            "productive_placements": str(productive),
            "civic_service_placements": str(total - productive),
            "max_location_placements": str(max(location_counts_by_tag[tag].values(), default=0)),
            "source": "P12.1;P12.3;P13;PER",
            "confidence": "contested",
            "note": (
                "Capacity-bounded opening settlement sample; named sites remain "
                "in the special-building ledger and absence is not archaeological evidence."
            ),
        })
    return rows, audit_rows


def render(rows: list[dict[str, str]], fields: tuple[str, ...]) -> str:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        seeds, audit = generate()
    except (KeyError, ValueError) as exc:
        print(f"s2_global_settlements: FAIL\n  - {exc}")
        return 1
    outputs = {
        SEEDS: render(seeds, SEED_FIELDS),
        AUDIT: render(audit, AUDIT_FIELDS),
    }
    if args.write:
        for path, text in outputs.items():
            path.write_text(text, encoding="utf-8", newline="")
        print(
            "s2_global_settlements: wrote "
            f"{len(seeds)} direct placements and {len(audit)} polity audit rows"
        )
        return 0
    stale = [
        str(path.relative_to(ROOT))
        for path, expected in outputs.items()
        if not path.exists() or path.read_text(encoding="utf-8-sig") != expected
    ]
    if stale:
        print("s2_global_settlements: FAIL (stale generated files)\n  - " + "\n  - ".join(stale))
        return 1
    print(
        "s2_global_settlements: PASS "
        f"({len(seeds)} direct placements; {len(audit)} starting polities)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

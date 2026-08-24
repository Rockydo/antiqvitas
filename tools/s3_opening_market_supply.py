#!/usr/bin/env python3
"""Guarantee bounded opening construction circuits in major AD 1 markets."""

from __future__ import annotations

import argparse
import csv
import io
from collections import Counter, defaultdict
from pathlib import Path

from m5_regional_buildings import (
    BUNDLE_FIELDS,
    FOOD_SEEDS,
    MACROS,
    MACRO_LOCATION_OVERRIDES,
    PRODUCTION_RECIPES,
    REGIONAL_SEED_BUNDLES,
    SEEDS,
    SEED_FIELDS,
)

ROOT = Path(__file__).resolve().parents[1]
MARKETS = ROOT / "docs/m5/markets.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
OUTPUT = ROOT / "docs/m5/opening_market_building_seeds.csv"
REPORT = ROOT / "docs/m5/OPENING_MARKET_SUPPLY.md"

EXCLUDED_REGIONS = {
    "Andes",
    "Northern Andes",
    "Mesoamerica",
    "North America",
    "Caribbean-Amazon",
    "Oceania",
}
FLAGSHIPS = {
    "alexandria",
    "antioch",
    "anuradhapura",
    "attock",
    "baghdad",
    "chengdu",
    "constantinople",
    "jingzhao",
    "jerusalem",
    "kodungallur",
    "luoyang",
    "massawa",
    "panyu",
    "patna",
    "samarkand",
    "shendi",
    "tunis",
}
FAMILY_POOLS = {
    # Cordage is not an opening circuit unless its high-volume tar input is
    # present in the same market.  The previous report counted a seeded
    # ropewalk as coverage even when the live building operated at 0% for lack
    # of tar.  Give every covered Old World hub an opening wood-tar producer;
    # constructibility remains independently enforced by the raw-material
    # bootstrap package and the goods-reachability audit.
    "tar": (
        "antq_reg_charcoal_hearth",
    ),
    "antq_iron_hardware": (
        "antq_reg_ironmongery",
        "antq_reg_locksmith",
        "antq_reg_nailery",
        "antq_reg_chainmaker",
    ),
    "antq_cordage": (
        "antq_reg_ropewalk",
        "antq_reg_netmaker",
        "antq_reg_fishing_tackle",
    ),
    "masonry": (
        "antq_reg_brickworks",
        "antq_reg_lime_kiln",
        "antq_reg_stone_masonry_yard",
        "antq_reg_clay_brickworks",
    ),
    "tools": (
        "antq_reg_metalwork",
        "antq_reg_bronze_foundry",
        "antq_reg_copper_smithy",
        "antq_reg_iron_bloomery",
    ),
    "antq_grain_products": (
        "antq_reg_grain_mill",
        "antq_reg_bread_oven",
        "antq_reg_villa_rustica",
        "antq_reg_annona_bakery",
    ),
}
OUTPUT_ORDER = tuple(FAMILY_POOLS)
FAMILY_OUTPUT = {
    family: output
    for output, families in FAMILY_POOLS.items()
    for family in families
}


def rows(path: Path, fields: tuple[str, ...] | None = None) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        useful = (line for line in handle if not line.startswith("#"))
        result = list(csv.DictReader(useful))
    if fields:
        for number, row in enumerate(result, start=2):
            missing = [field for field in fields if field not in row]
            if missing:
                raise ValueError(f"{path.relative_to(ROOT)}:{number}: missing {missing}")
    return result


def base_seeds() -> list[dict[str, str]]:
    result = rows(SEEDS, SEED_FIELDS)
    result.extend(rows(FOOD_SEEDS, SEED_FIELDS))
    for bundle in rows(REGIONAL_SEED_BUNDLES, BUNDLE_FIELDS):
        families = tuple(part.strip() for part in bundle["families"].split("|"))
        if len(families) != 2:
            raise ValueError(f"{bundle['key']}: expected exactly two bundled families")
        for index, family in enumerate(families, start=1):
            result.append(
                {
                    "key": f"{bundle['key']}_{index}",
                    "family": family,
                    "location": bundle["location"],
                    "macro": bundle["macro"],
                    "source": bundle["source"],
                    "confidence": bundle["confidence"],
                    "note": bundle["note"],
                }
            )
    return result


def owner_map() -> dict[str, str]:
    return {row["location"]: row["tag"] for row in rows(OWNERSHIP)}


def roster_map() -> dict[str, dict[str, str]]:
    return {row["tag"]: row for row in rows(ROSTER)}


def macro_for(location: str, region: str) -> str:
    if location in MACRO_LOCATION_OVERRIDES:
        return MACRO_LOCATION_OVERRIDES[location]
    matches = [macro for macro, regions in MACROS.items() if region in regions]
    if len(matches) != 1:
        raise ValueError(f"{location}: region {region!r} has {len(matches)} macro matches")
    return matches[0]


def selected_markets() -> list[dict[str, str]]:
    owners = owner_map()
    polities = roster_map()
    selected: list[dict[str, str]] = []
    for market in rows(MARKETS):
        location = market["location"]
        tag = owners.get(location)
        polity = polities.get(tag or "")
        if not polity:
            raise ValueError(f"{location}: market has no opening owner/profile")
        if int(polity["tier"]) > 2 or polity["region"] in EXCLUDED_REGIONS:
            continue
        selected.append(
            {
                **market,
                "tag": tag or "",
                "polity": polity["name"],
                "region": polity["region"],
                "tier": polity["tier"],
                "macro": macro_for(location, polity["region"]),
            }
        )
    return selected


def target(location: str) -> int:
    # One functional circuit is the opening guarantee. Extra workshops should
    # be created by market demand, not multiplied merely because a hub is large.
    return 1


def generated_rows() -> list[dict[str, str]]:
    existing = base_seeds()
    pairs = {(row["location"], row["family"]) for row in existing}
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in existing:
        output = FAMILY_OUTPUT.get(row["family"])
        if output:
            counts[row["location"]][output] += 1

    generated: list[dict[str, str]] = []
    for market in selected_markets():
        location = market["location"]
        minimum = target(location)
        for output in OUTPUT_ORDER:
            needed = minimum - counts[location][output]
            for family in FAMILY_POOLS[output]:
                if needed <= 0:
                    break
                pair = (location, family)
                if pair in pairs:
                    continue
                suffix = family.removeprefix("antq_reg_")
                generated.append(
                    {
                        "key": f"reg_s3_market_{location}_{suffix}",
                        "family": family,
                        "location": location,
                        "macro": market["macro"],
                        "source": "P12.1;P12.2;P12.3;PER",
                        "confidence": "contested",
                        "note": (
                            "Opening market-capacity proxy; guarantees a bounded "
                            "construction circuit without asserting an excavated workshop."
                        ),
                    }
                )
                pairs.add(pair)
                counts[location][output] += 1
                needed -= 1
            if needed > 0:
                raise ValueError(
                    f"{location}: cannot reach {minimum} producers for {output}"
                )
    return generated


def csv_text(generated: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=SEED_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(generated)
    return buffer.getvalue()


def coverage(generated: list[dict[str, str]]) -> dict[str, Counter[str]]:
    result: dict[str, Counter[str]] = defaultdict(Counter)
    for row in (*base_seeds(), *generated):
        output = FAMILY_OUTPUT.get(row["family"])
        if output:
            result[row["location"]][output] += 1
    return result


def report_text(generated: list[dict[str, str]]) -> str:
    selected = selected_markets()
    totals = coverage(generated)
    tags = Counter(row["tag"] for row in selected)
    lines = [
        "# Opening Market Supply",
        "",
        "Generated by `tools/s3_opening_market_supply.py`.",
        "",
        f"- Covered Tier 1-2 Old World markets: {len(selected)}",
        f"- Added opening workshops: {len(generated)}",
        f"- Covered opening polities: {len(tags)}",
        "- Guaranteed outputs: Tar, Iron Hardware, Cordage, Masonry, Tools, Flour and Bread",
        "- Minimum: 1 producer/output in every covered market",
        "",
        "| Market | Owner | Target | Tar | Hardware | Cordage | Masonry | Tools | Food |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for market in selected:
        location = market["location"]
        count = totals[location]
        lines.append(
            f"| {market['name']} | {market['polity']} | {target(location)} | "
            f"{count['tar']} | "
            f"{count['antq_iron_hardware']} | {count['antq_cordage']} | "
            f"{count['masonry']} | {count['tools']} | "
            f"{count['antq_grain_products']} |"
        )
    return "\n".join(lines) + "\n"


def expected() -> tuple[str, str, list[dict[str, str]]]:
    generated = generated_rows()
    return csv_text(generated), report_text(generated), generated


def validate(generated: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    pairs = [(row["location"], row["family"]) for row in generated]
    if len(pairs) != len(set(pairs)):
        failures.append("generated market seeds contain duplicate location/family pairs")
    totals = coverage(generated)
    for market in selected_markets():
        location = market["location"]
        minimum = target(location)
        for output in OUTPUT_ORDER:
            if totals[location][output] < minimum:
                failures.append(
                    f"{location}: {output} coverage {totals[location][output]} < {minimum}"
                )
    if len(selected_markets()) < 45:
        failures.append("fewer than 45 Tier 1-2 Old World markets are covered")
    if len(generated) < 100:
        failures.append("opening-market expansion is unexpectedly shallow")
    return failures


def write(csv_content: str, report: str) -> None:
    OUTPUT.write_text(csv_content, encoding="utf-8-sig", newline="")
    REPORT.write_text(report, encoding="utf-8", newline="\n")
    print(f"s3_opening_market_supply: wrote {OUTPUT.relative_to(ROOT)}")
    print(f"s3_opening_market_supply: wrote {REPORT.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        csv_content, report, generated = expected()
        if args.write:
            write(csv_content, report)
        failures = validate(generated)
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != csv_content:
            failures.append(f"stale {OUTPUT.relative_to(ROOT)}")
        if not REPORT.is_file() or REPORT.read_text(encoding="utf-8-sig") != report:
            failures.append(f"stale {REPORT.relative_to(ROOT)}")
    except (OSError, ValueError, csv.Error) as exc:
        failures = [str(exc)]
        generated = []
    if failures:
        print("s3_opening_market_supply: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s3_opening_market_supply: PASS "
        f"({len(selected_markets())} major markets; {len(generated)} added workshops)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

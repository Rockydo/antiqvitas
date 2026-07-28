#!/usr/bin/env python3
"""Validate the sourced replacement of the Caucasian residual frame."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
AREAS = ROOT / "docs/world_1ad/ownership_areas.csv"
RESIDUAL = ROOT / "docs/world_1ad/ownership_residual_areas.csv"
DIRECT = ROOT / "docs/world_1ad/ownership_locations.csv"
PROFILES = ROOT / "docs/m4/tag_profiles.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
POP_OVERRIDES = ROOT / "docs/m4/population_location_overrides.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
SETTLEMENTS = ROOT / "docs/m5/global_settlement_audit.csv"
LAWS = ROOT / "docs/m6/ancient_law_profiles.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LEDGER = ROOT / "docs/m12/caucasian_granularity.csv"
LANGUAGE_CLIENTS = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

SOANES = {"lentekhi", "tsageri", "tsesi", "ushguli"}
COLCHIS = {
    "anacopia", "anaklia", "artanuji", "batumi", "bedia", "kutaisi",
    "lata_georgia", "ozurgeti", "parkhali", "pitsunda", "savsat",
    "shorapani", "skande", "sukhumi", "tsalenjikha", "vartsikhe",
}
IBERIA = {
    "akhaltsikhe", "alaverdi", "balakan", "bodbe", "dmanisi", "dusheti",
    "gori", "gremi", "hereti", "kasriskari", "khornabuji", "kldekari",
    "kvenipnevi", "oltu", "panaskerti", "qakh", "rustavi", "shatili",
    "tbilisi", "telavi", "tmogvi", "tsagvli",
}
ARMENIA = {"akhalkalaki", "ardahan", "ispir", "khikhani", "tortum"}
FORMER_CAU = SOANES | COLCHIS | IBERIA | ARMENIA
EXPECTED_OWNER = {
    **{location: "SVA" for location in SOANES},
    **{location: "CLZ" for location in COLCHIS},
    **{location: "IBR" for location in IBERIA},
    **{location: "ARM" for location in ARMENIA},
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "location_count",
    "former_cau_locations", "culture", "religion", "government_type",
    "reform", "seeded_locations", "placements", "emblem", "source",
    "confidence",
)


def rows(path: Path) -> list[dict[str, str]]:
    payload = "\n".join(
        line for line in path.read_text(encoding="utf-8-sig").splitlines()
        if not line.lstrip().startswith("#")
    )
    return list(csv.DictReader(io.StringIO(payload)))


def keyed(path: Path, key: str) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows(path):
        if row[key] in output:
            raise ValueError(f"{path.relative_to(ROOT)} repeats {key} {row[key]}")
        output[row[key]] = row
    return output


def audit() -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    roster = keyed(ROSTER, "tag")
    profiles = keyed(PROFILES, "tag")
    cultures = keyed(CULTURES, "key")
    governments = keyed(GOVERNMENTS, "design_tag")
    coas = keyed(COAS, "tag")
    settlements = keyed(SETTLEMENTS, "tag")
    laws = keyed(LAWS, "tag")
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership_rows = rows(OWNERSHIP)
    owner_by_location = {row["location"]: row["tag"] for row in ownership_rows}
    owned = {
        tag: {row["location"] for row in ownership_rows if row["tag"] == tag}
        for tag in ("SVA", "CLZ", "IBR", "ARM")
    }
    area_rows = rows(AREAS)
    area_sets = {
        tag: {row["geography"] for row in area_rows if row["tag"] == tag}
        for tag in ("SVA", "CLZ", "IBR", "ARM")
    }

    if len(FORMER_CAU) != 47:
        failures.append("validator's former CAU contract is not exactly 47 locations")
    if "CAU" in roster or any(row["tag"] == "CAU" for row in ownership_rows):
        failures.append("obsolete CAU catch-all survives in roster or ownership")
    for path in (AREAS, RESIDUAL, DIRECT):
        if any(row["tag"] == "CAU" for row in rows(path)):
            failures.append(f"obsolete CAU selector survives in {path.relative_to(ROOT)}")
    for location, tag in EXPECTED_OWNER.items():
        if owner_by_location.get(location) != tag:
            failures.append(
                f"former CAU location {location} belongs to "
                f"{owner_by_location.get(location)}, expected {tag}"
            )

    if not {"hereti_province", "kakheti_province", "kartli_province"}.issubset(area_sets["IBR"]):
        failures.append("Iberia lacks its reviewed eastern-Georgian province frame")
    if not {"abkhazia_province", "samegrelo_province"}.issubset(area_sets["CLZ"]):
        failures.append("Colchis lacks its reviewed western coastal province frame")
    expected_totals = {"SVA": 4, "CLZ": 17, "IBR": 23, "ARM": 75}
    for tag, expected in expected_totals.items():
        if len(owned[tag]) != expected:
            failures.append(f"{tag} owns {len(owned[tag])} locations, expected {expected}")

    polity = roster.get("SVA")
    profile = profiles.get("SVA")
    government = governments.get("SVA")
    settlement = settlements.get("SVA")
    culture = cultures.get("antq_soanian")
    if polity is None:
        failures.append("missing reviewed Soanes polity")
    elif (
        polity["name"] != "Soanes"
        or polity["tier"] != "2"
        or polity["region"] != "Caucasus"
        or polity["map_capital"] != "ushguli"
        or "STR-CAUC" not in polity["source"]
    ):
        failures.append("Soanes identity, tier, capital, or source changed")
    if profile is None or profile["culture"] != "antq_soanian":
        failures.append("Soanes lacks its reviewed culture profile")
    if culture is None or culture["group"] != "antq_caucasian_group":
        failures.append("missing reviewed Soanian Caucasian culture")
    if government is None or (
        government["government_type"] != "tribe"
        or government["reform"] != "antq_soanian_king_and_council"
        or government["ruler"] != "random"
    ):
        failures.append("Soanes lacks its sourced anonymous king-and-council government")
    if settlement is None or int(settlement["seeded_locations"]) < 1:
        failures.append("Soanes lacks an opening settlement seed")
    if laws.get("SVA", {}).get("profile") != "iranian":
        failures.append("Soanes lacks the reviewed Caucasian legal adapter")
    if "SVA" not in coas or not coas["SVA"]["emblem"]:
        failures.append("Soanes lacks a direct reviewed UI standard")

    pop_overrides = keyed(POP_OVERRIDES, "location")
    for location in SOANES:
        override = pop_overrides.get(location)
        if override is None or override["culture"] != "antq_soanian":
            failures.append(f"{location} lacks its exact Soanian population override")

    reform = "antq_soanian_king_and_council"
    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")
    if not re.search(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reform_text):
        failures.append("generated Soanian king-and-council reform is missing")
    if f"unlock_government_reform = {reform}" not in advance_text:
        failures.append("opening research does not unlock the Soanian reform")

    engine_tag = mapping.get("SVA", "")
    for language in LANGUAGE_CLIENTS:
        text = (
            ROOT / f"main_menu/localization/{language}/antq_m3_countries_l_{language}.yml"
        ).read_text(encoding="utf-8-sig")
        for suffix in ("", "_ADJ"):
            key = engine_tag + suffix
            if not engine_tag or not re.search(rf"^\s*{re.escape(key)}:\s+\"", text, re.MULTILINE):
                failures.append(f"{language} lacks {key or 'the Soanes engine tag'}")
        if re.search(r'^\s*\w+:\s+"[^"]*Caucasian Highland Societies', text, re.I | re.M):
            failures.append(f"{language} retains the obsolete CAU display name")

    output = [{
        "design_tag": "SVA",
        "engine_tag": engine_tag,
        "name": polity["name"] if polity else "",
        "map_capital": polity["map_capital"] if polity else "",
        "location_count": str(len(owned["SVA"])),
        "former_cau_locations": str(len(owned["SVA"] & FORMER_CAU)),
        "culture": profile["culture"] if profile else "",
        "religion": profile["religion"] if profile else "",
        "government_type": government["government_type"] if government else "",
        "reform": government["reform"] if government else "",
        "seeded_locations": settlement["seeded_locations"] if settlement else "",
        "placements": settlement["placements"] if settlement else "",
        "emblem": coas.get("SVA", {}).get("emblem", ""),
        "source": polity["source"] if polity else "",
        "confidence": polity["confidence"] if polity else "",
    }]
    return output, failures


def render(output: list[dict[str, str]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(output)
    return stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        output, failures = audit()
        content = render(output)
        if args.write and not failures:
            LEDGER.write_text(content, encoding="utf-8-sig", newline="")
            print(f"s2_caucasian_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_caucasian_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print("s2_caucasian_granularity: PASS (47 former CAU locations repaired)")
        return 0
    except (KeyError, OSError, ValueError) as exc:
        print(f"s2_caucasian_granularity: FAIL ({exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate the sourced AD 1 Central Indian, Tamilakam, and atoll repair."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
RESIDUAL = ROOT / "docs/world_1ad/ownership_residual_areas.csv"
DIRECT_OWNERSHIP = ROOT / "docs/world_1ad/ownership_locations.csv"
PROFILES = ROOT / "docs/m4/tag_profiles.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
RELIGIONS = ROOT / "docs/m4/religions.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
DOCTRINES = ROOT / "docs/m12/religious_family_doctrines.csv"
DIRECT_RELIGION_ICONS = ROOT / "docs/m11/direct_religion_icons.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
SETTLEMENTS = ROOT / "docs/m5/global_settlement_audit.csv"
RGO_ANCHORS = ROOT / "docs/m5/rgo_anchors.csv"
LOCATION_NAMES = ROOT / "docs/m4/qualified_location_name_overrides.csv"
LEDGER = ROOT / "docs/m12/central_indian_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

# New frames contain 115 former CIN locations. The four bounded expansions
# contain the remaining 52: Chola 11, Pandya 12, Chera 11, Satavahana 18.
EXPECTED = {
    "TND": ("Tondai-Kanchi Polity", "kanchipuram", 10, "antq_tamil", "antq_brahmanism", "antq_tamilakam_velir_court"),
    "ATY": ("Atiyaman of Tagadur", "dharmapuri", 7, "antq_tamil", "antq_brahmanism", "antq_tamilakam_velir_court"),
    "UJJ": ("Ujjayini Urban Polity", "ujjain", 9, "antq_avanti_prakrit", "antq_brahmanism", "antq_central_indian_urban_kingship"),
    "VDS": ("Vedisa Urban Polity", "bhilsa", 9, "antq_avanti_prakrit", "antq_brahmanism", "antq_central_indian_urban_kingship"),
    "CED": ("Chedi Janapada", "kalinjar", 17, "antq_chedi_prakrit", "antq_brahmanism", "antq_central_indian_janapada"),
    "NVM": ("Narmada-Vindhya Megalithic Networks", "mandla", 18, "antq_narmada_vindhya_megalithic", "antq_central_indian_traditions", "antq_central_indian_megalithic_network"),
    "BGL": ("Son-Vindhya Iron-Age Networks", "rewa", 11, "antq_son_vindhya_iron_age", "antq_central_indian_traditions", "antq_central_indian_megalithic_network"),
    "DKS": ("Dakshina Kosala", "raipur", 21, "antq_upper_mahanadi", "antq_brahmanism", "antq_upper_mahanadi_kingship"),
    "BSR": ("Bastar Megalithic Networks", "jagdalpur", 9, "antq_bastar_megalithic", "antq_central_indian_traditions", "antq_central_indian_megalithic_network"),
    "MLD": ("Maldivian Atoll Networks", "male_atoll", 4, "antq_maldivian_maritime", "antq_brahmanism", "antq_indian_ocean_atoll_network"),
}
EXPANSIONS = {
    "CHL": (12, 1, "srirangam"),
    "PND": (13, 1, "madurai"),
    "CHE": (36, 25, "kodungallur"),
    "SAT": (255, 237, "daulatabad"),
}
CAPITAL_NAMES = {
    "kanchipuram": "Kanchi",
    "dharmapuri": "Tagadur Uplands",
    "ujjain": "Ujjayini",
    "bhilsa": "Vedisa",
    "kalinjar": "Chedi Uplands",
    "mandla": "Upper Narmada Corridor",
    "rewa": "Son-Vindhya Uplands",
    "raipur": "Upper Mahanadi Plain",
    "jagdalpur": "Bastar Plateau Horizon",
    "male_atoll": "Central Maldivian Atolls",
}
RGO_CONTRACT = {
    "male_atoll": "pearls",
    "addu_atoll": "fish",
    "nilandhe_atoll": "fish",
    "thiladhunmathi_atoll": "fish",
    "kayal": "pearls",
    "thoothukudi": "pearls",
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "location_count",
    "former_cin_locations", "culture", "religion", "government_type",
    "reform", "seeded_locations", "placements", "emblem", "source",
    "confidence",
)


def csv_rows(path: Path) -> list[dict[str, str]]:
    payload = "\n".join(
        line for line in path.read_text(encoding="utf-8-sig").splitlines()
        if not line.lstrip().startswith("#")
    )
    return list(csv.DictReader(io.StringIO(payload)))


def keyed(path: Path, key: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in csv_rows(path):
        value = row[key]
        if value in result:
            raise ValueError(f"{path.relative_to(ROOT)} repeats {key} {value}")
        result[value] = row
    return result


def expected_rows() -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    roster = keyed(ROSTER, "tag")
    profiles = keyed(PROFILES, "tag")
    cultures = keyed(CULTURES, "key")
    religions = keyed(RELIGIONS, "key")
    governments = keyed(GOVERNMENTS, "design_tag")
    coas = keyed(COAS, "tag")
    settlements = keyed(SETTLEMENTS, "tag")
    names = keyed(LOCATION_NAMES, "location")
    anchors = keyed(RGO_ANCHORS, "location")
    doctrine_rows = keyed(DOCTRINES, "religion")
    direct_religions = keyed(DIRECT_RELIGION_ICONS, "key")
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership = csv_rows(OWNERSHIP)
    counts = Counter(row["tag"] for row in ownership)
    owner = {row["location"]: row["tag"] for row in ownership}

    if "CIN" in roster or counts["CIN"]:
        failures.append("obsolete CIN catch-all survives in roster or ownership")
    if any(row["tag"] == "CIN" for row in csv_rows(RESIDUAL)):
        failures.append("obsolete CIN residual selector survives")
    if any(row["tag"] == "CIN" for row in csv_rows(DIRECT_OWNERSHIP)):
        failures.append("obsolete CIN direct selector survives")

    replacement_total = sum(value[2] for value in EXPECTED.values())
    expansion_total = sum(current - before for current, before, _ in EXPANSIONS.values())
    if replacement_total + expansion_total != 167:
        failures.append("former CIN contract must total exactly 167 locations")
    for tag, (current, _, capital) in EXPANSIONS.items():
        if counts[tag] != current:
            failures.append(f"{tag} bounded expansion changed from {current} locations")
        if owner.get(capital) != tag:
            failures.append(f"{tag} lost direct capital precedence at {capital}")

    if "antq_central_indian_traditions" not in religions:
        failures.append("Central Indian plural local-tradition family is missing")
    doctrine = doctrine_rows.get("antq_central_indian_traditions")
    if doctrine is None or any(not doctrine[f"choice_{index}"] for index in range(1, 5)):
        failures.append("Central Indian traditions lack four doctrine choices")
    direct_icon = direct_religions.get("antq_central_indian_traditions")
    if direct_icon is None or direct_icon["status"] != "complete":
        failures.append("Central Indian traditions lack a complete direct religion icon")
    for location, good in RGO_CONTRACT.items():
        anchor = anchors.get(location)
        if anchor is None or anchor["good"] != good:
            failures.append(f"{location} RGO must be directly anchored to {good}")

    rows: list[dict[str, str]] = []
    for tag, (name, capital, count, culture, religion, reform) in EXPECTED.items():
        polity = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        settlement = settlements.get(tag)
        if polity is None:
            failures.append(f"missing reviewed frame {tag}")
            continue
        if polity["name"] != name:
            failures.append(f"{tag} name changed: {polity['name']!r}")
        if re.search(r"\b(?:societies|land of|generic|placeholder)\b", polity["name"], re.I):
            failures.append(f"{tag} retains generic display name {polity['name']!r}")
        if polity["map_capital"] != capital or owner.get(capital) != tag:
            failures.append(f"{tag} must own reviewed capital {capital}")
        if counts[tag] != count:
            failures.append(f"{tag} ownership changed from {count} to {counts[tag]}")
        if profile is None or profile["culture"] != culture:
            failures.append(f"{tag} lacks reviewed culture {culture}")
        if profile is None or profile["religion"] != religion:
            failures.append(f"{tag} lacks reviewed religion {religion}")
        if culture not in cultures:
            failures.append(f"{tag} references undefined culture {culture}")
        if government is None or government["reform"] != reform:
            found = government["reform"] if government else "<missing>"
            failures.append(f"{tag} reform must be {reform}, found {found}")
        if coa is None or not coa["emblem"]:
            failures.append(f"{tag} lacks a direct reviewed UI standard")
        if settlement is None or int(settlement["seeded_locations"]) < 1:
            failures.append(f"{tag} lacks an opening settlement seed")
        name_row = names.get(capital)
        if name_row is None or name_row["historical_name"] != CAPITAL_NAMES[capital]:
            failures.append(f"{capital} lacks reviewed period-safe display name")
        engine_tag = mapping.get(tag, "")
        if not engine_tag:
            failures.append(f"{tag} lacks a collision-safe engine tag")
        rows.append({
            "design_tag": tag,
            "engine_tag": engine_tag,
            "name": polity["name"],
            "map_capital": polity["map_capital"],
            "location_count": str(counts[tag]),
            "former_cin_locations": str(count),
            "culture": profile["culture"] if profile else "",
            "religion": profile["religion"] if profile else "",
            "government_type": government["government_type"] if government else "",
            "reform": government["reform"] if government else "",
            "seeded_locations": settlement["seeded_locations"] if settlement else "",
            "placements": settlement["placements"] if settlement else "",
            "emblem": coa["emblem"] if coa else "",
            "source": polity["source"],
            "confidence": polity["confidence"],
        })

    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")
    for reform in {value[5] for value in EXPECTED.values()}:
        if not re.search(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reform_text):
            failures.append(f"generated reform definition missing {reform}")
        if f"unlock_government_reform = {reform}" not in advance_text:
            failures.append(f"opening research does not unlock {reform}")

    for language in LANGUAGES:
        text = (
            ROOT / f"main_menu/localization/{language}/antq_m3_countries_l_{language}.yml"
        ).read_text(encoding="utf-8-sig")
        for row in rows:
            for suffix in ("", "_ADJ"):
                key = row["engine_tag"] + suffix
                if not re.search(rf"^\s*{re.escape(key)}:\s+\"", text, re.MULTILINE):
                    failures.append(f"{language} lacks {key}")
        if re.search(r'^\s*\w+:\s+"[^"]*Central Indian Societies', text, re.I | re.M):
            failures.append(f"{language} retains generic CIN localization")
    return rows, failures


def render(rows: list[dict[str, str]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        rows, failures = expected_rows()
        content = render(rows)
        if args.write and not failures:
            LEDGER.parent.mkdir(parents=True, exist_ok=True)
            LEDGER.write_text(content, encoding="utf-8-sig", newline="")
            print(f"s2_central_indian_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_central_indian_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print(
            "s2_central_indian_granularity: PASS "
            "(CIN removed; 167 locations repaired; 10 new frames; "
            "7 cultures; 6 reforms; 10 standards; 6 direct RGO anchors; "
            "4 direct doctrine icons; 11-client localization)"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_central_indian_granularity: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

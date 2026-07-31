#!/usr/bin/env python3
"""Validate the eight exact AD 1 replacements for the final placeholder census."""

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
SELECTORS = tuple(
    ROOT / relative for relative in (
        "docs/world_1ad/ownership_areas.csv",
        "docs/world_1ad/ownership_residual_areas.csv",
        "docs/world_1ad/ownership_locations.csv",
    )
)
PROFILES = ROOT / "docs/m4/tag_profiles.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
RELIGIONS = ROOT / "docs/m4/religions.csv"
CULTURE_REMAP = ROOT / "docs/culture_remap.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
SETTLEMENTS = ROOT / "docs/m5/global_settlement_audit.csv"
LAWS = ROOT / "docs/m6/ancient_law_profiles.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
RELIGION_DEFINITIONS = ROOT / "in_game/common/religions/antq_m4_religions.txt"
LEDGER = ROOT / "docs/m12/final_placeholder_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)
OBSOLETE = {
    "MEL": "Melanesian Societies",
    "MIC": "Micronesian Societies",
    "ARA": "Arawak Societies",
    "CAR": "Carib Societies",
    "PAC": "Pacific Coast Societies",
    "TUP": "Tupi Societies",
}

# name, region, capital, culture, religion, reform, emblem prefix, exact locations
EXPECTED = {
    "DGU": (
        "Daga Highland", "Oceania", "daga_papua",
        "antq_daga_highland", "antq_papuan_local_traditions",
        "antq_daga_highland_garden_network", "ce_papua_",
        {"daga_papua"},
    ),
    "KBC": (
        "Bomberai South-Coast", "Oceania", "kaimana",
        "antq_bomberai_south_coast", "antq_papuan_local_traditions",
        "antq_bomberai_coastal_community_network", "ce_papua_",
        {"buruwai", "kaimana"},
    ),
    "EMR": (
        "Early Mariana Island", "Oceania", "guahan",
        "antq_early_mariana_island", "antq_mariana_island_traditions",
        "antq_early_mariana_island_network", "ce_polynesian_",
        {"guahan", "saipan"},
    ),
    "WCR": (
        "Yap-Ulithi Island", "Oceania", "yap",
        "antq_yap_ulithi_island", "antq_western_caroline_traditions",
        "antq_yap_ulithi_island_network", "ce_polynesian_",
        {"ulithi_atoll", "yap"},
    ),
    "OLC": (
        "Orinoco-Llanos Ceramic", "Caribbean-Amazon", "guamontey",
        "antq_orinoco_llanos_ceramic", "antq_caribbean",
        "antq_orinoco_llanos_ceramic_network", "ce_taino_",
        {"guamontey"},
    ),
    "WIC": (
        "Windward Island Ceramic", "Caribbean-Amazon", "carucairi",
        "antq_windward_island_ceramic", "antq_caribbean",
        "antq_windward_island_ceramic_network", "ce_taino_",
        {"carucairi"},
    ),
    "CCF": (
        "Central California Coast", "North America", "awaswas",
        "antq_central_california_coastal", "antq_north_american",
        "antq_central_california_coastal_network", "ce_native_american_",
        {"awaswas", "chochenyo", "mutsun", "tepotahal"},
    ),
    "ACU": (
        "Acutuba Central-Amazon", "Caribbean-Amazon", "manaos",
        "antq_acutuba_central_amazon", "antq_central_amazon_traditions",
        "antq_acutuba_central_amazon_network", "ce_native_american_",
        {"manaos"},
    ),
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "location_count",
    "culture", "religion", "government_type", "reform", "seeded_locations",
    "placements", "emblem", "source", "confidence",
)


def rows(path: Path) -> list[dict[str, str]]:
    payload = "\n".join(
        line for line in path.read_text(encoding="utf-8-sig").splitlines()
        if not line.lstrip().startswith("#")
    )
    return list(csv.DictReader(io.StringIO(payload)))


def keyed(path: Path, key: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows(path):
        value = row[key]
        if value in result:
            raise ValueError(f"{path.relative_to(ROOT)} repeats {key} {value}")
        result[value] = row
    return result


def audit() -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    roster = keyed(ROSTER, "tag")
    profiles = keyed(PROFILES, "tag")
    cultures = keyed(CULTURES, "key")
    religions = keyed(RELIGIONS, "key")
    governments = keyed(GOVERNMENTS, "design_tag")
    coas = keyed(COAS, "tag")
    settlements = keyed(SETTLEMENTS, "tag")
    laws = keyed(LAWS, "tag")
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership = rows(OWNERSHIP)
    owner = {row["location"]: row["tag"] for row in ownership}
    counts = Counter(row["tag"] for row in ownership)
    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")
    religion_text = RELIGION_DEFINITIONS.read_text(encoding="utf-8-sig")
    remap = rows(CULTURE_REMAP)

    expected_locations = set().union(*(item[7] for item in EXPECTED.values()))
    actual_locations = {row["location"] for row in ownership if row["tag"] in EXPECTED}
    if len(expected_locations) != 14 or actual_locations != expected_locations:
        failures.append("final replacement surface must contain exactly the pinned 14 land/island locations")
    for invalid_anchor in ("mariana", "monterey_coast"):
        if invalid_anchor in owner:
            failures.append(f"invalid former placeholder anchor remains controlled: {invalid_anchor}")
    for tag in OBSOLETE:
        if tag in roster or tag in profiles or tag in governments or counts[tag]:
            failures.append(f"obsolete placeholder {tag} survives in source or resolved output")
        for path in SELECTORS:
            if any(row["tag"] == tag for row in rows(path)):
                failures.append(f"obsolete {tag} selector survives in {path.relative_to(ROOT)}")

    exact_remaps = {
        (row["selector"], row["culture"])
        for row in remap
        if row["selector_type"] == "location" and row["selector"] in expected_locations
    }
    expected_remaps = {
        (location, item[3])
        for item in EXPECTED.values()
        for location in item[7]
    }
    if exact_remaps != expected_remaps:
        failures.append("the 14 reviewed locations lack exact culture remaps")
    for forbidden in ("micronesia_region", "piranga_province"):
        if any(row["selector"] == forbidden for row in remap):
            failures.append(f"obsolete broad or erroneous culture selector survives: {forbidden}")

    output: list[dict[str, str]] = []
    for tag, item in EXPECTED.items():
        name, region, capital, culture, religion, reform, emblem_prefix, locations = item
        polity = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        settlement = settlements.get(tag)
        if polity is None:
            failures.append(f"missing final replacement {tag}")
            continue
        actual = {location for location in locations if owner.get(location) == tag}
        if actual != locations or counts[tag] != len(locations):
            failures.append(f"{tag} must own exactly {sorted(locations)}")
        if polity["name"] != name or polity["region"] != region or polity["map_capital"] != capital:
            failures.append(f"{tag} identity, region, or capital changed")
        if profile is None or profile["culture"] != culture or profile["religion"] != religion:
            failures.append(f"{tag} lacks its reviewed culture/religion profile")
        if culture not in cultures:
            failures.append(f"{tag} references undefined culture {culture}")
        if religion not in religions:
            failures.append(f"{tag} references undefined religion {religion}")
        if not re.search(rf"(?m)^{re.escape(religion)}\s*=\s*\{{", religion_text):
            failures.append(f"generated religion definition missing {religion}")
        if government is None or government["government_type"] != "tribe" or government["reform"] != reform:
            failures.append(f"{tag} lacks reviewed government reform {reform}")
        if coa is None or not coa["emblem"].startswith(emblem_prefix):
            failures.append(f"{tag} lacks a reviewed direct regional standard")
        if settlement is None or int(settlement["seeded_locations"]) < 1:
            failures.append(f"{tag} lacks an opening settlement seed")
        if laws.get(tag, {}).get("profile") != "transoceanic":
            failures.append(f"{tag} lacks the transoceanic legal profile")
        if not re.search(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reform_text):
            failures.append(f"generated reform definition missing {reform}")
        if f"unlock_government_reform = {reform}" not in advance_text:
            failures.append(f"opening research does not unlock {reform}")
        output.append({
            "design_tag": tag,
            "engine_tag": mapping.get(tag, ""),
            "name": name,
            "map_capital": capital,
            "location_count": str(counts[tag]),
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

    obsolete_names = "|".join(re.escape(name) for name in OBSOLETE.values())
    for language in LANGUAGES:
        text = (
            ROOT / f"main_menu/localization/{language}/antq_m3_countries_l_{language}.yml"
        ).read_text(encoding="utf-8-sig")
        for entry in output:
            for suffix in ("", "_ADJ"):
                key = entry["engine_tag"] + suffix
                if not key or not re.search(rf"^\s*{re.escape(key)}:\s+\"", text, re.MULTILINE):
                    failures.append(f"{language} lacks {key or entry['design_tag']}")
        if re.search(rf'^\s*\w+:\s+"[^"]*(?:{obsolete_names})', text, re.I | re.M):
            failures.append(f"{language} retains an obsolete placeholder display name")
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
            print(f"s2_final_placeholder_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_final_placeholder_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print("s2_final_placeholder_granularity: PASS (8 frames; 14 exact land/island locations)")
        return 0
    except (KeyError, OSError, ValueError) as exc:
        print(f"s2_final_placeholder_granularity: FAIL ({exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

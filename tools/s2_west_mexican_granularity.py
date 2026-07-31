#!/usr/bin/env python3
"""Validate the sourced AD 1 West Mexican catch-all repair."""

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
AREAS = ROOT / "docs/world_1ad/ownership_areas.csv"
RESIDUAL = ROOT / "docs/world_1ad/ownership_residual_areas.csv"
DIRECT = ROOT / "docs/world_1ad/ownership_locations.csv"
PROFILES = ROOT / "docs/m4/tag_profiles.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
QUALIFIED_NAMES = ROOT / "docs/m4/qualified_location_name_overrides.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
SETTLEMENTS = ROOT / "docs/m5/global_settlement_audit.csv"
LAWS = ROOT / "docs/m6/ancient_law_profiles.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LEDGER = ROOT / "docs/m12/west_mexican_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

EXPECTED = {
    "NYS": ("Nayarit Shaft-Tomb", "Mesoamerica", "ahuacatlan", 6, "antq_nayarit_shaft_tomb", "antq_west_mexican_shaft_tomb_chiefdom"),
    "TJC": ("Central Jalisco Teuchitlan Networks", "Mesoamerica", "etzatlan", 10, "antq_central_jalisco_teuchitlan", "antq_teuchitlan_civic_center_network"),
    "SJB": ("Southern Jalisco Basin", "Mesoamerica", "sayula", 8, "antq_southern_jalisco_basin", "antq_west_mexican_shaft_tomb_chiefdom"),
    "COL": ("Colima-Coahuayana", "Mesoamerica", "coliman", 10, "antq_colima_coahuayana", "antq_west_mexican_shaft_tomb_chiefdom"),
    "BJC": ("Chupicuaro-Bajio", "Mesoamerica", "yuririapundaro", 8, "antq_chupicuaro_bajio", "antq_west_mexican_basin_community_network"),
    "PHC": ("Patzcuaro Highland", "Mesoamerica", "patzcuaro", 7, "antq_patzcuaro_highland", "antq_west_mexican_basin_community_network"),
    "MBC": ("Central Michoacan Basin", "Mesoamerica", "zinapecuaro", 11, "antq_central_michoacan_basin", "antq_west_mexican_basin_community_network"),
    "TVC": ("Toluca Valley Formative", "Mesoamerica", "ixtlahuaca", 9, "antq_toluca_valley_formative", "antq_west_mexican_basin_community_network"),
    "MZC": ("Mezcala-Balsas Preurban", "Mesoamerica", "tepecoacuilco", 6, "antq_mezcala_balsas_preurban", "antq_west_mexican_highland_corridor_network"),
    "JZH": ("Jalisco-Zacatecas", "Mesoamerica", "huaxtla", 15, "antq_jalisco_zacatecas_highland", "antq_west_mexican_highland_corridor_network"),
    "SDR": ("Ancestral Sonoran Desert", "North America", "shiewhibak", 8, "antq_ancestral_sonoran_desert", "antq_sonoran_desert_farming_network"),
}
PROVINCES = {
    "NYS": {"ahuacatlan_province", "aztatlan_province"},
    "TJC": {"autlan_province", "tonala_province"},
    "SJB": {"cuzalapa_province", "tochpan_province"},
    "COL": {"coliman_province", "tomatlan_province"},
    "BJC": {"cuitzeo_province", "ihuatzio_province"},
    "PHC": {"patzcuaro_province"},
    "MBC": {"tzintzuntzan_province", "zula_province"},
    "TVC": {"matlatzinco_province", "temascaltepec_province"},
    "MZC": {"tepecoacuilco_province"},
    "JZH": {"cuauhchinanco_province", "tepactitlan_province", "teulinchan_province"},
    "SDR": {"shiewhibak_province"},
}
FIELDS = (
    "design_tag", "engine_tag", "name", "region", "map_capital",
    "location_count", "former_wms_locations", "culture", "religion",
    "government_type", "reform", "seeded_locations", "placements", "emblem",
    "source", "confidence",
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
    governments = keyed(GOVERNMENTS, "design_tag")
    coas = keyed(COAS, "tag")
    settlements = keyed(SETTLEMENTS, "tag")
    laws = keyed(LAWS, "tag")
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership = rows(OWNERSHIP)
    counts = Counter(row["tag"] for row in ownership)
    owner = {row["location"]: row["tag"] for row in ownership}

    if "WMS" in roster or counts["WMS"]:
        failures.append("obsolete WMS catch-all survives in roster or ownership")
    for path in (AREAS, RESIDUAL, DIRECT):
        if any(row["tag"] == "WMS" for row in rows(path)):
            failures.append(f"obsolete WMS selector survives in {path.relative_to(ROOT)}")
    if sum(counts[tag] for tag in EXPECTED) != 98:
        failures.append("former WMS ownership must total exactly 98 locations")

    actual_provinces = {tag: set() for tag in EXPECTED}
    for row in rows(AREAS):
        if row["tag"] in actual_provinces:
            actual_provinces[row["tag"]].add(row["geography"])
    for tag, expected in PROVINCES.items():
        if actual_provinces[tag] != expected:
            failures.append(
                f"{tag} province contract changed: expected {sorted(expected)}, "
                f"found {sorted(actual_provinces[tag])}"
            )

    qualified = rows(QUALIFIED_NAMES)
    if not any(
        row.get("location") == "huaxtla"
        and row.get("culture") == "antq_jalisco_zacatecas_highland"
        and row.get("historical_name") == "Jalisco-Zacatecas Highlands"
        for row in qualified
    ):
        failures.append("JZH lacks the reviewed Huaxtla qualified location name")

    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")
    output: list[dict[str, str]] = []
    for tag, (name, region, capital, count, culture, reform) in EXPECTED.items():
        polity = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        settlement = settlements.get(tag)
        if polity is None:
            failures.append(f"missing reviewed West Mexican frame {tag}")
            continue
        if polity["name"] != name or polity["region"] != region or polity["map_capital"] != capital:
            failures.append(f"{tag} identity, region, or capital changed")
        if owner.get(capital) != tag or counts[tag] != count:
            failures.append(f"{tag} ownership must be {count} locations including {capital}")
        religion = "antq_north_american" if tag == "SDR" else "antq_mesoamerican"
        if profile is None or profile["culture"] != culture or profile["religion"] != religion:
            failures.append(f"{tag} lacks reviewed culture/religion profile")
        if culture not in cultures:
            failures.append(f"{tag} references undefined culture {culture}")
        if government is None or government["reform"] != reform:
            failures.append(f"{tag} lacks reviewed government reform {reform}")
        if coa is None or not coa["emblem"]:
            failures.append(f"{tag} lacks a direct reviewed UI standard")
        if settlement is None or int(settlement["seeded_locations"]) < 1:
            failures.append(f"{tag} lacks an opening settlement seed")
        if laws.get(tag, {}).get("profile") != "transoceanic":
            failures.append(f"{tag} lacks the reviewed transoceanic legal profile")
        if not re.search(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reform_text):
            failures.append(f"generated reform definition missing {reform}")
        if f"unlock_government_reform = {reform}" not in advance_text:
            failures.append(f"opening research does not unlock {reform}")
        engine_tag = mapping.get(tag, "")
        if not engine_tag:
            failures.append(f"{tag} lacks a collision-safe engine tag")
        output.append({
            "design_tag": tag,
            "engine_tag": engine_tag,
            "name": name,
            "region": region,
            "map_capital": capital,
            "location_count": str(counts[tag]),
            "former_wms_locations": str(counts[tag]),
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

    for language in LANGUAGES:
        text = (
            ROOT / f"main_menu/localization/{language}/antq_m3_countries_l_{language}.yml"
        ).read_text(encoding="utf-8-sig")
        for entry in output:
            for suffix in ("", "_ADJ"):
                key = entry["engine_tag"] + suffix
                if not re.search(rf"^\s*{re.escape(key)}:\s+\"", text, re.MULTILINE):
                    failures.append(f"{language} lacks {key}")
        if re.search(r'^\s*\w+:\s+"[^"]*West Mexican Societies', text, re.I | re.M):
            failures.append(f"{language} retains the obsolete WMS display name")
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
            print(f"s2_west_mexican_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_west_mexican_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print("s2_west_mexican_granularity: PASS (11 frames; 98 former WMS locations)")
        return 0
    except (KeyError, OSError, ValueError) as exc:
        print(f"s2_west_mexican_granularity: FAIL ({exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

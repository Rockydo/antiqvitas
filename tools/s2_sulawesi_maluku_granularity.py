#!/usr/bin/env python3
"""Validate the sourced AD 1 Sulawesi and North Maluku catch-all repair."""

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
LANGUAGES = ROOT / "docs/m4/languages.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
SETTLEMENTS = ROOT / "docs/m5/global_settlement_audit.csv"
LAWS = ROOT / "docs/m6/ancient_law_profiles.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LEDGER = ROOT / "docs/m12/sulawesi_maluku_granularity.csv"
LANGUAGE_CLIENTS = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

EXPECTED = {
    "BGT": ("Banggai-Tomini Maritime Communities", "banggai", "banggai_province", 6, "antq_banggai_tomini_maritime", "antq_sulawesi_coastal_exchange_network"),
    "BNC": ("Bone-Cenrana Coastal Communities", "bone", "bone_province", 5, "antq_bone_cenrana_coast", "antq_sulawesi_coastal_exchange_network"),
    "BGU": ("Bungku-Kendari Coast Communities", "bungku", "bungku_province", 5, "antq_bungku_kendari_coast", "antq_sulawesi_coastal_exchange_network"),
    "BTM": ("Buton-Muna Island Communities", "butung", "butung_province", 6, "antq_buton_muna_island", "antq_sulawesi_island_exchange_network"),
    "LRP": ("Lore-Poso Highland Communities", "loree", "donggala_province", 7, "antq_lore_poso_highland", "antq_sulawesi_highland_mortuary_network"),
    "GRT": ("Gorontalo-Tomini Communities", "gorontalo", "gorontalo_province", 7, "antq_gorontalo_tomini", "antq_sulawesi_peninsula_community_network"),
    "MKS": ("South Sulawesi Coastal Communities", "gowa", "makassar_province", 6, "antq_south_sulawesi_coast", "antq_sulawesi_coastal_exchange_network"),
    "KRM": ("Karama Valley Metal-Age Communities", "kalumpang", "mamudju_province", 6, "antq_karama_valley_metal_age", "antq_sulawesi_river_lake_network"),
    "MNH": ("North Sulawesi Peninsula Communities", "manado", "manado_province", 4, "antq_north_sulawesi_peninsula", "antq_sulawesi_peninsula_community_network"),
    "LWM": ("Matano-Luwu Lake-Coast Communities", "matano", "palopo_province", 5, "antq_matano_luwu_lake_coast", "antq_sulawesi_river_lake_network"),
    "NHM": ("North Halmahera Metal-Age Communities", "jailolo", "ternate_province", 6, "antq_north_halmahera_metal_age", "antq_north_maluku_metal_age_network"),
    "SHM": ("South Halmahera Metal-Age Communities", "maba_celebes", "tidore_province", 5, "antq_south_halmahera_metal_age", "antq_north_maluku_metal_age_network"),
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "province",
    "location_count", "former_ins_locations", "culture", "culture_group",
    "religion", "government_type", "reform", "seeded_locations",
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
    languages = keyed(LANGUAGES, "key")
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

    if "INS" in roster or counts["INS"]:
        failures.append("obsolete INS catch-all survives in roster or ownership")
    for path in (AREAS, RESIDUAL, DIRECT):
        if any(row["tag"] == "INS" for row in rows(path)):
            failures.append(f"obsolete INS selector survives in {path.relative_to(ROOT)}")
    if sum(counts[tag] for tag in EXPECTED) != 68:
        failures.append("former INS ownership must total exactly 68 locations")
    if languages.get("antq_north_maluku_language", {}).get("group") != "antq_north_maluku_group":
        failures.append("North Maluku mixed-language adapter is missing")

    actual_provinces = {tag: set() for tag in EXPECTED}
    for row in rows(AREAS):
        if row["tag"] in actual_provinces:
            actual_provinces[row["tag"]].add(row["geography"])

    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")
    output: list[dict[str, str]] = []
    for tag, (name, capital, province, count, culture, reform) in EXPECTED.items():
        polity = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        settlement = settlements.get(tag)
        culture_row = cultures.get(culture)
        if polity is None:
            failures.append(f"missing reviewed Sulawesi/Maluku frame {tag}")
            continue
        if polity["name"] != name or polity["region"] != "Southeast Asia" or polity["map_capital"] != capital:
            failures.append(f"{tag} identity, region, or capital changed")
        if owner.get(capital) != tag or counts[tag] != count:
            failures.append(f"{tag} ownership must be {count} locations including {capital}")
        if actual_provinces[tag] != {province}:
            failures.append(f"{tag} must use only {province}")
        if profile is None or profile["culture"] != culture or profile["religion"] != "antq_austronesian_religion":
            failures.append(f"{tag} lacks reviewed culture/religion profile")
        expected_group = "antq_north_maluku_group" if tag in {"NHM", "SHM"} else "antq_austronesian_group"
        if culture_row is None or culture_row["group"] != expected_group:
            failures.append(f"{tag} lacks reviewed culture-group boundary")
        if government is None or government["reform"] != reform:
            failures.append(f"{tag} lacks reviewed government reform {reform}")
        if coa is None or not coa["emblem"]:
            failures.append(f"{tag} lacks a direct reviewed UI standard")
        if settlement is None or int(settlement["seeded_locations"]) < 1:
            failures.append(f"{tag} lacks an opening settlement seed")
        if laws.get(tag, {}).get("profile") != "eastern":
            failures.append(f"{tag} lacks the reviewed Southeast Asian legal profile")
        if not re.search(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reform_text):
            failures.append(f"generated reform definition missing {reform}")
        if f"unlock_government_reform = {reform}" not in advance_text:
            failures.append(f"opening research does not unlock {reform}")
        engine_tag = mapping.get(tag, "")
        if not engine_tag:
            failures.append(f"{tag} lacks a collision-safe engine tag")
        output.append({
            "design_tag": tag, "engine_tag": engine_tag, "name": name,
            "map_capital": capital, "province": province,
            "location_count": str(counts[tag]),
            "former_ins_locations": str(counts[tag]), "culture": culture,
            "culture_group": culture_row["group"] if culture_row else "",
            "religion": profile["religion"] if profile else "",
            "government_type": government["government_type"] if government else "",
            "reform": government["reform"] if government else "",
            "seeded_locations": settlement["seeded_locations"] if settlement else "",
            "placements": settlement["placements"] if settlement else "",
            "emblem": coa["emblem"] if coa else "",
            "source": polity["source"], "confidence": polity["confidence"],
        })

    for language in LANGUAGE_CLIENTS:
        text = (
            ROOT / f"main_menu/localization/{language}/antq_m3_countries_l_{language}.yml"
        ).read_text(encoding="utf-8-sig")
        for entry in output:
            for suffix in ("", "_ADJ"):
                key = entry["engine_tag"] + suffix
                if not re.search(rf"^\s*{re.escape(key)}:\s+\"", text, re.MULTILINE):
                    failures.append(f"{language} lacks {key}")
        if re.search(r'^\s*\w+:\s+"[^"]*Island Southeast Asian Societies', text, re.I | re.M):
            failures.append(f"{language} retains the obsolete INS display name")
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
            print(f"s2_sulawesi_maluku_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_sulawesi_maluku_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print("s2_sulawesi_maluku_granularity: PASS (12 frames; 68 former INS locations)")
        return 0
    except (KeyError, OSError, ValueError) as exc:
        print(f"s2_sulawesi_maluku_granularity: FAIL ({exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

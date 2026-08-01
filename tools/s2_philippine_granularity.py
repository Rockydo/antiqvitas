#!/usr/bin/env python3
"""Validate the sourced AD 1 Philippine catch-all repair."""

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
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
SETTLEMENTS = ROOT / "docs/m5/global_settlement_audit.csv"
LAWS = ROOT / "docs/m6/ancient_law_profiles.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LEDGER = ROOT / "docs/m12/philippine_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

EXPECTED = {
    "LZC": ("Northwest Luzon Coastal", "binalatongan", "samtoy_province", 4, "antq_northwest_luzon_coast", "antq_philippine_coastal_river_network"),
    "CXR": ("Central Luzon River", "pulilan", "pampanga_province", 5, "antq_central_luzon_river", "antq_philippine_coastal_river_network"),
    "MBL": ("Manila Bay-Laguna", "maynila", "katagalugan_province", 6, "antq_manila_bay_laguna", "antq_philippine_coastal_river_network"),
    "BCP": ("Bicol Peninsula Metal-Age", "naga_bikol", "ibalong_province", 6, "antq_bicol_peninsula_metal_age", "antq_philippine_coastal_river_network"),
    "MDR": ("Mindoro Maritime", "kalapang", "mait_province", 4, "antq_mindoro_maritime", "antq_philippine_cave_coast_network"),
    "PNY": ("Panay Metal-Age", "irong_irong", "panay_province", 5, "antq_panay_metal_age", "antq_philippine_mortuary_community_network"),
    "NGR": ("Negros Metal-Age", "tanjay", "buglas_province", 4, "antq_negros_metal_age", "antq_philippine_mortuary_community_network"),
    "CBH": ("Cebu-Bohol Island", "singhapala", "central_visayas_province", 4, "antq_cebu_bohol_island", "antq_philippine_island_exchange_network"),
    "PLW": ("Palawan Cave-Coast", "taytay", "palawan_province", 3, "antq_palawan_cave_coast", "antq_philippine_cave_coast_network"),
    "AGS": ("Agusan River", "butuan", "agusan_province", 6, "antq_agusan_river", "antq_philippine_coastal_river_network"),
    "LNO": ("Lanao Coast-Lake", "malabang", "agus_province", 3, "antq_lanao_coast_lake", "antq_philippine_coastal_river_network"),
    "PCT": ("Pulangi-Cotabato Basin", "kuta_watu", "mindanao_province", 8, "antq_pulangi_cotabato_basin", "antq_philippine_coastal_river_network"),
    "MTT": ("Maitum-Sarangani Mortuary", "makar", "tagloc_province", 2, "antq_maitum_sarangani", "antq_philippine_mortuary_community_network"),
    "ZBG": ("Zamboanga Peninsula", "samboangan", "zamboanga_province", 6, "antq_zamboanga_peninsula", "antq_philippine_coastal_river_network"),
    "SLU": ("Sulu Island", "maimbung", "sulu_province", 3, "antq_sulu_island", "antq_philippine_island_exchange_network"),
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "province",
    "location_count", "former_phl_locations", "culture", "religion",
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

    if "PHL" in roster or counts["PHL"]:
        failures.append("obsolete PHL catch-all survives in roster or ownership")
    for path in (AREAS, RESIDUAL, DIRECT):
        if any(row["tag"] == "PHL" for row in rows(path)):
            failures.append(f"obsolete PHL selector survives in {path.relative_to(ROOT)}")
    if sum(counts[tag] for tag in EXPECTED) != 69:
        failures.append("former PHL ownership must total exactly 69 locations")

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
        if polity is None:
            failures.append(f"missing reviewed Philippine frame {tag}")
            continue
        if polity["name"] != name or polity["region"] != "Southeast Asia" or polity["map_capital"] != capital:
            failures.append(f"{tag} identity, region, or capital changed")
        if owner.get(capital) != tag or counts[tag] != count:
            failures.append(f"{tag} ownership must be {count} locations including {capital}")
        if actual_provinces[tag] != {province}:
            failures.append(f"{tag} must use only {province}")
        if profile is None or profile["culture"] != culture or profile["religion"] != "antq_austronesian_religion":
            failures.append(f"{tag} lacks reviewed culture/religion profile")
        if culture not in cultures:
            failures.append(f"{tag} references undefined culture {culture}")
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
        if f"unlock_government_reform = {reform}" in advance_text:
            failures.append(f"opening reform leaked into research: {reform}")
        engine_tag = mapping.get(tag, "")
        if not engine_tag:
            failures.append(f"{tag} lacks a collision-safe engine tag")
        output.append({
            "design_tag": tag, "engine_tag": engine_tag, "name": name,
            "map_capital": capital, "province": province,
            "location_count": str(counts[tag]),
            "former_phl_locations": str(counts[tag]),
            "culture": profile["culture"] if profile else "",
            "religion": profile["religion"] if profile else "",
            "government_type": government["government_type"] if government else "",
            "reform": government["reform"] if government else "",
            "seeded_locations": settlement["seeded_locations"] if settlement else "",
            "placements": settlement["placements"] if settlement else "",
            "emblem": coa["emblem"] if coa else "",
            "source": polity["source"], "confidence": polity["confidence"],
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
        if re.search(r'^\s*\w+:\s+"[^"]*Philippine Societies', text, re.I | re.M):
            failures.append(f"{language} retains the obsolete PHL display name")
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
            print(f"s2_philippine_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_philippine_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print("s2_philippine_granularity: PASS (15 frames; 69 former PHL locations)")
        return 0
    except (KeyError, OSError, ValueError) as exc:
        print(f"s2_philippine_granularity: FAIL ({exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate the sourced AD 1 Mesoamerican catch-all repair."""

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
LEDGER = ROOT / "docs/m12/mesoamerican_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

EXPECTED = {
    "SLC": ("Basin South-Lake Communities", "chalco", 4, "antq_basin_south_lake", "antq_mesoamerican_formative_civic_network"),
    "PTF": ("Puebla-Tlaxcala Formative Centers", "cholollan", 16, "antq_puebla_tlaxcala_formative", "antq_mesoamerican_formative_civic_network"),
    "MRF": ("Morelos Formative Communities", "cuauhnahuac", 6, "antq_morelos_formative", "antq_mesoamerican_formative_civic_network"),
    "NHC": ("Northern Highland Corridor Communities", "ixmiquilpan", 14, "antq_northern_highland_corridor", "antq_mesoamerican_exchange_corridor_network"),
    "TPC": ("Tamtoc-Panuco Communities", "tamtoc", 6, "antq_tamtoc_panuco", "antq_mesoamerican_formative_civic_network"),
    "GLS": ("Gulf Lowland-Sierra Networks", "xalapa", 13, "antq_gulf_lowland_sierra", "antq_mesoamerican_exchange_corridor_network"),
    "GPC": ("Guerrero Pacific Communities", "tlapan", 13, "antq_guerrero_pacific", "antq_mesoamerican_exchange_corridor_network"),
    "ONH": ("Oaxaca Northwest Highland Communities", "huajuapan", 6, "antq_oaxaca_northwest_highland", "antq_mesoamerican_highland_community_network"),
    "IZA": ("Izapa-Soconusco Center", "huehuetan", 4, "antq_izapa_soconusco", "antq_mesoamerican_urban_ritual_center"),
    "CPH": ("Chiapas Highland-Lowland Networks", "zinacantan", 11, "antq_chiapas_highland_lowland", "antq_mesoamerican_highland_community_network"),
}
TEO = ("Teotihuacan", "tehotihuacan", 10, "antq_teotihuacano", "antq_mesoamerican_urban_ritual_center")
CUI = ("Cuicuilco", "azcapotzalco", 1, "antq_teotihuacano", "antq_mesoamerican_formative_civic_network")
AREA_CONTRACT = {
    "TEO": {"tetzcoco_province", "tlapacoya_province"},
    "SLC": set(),
    "PTF": {"tlaxcala_province", "tepeyacac_province", "tetela_province"},
    "MRF": {"tlalnahuac_province"},
    "NHC": {"axocopan_province", "xilotepec_province", "metztitlan_province"},
    "TPC": {"huasteca_province", "tetzapotitlan_province"},
    "GLS": {"tlatlauquitepec_province", "tuxpan_province", "xalapa_province"},
    "GPC": {"cihuatlan_province", "tlapan_province", "yopitzinco_province"},
    "ONH": {"yohualtepec_province"},
    "IZA": {"zaklohpakab_province"},
    "CPH": {"otolum_province", "zinacantan_province"},
}
SLC_DIRECT = {"chalco", "tenochtitlan", "tlacopan", "xochimilco"}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "location_count",
    "former_mss_locations", "culture", "religion", "government_type", "reform",
    "seeded_locations", "placements", "emblem", "source", "confidence",
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
    law_profiles = keyed(LAWS, "tag")
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership = rows(OWNERSHIP)
    counts = Counter(row["tag"] for row in ownership)
    owner = {row["location"]: row["tag"] for row in ownership}

    if "MSS" in roster or counts["MSS"]:
        failures.append("obsolete MSS catch-all survives in roster or ownership")
    if any(row["tag"] == "MSS" for row in rows(RESIDUAL)):
        failures.append("obsolete MSS residual selector survives")
    if any(row["tag"] == "MSS" for row in rows(DIRECT)):
        failures.append("obsolete MSS direct selector survives")
    if sum(value[2] for value in EXPECTED.values()) != 93:
        failures.append("successor-frame contract must total exactly 93 locations")
    if sum(counts[tag] for tag in EXPECTED) + counts["TEO"] - 1 != 102:
        failures.append("former MSS ownership must total 102: 93 successors plus 9 Teotihuacan locations")

    actual_areas: dict[str, set[str]] = {tag: set() for tag in AREA_CONTRACT}
    for row in rows(AREAS):
        if row["tag"] in actual_areas:
            actual_areas[row["tag"]].add(row["geography"])
    for tag, expected in AREA_CONTRACT.items():
        if actual_areas[tag] != expected:
            failures.append(
                f"{tag} geography contract changed: expected {sorted(expected)}, "
                f"found {sorted(actual_areas[tag])}"
            )

    direct = rows(DIRECT)
    slc_direct = {row["location"] for row in direct if row["tag"] == "SLC"}
    if slc_direct != SLC_DIRECT:
        failures.append("SLC exact-field contract changed around the separately owned Cuicuilco proxy")
    expected_capitals = {
        (tag, value[1]) for tag, value in EXPECTED.items()
    } | {("TEO", TEO[1]), ("CUI", CUI[1])}
    actual_capitals = {
        (row["tag"], row["location"])
        for row in direct
        if row["tag"] in set(EXPECTED) | {"TEO", "CUI"}
        and row["location"] in {value[1] for value in EXPECTED.values()} | {TEO[1], CUI[1]}
    }
    if actual_capitals != expected_capitals:
        failures.append("Mesoamerican direct-capital contract changed")

    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")
    output: list[dict[str, str]] = []
    contracts = {**EXPECTED, "TEO": TEO, "CUI": CUI}
    for tag, (name, capital, count, culture, reform) in contracts.items():
        polity = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        settlement = settlements.get(tag)
        if polity is None:
            failures.append(f"missing reviewed Mesoamerican frame {tag}")
            continue
        if polity["name"] != name or polity["map_capital"] != capital:
            failures.append(f"{tag} identity or capital changed")
        if owner.get(capital) != tag or counts[tag] != count:
            failures.append(f"{tag} ownership must be {count} locations including {capital}")
        if profile is None or profile["culture"] != culture or profile["religion"] != "antq_mesoamerican":
            failures.append(f"{tag} lacks reviewed culture/religion profile")
        if culture not in cultures:
            failures.append(f"{tag} references undefined culture {culture}")
        if government is None or government["reform"] != reform:
            failures.append(f"{tag} lacks reviewed government reform {reform}")
        if coa is None or not coa["emblem"]:
            failures.append(f"{tag} lacks a direct reviewed UI standard")
        if settlement is None or int(settlement["seeded_locations"]) < 1:
            failures.append(f"{tag} lacks an opening settlement seed")
        if law_profiles.get(tag, {}).get("profile") != "transoceanic":
            failures.append(f"{tag} lacks the reviewed Mesoamerican legal profile")
        if not re.search(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reform_text):
            failures.append(f"generated reform definition missing {reform}")
        if f"unlock_government_reform = {reform}" not in advance_text:
            failures.append(f"opening research does not unlock {reform}")
        engine_tag = mapping.get(tag, "")
        if not engine_tag:
            failures.append(f"{tag} lacks a collision-safe engine tag")
        former = count if tag in EXPECTED else (9 if tag == "TEO" else 0)
        output.append({
            "design_tag": tag,
            "engine_tag": engine_tag,
            "name": name,
            "map_capital": capital,
            "location_count": str(counts[tag]),
            "former_mss_locations": str(former),
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
        if re.search(r'^\s*\w+:\s+"[^"]*Mesoamerican Societies', text, re.I | re.M):
            failures.append(f"{language} retains the obsolete MSS display name")
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
            print(f"s2_mesoamerican_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_mesoamerican_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print("s2_mesoamerican_granularity: PASS (12 frames; 102 former MSS locations)")
        return 0
    except (KeyError, OSError, ValueError) as exc:
        print(f"s2_mesoamerican_granularity: FAIL ({exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

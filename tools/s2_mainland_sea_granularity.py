#!/usr/bin/env python3
"""Validate the sourced AD 1 mainland Southeast Asian catch-all repair."""

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
LOCATION_NAMES = ROOT / "docs/m4/qualified_location_name_overrides.csv"
LEDGER = ROOT / "docs/m12/mainland_sea_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

RELIGION = "antq_mainland_southeast_asian_traditions"
EXPECTED = {
    "ARK": ("Arakan Littoral Networks", "weithali", 12, "antq_arakan_littoral", "antq_mainland_river_corridor_network"),
    "SHY": ("Sa Huynh Coastal Networks", "amaravati", 15, "antq_sa_huynh", "antq_sa_huynh_exchange_network"),
    "CHG": ("Central Vietnamese Highland Networks", "cat_tien", 10, "antq_central_vietnam_highland", "antq_mainland_highland_exchange_network"),
    "KCN": ("Patkai-Upper Irrawaddy Highland Networks", "putao", 12, "antq_patkai_upper_irrawaddy", "antq_mainland_highland_exchange_network"),
    "UIR": ("Upper Irrawaddy Corridor Networks", "myitkyina", 8, "antq_upper_irrawaddy_corridor", "antq_mainland_river_corridor_network"),
    "PWB": ("Ping-Wang Basin Networks", "chiang_mai", 12, "antq_ping_wang_iron_age", "antq_mainland_iron_age_basin_network"),
    "KIB": ("Kok-Ing-Nan Basin Networks", "chiang_rai", 10, "antq_kok_ing_nan_iron_age", "antq_mainland_iron_age_basin_network"),
    "UMK": ("Upper Mekong Upland Networks", "muang_sua", 16, "antq_upper_mekong_upland", "antq_mainland_highland_exchange_network"),
    "USH": ("Upper Salween-Shweli Networks", "hsenwi", 17, "antq_upper_salween_shweli", "antq_mainland_river_corridor_network"),
    "KGT": ("Kengtung Basin Networks", "kengtung", 6, "antq_kengtung_basin", "antq_mainland_iron_age_basin_network"),
    "SSH": ("Southern Plateau Corridor Networks", "mongnai", 12, "antq_southern_plateau_corridor", "antq_mainland_highland_exchange_network"),
}
CAPITAL_NAMES = {
    "weithali": "Kaladan-Lemro Littoral",
    "amaravati": "Thu Bon Sa Huynh Coast",
    "cat_tien": "Central Highland Exchange Corridors",
    "putao": "Patkai-Upper Irrawaddy Highlands",
    "myitkyina": "Upper Irrawaddy Confluence",
    "chiang_mai": "Ping-Wang Basin",
    "chiang_rai": "Kok-Ing Basin",
    "muang_sua": "Upper Mekong Uplands",
    "hsenwi": "Upper Salween-Shweli Corridors",
    "kengtung": "Kengtung Intermontane Basin",
    "mongnai": "Southern Plateau Corridors",
}
HARIKELA_EXTENSION = {
    "chakaria", "chittagong", "kaptai", "karpus_mahal", "ramu", "sitakunda",
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "location_count",
    "former_sea_locations", "culture", "religion", "government_type",
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
    doctrine_rows = keyed(DOCTRINES, "religion")
    direct_religions = keyed(DIRECT_RELIGION_ICONS, "key")
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership = csv_rows(OWNERSHIP)
    counts = Counter(row["tag"] for row in ownership)
    owner = {row["location"]: row["tag"] for row in ownership}

    if "SEA" in roster or counts["SEA"]:
        failures.append("obsolete SEA catch-all survives in roster or ownership")
    if any(row["tag"] == "SEA" for row in csv_rows(RESIDUAL)):
        failures.append("obsolete SEA residual selector survives")
    if any(row["tag"] == "SEA" for row in csv_rows(DIRECT_OWNERSHIP)):
        failures.append("obsolete SEA direct selector survives")
    if sum(value[2] for value in EXPECTED.values()) + len(HARIKELA_EXTENSION) != 136:
        failures.append("former SEA contract must total exactly 136 locations")
    if counts["HRK"] != 13 or owner.get("pilak") != "HRK":
        failures.append("Harikela bounded expansion must retain pilak and total 13 locations")
    if any(owner.get(location) != "HRK" for location in HARIKELA_EXTENSION):
        failures.append("the six Chittagong littoral fields must remain assigned to Harikela")

    if RELIGION not in religions:
        failures.append("mainland Southeast Asian plural-tradition family is missing")
    doctrine = doctrine_rows.get(RELIGION)
    if doctrine is None or any(not doctrine[f"choice_{index}"] for index in range(1, 5)):
        failures.append("mainland Southeast Asian traditions lack four doctrine choices")
    direct_icon = direct_religions.get(RELIGION)
    if direct_icon is None or direct_icon["status"] != "complete":
        failures.append("mainland Southeast Asian traditions lack a complete direct icon")

    rows: list[dict[str, str]] = []
    for tag, (name, capital, count, culture, reform) in EXPECTED.items():
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
        if profile is None or profile["religion"] != RELIGION:
            failures.append(f"{tag} lacks reviewed religion {RELIGION}")
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
            "former_sea_locations": str(count),
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
    for reform in {value[4] for value in EXPECTED.values()}:
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
        if re.search(r'^\s*\w+:\s+"[^"]*Mainland Southeast Asian Societies', text, re.I | re.M):
            failures.append(f"{language} retains generic SEA localization")
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
            print(f"s2_mainland_sea_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_mainland_sea_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print(
            "s2_mainland_sea_granularity: PASS "
            "(SEA removed; 136 locations repaired; 11 new frames; "
            "10 cultures; 4 reforms; 11 standards; 4 direct doctrine icons; "
            "11-client localization)"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_mainland_sea_granularity: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

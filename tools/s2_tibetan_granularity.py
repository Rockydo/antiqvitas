#!/usr/bin/env python3
"""Validate the sourced AD 1 Tibetan Plateau replacement."""

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
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
SETTLEMENTS = ROOT / "docs/m5/global_settlement_audit.csv"
RGO_ANCHORS = ROOT / "docs/m5/rgo_anchors.csv"
CUSTOM_GOODS = ROOT / "docs/m5/custom_goods.csv"
LOCATION_NAMES = ROOT / "docs/m4/qualified_location_name_overrides.csv"
LEDGER = ROOT / "docs/m12/tibetan_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

EXPECTED = {
    "ZHZ": ("Zhang Zhung", "khyunglung", 38, "antq_zhangzhung", "antq_western_plateau_traditions", "antq_zhangzhung_plateau_kingship"),
    "SMP": ("Sumpa", "chabcha", 33, "antq_sumpa", "antq_western_plateau_traditions", "antq_sumpa_highland_confederacy"),
    "CTP": ("Changtang Pastoral Networks", "shantsa", 7, "antq_changtang_pastoral", "antq_western_plateau_traditions", "antq_changtang_pastoral_network"),
    "YAR": ("Bangga-Yarlung Horizon", "nedong", 6, "antq_yarlung_agropastoral", "antq_central_plateau_traditions", "antq_central_plateau_agropastoral_network"),
    "UTV": ("Central Tsangpo Valley Network", "lhasa", 22, "antq_central_tsangpo", "antq_central_plateau_traditions", "antq_central_plateau_agropastoral_network"),
    "TSG": ("Western Tsang Valley Network", "shigatse", 18, "antq_western_tsang", "antq_central_plateau_traditions", "antq_central_plateau_agropastoral_network"),
    "QMC": ("Qamdo River-Corridor Network", "chamdo", 28, "antq_qamdo_corridor", "antq_eastern_plateau_traditions", "antq_eastern_plateau_corridor_network"),
    "DRC": ("Drichu Highland Network", "derge", 29, "antq_drichu_highland", "antq_eastern_plateau_traditions", "antq_eastern_plateau_corridor_network"),
    "EPC": ("Eastern Plateau Corridor Network", "dartsedo", 18, "antq_eastern_plateau_corridor", "antq_eastern_plateau_traditions", "antq_eastern_plateau_corridor_network"),
}
CAPITAL_NAMES = {
    "khyunglung": "Western Zhang Zhung Plateau",
    "chabcha": "Sumpa Northeastern Plateau",
    "shantsa": "Northern Changtang Pastures",
    "nedong": "Bangga-Yarlung Valley",
    "lhasa": "Qugong Valley",
    "shigatse": "Western Tsangpo Valleys",
    "chamdo": "Qamdo River Corridors",
    "derge": "Drichu Highlands",
    "dartsedo": "Eastern Plateau Passage",
}
FAITHS = {
    "antq_western_plateau_traditions",
    "antq_central_plateau_traditions",
    "antq_eastern_plateau_traditions",
}
RGO_CONTRACT = {
    "lhasa": "antq_barley",
    "nedong": "antq_barley",
    "shigatse": "antq_barley",
    "shantsa": "livestock",
    "derge": "livestock",
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "location_count",
    "culture", "religion", "government_type", "reform", "seeded_locations",
    "placements", "emblem", "source", "confidence",
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
    goods = keyed(CUSTOM_GOODS, "key")
    anchors = keyed(RGO_ANCHORS, "location")
    doctrines = keyed(DOCTRINES, "religion")
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership = csv_rows(OWNERSHIP)
    counts = Counter(row["tag"] for row in ownership)
    owner = {row["location"]: row["tag"] for row in ownership}

    if "TIB" in roster or counts["TIB"]:
        failures.append("obsolete TIB catch-all survives in roster or resolved ownership")
    if any(row["tag"] == "TIB" for row in csv_rows(RESIDUAL)):
        failures.append("obsolete TIB residual selector survives")
    if any(row["tag"] == "TIB" for row in csv_rows(DIRECT_OWNERSHIP)):
        failures.append("obsolete TIB direct selector survives")
    if sum(counts[tag] for tag in EXPECTED) != 199:
        failures.append("nine replacement frames must control exactly 199 locations")
    if max((counts[tag] for tag in EXPECTED), default=0) > 38:
        failures.append("no replacement frame may exceed the reviewed 38-location bound")

    for faith in FAITHS:
        if faith not in religions:
            failures.append(f"missing plural plateau belief family {faith}")
        doctrine = doctrines.get(faith)
        if doctrine is None or any(not doctrine[f"choice_{index}"] for index in range(1, 5)):
            failures.append(f"{faith} lacks four direct doctrine choices")

    if "antq_barley" not in goods:
        failures.append("plateau naked barley is not registered as a custom raw good")
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
        if settlement is None or int(settlement["seeded_locations"]) < 1 or int(settlement["placements"]) < 1:
            failures.append(f"{tag} lacks a capacity-bounded opening settlement seed")
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
        if re.search(r'^\s*\w+:\s+"[^"]*Tibetan Societies', text, re.MULTILINE | re.I):
            failures.append(f"{language} retains generic TIB localization")
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
            print(f"s2_tibetan_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_tibetan_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print(
            "s2_tibetan_granularity: PASS "
            "(TIB removed; 9 frames/199 locations; 8 new cultures; "
            "3 belief families/12 doctrines; 5 reforms; 9 standards; "
            "9 settlement seeds; barley/livestock RGO corrections; "
            "11-client localization)"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_tibetan_granularity: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

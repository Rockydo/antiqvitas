#!/usr/bin/env python3
"""Validate the sourced AD 1 Bornean catch-all repair."""

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
RELIGIONS = ROOT / "docs/m4/religions.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
DOCTRINES = ROOT / "docs/m12/religious_family_doctrines.csv"
DIRECT_RELIGION_ICONS = ROOT / "docs/m11/direct_religion_icons.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
SETTLEMENTS = ROOT / "docs/m5/global_settlement_audit.csv"
LOCATION_NAMES = ROOT / "docs/m4/qualified_location_name_overrides.csv"
LEDGER = ROOT / "docs/m12/bornean_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

RELIGION = "antq_borneo_late_prehistoric_traditions"
EXPECTED = {
    "NBR": ("Niah-Brunei Bay Cave-River Communities", "niah", 10, "antq_niah_brunei_bay", "antq_borneo_cave_river_network"),
    "RSW": ("Rajang-Sarawak Coastal Networks", "santubong", 10, "antq_rajang_sarawak", "antq_borneo_coastal_exchange_network"),
    "KSB": ("Kinabatangan-Sabah Littoral Networks", "kinabatangan", 11, "antq_kinabatangan_sabah", "antq_borneo_coastal_exchange_network"),
    "NEB": ("Northeast Borneo River-Sea Networks", "sesayap", 11, "antq_northeast_borneo_river_sea", "antq_borneo_coastal_exchange_network"),
    "SGK": ("Sangkulirang Karst Communities", "karangan", 5, "antq_sangkulirang_karst", "antq_borneo_cave_river_network"),
    "MHK": ("Mahakam River Networks", "muarakaman", 13, "antq_mahakam_river", "antq_borneo_interior_river_network"),
    "KPM": ("Kapuas-Melawi River Networks", "pinoh", 11, "antq_kapuas_melawi", "antq_borneo_interior_river_network"),
    "WBC": ("Western Borneo Coastal Networks", "sambas", 12, "antq_west_borneo_coastal", "antq_borneo_coastal_exchange_network"),
    "CSB": ("Central-Southern Borneo River Networks", "sampit", 14, "antq_central_south_borneo", "antq_borneo_interior_river_network"),
    "BPR": ("Banjar-Paser River-Coast Networks", "banua_lawas", 13, "antq_banjar_paser", "antq_borneo_foothill_iron_network"),
}
CAPITAL_NAMES = {
    "niah": "Niah Cave-River Corridor",
    "santubong": "Sarawak Delta Corridors",
    "kinabatangan": "Kinabatangan Littoral Corridor",
    "sesayap": "Northeast River-Sea Corridors",
    "karangan": "Sangkulirang Karst",
    "muarakaman": "Middle Mahakam Corridor",
    "pinoh": "Kapuas-Melawi Interior",
    "sambas": "Western Borneo Littoral",
    "sampit": "Central-Southern River Corridors",
    "banua_lawas": "Meratus-Barito Foothills",
}
AREA_CONTRACT = {
    "NBR": {"baram_province", "lower_brunei_province", "upper_brunei_province"},
    "RSW": {"lower_rajang_province", "santubong_province"},
    "KSB": {"kinabatangan_province", "kudat_province"},
    "NEB": {"berau_province", "tarakan_province"},
    "SGK": {"karangan_province"},
    "MHK": {"lower_mahakam_province", "upper_mahakam_province"},
    "KPM": {"upper_kapuas_province", "lower_kapuas_province"},
    "WBC": {"sambas_province", "sukadana_province"},
    "CSB": {
        "kuripan_province", "lamandau_province", "mendawai_province",
        "sampit_province", "upper_barito_province",
    },
    "BPR": {"banjar_province", "paser_province"},
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "location_count",
    "former_bor_locations", "culture", "religion", "government_type",
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
    doctrines = keyed(DOCTRINES, "religion")
    direct_religions = keyed(DIRECT_RELIGION_ICONS, "key")
    names = {
        (row["location"], row["culture"]): row
        for row in csv_rows(LOCATION_NAMES)
    }
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership = csv_rows(OWNERSHIP)
    counts = Counter(row["tag"] for row in ownership)
    owner = {row["location"]: row["tag"] for row in ownership}

    if "BOR" in roster or counts["BOR"]:
        failures.append("obsolete BOR catch-all survives in roster or ownership")
    if any(row["tag"] == "BOR" for row in csv_rows(RESIDUAL)):
        failures.append("obsolete BOR residual selector survives")
    if any(row["tag"] == "BOR" for row in csv_rows(DIRECT)):
        failures.append("obsolete BOR direct selector survives")
    if any(row.get("historical_name") == "Bornean Societies" for row in csv_rows(LOCATION_NAMES)):
        failures.append("obsolete Bornean Societies qualified name survives")
    if sum(value[2] for value in EXPECTED.values()) != 110:
        failures.append("former BOR contract must total exactly 110 locations")
    if sum(counts[tag] for tag in EXPECTED) != 110:
        failures.append("reviewed successor ownership must total exactly 110 locations")

    actual_areas: dict[str, set[str]] = {tag: set() for tag in EXPECTED}
    for row in csv_rows(AREAS):
        if row["tag"] in actual_areas:
            actual_areas[row["tag"]].add(row["geography"])
    for tag, expected in AREA_CONTRACT.items():
        if actual_areas[tag] != expected:
            failures.append(
                f"{tag} area contract changed: expected {sorted(expected)}, "
                f"found {sorted(actual_areas[tag])}"
            )

    direct_rows = csv_rows(DIRECT)
    expected_direct = {(tag, capital) for tag, (_, capital, *_rest) in EXPECTED.items()}
    actual_direct = {
        (row["tag"], row["location"])
        for row in direct_rows if row["tag"] in EXPECTED
    }
    if actual_direct != expected_direct:
        failures.append("Bornean direct-capital ownership contract changed")
    if RELIGION not in religions:
        failures.append("Bornean late-prehistoric plural-tradition family is missing")
    doctrine = doctrines.get(RELIGION)
    if doctrine is None or any(not doctrine[f"choice_{index}"] for index in range(1, 5)):
        failures.append("Bornean traditions lack four doctrine choices")
    icon = direct_religions.get(RELIGION)
    if icon is None or icon["status"] != "complete":
        failures.append("Bornean traditions lack a complete direct icon")

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
        if names.get((capital, culture), {}).get("historical_name") != CAPITAL_NAMES[capital]:
            failures.append(f"{capital} lacks reviewed culture-qualified display name")
        engine_tag = mapping.get(tag, "")
        if not engine_tag:
            failures.append(f"{tag} lacks a collision-safe engine tag")
        rows.append({
            "design_tag": tag,
            "engine_tag": engine_tag,
            "name": polity["name"],
            "map_capital": polity["map_capital"],
            "location_count": str(counts[tag]),
            "former_bor_locations": str(count),
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
        if re.search(r'^\s*\w+:\s+"[^"]*Bornean Societies', text, re.I | re.M):
            failures.append(f"{language} retains generic BOR localization")
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
            print(f"s2_bornean_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_bornean_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print(f"s2_bornean_granularity: PASS ({len(rows)} frames, 110 locations)")
        return 0
    except (KeyError, OSError, ValueError) as exc:
        print(f"s2_bornean_granularity: FAIL ({exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

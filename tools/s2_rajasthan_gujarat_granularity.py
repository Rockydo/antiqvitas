#!/usr/bin/env python3
"""Validate the sourced AD 1 Rajasthan-Gujarat catch-all repair."""

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
COAS = ROOT / "docs/m11/core_coas.csv"
SETTLEMENTS = ROOT / "docs/m5/global_settlement_audit.csv"
LEDGER = ROOT / "docs/m12/rajasthan_gujarat_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

EXPECTED = {
    "ANR": ("Anarta-Sarasvati Settlement Networks", "patan", 10, "antq_anarta_sarasvati"),
    "LBR": ("Lata-Barygaza Trade Corridor", "broach", 6, "antq_lata_barygaza"),
    "RKU": ("Rewa-Kantha Upland", "champaner", 3, "antq_rewa_kantha"),
    "SRS": ("Saurashtra Coastal Networks", "junagarh", 16, "antq_saurashtra_early_historic"),
    "KCH": ("Kutch Island-Coast Networks", "lakhiyarvira", 4, "antq_kutch_early_historic"),
    "MTS": ("Matsya-Dhundhar", "ajmer", 8, "antq_matsya_dhundhar"),
    "CHB": ("Chambal-Gird", "kota", 14, "antq_chambal_gird"),
    "ABN": ("Ahar-Banas Highland", "chittor", 11, "antq_ahar_banas"),
    "MRN": ("Marwar-Nagaur Caravan Networks", "osian", 22, "antq_marwar_nagaur"),
    "JGP": ("Jangladesh Pastoral Networks", "bhatnir", 15, "antq_jangladesh_pastoral"),
}
AREA_CONTRACT = {
    "ANR": {"khekassala", "sarasvata"},
    "LBR": {"lata"},
    "RKU": {"rewa_kantha"},
    "SRS": {"gohilwad", "halar", "jhalavad", "sorath"},
    "KCH": {"kutch"},
    "MTS": {"dhundhar"},
    "CHB": {"gird", "hadoti"},
    "ABN": {"mewar", "vagad"},
    "MRN": {"godwar", "jaisalmer_province", "marwar", "nagaur_province"},
    "JGP": {"jangladesh", "shekhawati"},
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "location_count",
    "former_rjs_locations", "culture", "religion", "seeded_locations",
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


def expected_rows() -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    roster = keyed(ROSTER, "tag")
    profiles = keyed(PROFILES, "tag")
    cultures = keyed(CULTURES, "key")
    coas = keyed(COAS, "tag")
    settlements = keyed(SETTLEMENTS, "tag")
    ownership = rows(OWNERSHIP)
    counts = Counter(row["tag"] for row in ownership)
    owner = {row["location"]: row["tag"] for row in ownership}
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }

    if "RJS" in roster or counts["RJS"]:
        failures.append("obsolete RJS catch-all survives in roster or ownership")
    if any(row["tag"] == "RJS" for row in rows(RESIDUAL) + rows(DIRECT) + rows(AREAS)):
        failures.append("obsolete RJS selector survives")
    if sum(value[2] for value in EXPECTED.values()) != 109:
        failures.append("former RJS contract must total exactly 109 locations")
    if sum(counts[tag] for tag in EXPECTED) != 109:
        failures.append("reviewed successor ownership must total exactly 109 locations")

    actual_areas: dict[str, set[str]] = {tag: set() for tag in EXPECTED}
    for row in rows(AREAS):
        if row["tag"] in actual_areas:
            actual_areas[row["tag"]].add(row["geography"])
    for tag, expected in AREA_CONTRACT.items():
        if actual_areas[tag] != expected:
            failures.append(f"{tag} area contract changed")

    expected_direct = {(tag, value[1]) for tag, value in EXPECTED.items()}
    actual_direct = {
        (row["tag"], row["location"])
        for row in rows(DIRECT) if row["tag"] in EXPECTED
    }
    if actual_direct != expected_direct:
        failures.append("western-India direct-capital contract changed")

    output: list[dict[str, str]] = []
    for tag, (name, capital, count, culture) in EXPECTED.items():
        polity = roster.get(tag)
        profile = profiles.get(tag)
        coa = coas.get(tag)
        settlement = settlements.get(tag)
        if polity is None:
            failures.append(f"missing reviewed frame {tag}")
            continue
        if polity["name"] != name or polity["map_capital"] != capital:
            failures.append(f"{tag} identity or capital changed")
        if owner.get(capital) != tag or counts[tag] != count:
            failures.append(f"{tag} ownership changed")
        if re.search(r"\b(?:societies|land of|generic|placeholder)\b", name, re.I):
            failures.append(f"{tag} retains generic display name")
        if profile is None or profile["culture"] != culture:
            failures.append(f"{tag} lacks culture {culture}")
        if profile is None or profile["religion"] != "antq_brahmanism":
            failures.append(f"{tag} lacks reviewed broad religion family")
        if culture not in cultures:
            failures.append(f"{tag} references undefined culture {culture}")
        if coa is None or not coa["emblem"]:
            failures.append(f"{tag} lacks a direct UI standard")
        if settlement is None or int(settlement["seeded_locations"]) < 1:
            failures.append(f"{tag} lacks an opening settlement seed")
        output.append({
            "design_tag": tag,
            "engine_tag": mapping.get(tag, ""),
            "name": name,
            "map_capital": capital,
            "location_count": str(counts[tag]),
            "former_rjs_locations": str(count),
            "culture": culture,
            "religion": profile["religion"] if profile else "",
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
        for row in output:
            for suffix in ("", "_ADJ"):
                key = row["engine_tag"] + suffix
                if not re.search(rf"^\s*{re.escape(key)}:\s+\"", text, re.MULTILINE):
                    failures.append(f"{language} lacks {key}")
        if "Rajasthan-Gujarat Societies" in text:
            failures.append(f"{language} retains obsolete RJS localization")
    return output, failures


def render(data: list[dict[str, str]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(data)
    return stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        data, failures = expected_rows()
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as exc:
        failures = [str(exc)]
        data = []
    payload = render(data)
    if args.write and not failures:
        LEDGER.write_text(payload, encoding="utf-8", newline="")
        print(f"s2_rajasthan_gujarat_granularity: wrote {LEDGER.relative_to(ROOT)}")
        return 0
    if args.check and (not LEDGER.is_file() or LEDGER.read_text(encoding="utf-8-sig") != payload):
        failures.append(f"stale or missing {LEDGER.relative_to(ROOT)}")
    if failures:
        print("s2_rajasthan_gujarat_granularity: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("s2_rajasthan_gujarat_granularity: PASS (10 frames, 109 locations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

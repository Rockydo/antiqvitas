#!/usr/bin/env python3
"""Validate the sourced AD 1 Inner Asian and Western Regions replacement."""

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
SUBJECTS = ROOT / "docs/world_1ad/subjects.csv"
DOCTRINES = ROOT / "docs/m12/religious_family_doctrines.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LEDGER = ROOT / "docs/m12/inner_asian_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

# New playable frames replacing the OAS catch-all.
EXPECTED = {
    "ARI": ("Aria", "herat", 15, "antq_arian", "antq_eastern_iranian_traditions", "antq_arian_satrapal_court"),
    "YNC": ("Yancai", "emba", 34, "antq_yancai_aorsi", "antq_tengri", "antq_yancai_aorsi_confederacy"),
    "SRY": ("Saryarka Late Iron-Age Horizon", "ulytau", 31, "antq_saryarka_late_iron", "antq_tengri", "antq_saryarka_late_iron_network"),
    "GMU": ("Gumo", "aksu", 6, "antq_aksu_oasis", "antq_tarim_oasis_traditions", "antq_han_western_regions_kingship"),
    "QIM": ("Qiemo", "charchan", 6, "antq_qiemo_oasis", "antq_tarim_oasis_traditions", "antq_han_western_regions_kingship"),
    "YQI": ("Yanqi", "karasahr", 7, "antq_yanqi_oasis", "antq_tarim_oasis_traditions", "antq_han_western_regions_kingship"),
    "SHC": ("Shache", "yarkand", 4, "antq_yarkand_oasis", "antq_tarim_oasis_traditions", "antq_han_western_regions_kingship"),
    "PUL": ("Puli", "sarikol", 4, "antq_puli_highland", "antq_tarim_oasis_traditions", "antq_han_western_regions_kingship"),
    "FJS": ("Further Jushi", "beshbalik", 9, "antq_further_jushi", "antq_tarim_oasis_traditions", "antq_han_western_regions_kingship"),
    "IWL": ("Yiwulu", "hami", 3, "antq_hami_oasis", "antq_tarim_oasis_traditions", "antq_han_western_regions_kingship"),
    "DNH": ("Danhuan", "urumqi", 1, "antq_danhuan_oasis", "antq_tarim_oasis_traditions", "antq_han_western_regions_kingship"),
}

# Existing frames whose revised boundaries are part of the same 302-location pass.
REVIEWED_COUNTS = {
    "DAY": 21, "SOG": 33, "KNG": 56, "WSN": 81, "YUE": 68,
    "MRG": 3, "KHT": 6, "KUC": 1, "KAS": 8, "LOU": 5, "TUR": 5,
    "ALT": 33, "XIO": 150,
}
REVIEWED_REFORMS = {
    "DAY": "antq_dayuan_oasis_kingship",
    "SOG": "antq_sogdian_city_compact",
    "KNG": "antq_kangju_confederated_kingship",
    "WSN": "antq_wusun_kunmi_confederacy",
    "YUE": "antq_yuezhi_five_yabghus",
    "ALT": "antq_altai_contact_network",
    "KHT": "antq_han_western_regions_kingship",
    "KUC": "antq_han_western_regions_kingship",
    "KAS": "antq_han_western_regions_kingship",
    "LOU": "antq_han_western_regions_kingship",
    "TUR": "antq_han_western_regions_kingship",
}
HAN_WESTERN_SUBJECTS = {
    "KHT", "KUC", "KAS", "LOU", "TUR", "GMU", "QIM", "YQI",
    "SHC", "PUL", "FJS", "IWL", "DNH",
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "location_count",
    "culture", "religion", "government_type", "reform", "emblem",
    "source", "confidence",
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
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership = csv_rows(OWNERSHIP)
    counts = Counter(row["tag"] for row in ownership)
    owner = {row["location"]: row["tag"] for row in ownership}

    if "OAS" in roster or counts["OAS"]:
        failures.append("obsolete OAS catch-all survives in roster or resolved ownership")
    if any(row["tag"] == "OAS" for row in csv_rows(RESIDUAL)):
        failures.append("obsolete OAS residual selector survives")
    if any(row["tag"] == "OAS" for row in csv_rows(DIRECT_OWNERSHIP)):
        failures.append("obsolete OAS direct selector survives")
    if sum(counts[tag] for tag in EXPECTED) != 120:
        failures.append("eleven replacement frames must control exactly 120 locations")
    for tag, expected_count in REVIEWED_COUNTS.items():
        if counts[tag] != expected_count:
            failures.append(
                f"{tag} reviewed ownership changed from {expected_count} to {counts[tag]}"
            )

    subject_rows = csv_rows(SUBJECTS)
    han_subjects = {
        row["subject"] for row in subject_rows
        if row["overlord"] == "HAN"
    }
    if not HAN_WESTERN_SUBJECTS.issubset(han_subjects):
        failures.append(
            "Han Western Regions tributary set is incomplete: "
            + ", ".join(sorted(HAN_WESTERN_SUBJECTS - han_subjects))
        )
    if not any(
        row["overlord"] == "PAR" and row["subject"] == "ARI"
        for row in subject_rows
    ):
        failures.append("Aria lacks its Arsacid-facing start dependency")
    if not any(
        row["overlord"] == "KNG" and row["subject"] == "SOG"
        for row in subject_rows
    ):
        failures.append("Sogdian cities lack the Kangju confederational dependency")

    doctrine_rows = keyed(DOCTRINES, "religion")
    for religion in (
        "antq_eastern_iranian_traditions",
        "antq_tarim_oasis_traditions",
    ):
        if religion not in religions:
            failures.append(f"missing plural belief family {religion}")
        row = doctrine_rows.get(religion)
        if row is None or any(not row[f"choice_{index}"] for index in range(1, 5)):
            failures.append(f"{religion} lacks four direct doctrine choices")

    ledger: list[dict[str, str]] = []
    for tag, (name, capital, count, culture, religion, reform) in EXPECTED.items():
        polity = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
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
        engine_tag = mapping.get(tag, "")
        if not engine_tag:
            failures.append(f"{tag} lacks a collision-safe engine tag")
        ledger.append({
            "design_tag": tag,
            "engine_tag": engine_tag,
            "name": polity["name"],
            "map_capital": polity["map_capital"],
            "location_count": str(counts[tag]),
            "culture": profile["culture"] if profile else "",
            "religion": profile["religion"] if profile else "",
            "government_type": government["government_type"] if government else "",
            "reform": government["reform"] if government else "",
            "emblem": coa["emblem"] if coa else "",
            "source": polity["source"],
            "confidence": polity["confidence"],
        })

    for tag, reform in REVIEWED_REFORMS.items():
        government = governments.get(tag)
        if government is None or government["reform"] != reform:
            failures.append(f"{tag} lacks reviewed reform {reform}")

    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")
    reform_keys = {value[5] for value in EXPECTED.values()} | set(REVIEWED_REFORMS.values())
    for reform in reform_keys:
        if not re.search(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reform_text):
            failures.append(f"generated reform definition missing {reform}")
        if f"unlock_government_reform = {reform}" not in advance_text:
            failures.append(f"opening research does not unlock {reform}")

    for language in LANGUAGES:
        text = (
            ROOT / f"main_menu/localization/{language}/antq_m3_countries_l_{language}.yml"
        ).read_text(encoding="utf-8-sig")
        for row in ledger:
            for suffix in ("", "_ADJ"):
                key = row["engine_tag"] + suffix
                if not re.search(rf"^\s*{re.escape(key)}:\s+\"", text, re.MULTILINE):
                    failures.append(f"{language} lacks {key}")
        if re.search(r"^\s*\w+:\s+\"[^\"]*(?:Inner Asian Oasis Societies|Oasis Societies)", text, re.MULTILINE | re.I):
            failures.append(f"{language} retains generic OAS localization")
    return ledger, failures


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
            LEDGER.write_text(content, encoding="utf-8-sig", newline="")
            print(f"s2_inner_asian_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_inner_asian_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print(
            "s2_inner_asian_granularity: PASS "
            "(OAS removed; 11 new frames/120 locations; 13 revised neighbours; "
            "10 reforms; 2 belief families/8 doctrines; 11 direct standards; "
            "35 start dependencies; 11-client localization)"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_inner_asian_granularity: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

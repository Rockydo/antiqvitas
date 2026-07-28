#!/usr/bin/env python3
"""Validate the sourced AD 1 northern-India and eastern-hill replacement."""

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
PROFILES = ROOT / "docs/m4/tag_profiles.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
RELIGION_REMAP = ROOT / "docs/religion_remap.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LEDGER = ROOT / "docs/m12/gangetic_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)
EXPECTED = {
    "AUD": ("Audumbara", "nagarkot", 25, "antq_audumbara_hill", "antq_indian_ganasangha"),
    "NMS": ("Northern Satrapy of Mathura", "mathura", 6, "antq_shauraseni_prakrit", "antq_indo_scythian_kingship"),
    "PCM": ("Panchala Mitra Kingdom", "bareilly", 22, "antq_panchala_prakrit", "antq_northern_indian_coin_kingship"),
    "KSM": ("Kaushambi Mitra Kingdom", "prayag", 5, "antq_kaushambi_prakrit", "antq_northern_indian_coin_kingship"),
    "AYM": ("Ayodhya Mitra Kingdom", "awadh", 24, "antq_kosala_prakrit", "antq_northern_indian_coin_kingship"),
    "KSH": ("Kashi Janapada", "varanasi", 12, "antq_kashi_prakrit", "antq_northern_indian_coin_kingship"),
    "MLL": ("Malla Assemblies", "kushinagar", 6, "antq_malla_prakrit", "antq_indian_ganasangha"),
    "GNG": ("Magadha", "patna", 13, "antq_magadhi_prakrit", "antq_northern_indian_coin_kingship"),
    "VDJ": ("Videha Janapada", "darbhanga", 18, "antq_videha_prakrit", "antq_indian_ganasangha"),
    "AGA": ("Anga Janapada", "bhagalpur", 6, "antq_anga_prakrit", "antq_northern_indian_coin_kingship"),
    "PDR": ("Pundravardhana", "bogra", 20, "antq_pundra_early_historic", "antq_pundranagara_urban_kingship"),
    "RAR": ("Rarh", "bardhaman", 14, "antq_rarh_early_historic", "antq_bengal_riverine_community_network"),
    "VNG": ("Vanga", "nadia", 20, "antq_vanga_early_historic", "antq_bengal_riverine_community_network"),
    "SMT": ("Samatata", "sonargaon", 18, "antq_samatata_early_historic", "antq_bengal_riverine_community_network"),
    # Seven locations belong to the original Gangetic repair; the six-field
    # Chittagong littoral extension is independently pinned by the SEA repair.
    "HRK": ("Harikela", "pilak", 13, "antq_harikela_early_historic", "antq_bengal_riverine_community_network"),
    "CNP": ("Chota Nagpur Megalithic Networks", "ranchi", 27, "antq_chota_nagpur_megalithic", "antq_eastern_megalithic_community_network"),
    "AMB": ("Ambari Horizon", "guwahati", 11, "antq_ambari_horizon", "antq_eastern_hill_valley_network"),
    "DDV": ("Doyang-Dhansiri Valley", "dimapur", 8, "antq_doyang_dhansiri", "antq_eastern_hill_valley_network"),
    "KJH": ("Khasi-Jaintia Highlands", "sohra", 8, "antq_khasi_jaintia_highland", "antq_eastern_hill_valley_network"),
    "UBR": ("Upper Brahmaputra Foothills", "dibrugarh", 8, "antq_upper_brahmaputra", "antq_eastern_hill_valley_network"),
    "SDY": ("Sadiya Foothills", "sadiya", 7, "antq_sadiya_foothill", "antq_eastern_hill_valley_network"),
    "MYL": ("Monyul Highlands", "paro", 9, "antq_monyul_highland", "antq_himalayan_highland_network"),
    "SKM": ("Sikkim Foothills", "yuksom", 5, "antq_sikkim_foothill", "antq_himalayan_highland_network"),
    "IMV": ("Imphal Valley Networks", "imphal", 2, "antq_imphal_valley", "antq_eastern_hill_valley_network"),
}
HILL_TAGS = {"CNP", "AMB", "DDV", "KJH", "UBR", "SDY", "MYL", "SKM", "IMV"}
REFORM_KEYS = {value[4] for value in EXPECTED.values()} - {
    "antq_indian_ganasangha", "antq_indo_scythian_kingship",
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
    governments = keyed(GOVERNMENTS, "design_tag")
    coas = keyed(COAS, "tag")
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership = csv_rows(OWNERSHIP)
    counts = Counter(row["tag"] for row in ownership)
    owner = {row["location"]: row["tag"] for row in ownership}
    residuals = {(row["tag"], row["geography"]) for row in csv_rows(RESIDUAL)}
    if ("GNG", "bengal_region") in residuals or ("GNG", "hindustan_region") in residuals:
        failures.append("obsolete Gangetic regional residual survives")
    if ("ISK", "punjab_region") in residuals:
        failures.append("obsolete Indo-Scythian Punjab residual survives")
    if owner.get("mathura") != "NMS":
        failures.append("Mathura must belong to the Northern Satrapy, not Arjunayana")
    if sum(counts[tag] for tag in EXPECTED) - 6 != 301:
        failures.append("reviewed replacement frames must control exactly 301 locations")

    remapped_religions = {
        row["religion"] for row in csv_rows(RELIGION_REMAP)
    }
    if "antq_eastern_hill_traditions" not in remapped_religions:
        failures.append("eastern hill population religion remap is missing")

    ledger: list[dict[str, str]] = []
    for tag, (name, capital, count, culture, reform) in EXPECTED.items():
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
        expected_religion = (
            "antq_eastern_hill_traditions" if tag in HILL_TAGS else "antq_brahmanism"
        )
        if profile is None or profile["religion"] != expected_religion:
            failures.append(f"{tag} lacks reviewed religion {expected_religion}")
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

    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")
    for reform in REFORM_KEYS:
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
                if not re.search(
                    rf"^\s*{re.escape(row['engine_tag'] + suffix)}:\s+\"",
                    text, re.MULTILINE,
                ):
                    failures.append(f"{language} lacks {row['engine_tag'] + suffix}")
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
            print(f"s2_gangetic_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_gangetic_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print(
            "s2_gangetic_granularity: PASS "
            "(24 frames; 301 original locations + 6 Chittagong extension; "
            "largest 27; 24 cultures; "
            "6 new reforms; 24 standards; 11-client localization)"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_gangetic_granularity: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

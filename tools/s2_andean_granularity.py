#!/usr/bin/env python3
"""Validate the sourced AD 1 reconstruction of the complete Andean surface."""

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
SELECTORS = tuple(
    ROOT / relative for relative in (
        "docs/world_1ad/ownership_areas.csv",
        "docs/world_1ad/ownership_residual_areas.csv",
        "docs/world_1ad/ownership_locations.csv",
    )
)
PROFILES = ROOT / "docs/m4/tag_profiles.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
SETTLEMENTS = ROOT / "docs/m5/global_settlement_audit.csv"
LAWS = ROOT / "docs/m6/ancient_law_profiles.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LEDGER = ROOT / "docs/m12/andean_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

EXPECTED = {
    "VCS": ("Vicus", "apurlec", "antq_vicus", "antq_andean_irrigated_valley_network", {"apurlec", "xllang"}),
    "VIR": ("Gallinazo", "chan_chan", "antq_gallinazo", "antq_andean_irrigated_valley_network", {"chan_chan", "chao", "farfan", "pakatnamu", "paramonga", "sana"}),
    "NAZ": ("Nazca", "cahuachi", "antq_nazca", "antq_andean_ceremonial_centre_network", {"cahuachi", "chinchay", "ica", "puka_tampu"}),
    "LIM": ("Lima Culture", "rimaq", "antq_lima_central_coast", "antq_andean_irrigated_valley_network", {"cantamarca", "chilca", "collique", "huarco", "huarochiri", "incahuasi", "ishma", "rimaq"}),
    "ATC": ("Atico-Caraveli Valley", "atico", "antq_atico_caraveli", "antq_andean_irrigated_valley_network", {"aruni", "atico", "caraveli", "arequipa"}),
    "CBA": ("Cusco Basin", "qusqu", "antq_cusco_late_formative", "antq_andean_highland_community_network", {"pikillaqta", "pisaq", "quillarumiyoc", "qusqu", "urupampa", "waqrapukara", "ullantaytampu", "willka_pampa", "yanatile"}),
    "REC": ("Recuay", "waricoto", "antq_recuay", "antq_andean_highland_community_network", {"waricoto"}),
    "HUA": ("Huarpa", "huaman_karpa", "antq_huarpa", "antq_andean_highland_community_network", {"auccapana", "challwanqa", "huaman_karpa", "sondor", "soras", "allpas", "choccalpata", "paqwayranra", "pariahuanca", "wari_peru", "churkampa", "llacsapallanca", "tampu_machay", "tayaccasa"}),
    "PUK": ("Pukara", "ayaviri", "antq_pukara", "antq_andean_ceremonial_centre_network", {"sausaya", "tucssa", "yanahuara", "ayaviri", "macaya", "wankani", "chucuito", "contornasa", "hatunqulla", "pomata"}),
    "TIW": ("Early Tiwanaku", "tiwanaku", "antq_tiwanaku", "antq_andean_ceremonial_centre_network", {"achacachi", "axawiri", "calamarca", "chuqiyapu", "machaqa", "tiwanaku", "viacha"}),
    "WNK": ("Wankarani", "oruro", "antq_wankarani", "antq_wankarani_mound_village_network", {"charka", "colquechaca", "kori_bara_karaa_ancas", "matarjawira", "sicasica", "sura", "karanka", "oruro"}),
    "MRH": ("Cajamarca-Marcahuamachuco", "markahuamachuco", "antq_cajamarca_marcahuamachuco", "antq_andean_highland_community_network", {"chimu", "illapa", "kaxa_marca", "llucho", "markahuamachuco", "tantaricuy"}),
    "UTC": ("Upper Utcubamba", "karajia", "antq_upper_utcubamba", "antq_andean_highland_community_network", {"congona", "huamanpata", "kuelap", "olan", "huancachaca", "karajia", "utkhupampa"}),
    "YUN": ("Eastern Yunga Valley Networks", "incarraqay", "antq_eastern_yunga", "antq_andean_highland_community_network", {"arque", "incarraqay", "sachchaa_mukku", "ayopaya", "paititi", "sarkajpa"}),
    "MYB": ("Moyobamba Foothill", "moyobamba", "antq_moyobamba_foothill", "antq_andean_highland_community_network", {"chatuza", "lamas", "moyobamba"}),
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "location_count",
    "culture", "religion", "government_type", "reform", "seeded_locations",
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
    governments = keyed(GOVERNMENTS, "design_tag")
    coas = keyed(COAS, "tag")
    settlements = keyed(SETTLEMENTS, "tag")
    laws = keyed(LAWS, "tag")
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership = rows(OWNERSHIP)
    owner = {row["location"]: row["tag"] for row in ownership}
    counts = Counter(row["tag"] for row in ownership)
    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")

    expected_locations = set().union(*(item[4] for item in EXPECTED.values()))
    actual_locations = {row["location"] for row in ownership if row["tag"] in EXPECTED}
    if len(expected_locations) != 95 or actual_locations != expected_locations:
        failures.append("reviewed Andean surface must contain exactly the pinned 95 locations")
    if "AND" in roster or counts["AND"]:
        failures.append("obsolete AND catch-all survives in roster or resolved ownership")
    for path in SELECTORS:
        if any(row["tag"] == "AND" for row in rows(path)):
            failures.append(f"obsolete AND selector survives in {path.relative_to(ROOT)}")

    output: list[dict[str, str]] = []
    for tag, (name, capital, culture, reform, locations) in EXPECTED.items():
        polity = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        settlement = settlements.get(tag)
        if polity is None:
            failures.append(f"missing reviewed Andean frame {tag}")
            continue
        actual = {location for location in locations if owner.get(location) == tag}
        if actual != locations or counts[tag] != len(locations):
            failures.append(f"{tag} must own exactly {sorted(locations)}")
        if polity["name"] != name or polity["region"] != "Andes" or polity["map_capital"] != capital:
            failures.append(f"{tag} identity, region, or capital changed")
        if profile is None or profile["culture"] != culture or profile["religion"] != "antq_andean":
            failures.append(f"{tag} lacks reviewed Andean culture/religion profile")
        if culture not in cultures:
            failures.append(f"{tag} references undefined culture {culture}")
        if government is None or government["government_type"] != "tribe" or government["reform"] != reform:
            failures.append(f"{tag} lacks reviewed government reform {reform}")
        if coa is None or not coa["emblem"].startswith("ce_andean_"):
            failures.append(f"{tag} lacks a reviewed direct Andean standard")
        if settlement is None or int(settlement["seeded_locations"]) < 1:
            failures.append(f"{tag} lacks an opening settlement seed")
        if laws.get(tag, {}).get("profile") != "transoceanic":
            failures.append(f"{tag} lacks the transoceanic legal profile")
        if not re.search(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reform_text):
            failures.append(f"generated reform definition missing {reform}")
        if f"unlock_government_reform = {reform}" not in advance_text:
            failures.append(f"opening research does not unlock {reform}")
        output.append({
            "design_tag": tag, "engine_tag": mapping.get(tag, ""),
            "name": name, "map_capital": capital,
            "location_count": str(counts[tag]),
            "culture": profile["culture"] if profile else "",
            "religion": profile["religion"] if profile else "",
            "government_type": government["government_type"] if government else "",
            "reform": government["reform"] if government else "",
            "seeded_locations": settlement["seeded_locations"] if settlement else "",
            "placements": settlement["placements"] if settlement else "",
            "emblem": coa["emblem"] if coa else "", "source": polity["source"],
            "confidence": polity["confidence"],
        })

    for language in LANGUAGES:
        text = (
            ROOT / f"main_menu/localization/{language}/antq_m3_countries_l_{language}.yml"
        ).read_text(encoding="utf-8-sig")
        for entry in output:
            for suffix in ("", "_ADJ"):
                key = entry["engine_tag"] + suffix
                if not key or not re.search(rf"^\s*{re.escape(key)}:\s+\"", text, re.MULTILINE):
                    failures.append(f"{language} lacks {key or entry['design_tag']}")
        if re.search(r'^\s*\w+:\s+"[^"]*Andean Societies', text, re.I | re.M):
            failures.append(f"{language} retains the obsolete AND display name")
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
            print(f"s2_andean_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_andean_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print("s2_andean_granularity: PASS (15 frames; 95 exact Andean locations)")
        return 0
    except (KeyError, OSError, ValueError) as exc:
        print(f"s2_andean_granularity: FAIL ({exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

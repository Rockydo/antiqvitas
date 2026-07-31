#!/usr/bin/env python3
"""Validate the sourced AD 1 Korean commandery and small-state repair."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
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
POP_OVERRIDES = ROOT / "docs/m4/population_location_overrides.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
SETTLEMENTS = ROOT / "docs/m5/global_settlement_audit.csv"
LAWS = ROOT / "docs/m6/ancient_law_profiles.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LEDGER = ROOT / "docs/m12/korean_peninsula_granularity.csv"
LANGUAGE_CLIENTS = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

LELANG = {
    "anak", "baekcheon", "bongju", "cheongsong", "gokju", "haeju",
    "hwangju", "jaeryeong", "jangyeon", "ongjin", "pungcheon",
    "pyeongju", "suan", "tosan",
}
HMR_KRS = {
    "gwangju", "icheon", "namgyeong", "suwon", "gapyeong", "inju",
    "jipyeong", "kaesong", "papyeong", "pocheon", "yangju",
}
HMR_HOSEO = {"chungju", "danyang_korea", "eumseong", "goeju", "jecheon"}
GMR_HOSEO = {
    "cheonan", "cheongju", "gongju", "jinjam", "yeongdong", "yeonsan",
    "aju", "boryeong", "hansan", "hongju", "seosan",
}
JIN_KRS = {
    "andong", "bonghwa", "mungyeong", "sangju", "yeongcheon",
    "boseongbu", "yeongdeok", "yeongil", "yeongju", "yeongyang",
    "gaeryeong", "seongju", "seonsan", "taegu", "uiseong",
}
BYE_KRS = {
    "dongnae", "miryang", "ulju", "geochang", "geoje", "hadong",
    "hapcheon", "jinju", "namhae", "sacheon",
}
FORMER_KRS = LELANG | HMR_KRS | JIN_KRS | BYE_KRS
FORMER_BYE_HOSEO = HMR_HOSEO | GMR_HOSEO | {"uian"}

EXPECTED = {
    "HMR": (
        "Han River Mahan", "suwon",
        {"hanseong_province", "kaesong_province", "chungju_province"},
        "antq_mahan_small_state_league", HMR_KRS | HMR_HOSEO,
    ),
    "GMR": (
        "Geum River Mahan", "gongju",
        {"gongju_province", "hongju_province"},
        "antq_mahan_small_state_league", GMR_HOSEO,
    ),
    "JIN": (
        "Jinhan", "gyeongju",
        {"andong_province", "gyeongju_province", "seongju_province"},
        "antq_jinhan_small_state_league", JIN_KRS | {"gyeongju"},
    ),
    "BYE": (
        "Byeonhan", "uian",
        {"jinju_province", "dongnae_province"},
        "antq_byeonhan_iron_exchange_league", BYE_KRS | {"uian"},
    ),
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "provinces",
    "location_count", "former_krs_locations", "former_hoseo_locations",
    "culture", "religion", "reform", "seeded_locations", "placements",
    "emblem", "source", "confidence",
)


def rows(path: Path) -> list[dict[str, str]]:
    payload = "\n".join(
        line for line in path.read_text(encoding="utf-8-sig").splitlines()
        if not line.lstrip().startswith("#")
    )
    return list(csv.DictReader(io.StringIO(payload)))


def keyed(path: Path, key: str) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows(path):
        if row[key] in output:
            raise ValueError(f"{path.relative_to(ROOT)} repeats {key} {row[key]}")
        output[row[key]] = row
    return output


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
    ownership_rows = rows(OWNERSHIP)
    owner_by_location = {row["location"]: row["tag"] for row in ownership_rows}
    area_rows = rows(AREAS)
    provinces = {
        tag: {row["geography"] for row in area_rows if row["tag"] == tag}
        for tag in EXPECTED
    }
    owned = {
        tag: {row["location"] for row in ownership_rows if row["tag"] == tag}
        for tag in EXPECTED
    }
    if "KRS" in roster or any(row["tag"] == "KRS" for row in ownership_rows):
        failures.append("obsolete KRS catch-all survives in roster or ownership")
    for path in (AREAS, RESIDUAL, DIRECT):
        if any(row["tag"] == "KRS" for row in rows(path)):
            failures.append(f"obsolete KRS selector survives in {path.relative_to(ROOT)}")
    if len(FORMER_KRS) != 50:
        failures.append("validator's former KRS contract is not exactly 50 locations")
    expected_krs_owners = {
        **{location: "HAN" for location in LELANG},
        **{location: "HMR" for location in HMR_KRS},
        **{location: "JIN" for location in JIN_KRS},
        **{location: "BYE" for location in BYE_KRS},
    }
    for location, tag in expected_krs_owners.items():
        if owner_by_location.get(location) != tag:
            failures.append(f"former KRS location {location} belongs to {owner_by_location.get(location)}, expected {tag}")
    expected_hoseo_owners = {
        **{location: "HMR" for location in HMR_HOSEO},
        **{location: "GMR" for location in GMR_HOSEO},
        "uian": "BYE",
    }
    for location, tag in expected_hoseo_owners.items():
        if owner_by_location.get(location) != tag:
            failures.append(f"former Byeonhan-Hoseo location {location} belongs to {owner_by_location.get(location)}, expected {tag}")

    pop_overrides = keyed(POP_OVERRIDES, "location")
    lelang_culture = cultures.get("antq_lelang_gojoseon")
    if lelang_culture is None or lelang_culture["group"] != "antq_korean_group":
        failures.append("missing reviewed Lelang-Gojoseon population culture")
    for location in LELANG:
        override = pop_overrides.get(location)
        if (
            override is None
            or override["culture"] != "antq_lelang_gojoseon"
            or override["religion"] != "antq_korean_muism"
        ):
            failures.append(f"{location} lacks the indigenous-majority Lelang population override")

    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")
    output: list[dict[str, str]] = []
    for tag, (name, capital, expected_provinces, reform, locations) in EXPECTED.items():
        polity = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        settlement = settlements.get(tag)
        if polity is None:
            failures.append(f"missing reviewed Korean frame {tag}")
            continue
        if polity["name"] != name or polity["region"] != "Korea" or polity["map_capital"] != capital:
            failures.append(f"{tag} identity, region, or capital changed")
        if owned[tag] != locations or capital not in owned[tag]:
            failures.append(f"{tag} ownership differs from its reviewed Korean set")
        if provinces[tag] != expected_provinces:
            failures.append(f"{tag} installed-province frame changed")
        if profile is None or profile["culture"] != "antq_samhan" or profile["religion"] != "antq_korean_muism":
            failures.append(f"{tag} lacks the reviewed Samhan population profile")
        if government is None or government["reform"] != reform:
            failures.append(f"{tag} lacks reviewed government reform {reform}")
        if tag in {"HMR", "GMR"} and (tag not in coas or not coas[tag]["emblem"]):
            failures.append(f"{tag} lacks a direct reviewed UI standard")
        if settlement is None or int(settlement["seeded_locations"]) < 1:
            failures.append(f"{tag} lacks an opening settlement seed")
        if laws.get(tag, {}).get("profile") != "eastern":
            failures.append(f"{tag} lacks the reviewed eastern legal profile")
        if not re.search(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reform_text):
            failures.append(f"generated reform definition missing {reform}")
        if f"unlock_government_reform = {reform}" not in advance_text:
            failures.append(f"opening research does not unlock {reform}")
        engine_tag = mapping.get(tag, "")
        if not engine_tag:
            failures.append(f"{tag} lacks a collision-safe engine tag")
        output.append({
            "design_tag": tag,
            "engine_tag": engine_tag,
            "name": name,
            "map_capital": capital,
            "provinces": "|".join(sorted(expected_provinces)),
            "location_count": str(len(locations)),
            "former_krs_locations": str(len(locations & FORMER_KRS)),
            "former_hoseo_locations": str(len(locations & FORMER_BYE_HOSEO)),
            "culture": profile["culture"] if profile else "",
            "religion": profile["religion"] if profile else "",
            "reform": government["reform"] if government else "",
            "seeded_locations": settlement["seeded_locations"] if settlement else "",
            "placements": settlement["placements"] if settlement else "",
            "emblem": coas.get(tag, {}).get("emblem", ""),
            "source": polity["source"],
            "confidence": polity["confidence"],
        })

    han_areas = {row["geography"] for row in area_rows if row["tag"] == "HAN"}
    if not {"hwangju_province", "haeju_province"}.issubset(han_areas):
        failures.append("Western Han lacks the two reviewed Lelang commandery provinces")
    mahan_gov = governments.get("MAH")
    if mahan_gov is None or mahan_gov["reform"] != "antq_mahan_small_state_league":
        failures.append("Mahan lacks the reviewed small-state league reform")

    for language in LANGUAGE_CLIENTS:
        text = (
            ROOT / f"main_menu/localization/{language}/antq_m3_countries_l_{language}.yml"
        ).read_text(encoding="utf-8-sig")
        for entry in output:
            for suffix in ("", "_ADJ"):
                key = entry["engine_tag"] + suffix
                if not re.search(rf"^\s*{re.escape(key)}:\s+\"", text, re.MULTILINE):
                    failures.append(f"{language} lacks {key}")
        if re.search(r'^\s*\w+:\s+"[^"]*Korean Peninsula Societies', text, re.I | re.M):
            failures.append(f"{language} retains the obsolete KRS display name")
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
            print(f"s2_korean_peninsula_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_korean_peninsula_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print("s2_korean_peninsula_granularity: PASS (50 KRS + 16 Hoseo locations repaired)")
        return 0
    except (KeyError, OSError, ValueError) as exc:
        print(f"s2_korean_peninsula_granularity: FAIL ({exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

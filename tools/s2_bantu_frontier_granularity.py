#!/usr/bin/env python3
"""Validate the sourced AD 1 central/eastern/southern African replacement."""

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
LOCATIONS = ROOT / "docs/world_1ad/ownership_locations.csv"
EMPTY = ROOT / "docs/world_1ad/intentional_empty_areas.csv"
TAG_PROFILES = ROOT / "docs/m4/tag_profiles.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LEDGER = ROOT / "docs/m12/bantu_frontier_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)
EXPECTED = {
    "BNT": (
        "Ngovo Horizon", "mbanza_kongo", 20, "antq_ngovo",
        "antq_bantu_religion", "antq_early_ironworking_community_network",
    ),
    "URW": (
        "Urewe Horizon", "rubaga", 8, "antq_urewe",
        "antq_bantu_religion", "antq_early_ironworking_community_network",
    ),
    "KWL": (
        "Kwale Horizon", "mombasa", 21, "antq_kwale",
        "antq_bantu_religion", "antq_early_ironworking_community_network",
    ),
    "RUV": (
        "Ruvuma-Lurio Frontier", "lindi", 12, "antq_ruvuma_lurio",
        "antq_bantu_religion", "antq_early_ironworking_community_network",
    ),
    "LMP": (
        "Limpopo Hunter-Herder Networks", "impakwe", 10,
        "antq_limpopo_hunter_herder",
        "antq_southern_african_hunter_herder_traditions",
        "antq_mobile_hunter_herder_network",
    ),
    "ZHF": (
        "Zambezi Hunter-Herder Networks", "mtoko", 16,
        "antq_zambezi_forager",
        "antq_southern_african_hunter_herder_traditions",
        "antq_mobile_hunter_herder_network",
    ),
    "WDP": (
        "Wadai Plateau", "ouara", 5, "antq_wadai_plateau",
        "antq_west_african", "antq_early_ironworking_community_network",
    ),
    "BCH": (
        "Bauchi Plateau", "bauchi", 1, "antq_post_nok",
        "antq_west_african", "antq_early_ironworking_community_network",
    ),
}
EXPECTED_CULTURE_LANGUAGES = {
    "antq_ngovo": "antq_ngovo_horizon_language",
    "antq_urewe": "antq_urewe_horizon_language",
    "antq_kwale": "antq_kwale_horizon_language",
    "antq_ruvuma_lurio": "antq_ruvuma_lurio_language",
    "antq_limpopo_hunter_herder": "antq_limpopo_hunter_herder_language",
    "antq_zambezi_forager": "antq_zambezi_forager_language",
}
FORBIDDEN_CULTURES = {
    "antq_equatorial_bantu", "antq_kongo_bantu", "antq_great_lakes_bantu",
    "antq_eastern_bantu", "antq_southern_bantu",
}
FORBIDDEN_BNT_AREAS = {
    "central_africa_region", "swahili_coast_region", "zimbabwe_region",
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "location_count",
    "culture", "religion", "government_type", "reform", "emblem",
    "source", "confidence",
)


def csv_rows(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig")
    payload = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )
    return list(csv.DictReader(io.StringIO(payload)))


def keyed(path: Path, key: str) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for row in csv_rows(path):
        value = row[key]
        if value in rows:
            raise ValueError(f"{path.relative_to(ROOT)} repeats {key} {value}")
        rows[value] = row
    return rows


def expected_rows() -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    roster = keyed(ROSTER, "tag")
    profiles = keyed(TAG_PROFILES, "tag")
    cultures = keyed(CULTURES, "key")
    governments = keyed(GOVERNMENTS, "design_tag")
    coas = keyed(COAS, "tag")
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership_rows = csv_rows(OWNERSHIP)
    owner = {row["location"]: row["tag"] for row in ownership_rows}
    counts = Counter(row["tag"] for row in ownership_rows)
    areas = {(row["tag"], row["geography"]) for row in csv_rows(AREAS)}
    locations = {(row["tag"], row["location"]) for row in csv_rows(LOCATIONS)}
    empty = {row["geography"] for row in csv_rows(EMPTY)}

    if sum(counts[tag] for tag in EXPECTED) != 93:
        failures.append("reviewed replacement must control exactly 93 locations")
    if "ngazidja" not in empty:
        failures.append("Ngazidja must remain an explicit evidence-led empty area")
    if ("BCH", "bauchi") not in locations:
        failures.append("Bauchi post-Nok anchor must be an explicit location claim")
    for geography in FORBIDDEN_BNT_AREAS:
        if ("BNT", geography) in areas:
            failures.append(f"obsolete BNT macro-claim remains: {geography}")

    active_cultures = set(cultures)
    for culture in FORBIDDEN_CULTURES & active_cultures:
        failures.append(f"obsolete broad culture remains active: {culture}")

    ledger: list[dict[str, str]] = []
    for tag, expected in EXPECTED.items():
        name, capital, count, culture, religion, reform = expected
        row = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        if row is None:
            failures.append(f"missing reviewed frame {tag}")
            continue
        if row["name"] != name:
            failures.append(f"{tag} must display as {name}, found {row['name']}")
        if re.search(r"\b(?:societies|generic|placeholder)\b", row["name"], re.I):
            failures.append(f"{tag} retains generic display name {row['name']}")
        if row["map_capital"] != capital or owner.get(capital) != tag:
            failures.append(f"{tag} must own reviewed capital {capital}")
        if counts[tag] != count:
            failures.append(
                f"{tag} reviewed ownership changed from {count} to {counts[tag]}"
            )
        if row["confidence"] != "contested" or not row["source"]:
            failures.append(f"{tag} must expose contested source metadata")
        if profile is None:
            failures.append(f"{tag} lacks a culture/religion profile")
        else:
            if profile["culture"] != culture:
                failures.append(
                    f"{tag} culture must be {culture}, found {profile['culture']}"
                )
            if profile["religion"] != religion:
                failures.append(
                    f"{tag} religion must be {religion}, found {profile['religion']}"
                )
        if culture not in cultures:
            failures.append(f"{tag} references undefined reviewed culture {culture}")
        elif culture in EXPECTED_CULTURE_LANGUAGES:
            expected_language = EXPECTED_CULTURE_LANGUAGES[culture]
            if cultures[culture]["language"] != expected_language:
                failures.append(
                    f"{culture} language must be {expected_language}, "
                    f"found {cultures[culture]['language']}"
                )
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
            "name": row["name"],
            "map_capital": row["map_capital"],
            "location_count": str(counts[tag]),
            "culture": profile["culture"] if profile else "",
            "religion": profile["religion"] if profile else "",
            "government_type": government["government_type"] if government else "",
            "reform": government["reform"] if government else "",
            "emblem": coa["emblem"] if coa else "",
            "source": row["source"],
            "confidence": row["confidence"],
        })

    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")
    for reform in {
        "antq_early_ironworking_community_network",
        "antq_mobile_hunter_herder_network",
    }:
        if not re.search(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reform_text):
            failures.append(f"generated reform definition missing {reform}")
        if f"unlock_government_reform = {reform}" not in advance_text:
            failures.append(f"opening research does not unlock {reform}")

    for language in LANGUAGES:
        path = (
            ROOT
            / f"main_menu/localization/{language}/antq_m3_countries_l_{language}.yml"
        )
        text = path.read_text(encoding="utf-8-sig")
        for row in ledger:
            for suffix in ("", "_ADJ"):
                key = row["engine_tag"] + suffix
                if not re.search(
                    rf"^\s*{re.escape(key)}:\s+\"", text, re.MULTILINE
                ):
                    failures.append(f"{language} lacks {key} localization")
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
            LEDGER.parent.mkdir(parents=True, exist_ok=True)
            LEDGER.write_text(content, encoding="utf-8-sig", newline="")
            print(
                "s2_bantu_frontier_granularity: wrote "
                f"{LEDGER.relative_to(ROOT)} ({len(rows)} frames)"
            )
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_bantu_frontier_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print(
            "s2_bantu_frontier_granularity: PASS "
            "(8 frames; 93 owned entries; Ngazidja empty; 8 cultures; "
            "2 reforms; 8 standards; 11-client localization)"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_bantu_frontier_granularity: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

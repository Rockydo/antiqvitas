#!/usr/bin/env python3
"""Validate the sourced AD 1 Germania/Baltic/northern-Europe remediation."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter
from pathlib import Path

from ownership_map import descendants


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
RESIDUAL = ROOT / "docs/world_1ad/ownership_residual_areas.csv"
HIERARCHY = ROOT / "docs/vanilla_symbols/geography_hierarchy.json"
LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
TAG_PROFILES = ROOT / "docs/m4/tag_profiles.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
PRIVILEGES = ROOT / "docs/m6/privileges.csv"
LAWS = ROOT / "docs/m6/laws.csv"
OVERLAYS = ROOT / "docs/m6/regional_government_overlays.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
PRIVILEGE_ART = ROOT / "docs/m11/direct_privilege_icons.csv"
UNITS = ROOT / "docs/m7/units.csv"
UNIT_ART = ROOT / "docs/m12/unit_art_ledger.csv"
START_POPS = ROOT / "main_menu/setup/start/06_pops.txt"
LEDGER = ROOT / "docs/m12/northern_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)
REQUIRED = (
    "GER", "AES", "WBB", "BPC", "WSC", "ETG",
    "FIN", "SUE", "GTL", "SKN", "SNR", "NNR",
)
EXPECTED_NAMES = {
    "GER": "Angrivarii",
    "AES": "Aestii",
    "WBB": "West Balt Barrow Culture",
    "BPC": "Brushed Pottery Culture",
    "WSC": "West Lithuanian Stone-Circle Culture",
    "ETG": "Early Tarand-Grave Horizon",
    "FIN": "Fenni",
    "SUE": "Suebi",
    "GTL": "Gutae",
    "SKN": "Chaedini",
    "SNR": "Dauciones",
    "NNR": "Hilleviones",
}
EXPECTED_COUNTS = {
    "GER": 13,
    "AES": 16,
    "WBB": 15,
    "BPC": 50,
    "WSC": 27,
    "ETG": 29,
}
REQUIRED_PRIVILEGES = {
    "antq_germanic_assembly_acclamation",
    "antq_germanic_household_retainers",
    "antq_germanic_sacred_grove_custodians",
    "antq_baltic_amber_route_brokers",
    "antq_baltic_hillfort_households",
    "antq_baltic_burial_custodians",
}
REQUIRED_LAWS = {
    "antq_germanic_assembly_law",
    "antq_germanic_retinue_law",
    "antq_germanic_grove_law",
    "antq_baltic_amber_law",
    "antq_baltic_hillfort_law",
    "antq_baltic_mortuary_law",
}
EXPECTED_OVERLAY_TAGS = {
    "antq_germanic_assembly_layer": {
        "MCM", "CRU", "CHT", "FRI", "BTV", "LAN", "SEM", "HER", "QUA",
        "GUT", "VAN", "RUG", "BRG", "ANG", "SAX", "JUT", "GER", "SUE",
        "GTL", "SKN", "SNR", "NNR",
    },
    "antq_baltic_amber_coast": {"AES", "WBB"},
    "antq_baltic_hillfort_zone": {"BPC", "WSC"},
    "antq_baltic_tarand_zone": {"ETG"},
}
EXPECTED_UNIT_TAGS = {
    "antq_angrivarian_spear_following": {"GER"},
    "antq_suebian_household_retinue": {"SUE", "MCM", "SEM", "HER", "QUA", "NAR"},
    "antq_baltic_hillfort_spearmen": {"BPC", "WSC"},
    "antq_baltic_forest_skirmishers": {"AES", "WBB", "BPC", "WSC", "ETG"},
}
FORBIDDEN_NAME = re.compile(
    r"\b(?:societies|communities|land of|generic|placeholder)\b",
    re.IGNORECASE,
)
POP_CULTURE = re.compile(
    r"(?m)^\t(?P<location>[a-z0-9_]+) = \{\r?\n"
    r"\t\tdefine_pop = \{[^\r\n]*\bculture = (?P<culture>[a-z0-9_]+)"
)
FIELDS = (
    "design_tag", "engine_tag", "name", "kind", "map_capital",
    "location_count", "culture", "religion", "government_type", "reform",
    "emblem", "source", "confidence",
)


def csv_rows(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig")
    payload = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )
    return list(csv.DictReader(io.StringIO(payload)))


def keyed(path: Path, key: str) -> dict[str, dict[str, str]]:
    values: dict[str, dict[str, str]] = {}
    for row in csv_rows(path):
        value = row[key]
        if value in values:
            raise ValueError(f"{path.relative_to(ROOT)} repeats {key} {value}")
        values[value] = row
    return values


def expected_rows() -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    roster = keyed(ROSTER, "tag")
    for tag, expected in EXPECTED_NAMES.items():
        row = roster.get(tag)
        if row is None:
            failures.append(f"missing reviewed northern tag {tag}")
            continue
        if row["name"] != expected:
            failures.append(f"{tag} must display as {expected}, found {row['name']}")
        if FORBIDDEN_NAME.search(row["name"]):
            failures.append(f"{tag} retains generic display name {row['name']}")
        if not row["source"] or row["confidence"] not in {"secure", "contested"}:
            failures.append(f"{tag} lacks source/confidence metadata")

    # FIN is checked explicitly above. The remaining Volga/Ural/Siberian
    # archaeological frames are a separate, still-open global macro-polity
    # batch and must not be silently claimed as completed by this ledger.
    northern_regions = {"Germania", "Scandinavia", "Baltic"}
    for row in roster.values():
        if row["region"] in northern_regions and FORBIDDEN_NAME.search(row["name"]):
            failures.append(
                f"{row['tag']} retains northern generic display name {row['name']}"
            )

    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership_rows = csv_rows(OWNERSHIP)
    owner = {row["location"]: row["tag"] for row in ownership_rows}
    counts = Counter(row["tag"] for row in ownership_rows)
    hierarchy = json.loads(HIERARCHY.read_text(encoding="utf-8-sig"))
    locations = set(json.loads(LOCATIONS.read_text(encoding="utf-8-sig")))

    for tag, expected in EXPECTED_COUNTS.items():
        if counts[tag] != expected:
            failures.append(
                f"{tag} reviewed ownership changed from {expected} to {counts[tag]}"
            )
    for tag in REQUIRED:
        row = roster.get(tag)
        if row is not None and owner.get(row["map_capital"]) != tag:
            failures.append(
                f"{tag} does not own reviewed capital {row['map_capital']}"
            )
    for tag in ("AES", "WBB", "BPC", "WSC", "ETG"):
        if counts[tag] > 60:
            failures.append(f"{tag} exceeds the 60-location Baltic outlier cap")

    alsace = descendants("alsace_area", hierarchy, locations)
    non_roman_alsace = sorted(
        location for location in alsace if location in owner and owner[location] != "ROM"
    )
    if non_roman_alsace:
        failures.append(
            "Roman Alsace retains non-Roman ownership: "
            + ",".join(non_roman_alsace[:8])
        )

    angrivarian_frame = descendants("hanover_province", hierarchy, locations) | {
        "dannenberg", "ebstorf", "isenhagen", "luchow",
        "luneburg", "uelzen", "winsen_aller",
    }
    stray_ger = sorted(
        row["location"]
        for row in ownership_rows
        if row["tag"] == "GER" and row["location"] not in angrivarian_frame
    )
    if stray_ger:
        failures.append(
            "Angrivarii retain disconnected/out-of-frame ownership: "
            + ",".join(stray_ger[:8])
        )

    residual = RESIDUAL.read_text(encoding="utf-8-sig")
    for token in ("AES,baltic_region", "GER,north_german_region",
                  "GER,south_german_region"):
        if token in residual:
            failures.append(f"forbidden macro residual remains: {token}")

    profiles = keyed(TAG_PROFILES, "tag")
    governments = keyed(GOVERNMENTS, "design_tag")
    coas = keyed(COAS, "tag")
    privileges = keyed(PRIVILEGES, "key")
    laws = keyed(LAWS, "law")
    overlays = keyed(OVERLAYS, "key")
    privilege_art = keyed(PRIVILEGE_ART, "key")
    units = keyed(UNITS, "key")
    unit_art = keyed(UNIT_ART, "key")

    for key in sorted(REQUIRED_PRIVILEGES):
        row = privileges.get(key)
        art = privilege_art.get(key)
        if row is None:
            failures.append(f"missing northern privilege {key}")
        elif row["confidence"] != "contested" or not row["source"]:
            failures.append(f"{key} lacks bounded source/confidence metadata")
        if art is None or art["status"] != "complete" or art["confidence"] != "secure":
            failures.append(f"{key} lacks complete direct privilege art")
        slug = key.removeprefix("antq_")
        for path in (
            ROOT / f"assets_queue/generated_sources/antq_privilege_{slug}_source.png",
            ROOT / f"assets_queue/generated/antq_privilege_{slug}_64x90.png",
            ROOT / f"main_menu/gfx/interface/icons/privileges/{key}.dds",
        ):
            if not path.is_file():
                failures.append(f"{key} lacks art asset {path.relative_to(ROOT)}")

    for key in sorted(REQUIRED_LAWS):
        row = laws.get(key)
        if row is None:
            failures.append(f"missing northern law {key}")
        elif row["confidence"] != "contested" or not row["source"]:
            failures.append(f"{key} lacks bounded source/confidence metadata")

    for key, expected_tags in EXPECTED_OVERLAY_TAGS.items():
        row = overlays.get(key)
        if row is None:
            failures.append(f"missing northern government overlay {key}")
            continue
        actual_tags = set(row["tags"].split("|"))
        if actual_tags != expected_tags:
            failures.append(
                f"{key} tag coverage changed: expected "
                f"{'|'.join(sorted(expected_tags))}, found {'|'.join(sorted(actual_tags))}"
            )

    for key, expected_tags in EXPECTED_UNIT_TAGS.items():
        row = units.get(key)
        art = unit_art.get(key)
        if row is None:
            failures.append(f"missing northern unit {key}")
            continue
        actual_tags = set(row["tags"].split("|"))
        if actual_tags != expected_tags:
            failures.append(
                f"{key} availability changed: expected "
                f"{'|'.join(sorted(expected_tags))}, found {'|'.join(sorted(actual_tags))}"
            )
        if row["confidence"] != "contested" or not row["source"]:
            failures.append(f"{key} lacks bounded source/confidence metadata")
        if art is None or art["status"] != "complete":
            failures.append(f"{key} lacks direct recruitment art")

    pop_cultures = {
        match.group("location"): match.group("culture")
        for match in POP_CULTURE.finditer(
            START_POPS.read_text(encoding="utf-8-sig")
        )
    }
    cultures_by_tag: dict[str, set[str]] = {}
    for row in ownership_rows:
        culture = pop_cultures.get(row["location"])
        if culture:
            cultures_by_tag.setdefault(row["tag"], set()).add(culture)

    ledger: list[dict[str, str]] = []
    for tag in REQUIRED:
        row = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        if row is None:
            continue
        if profile is None:
            failures.append(f"{tag} lacks a culture/religion profile")
        elif profile["culture"] not in cultures_by_tag.get(tag, set()):
            failures.append(
                f"{tag} primary culture {profile['culture']} is absent from owned pops"
            )
        if government is None:
            failures.append(f"{tag} lacks a government/reform package")
        if coa is None:
            failures.append(f"{tag} lacks a direct reviewed UI standard")
        engine_tag = mapping.get(tag, "")
        if not engine_tag:
            failures.append(f"{tag} lacks a collision-safe engine tag")
        ledger.append({
            "design_tag": tag,
            "engine_tag": engine_tag,
            "name": row["name"],
            "kind": row["kind"],
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
                    rf"^\s*{re.escape(key)}:\s+\"",
                    text,
                    re.MULTILINE,
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
                "s2_northern_granularity: wrote "
                f"{LEDGER.relative_to(ROOT)} ({len(rows)} reviewed frames)"
            )
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_northern_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print(
            "s2_northern_granularity: PASS "
            f"({len(rows)} reviewed frames; largest Baltic frame "
            f"{max(int(row['location_count']) for row in rows if row['design_tag'] in {'AES','WBB','BPC','WSC','ETG'})}; "
            f"{len(REQUIRED_PRIVILEGES)} privileges; {len(REQUIRED_LAWS)} laws; "
            f"{len(EXPECTED_UNIT_TAGS)} direct-art units; 11-client localization)"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_northern_granularity: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

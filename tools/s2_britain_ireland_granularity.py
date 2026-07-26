#!/usr/bin/env python3
"""Validate the sourced AD 1 Britain-and-Ireland political replacement."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter
from pathlib import Path

from ownership_map import descendants, vanilla_owned_locations


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
RESIDUAL = ROOT / "docs/world_1ad/ownership_residual_areas.csv"
EMPTY = ROOT / "docs/world_1ad/intentional_empty_areas.csv"
HIERARCHY = ROOT / "docs/vanilla_symbols/geography_hierarchy.json"
LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
TAG_PROFILES = ROOT / "docs/m4/tag_profiles.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
GOVERNMENT_OVERLAYS = ROOT / "docs/m6/regional_government_overlays.csv"
PRIVILEGES = ROOT / "docs/m6/privileges.csv"
LAWS = ROOT / "docs/m6/laws.csv"
PRIVILEGE_ICONS = ROOT / "docs/m11/direct_privilege_icons.csv"
BUILDING_BUNDLES = ROOT / "docs/m5/s2_britain_ireland_building_seeds.csv"
UNITS = ROOT / "docs/m7/units.csv"
UNIT_ART = ROOT / "docs/m12/unit_art_ledger.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
HISTORIES = ROOT / "docs/m12/country_history_agendas.csv"
LEDGER = ROOT / "docs/m12/britain_ireland_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)
BRITAIN = (
    "CAT", "TRI", "ICE", "BRI", "ATB", "SIL", "ORD", "DUM", "BRT",
    "REG", "BLG", "DUR", "DOB", "COR", "CNV", "PBI", "CRV", "DEM",
    "DEC", "VOT", "SEL", "NOV", "DAM", "VCN", "TAE", "EPD", "VAC",
    "DCT", "CAE", "CRE", "CNA", "LGB", "SME", "NCR", "CAL",
)
IRELAND = (
    "VNI", "RHB", "DAR", "ERD", "ULA", "NAG", "AUT", "GAN",
    "VEL", "IVN", "USD", "IBG", "CND", "MNP", "CCI", "EBL",
)
REQUIRED = BRITAIN + IRELAND
REQUIRED_PRIVILEGES = {
    "antq_oppidum_councils", "antq_hillfort_retinues",
    "antq_channel_exchange_compacts", "antq_hibernian_cattle_compacts",
    "antq_hibernian_maritime_followings", "antq_hibernian_ritual_specialists",
}
REQUIRED_LAWS = {
    "antq_british_landholding_law", "antq_british_muster_law",
    "antq_british_ritual_law", "antq_hibernian_cattle_law",
    "antq_hibernian_seaway_law", "antq_hibernian_ritual_law",
}
REQUIRED_UNITS = {
    "antq_british_hillfort_spearmen", "antq_northern_british_skirmishers",
    "antq_hibernian_javelin_bands", "antq_hibernian_coastal_warbands",
}
FORBIDDEN_NAME = re.compile(
    r"\b(?:societies|brittonic societies|caledonian societies|ulaid|land of)\b",
    re.IGNORECASE,
)
FIELDS = (
    "design_tag", "engine_tag", "name", "region", "kind", "map_capital",
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
    regional = {
        tag: row
        for tag, row in roster.items()
        if row["region"] in {"Britain", "Ireland"}
    }
    if set(regional) != set(REQUIRED):
        failures.append("Britain/Ireland roster must be the 51 reviewed frames")
    for tag, row in regional.items():
        visible = " ".join(
            row[field] for field in ("name", "historical_capital")
        )
        if FORBIDDEN_NAME.search(visible):
            failures.append(f"{tag} retains generic or later naming: {visible}")
        if not row["source"] or row["confidence"] not in {"secure", "contested"}:
            failures.append(f"{tag} lacks source/confidence metadata")

    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership_rows = csv_rows(OWNERSHIP)
    owner = {row["location"]: row["tag"] for row in ownership_rows}
    counts = Counter(row["tag"] for row in ownership_rows)
    hierarchy = json.loads(HIERARCHY.read_text(encoding="utf-8-sig"))
    locations = set(json.loads(LOCATIONS.read_text(encoding="utf-8-sig")))
    ownable = vanilla_owned_locations(locations)
    britain_surface = descendants(
        "great_britain_region", hierarchy, locations
    ) & ownable
    ireland_surface = descendants("ireland_region", hierarchy, locations) & ownable
    if len(britain_surface) != 234:
        failures.append(
            f"installed British surface changed from 234 to {len(britain_surface)}"
        )
    if len(ireland_surface) != 95:
        failures.append(
            f"installed Irish surface changed from 95 to {len(ireland_surface)}"
        )
    assigned_britain = {
        loc for loc in britain_surface if owner.get(loc) in set(BRITAIN)
    }
    assigned_ireland = {
        loc for loc in ireland_surface if owner.get(loc) in set(IRELAND)
    }
    if assigned_britain != britain_surface:
        failures.append("the Great Britain surface is not completely assigned")
    if assigned_ireland != ireland_surface:
        failures.append("Irish surface is not completely assigned")
    if owner.get("orkney") != "NCR" or owner.get("shetland") != "NCR":
        failures.append("northern island communities are not attached to NCR")
    if "torshavn" not in EMPTY.read_text(encoding="utf-8-sig"):
        failures.append("torshavn is not documented as intentionally empty")
    if max((counts[tag] for tag in REQUIRED), default=0) > 25:
        failures.append("a replacement exceeds the 25-location cap")
    if min((counts[tag] for tag in REQUIRED), default=0) < 1:
        failures.append("a replacement owns no location")
    for tag in REQUIRED:
        row = roster.get(tag)
        if row and owner.get(row["map_capital"]) != tag:
            failures.append(
                f"{tag} does not own reviewed capital {row['map_capital']}"
            )

    residual_text = RESIDUAL.read_text(encoding="utf-8-sig")
    if (
        "great_britain_region" in residual_text
        or "ireland_region" in residual_text
        or "Brittonic" in residual_text
    ):
        failures.append("broad Britain/Ireland residual ownership remains")

    profiles = keyed(TAG_PROFILES, "tag")
    governments = keyed(GOVERNMENTS, "design_tag")
    coas = keyed(COAS, "tag")
    histories = keyed(HISTORIES, "design_tag")
    cultures: set[str] = set()
    ledger: list[dict[str, str]] = []
    for tag in REQUIRED:
        row = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        history = histories.get(tag)
        if row is None:
            continue
        if profile is None:
            failures.append(f"{tag} lacks a culture/religion profile")
        elif profile["culture"] in cultures:
            failures.append(f"{tag} reuses regional culture {profile['culture']}")
        elif profile["culture"] in {"antq_brittonic", "antq_gaelic"}:
            failures.append(f"{tag} retains a broad culture fallback")
        else:
            cultures.add(profile["culture"])
        if government is None:
            failures.append(f"{tag} lacks a government/reform package")
        if coa is None:
            failures.append(f"{tag} lacks a direct UI standard")
        if history is None:
            failures.append(f"{tag} lacks an opening agenda")
        elif "Ptolemy" not in history["text"]:
            failures.append(f"{tag} agenda omits the dated-evidence caveat")
        engine_tag = mapping.get(tag, "")
        if not engine_tag:
            failures.append(f"{tag} lacks a collision-safe engine tag")
        ledger.append({
            "design_tag": tag,
            "engine_tag": engine_tag,
            "name": row["name"],
            "region": row["region"],
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

    overlay_rows = keyed(GOVERNMENT_OVERLAYS, "key")
    expected_overlays = {
        "antq_britain_hillfort_layer", "antq_southern_britain_oppida",
        "antq_british_channel_exchange", "antq_hibernian_household_layer",
    }
    if set(overlay_rows) != expected_overlays:
        failures.append("regional government overlay set is incomplete")
    overlay_tags = set()
    for row in overlay_rows.values():
        overlay_tags.update(row["tags"].split("|"))
    if overlay_tags != set(REQUIRED):
        failures.append("regional government overlays do not cover exactly all 51 frames")
    privilege_rows = keyed(PRIVILEGES, "key")
    law_rows = keyed(LAWS, "law")
    icon_rows = keyed(PRIVILEGE_ICONS, "key")
    if not REQUIRED_PRIVILEGES <= set(privilege_rows):
        failures.append("Britain/Ireland privilege definitions are incomplete")
    if not REQUIRED_PRIVILEGES <= set(icon_rows):
        failures.append("Britain/Ireland direct privilege icons are incomplete")
    if not REQUIRED_LAWS <= set(law_rows):
        failures.append("Britain/Ireland law definitions are incomplete")

    building_rows = keyed(BUILDING_BUNDLES, "key")
    building_capitals = {row["location"] for row in building_rows.values()}
    expected_capitals = {roster[tag]["map_capital"] for tag in REQUIRED}
    if building_capitals != expected_capitals or len(building_rows) != len(REQUIRED):
        failures.append("every island opening capital must have one two-family building bundle")
    for row in building_rows.values():
        if len(row["families"].split("|")) != 2:
            failures.append(f"{row['key']} does not provide exactly two building seeds")

    unit_rows = keyed(UNITS, "key")
    unit_art_rows = keyed(UNIT_ART, "key")
    if not REQUIRED_UNITS <= set(unit_rows):
        failures.append("Britain/Ireland regional unit definitions are incomplete")
    if not REQUIRED_UNITS <= set(unit_art_rows):
        failures.append("Britain/Ireland direct recruitment art is incomplete")
    if not set(BRITAIN) <= set(unit_rows.get(
        "antq_british_hillfort_spearmen", {}
    ).get("tags", "").split("|")):
        failures.append("British hillfort spearmen do not cover all British frames")
    for key in ("antq_hibernian_javelin_bands", "antq_hibernian_coastal_warbands"):
        if not set(IRELAND) <= set(unit_rows.get(key, {}).get("tags", "").split("|")):
            failures.append(f"{key} does not cover all Hibernian frames")

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
                "s2_britain_ireland_granularity: wrote "
                f"{LEDGER.relative_to(ROOT)} ({len(rows)} frames)"
            )
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_britain_ireland_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        counts = [int(row["location_count"]) for row in rows]
        print(
            "s2_britain_ireland_granularity: PASS "
            f"({len(BRITAIN)} British + {len(IRELAND)} Hibernian frames; "
            f"{sum(counts)} owned entries; largest {max(counts)}; "
            "6 privileges; 6 laws; 102 capital seeds; 4 direct-art units; "
            "11-client localization)"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_britain_ireland_granularity: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

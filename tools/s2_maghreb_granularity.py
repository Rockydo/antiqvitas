#!/usr/bin/env python3
"""Validate the first sourced AD 1 Maghreb political-map replacement."""

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
AREA_OWNERSHIP = ROOT / "docs/world_1ad/ownership_areas.csv"
RESIDUAL = ROOT / "docs/world_1ad/ownership_residual_areas.csv"
CULTURE_REMAP = ROOT / "docs/culture_remap.csv"
TAG_PROFILES = ROOT / "docs/m4/tag_profiles.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
LEDGER = ROOT / "docs/m12/maghreb_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)
REQUIRED = ("MAU", "BER", "MUS")
EXPECTED_NAMES = {
    "MAU": "Mauretania",
    "BER": "Gaetuli",
    "MUS": "Musulamii",
}
EXPECTED_CAPITALS = {
    "MAU": "cherchell",
    "BER": "djelfa",
    "MUS": "biskra",
}
EXPECTED_COUNTS = {
    "MAU": 128,
    "BER": 19,
    "MUS": 11,
}
EXPECTED_CULTURES = {
    "MAU": "antq_berber",
    "BER": "antq_gaetulian",
    "MUS": "antq_musulamian",
}
REQUIRED_AREA_OWNERS = {
    ("MAU", "algiers_area"),
    ("MUS", "aures_province"),
    ("MUS", "hodna_province"),
}
REQUIRED_CULTURE_SELECTORS = {
    ("area", "atlas_high_plateau", "antq_gaetulian"),
    ("province", "aures_province", "antq_musulamian"),
    ("province", "hodna_province", "antq_musulamian"),
}
FORBIDDEN_NAME = re.compile(
    r"\b(?:societies|communities|land of|generic|placeholder)\b",
    re.IGNORECASE,
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
    profiles = keyed(TAG_PROFILES, "tag")
    governments = keyed(GOVERNMENTS, "design_tag")
    coas = keyed(COAS, "tag")
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership_rows = csv_rows(OWNERSHIP)
    owner = {row["location"]: row["tag"] for row in ownership_rows}
    counts = Counter(row["tag"] for row in ownership_rows)

    area_owners = {
        (row["tag"], row["geography"]) for row in csv_rows(AREA_OWNERSHIP)
    }
    for required in REQUIRED_AREA_OWNERS:
        if required not in area_owners:
            failures.append(
                f"missing reviewed ownership selector {required[0]}:{required[1]}"
            )
    residual = {
        (row["tag"], row["geography"]) for row in csv_rows(RESIDUAL)
    }
    if ("BER", "maghreb_region") in residual:
        failures.append("Gaetuli still use a Maghreb-wide residual superstate")
    if ("BER", "atlas_high_plateau") not in residual:
        failures.append("Gaetuli lack their bounded high-plateau residual")

    culture_selectors = {
        (row["selector_type"], row["selector"], row["culture"])
        for row in csv_rows(CULTURE_REMAP)
    }
    for required in REQUIRED_CULTURE_SELECTORS:
        if required not in culture_selectors:
            failures.append(
                "missing reviewed culture selector " + ":".join(required)
            )

    ledger: list[dict[str, str]] = []
    for tag in REQUIRED:
        row = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        if row is None:
            failures.append(f"missing reviewed Maghreb tag {tag}")
            continue
        if row["name"] != EXPECTED_NAMES[tag]:
            failures.append(
                f"{tag} must display as {EXPECTED_NAMES[tag]}, found {row['name']}"
            )
        if FORBIDDEN_NAME.search(row["name"]):
            failures.append(f"{tag} retains generic display name {row['name']}")
        if row["map_capital"] != EXPECTED_CAPITALS[tag]:
            failures.append(
                f"{tag} capital changed from {EXPECTED_CAPITALS[tag]} "
                f"to {row['map_capital']}"
            )
        if owner.get(row["map_capital"]) != tag:
            failures.append(f"{tag} does not own {row['map_capital']}")
        if counts[tag] != EXPECTED_COUNTS[tag]:
            failures.append(
                f"{tag} reviewed ownership changed from {EXPECTED_COUNTS[tag]} "
                f"to {counts[tag]}"
            )
        if not row["source"] or row["confidence"] not in {"secure", "contested"}:
            failures.append(f"{tag} lacks source/confidence metadata")
        if profile is None:
            failures.append(f"{tag} lacks a country culture/religion profile")
        elif profile["culture"] != EXPECTED_CULTURES[tag]:
            failures.append(
                f"{tag} culture changed from {EXPECTED_CULTURES[tag]} "
                f"to {profile['culture']}"
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
                "s2_maghreb_granularity: wrote "
                f"{LEDGER.relative_to(ROOT)} ({len(rows)} frames)"
            )
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_maghreb_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print(
            "s2_maghreb_granularity: PASS "
            f"(3 frames; {sum(int(row['location_count']) for row in rows)} "
            "owned entries; 3 cultures; 3 direct standards; "
            "11-client localization)"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_maghreb_granularity: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

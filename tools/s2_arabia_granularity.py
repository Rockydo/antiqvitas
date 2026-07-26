#!/usr/bin/env python3
"""Validate the sourced AD 1 Arabian political-map replacement."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

from ownership_map import descendants, vanilla_owned_locations


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
RESIDUAL = ROOT / "docs/world_1ad/ownership_residual_areas.csv"
HIERARCHY = ROOT / "docs/vanilla_symbols/geography_hierarchy.json"
LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
TAG_PROFILES = ROOT / "docs/m4/tag_profiles.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
LEDGER = ROOT / "docs/m12/arabia_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)
REQUIRED = (
    "NAB", "SAB", "HIM", "QAT", "HAD", "KIN",
    "THM", "AGR", "GRH", "QTR", "OMN", "BED",
)
FORBIDDEN_NAME = re.compile(
    r"\b(?:societies|interior bedouin|arabian societies|land of)\b",
    re.IGNORECASE,
)
ANACHRONISTIC_TRIBES = re.compile(
    r"\b(?:ghassanids?|tanukhids?|tayyi?|abd al[- ]qays)\b",
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
    rows = csv_rows(path)
    values: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row[key]
        if value in values:
            raise ValueError(f"{path.relative_to(ROOT)} repeats {key} {value}")
        values[value] = row
    return values


def expected_rows() -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    roster_rows = csv_rows(ROSTER)
    roster = {row["tag"]: row for row in roster_rows}
    arabian = {tag: row for tag, row in roster.items() if row["region"] == "Arabia"}
    if set(arabian) != set(REQUIRED):
        failures.append(
            "Arabian roster must be exactly the twelve reviewed frames: "
            + ",".join(REQUIRED)
        )
    for row in arabian.values():
        visible = " ".join(
            row[field] for field in ("name", "historical_capital")
        )
        if FORBIDDEN_NAME.search(visible):
            failures.append(f"{row['tag']} retains generic Arabian naming: {visible}")
        if ANACHRONISTIC_TRIBES.search(visible):
            failures.append(f"{row['tag']} backdates a later tribal identity: {visible}")
        if not row["source"] or row["confidence"] not in {"secure", "contested"}:
            failures.append(f"{row['tag']} lacks source/confidence metadata")

    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership_rows = csv_rows(OWNERSHIP)
    owner = {row["location"]: row["tag"] for row in ownership_rows}
    counts = Counter(row["tag"] for row in ownership_rows)
    hierarchy = json.loads(HIERARCHY.read_text(encoding="utf-8-sig"))
    locations = set(json.loads(LOCATIONS.read_text(encoding="utf-8-sig")))
    arabia_locations = (
        descendants("arabia_region", hierarchy, locations)
        & vanilla_owned_locations(locations)
    )
    assigned_arabia = {
        location for location in arabia_locations if owner.get(location) in set(REQUIRED)
    }
    if assigned_arabia != arabia_locations:
        missing = sorted(arabia_locations - assigned_arabia)
        failures.append(
            f"Arabia has {len(missing)} locations outside reviewed frames: "
            + ",".join(missing[:8])
        )
    if len(arabia_locations) != 351:
        failures.append(
            f"installed Arabia ownable surface changed from reviewed 351 to "
            f"{len(arabia_locations)}"
        )
    if max((counts[tag] for tag in REQUIRED), default=0) > 60:
        failures.append("an Arabian replacement exceeds the 60-location outlier cap")
    if min((counts[tag] for tag in REQUIRED), default=0) < 8:
        failures.append("an Arabian replacement has fewer than eight owned locations")
    for tag in REQUIRED:
        row = roster.get(tag)
        if row is None:
            continue
        if owner.get(row["map_capital"]) != tag:
            failures.append(
                f"{tag} does not own its reviewed capital {row['map_capital']}"
            )

    residual_text = RESIDUAL.read_text(encoding="utf-8-sig")
    if "arabia_region" in residual_text or "Interior Bedouin" in residual_text:
        failures.append("peninsula-wide Arabian residual ownership remains")

    profiles = keyed(TAG_PROFILES, "tag")
    governments = keyed(GOVERNMENTS, "design_tag")
    coas = keyed(COAS, "tag")
    ledger: list[dict[str, str]] = []
    for tag in REQUIRED:
        row = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        if row is None:
            continue
        if profile is None:
            failures.append(f"{tag} lacks a country culture/religion profile")
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
                if not re.search(
                    rf"^\s*{re.escape(row['engine_tag'] + suffix)}:\s+\"",
                    text,
                    re.MULTILINE,
                ):
                    failures.append(
                        f"{language} lacks {row['engine_tag'] + suffix} localization"
                    )
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
                "s2_arabia_granularity: wrote "
                f"{LEDGER.relative_to(ROOT)} ({len(rows)} frames)"
            )
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_arabia_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        counts = [int(row["location_count"]) for row in rows]
        print(
            "s2_arabia_granularity: PASS "
            f"({len(rows)} frames; {sum(counts)} owned entries; "
            f"largest {max(counts)}; 11-client localization)"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_arabia_granularity: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

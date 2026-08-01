#!/usr/bin/env python3
"""Validate the sourced AD 1 Horn/Barbaria political-map replacement."""

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
CORRECTIONS = ROOT / "docs/m4/location_name_corrections.csv"
TAG_PROFILES = ROOT / "docs/m4/tag_profiles.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LEDGER = ROOT / "docs/m12/horn_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)
REQUIRED = ("BAR", "AVA", "MLA", "MUN", "MOS", "ARO", "OPO", "HAU", "AZA")
EXPECTED = {
    "BAR": ("Guban Pastoralists", "burao", 21, "antq_northern_horn_coastal"),
    "AVA": ("Avalites", "zeila", 1, "antq_northern_horn_coastal"),
    "MLA": ("Malao", "berbera", 1, "antq_northern_horn_coastal"),
    "MUN": ("Mundu", "maydh", 1, "antq_northern_horn_coastal"),
    "MOS": ("Mosyllon", "qandala", 1, "antq_northern_horn_coastal"),
    "ARO": ("Aromata Emporion", "bargaal", 1, "antq_northern_horn_coastal"),
    "OPO": ("Opone", "ras_hafun", 1, "antq_northern_horn_coastal"),
    "HAU": ("Haud Pastoralists", "degehabur", 22, "antq_horn_pastoral"),
    "AZA": ("Northern Azania", "mogadishu", 30, "antq_northern_azanian"),
}
PORTS = {"AVA", "MLA", "MUN", "MOS", "ARO", "OPO"}
EXPECTED_CORRECTIONS = {
    ("zeila", "Avalites"),
    ("berbera", "Malao"),
    ("maydh", "Mundu"),
    ("qandala", "Mosyllon"),
    ("bargaal", "Aromata Emporion"),
    ("ras_hafun", "Opone"),
}
FORBIDDEN_NAME = re.compile(
    r"\b(?:societies|land of|generic|placeholder)\b", re.IGNORECASE
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

    areas = {(row["tag"], row["geography"]) for row in csv_rows(AREAS)}
    if ("BAR", "somalia_region") in areas:
        failures.append("the Somalia-wide Barbaria ownership block remains")
    residuals = {
        (row["tag"], row["geography"]) for row in csv_rows(RESIDUAL)
    }
    for pair in {
        ("BAR", "northern_somalia_area"),
        ("HAU", "inner_somalia_area"),
        ("AZA", "southern_somalia_area"),
    }:
        if pair not in residuals:
            failures.append(f"missing bounded Horn residual {pair[0]}:{pair[1]}")

    corrections = {
        (row["location"], row["historical_name"])
        for row in csv_rows(CORRECTIONS)
        if row["culture"] == "antq_northern_horn_coastal"
    }
    for pair in EXPECTED_CORRECTIONS:
        if pair not in corrections:
            failures.append(f"missing reviewed port toponym {pair[0]}:{pair[1]}")

    ledger: list[dict[str, str]] = []
    for tag in REQUIRED:
        expected_name, capital, expected_count, culture = EXPECTED[tag]
        row = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        if row is None:
            failures.append(f"missing reviewed Horn tag {tag}")
            continue
        if row["name"] != expected_name:
            failures.append(
                f"{tag} must display as {expected_name}, found {row['name']}"
            )
        if FORBIDDEN_NAME.search(row["name"]):
            failures.append(f"{tag} retains generic display name {row['name']}")
        if row["map_capital"] != capital or owner.get(capital) != tag:
            failures.append(f"{tag} must own reviewed capital {capital}")
        if counts[tag] != expected_count:
            failures.append(
                f"{tag} reviewed ownership changed from {expected_count} "
                f"to {counts[tag]}"
            )
        if not row["source"] or row["confidence"] not in {"secure", "contested"}:
            failures.append(f"{tag} lacks source/confidence metadata")
        if profile is None or profile["culture"] != culture:
            found = profile["culture"] if profile else "<missing>"
            failures.append(f"{tag} culture must be {culture}, found {found}")
        if profile is not None and profile["religion"] != "antq_nile_cushitic":
            failures.append(f"{tag} retains a non-Horn religion profile")
        expected_reform = (
            "antq_far_side_port_chiefdom"
            if tag in PORTS
            else "antq_horn_pastoral_network"
        )
        if government is None or government["reform"] != expected_reform:
            found = government["reform"] if government else "<missing>"
            failures.append(
                f"{tag} reform must be {expected_reform}, found {found}"
            )
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

    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")
    for reform in ("antq_far_side_port_chiefdom", "antq_horn_pastoral_network"):
        if not re.search(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reform_text):
            failures.append(f"generated reform definition missing {reform}")
        if f"unlock_government_reform = {reform}" in advance_text:
            failures.append(f"opening reform leaked into research: {reform}")

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
                "s2_horn_granularity: wrote "
                f"{LEDGER.relative_to(ROOT)} ({len(rows)} frames)"
            )
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_horn_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print(
            "s2_horn_granularity: PASS "
            "(9 frames; 79 owned entries; largest 30; 6 independent ports; "
            "3 cultures; 2 reforms; 9 direct standards; 11-client localization)"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_horn_granularity: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

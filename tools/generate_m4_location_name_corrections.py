#!/usr/bin/env python3
"""Render reviewed late-loading corrections for M4 location names.

The full-map M4 generator intentionally keeps broad automated ledgers stable and
reproducible. This overlay is the authoritative exception layer for reviewed
corrections discovered after a bulk pass. Its filename sorts after the base M4
localization, so duplicate keys here supersede older labels without hand-editing
the generated 28,573-key files.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from dates import M2_MIRROR_LANGUAGES

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/m4/location_name_corrections.csv"
SOURCES = ROOT / "docs/m4/LOCATION_NAME_CORRECTION_SOURCES.md"
CULTURES = ROOT / "docs/m4/cultures.csv"
LANGUAGES = ROOT / "docs/m4/languages.csv"
ENGINE_LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
LOC_ROOT = ROOT / "main_menu/localization"
CLIENT_LANGUAGES = ("english", *M2_MIRROR_LANGUAGES)
CORRECTION_FIELDS = (
    "location",
    "culture",
    "historical_name",
    "source",
    "confidence",
    "note",
)
CULTURE_FIELDS = ("key", "name", "group", "language", "source", "confidence", "note")
LANGUAGE_FIELDS = (
    "group",
    "key",
    "name",
    "family",
    "fallback",
    "male_names",
    "female_names",
    "dynasty_names",
    "source",
    "confidence",
    "note",
)
ALLOWED_CONFIDENCE = frozenset(("secure", "tier2", "contested"))
OUTPUT_PREFIX = "antq_zz_m4_location_name_corrections_l_"
OUTPUT_GLOB = f"{OUTPUT_PREFIX}*.yml"
UTF8_BOM = b"\xef\xbb\xbf"
SOURCE_LINE = re.compile(r"^- `(?P<code>[A-Z0-9][A-Z0-9.-]*)`:")

Adapter = tuple[str, str]


@dataclass(frozen=True)
class Correction:
    location: str
    historical_name: str
    source: str
    confidence: str
    note: str
    adapters: tuple[Adapter, ...]


def csv_rows(path: Path, expected_fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != expected_fields:
            raise ValueError(f"{path.relative_to(ROOT)} must use header {','.join(expected_fields)}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} has no data rows")
    return rows


def unique_lookup(
    path: Path,
    rows: list[dict[str, str]],
    key_field: str,
    value_field: str,
) -> dict[str, str]:
    result: dict[str, str] = {}
    failures: list[str] = []
    for number, row in enumerate(rows, start=2):
        key = row.get(key_field, "").strip()
        value = row.get(value_field, "").strip()
        if not key or not value:
            failures.append(
                f"{path.relative_to(ROOT)}:{number}: blank {key_field} or {value_field}"
            )
            continue
        if key in result:
            failures.append(f"{path.relative_to(ROOT)}:{number}: duplicate {key_field} {key}")
            continue
        result[key] = value
    if failures:
        raise ValueError("\n".join(failures))
    return result


def source_codes() -> set[str]:
    codes: set[str] = set()
    duplicates: set[str] = set()
    for line in SOURCES.read_text(encoding="utf-8").splitlines():
        match = SOURCE_LINE.match(line)
        if match is None:
            continue
        code = match.group("code")
        if code in codes:
            duplicates.add(code)
        codes.add(code)
    if duplicates:
        raise ValueError(
            f"{SOURCES.relative_to(ROOT)} repeats source codes {','.join(sorted(duplicates))}"
        )
    if not codes:
        raise ValueError(f"{SOURCES.relative_to(ROOT)} contains no source-code definitions")
    return codes


def installed_locations() -> set[str]:
    payload = json.loads(ENGINE_LOCATIONS.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, list):
        raise ValueError(f"{ENGINE_LOCATIONS.relative_to(ROOT)} must contain a JSON list")
    locations: list[str] = []
    for index, value in enumerate(payload):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{ENGINE_LOCATIONS.relative_to(ROOT)}:{index}: location keys must be non-empty strings"
            )
        locations.append(value.strip())
    duplicates = {location for location, count in Counter(locations).items() if count > 1}
    if duplicates:
        raise ValueError(
            f"{ENGINE_LOCATIONS.relative_to(ROOT)} repeats locations {','.join(sorted(duplicates))}"
        )
    return set(locations)


def correction_entries() -> tuple[Correction, ...]:
    rows = csv_rows(LEDGER, CORRECTION_FIELDS)
    source_order = [row.get("location", "").strip() for row in rows]
    if source_order != sorted(source_order):
        raise ValueError(f"{LEDGER.relative_to(ROOT)} rows must be sorted by location")

    culture_groups = unique_lookup(
        CULTURES,
        csv_rows(CULTURES, CULTURE_FIELDS),
        "key",
        "group",
    )
    group_languages = unique_lookup(
        LANGUAGES,
        csv_rows(LANGUAGES, LANGUAGE_FIELDS),
        "group",
        "key",
    )
    known_sources = source_codes()
    known_locations = installed_locations()

    entries: list[Correction] = []
    seen_locations: set[str] = set()
    failures: list[str] = []
    for number, row in enumerate(rows, start=2):
        value = {field: row.get(field, "").strip() for field in CORRECTION_FIELDS}
        if any(not value[field] for field in CORRECTION_FIELDS):
            failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: blank required field")
            continue

        location = value["location"]
        if location in seen_locations:
            failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: duplicate location {location}")
            continue
        seen_locations.add(location)
        if location not in known_locations:
            failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: unknown installed location {location}")
            continue

        cultures = [culture.strip() for culture in value["culture"].split("|")]
        if any(not culture for culture in cultures):
            failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: blank culture adapter")
            continue
        if len(cultures) != len(set(cultures)):
            failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: duplicate culture adapter")
            continue

        source_tokens = [code.strip() for code in value["source"].split(";")]
        if any(not code for code in source_tokens):
            failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: blank source code")
            continue
        if len(source_tokens) != len(set(source_tokens)):
            failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: duplicate source code")
            continue
        unknown_sources = sorted(set(source_tokens) - known_sources)
        if unknown_sources:
            failures.append(
                f"{LEDGER.relative_to(ROOT)}:{number}: unknown source codes "
                f"{','.join(unknown_sources)}"
            )
            continue

        adapters: list[Adapter] = []
        invalid_adapter = False
        for culture in cultures:
            group = culture_groups.get(culture)
            if not group:
                failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: unknown M4 culture {culture}")
                invalid_adapter = True
                continue
            language = group_languages.get(group)
            if not language or not language.endswith("_language"):
                failures.append(
                    f"{LEDGER.relative_to(ROOT)}:{number}: culture {culture} has no valid language"
                )
                invalid_adapter = True
                continue
            adapter = (language.removesuffix("_language") + "_dialect", language)
            if adapter not in adapters:
                adapters.append(adapter)
        if invalid_adapter:
            continue

        if value["confidence"] not in ALLOWED_CONFIDENCE:
            failures.append(
                f"{LEDGER.relative_to(ROOT)}:{number}: confidence must be one of "
                f"{','.join(sorted(ALLOWED_CONFIDENCE))}"
            )
            continue

        entries.append(
            Correction(
                location=location,
                historical_name=value["historical_name"],
                source=";".join(source_tokens),
                confidence=value["confidence"],
                note=value["note"],
                adapters=tuple(adapters),
            )
        )
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return tuple(entries)


def esc(value: str) -> str:
    return value.replace('"', "'")


def output_path(client_language: str) -> Path:
    name = f"{OUTPUT_PREFIX}{client_language}.yml"
    base_name = f"antq_m4_location_names_l_{client_language}.yml"
    if name <= base_name:
        raise ValueError(f"correction output {name} would not load after {base_name}")
    return LOC_ROOT / client_language / name


def localization(entries: tuple[Correction, ...], client_language: str) -> str:
    lines = [
        f"l_{client_language}:",
        " # Generated authoritative corrections loaded after the bulk M4 location-name layer; English is mirrored by design.",
    ]
    for entry in entries:
        name = esc(entry.historical_name)
        lines.append(f' {entry.location}: "{name}"')
        for dialect, language in entry.adapters:
            lines.append(f' {entry.location}.{dialect}: "{name}"')
            lines.append(f' {entry.location}.{language}: "{name}"')
    return "\n".join(lines) + "\n"


def outputs(entries: tuple[Correction, ...]) -> dict[Path, bytes]:
    return {
        output_path(language): UTF8_BOM + localization(entries, language).encode("utf-8")
        for language in CLIENT_LANGUAGES
    }


def owned_outputs() -> set[Path]:
    if not LOC_ROOT.is_dir():
        return set()
    return {
        path
        for directory in LOC_ROOT.iterdir()
        if directory.is_dir()
        for path in directory.glob(OUTPUT_GLOB)
        if path.is_file()
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        entries = correction_entries()
        expected = outputs(entries)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"m4_location_name_corrections: FAIL\n  - {exc}")
        return 1

    actual = owned_outputs()
    extras = sorted(actual - set(expected))
    if args.write:
        for path, content in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            print(f"m4_location_name_corrections: wrote {path.relative_to(ROOT)}")
        for path in extras:
            path.unlink()
            print(f"m4_location_name_corrections: removed stale {path.relative_to(ROOT)}")
        return 0

    failures = [
        f"stale or missing generated output {path.relative_to(ROOT)}"
        for path, content in expected.items()
        if not path.is_file() or path.read_bytes() != content
    ]
    failures.extend(
        f"unexpected generated output {path.relative_to(ROOT)}"
        for path in extras
    )
    if failures:
        print("m4_location_name_corrections: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print(
        f"m4_location_name_corrections: PASS "
        f"({len(entries)} reviewed corrections; {len(CLIENT_LANGUAGES)} mirrored localizations)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

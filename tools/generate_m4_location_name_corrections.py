#!/usr/bin/env python3
"""Render reviewed late-loading corrections for M4 location names.

The full-map M4 generator intentionally keeps broad automated ledgers stable and
reproducible.  This small overlay is the authoritative exception layer for
reviewed corrections discovered after a bulk pass.  Its filename sorts after
the base M4 localization, so duplicate keys here supersede older labels without
mutating or hand-editing the generated 28,573-key files.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import TypeAlias

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/m4/location_name_corrections.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
LANGUAGES = ROOT / "docs/m4/languages.csv"
ENGINE_LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
LOC_ROOT = ROOT / "main_menu/localization"
CLIENT_LANGUAGES = (
    "english",
    "french",
    "german",
    "spanish",
    "polish",
    "russian",
    "braz_por",
    "simp_chinese",
    "japanese",
    "korean",
    "turkish",
)
FIELDS = ("location", "culture", "historical_name", "source", "confidence", "note")
ALLOWED_CONFIDENCE = frozenset(("secure", "tier2", "contested"))
OUTPUT_PREFIX = "antq_zz_m4_location_name_corrections_l_"
Adapter: TypeAlias = tuple[str, str]
CorrectionEntry: TypeAlias = dict[str, str | tuple[Adapter, ...]]


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def esc(value: str) -> str:
    return value.replace('"', "'")


def correction_entries() -> list[CorrectionEntry]:
    with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError(f"{LEDGER.relative_to(ROOT)} must use header {','.join(FIELDS)}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{LEDGER.relative_to(ROOT)} has no correction rows")

    culture_groups = {row["key"].strip(): row["group"].strip() for row in table(CULTURES)}
    group_languages = {row["group"].strip(): row["key"].strip() for row in table(LANGUAGES)}
    installed_locations = set(json.loads(ENGINE_LOCATIONS.read_text(encoding="utf-8-sig")))

    entries: list[CorrectionEntry] = []
    seen_locations: set[str] = set()
    failures: list[str] = []
    for number, row in enumerate(rows, start=2):
        value = {field: row.get(field, "").strip() for field in FIELDS}
        if any(not value[field] for field in FIELDS):
            failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: blank required field")
            continue
        location = value["location"]
        cultures = [culture.strip() for culture in value["culture"].split("|")]
        if any(not culture for culture in cultures):
            failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: blank culture adapter")
            continue
        if len(cultures) != len(set(cultures)):
            failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: duplicate culture adapter")
            continue
        if location in seen_locations:
            failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: duplicate location {location}")
            continue
        seen_locations.add(location)
        if location not in installed_locations:
            failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: unknown installed location {location}")
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
                failures.append(f"{LEDGER.relative_to(ROOT)}:{number}: culture {culture} has no valid language")
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
            {
                **value,
                "culture": "|".join(cultures),
                "adapters": tuple(adapters),
            }
        )
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return sorted(entries, key=lambda entry: entry["location"])


def localization(entries: list[CorrectionEntry], client_language: str) -> str:
    lines = [
        f"l_{client_language}:",
        " # Generated authoritative corrections loaded after the bulk M4 location-name layer; English is mirrored by design.",
    ]
    for entry in entries:
        location = entry["location"]
        name = esc(entry["historical_name"])
        lines.append(f' {location}: "{name}"')
        for dialect, language in entry["adapters"]:
            lines.append(f' {location}.{dialect}: "{name}"')
            lines.append(f' {location}.{language}: "{name}"')
    return "\n".join(lines) + "\n"


def outputs() -> dict[Path, str]:
    entries = correction_entries()
    return {
        LOC_ROOT / language / f"{OUTPUT_PREFIX}{language}.yml": localization(entries, language)
        for language in CLIENT_LANGUAGES
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        expected = outputs()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"m4_location_name_corrections: FAIL\n  - {exc}")
        return 1
    if args.write:
        for path, content in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8-sig", newline="\n")
            print(f"m4_location_name_corrections: wrote {path.relative_to(ROOT)}")
        return 0
    failures = [
        f"stale or missing generated output {path.relative_to(ROOT)}"
        for path, content in expected.items()
        if not path.is_file() or path.read_text(encoding="utf-8-sig") != content
    ]
    if failures:
        print("m4_location_name_corrections: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print(
        f"m4_location_name_corrections: PASS "
        f"({len(correction_entries())} reviewed corrections; {len(CLIENT_LANGUAGES)} mirrored localizations)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

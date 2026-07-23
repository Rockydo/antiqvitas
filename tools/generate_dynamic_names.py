#!/usr/bin/env python3
"""Render conservative M4 dynamic names from reviewed source anchors."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from io import StringIO
from pathlib import Path

from generate_country_definitions import historical_profile_for

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
COORDINATES = ROOT / "docs/world_1ad/capital_coordinates.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
LANGUAGES = ROOT / "docs/m4/languages.csv"
LOC_ROOT = ROOT / "main_menu/localization"
REPORT = ROOT / "docs/m4/dynamic_location_names.csv"
CURATED = ROOT / "docs/m4/dynamic_location_name_overrides.csv"
TIER2 = ROOT / "docs/m4/tier2_location_name_overrides.csv"
TIER3 = ROOT / "docs/m4/tier3_location_name_overrides.csv"
TIER3_MAP = ROOT / "docs/m4/tier3_map_name_fallbacks.csv"
ENGINE_LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
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


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def esc(value: str) -> str:
    return value.replace('"', "'")


def ledger_entries(
    path: Path,
    allowed_confidence: str,
    anchor_kind: str,
    description: str,
    culture_groups: dict[str, str],
    group_languages: dict[str, str],
    installed_locations: set[str],
    seen_locations: set[str],
) -> list[dict[str, str]]:
    """Load an explicitly bounded non-capital toponym ledger."""
    required = ("location", "culture", "historical_name", "source", "confidence", "note")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != required:
            raise ValueError(f"{path.relative_to(ROOT)} must use header {','.join(required)}")
        rows_ = list(reader)
    if not rows_:
        raise ValueError(f"{path.relative_to(ROOT)} has no {description} name rows")
    output: list[dict[str, str]] = []
    failures: list[str] = []
    for number, row in enumerate(rows_, start=2):
        value = {field: row.get(field, "").strip() for field in required}
        if any(not value[field] for field in required):
            failures.append(f"{path.relative_to(ROOT)}:{number}: blank required field")
            continue
        location = value["location"]
        culture = value["culture"]
        if location not in installed_locations:
            failures.append(f"{path.relative_to(ROOT)}:{number}: unknown installed location {location}")
            continue
        if location in seen_locations:
            failures.append(f"{path.relative_to(ROOT)}:{number}: duplicate dynamic-name location {location}")
            continue
        group = culture_groups.get(culture)
        if not group:
            failures.append(f"{path.relative_to(ROOT)}:{number}: unknown M4 culture {culture}")
            continue
        language = group_languages.get(group)
        if not language or not language.endswith("_language"):
            failures.append(f"{path.relative_to(ROOT)}:{number}: culture {culture} has no valid language")
            continue
        if value["confidence"] != allowed_confidence:
            failures.append(f"{path.relative_to(ROOT)}:{number}: only {allowed_confidence} toponyms are permitted")
            continue
        output.append(
            {
                "location": location,
                "anchor_kind": anchor_kind,
                "tag": "",
                "historical_name": value["historical_name"],
                "culture": culture,
                "language": language,
                "dialect": language.removesuffix("_language") + "_dialect",
                "source": value["source"],
                "confidence": value["confidence"],
                "note": value["note"],
            }
        )
        seen_locations.add(location)
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return output


def entries() -> list[dict[str, str]]:
    roster = {row["tag"]: row for row in rows(ROSTER)}
    culture_groups = {row["key"]: row["group"] for row in rows(CULTURES)}
    group_languages = {row["group"]: row["key"] for row in rows(LANGUAGES)}
    installed_locations = set(json.loads(ENGINE_LOCATIONS.read_text(encoding="utf-8-sig")))
    output: list[dict[str, str]] = []
    seen_locations: set[str] = set()
    for coordinate in rows(COORDINATES):
        tag = coordinate["tag"]
        if tag not in roster:
            raise ValueError(f"capital coordinate references unknown tag {tag}")
        row = roster[tag]
        # Coordinate-verified named cities only. Broad societies of peoples and
        # contested anchors remain on their current displayed name until a
        # location-specific historical name can be reviewed.
        if coordinate["confidence"] != "secure" or row["kind"] == "sop":
            continue
        location = row["map_capital"]
        if location not in installed_locations:
            raise ValueError(f"{tag} maps to unknown installed location {location}")
        if location in seen_locations:
            raise ValueError(f"multiple dynamic-name anchors use {location}")
        profile = historical_profile_for(row)
        group = culture_groups.get(profile.culture)
        if not group:
            raise ValueError(f"{tag} uses M4 culture without a group: {profile.culture}")
        language = group_languages.get(group)
        if not language:
            raise ValueError(f"{tag} culture group has no M4 language: {group}")
        if not language.endswith("_language"):
            raise ValueError(f"M4 language key does not end in _language: {language}")
        output.append(
            {
                "location": location,
                "anchor_kind": "capital",
                "tag": tag,
                "historical_name": row["historical_capital"],
                "culture": profile.culture,
                "language": language,
                "dialect": language.removesuffix("_language") + "_dialect",
                "source": f"{coordinate['source']};{row['source']}",
                "confidence": coordinate["confidence"],
                "note": "Coordinate-verified AD 1 capital anchor",
            }
        )
        seen_locations.add(location)
    output.extend(ledger_entries(CURATED, "secure", "curated", "reviewed direct", culture_groups, group_languages, installed_locations, seen_locations))
    output.extend(ledger_entries(TIER2, "tier2", "tier2", "bounded Tier-2", culture_groups, group_languages, installed_locations, seen_locations))
    output.extend(ledger_entries(TIER3, "tier3", "tier3", "retained-label Tier-3", culture_groups, group_languages, installed_locations, seen_locations))
    if not output:
        raise ValueError("no secure dynamic-name anchors were selected")
    return sorted(output, key=lambda entry: (entry["location"], entry["language"]))


def root_entries(entries_: list[dict[str, str]]) -> list[tuple[str, str]]:
    required = ("location", "historical_name", "source", "confidence", "note")
    with TIER3_MAP.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != required:
            raise ValueError(f"{TIER3_MAP.relative_to(ROOT)} must use header {','.join(required)}")
        roots = {row["location"].strip(): row["historical_name"].strip() for row in reader}
    if not roots or any(not location or not name for location, name in roots.items()):
        raise ValueError(f"{TIER3_MAP.relative_to(ROOT)} has blank root fallback data")
    for entry in entries_:
        roots[entry["location"]] = entry["historical_name"]
    return sorted(roots.items())


def localization(entries_: list[dict[str, str]], roots: list[tuple[str, str]], language: str) -> str:
    lines = [
        f"l_{language}:",
        " # Generated from M4 capital anchors plus direct, Tier-2, and explicit Tier-3 toponym ledgers; English is mirrored by design.",
    ]
    for location, name in roots:
        lines.append(f" {location}: \"{esc(name)}\"")
    for entry in entries_:
        name = esc(entry["historical_name"])
        # The engine resolves the culture's dialect, while the root entry makes
        # the same reviewed name available to root-language localization paths.
        lines.append(f" {entry['location']}.{entry['dialect']}: \"{name}\"")
        lines.append(f" {entry['location']}.{entry['language']}: \"{name}\"")
    return "\n".join(lines) + "\n"


def report(entries_: list[dict[str, str]]) -> str:
    stream = StringIO(newline="")
    fields = ("location", "anchor_kind", "tag", "historical_name", "culture", "language", "dialect", "source", "confidence", "note")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(entries_)
    return stream.getvalue()


def outputs() -> dict[Path, tuple[str, str]]:
    selected = entries()
    roots = root_entries(selected)
    result: dict[Path, tuple[str, str]] = {REPORT: (report(selected), "utf-8-sig")}
    for language in CLIENT_LANGUAGES:
        result[LOC_ROOT / language / f"antq_m4_location_names_l_{language}.yml"] = (
            localization(selected, roots, language),
            "utf-8-sig",
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        expected = outputs()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"dynamic_names: FAIL\n  - {exc}")
        return 1
    if args.write:
        for path, (content, encoding) in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding, newline="\n")
            print(f"dynamic_names: wrote {path.relative_to(ROOT)}")
        return 0
    failures = [
        f"stale or missing generated output {path.relative_to(ROOT)}"
        for path, (content, encoding) in expected.items()
        if not path.is_file() or path.read_text(encoding=encoding) != content
    ]
    if failures:
        print("dynamic_names: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    selected = entries()
    capitals = sum(entry["anchor_kind"] == "capital" for entry in selected)
    curated = sum(entry["anchor_kind"] == "curated" for entry in selected)
    tier2 = sum(entry["anchor_kind"] == "tier2" for entry in selected)
    tier3 = sum(entry["anchor_kind"] == "tier3" for entry in selected)
    print(f"dynamic_names: PASS ({capitals} capital + {curated} curated + {tier2} Tier-2 + {tier3} Tier-3 anchors; {len(CLIENT_LANGUAGES)} mirrored localizations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

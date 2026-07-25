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
QUALIFIED = ROOT / "docs/m4/qualified_location_name_overrides.csv"
TIER2 = ROOT / "docs/m4/tier2_location_name_overrides.csv"
TIER2_WIDE = ROOT / "docs/m4/tier2_wide_location_name_overrides.csv"
TIER2_REMOTE = ROOT / "docs/m4/tier2_remote_location_name_overrides.csv"
TIER2_FAR = ROOT / "docs/m4/tier2_far_location_name_overrides.csv"
TIER2_ULTRA = ROOT / "docs/m4/tier2_ultra_location_name_overrides.csv"
TIER3 = ROOT / "docs/m4/tier3_location_name_overrides.csv"
TIER3_MAP = ROOT / "docs/m4/tier3_map_name_fallbacks.csv"
CORRECTIONS = ROOT / "docs/m4/location_name_corrections.csv"
ROMAN = ROOT / "docs/m4/roman_location_name_overrides.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
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


def correction_locations() -> set[str]:
    """Locations owned exclusively by the reviewed late correction layer.

    EU5 reports duplicate localization keys and keeps the first definition, so
    an alphabetical overlay cannot safely supersede the bulk dynamic layer.
    Excluding these roots and culture adapters here gives the correction file
    sole ownership of its reviewed names.
    """
    required = ("location", "culture", "historical_name", "source", "confidence", "note")
    with CORRECTIONS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != required:
            raise ValueError(f"{CORRECTIONS.relative_to(ROOT)} must use header {','.join(required)}")
        locations = [str(row.get("location") or "").strip() for row in reader]
    if not locations or any(not location for location in locations):
        raise ValueError(f"{CORRECTIONS.relative_to(ROOT)} has blank correction locations")
    if len(locations) != len(set(locations)):
        raise ValueError(f"{CORRECTIONS.relative_to(ROOT)} has duplicate correction locations")
    return set(locations)


def roman_locations() -> set[str]:
    """Return every field owned by Rome in the generated AD 1 setup."""
    required = ("tag", "engine_tag", "location", "tenure", "source", "confidence", "note")
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(line for line in handle if not line.startswith("#"))
        if tuple(reader.fieldnames or ()) != required:
            raise ValueError(f"{OWNERSHIP.relative_to(ROOT)} has an unexpected header")
        result = {
            str(row.get("location") or "").strip()
            for row in reader
            if str(row.get("tag") or "").strip() == "ROM"
        }
    if not result or "" in result:
        raise ValueError(f"{OWNERSHIP.relative_to(ROOT)} has invalid Roman ownership rows")
    return result


def ledger_entries(
    path: Path,
    allowed_confidence: str,
    anchor_kind: str,
    description: str,
    culture_groups: dict[str, str],
    group_languages: dict[str, str],
    installed_locations: set[str],
    seen_locations: set[str],
    excluded_locations: set[str] | None = None,
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
        if excluded_locations and location in excluded_locations:
            continue
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
    roman = roman_locations()
    output.extend(ledger_entries(CURATED, "secure", "curated", "reviewed direct", culture_groups, group_languages, installed_locations, seen_locations))
    output.extend(ledger_entries(ROMAN, "tier2", "roman_identity", "reviewed Roman identity", culture_groups, group_languages, installed_locations, seen_locations))
    output.extend(ledger_entries(QUALIFIED, "tier2", "qualified", "reviewed qualified", culture_groups, group_languages, installed_locations, seen_locations, roman))
    output.extend(ledger_entries(TIER2, "tier2", "tier2", "bounded Tier-2", culture_groups, group_languages, installed_locations, seen_locations, roman))
    output.extend(ledger_entries(TIER2_WIDE, "tier2", "tier2", "wide Tier-2", culture_groups, group_languages, installed_locations, seen_locations, roman))
    output.extend(ledger_entries(TIER2_REMOTE, "tier2", "tier2_remote", "remote Tier-2", culture_groups, group_languages, installed_locations, seen_locations, roman))
    output.extend(ledger_entries(TIER2_FAR, "tier2", "tier2_far", "far Tier-2", culture_groups, group_languages, installed_locations, seen_locations, roman))
    output.extend(ledger_entries(TIER2_ULTRA, "tier2", "tier2_ultra", "ultra-far Tier-2", culture_groups, group_languages, installed_locations, seen_locations, roman))
    output.extend(ledger_entries(TIER3, "tier3", "tier3", "retained-label Tier-3", culture_groups, group_languages, installed_locations, seen_locations, roman))
    corrections = correction_locations()
    output = [entry for entry in output if entry["location"] not in corrections]
    if not output:
        raise ValueError("no secure dynamic-name anchors were selected")
    return sorted(output, key=lambda entry: (entry["location"], entry["language"]))


def root_entries(entries_: list[dict[str, str]]) -> list[tuple[str, str]]:
    required = ("location", "historical_name", "source", "confidence", "note")
    with TIER3_MAP.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != required:
            raise ValueError(f"{TIER3_MAP.relative_to(ROOT)} must use header {','.join(required)}")
        corrections = correction_locations()
        roman = roman_locations()
        roots = {
            row["location"].strip(): row["historical_name"].strip()
            for row in reader
            if row["location"].strip() not in corrections
            and row["location"].strip() not in roman
        }
    if not roots or any(not location or not name for location, name in roots.items()):
        raise ValueError(f"{TIER3_MAP.relative_to(ROOT)} has blank root fallback data")
    for entry in entries_:
        roots[entry["location"]] = entry["historical_name"]
    return sorted(roots.items())


def localization(entries_: list[dict[str, str]], roots: list[tuple[str, str]], language: str) -> str:
    lines = [
        f"l_{language}:",
        " # Generated from reviewed direct and identity ledgers plus non-Roman fallback tiers; unsupported Roman fields retain vanilla localization.",
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
    roman_identity = sum(entry["anchor_kind"] == "roman_identity" for entry in selected)
    tier2 = sum(entry["anchor_kind"] in {"qualified", "tier2", "tier2_remote", "tier2_far", "tier2_ultra"} for entry in selected)
    remote = sum(entry["anchor_kind"] == "tier2_remote" for entry in selected)
    far = sum(entry["anchor_kind"] == "tier2_far" for entry in selected)
    ultra = sum(entry["anchor_kind"] == "tier2_ultra" for entry in selected)
    tier3 = sum(entry["anchor_kind"] == "tier3" for entry in selected)
    print(f"dynamic_names: PASS ({capitals} capital + {curated} curated + {roman_identity} Roman identity + {tier2} non-Roman Tier-2 ({remote} remote, {far} far, {ultra} ultra-far) + {tier3} non-Roman Tier-3 anchors; {len(CLIENT_LANGUAGES)} mirrored localizations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

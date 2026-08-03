#!/usr/bin/env python3
"""Render conservative M4 dynamic names from reviewed source anchors."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import unicodedata
from io import StringIO
from pathlib import Path

from generate_country_definitions import historical_profile_for

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
COORDINATES = ROOT / "docs/world_1ad/capital_coordinates.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
LANGUAGES = ROOT / "docs/m4/languages.csv"
MOUNTED_CULTURES = ROOT / "in_game/common/cultures/antq_m4_cultures.txt"
MOUNTED_LANGUAGES = ROOT / "in_game/common/languages/antq_m4_languages.txt"
LOC_ROOT = ROOT / "main_menu/localization"
OWNER_EFFECT = ROOT / "in_game/common/scripted_effects/antq_frontier_owner_names.txt"
ON_ACTIONS = ROOT / "in_game/common/on_action/_hardcoded.txt"
REPORT = ROOT / "docs/m4/dynamic_location_names.csv"
CURATED = ROOT / "docs/m4/dynamic_location_name_overrides.csv"
PRIORITY = ROOT / "docs/m4/priority_location_name_overrides.csv"
QUALIFIED = ROOT / "docs/m4/qualified_location_name_overrides.csv"
TIER2 = ROOT / "docs/m4/tier2_location_name_overrides.csv"
TIER2_WIDE = ROOT / "docs/m4/tier2_wide_location_name_overrides.csv"
TIER2_REMOTE = ROOT / "docs/m4/tier2_remote_location_name_overrides.csv"
TIER2_FAR = ROOT / "docs/m4/tier2_far_location_name_overrides.csv"
TIER2_ULTRA = ROOT / "docs/m4/tier2_ultra_location_name_overrides.csv"
TIER3 = ROOT / "docs/m4/tier3_location_name_overrides.csv"
TIER3_MAP = ROOT / "docs/m4/tier3_map_name_fallbacks.csv"
CORRECTIONS = ROOT / "docs/m4/location_name_corrections.csv"
FRONTIER = ROOT / "docs/m4/frontier_language_names.csv"
ROMAN = ROOT / "docs/m4/roman_location_name_overrides.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
ENGINE_LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
R5_GEOGRAPHY = ROOT / "docs/r5/geography_names.csv"
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
ROMAN_CULTURE = "antq_latin"
OWNER_HOOK = "\t\tantq_frontier_owner_name_effect = yes"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def r5_root_overrides() -> dict[str, str]:
    if not R5_GEOGRAPHY.is_file():
        return {}
    result: dict[str, str] = {}
    for row in rows(R5_GEOGRAPHY):
        key = row.get("key", "").strip()
        name = row.get("ad1_name", "").strip()
        if not key or not name:
            raise ValueError(f"{R5_GEOGRAPHY.relative_to(ROOT)} has blank name data")
        prior = result.get(key)
        if prior is not None and prior != name:
            raise ValueError(f"{R5_GEOGRAPHY.relative_to(ROOT)} diverges for {key}")
        result[key] = name
    return result


def esc(value: str) -> str:
    return value.replace('"', "'")


def comparable_name(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value.casefold())
    return "".join(character for character in folded if character.isalnum())


def roman_resolver_keys() -> tuple[str, str]:
    """Resolve and verify the mounted Roman dynamic-localization keys."""
    culture_groups = {row["key"]: row["group"] for row in rows(CULTURES)}
    group_languages = {row["group"]: row["key"] for row in rows(LANGUAGES)}
    group = culture_groups.get(ROMAN_CULTURE)
    language = group_languages.get(group or "")
    if not language or not language.endswith("_language"):
        raise ValueError(f"{ROMAN_CULTURE} has no valid dynamic-name language")
    dialect = language.removesuffix("_language") + "_dialect"
    culture_script = MOUNTED_CULTURES.read_text(encoding="utf-8-sig")
    language_script = MOUNTED_LANGUAGES.read_text(encoding="utf-8-sig")
    if f"{ROMAN_CULTURE} = {{" not in culture_script or f"\tlanguage = {dialect}" not in culture_script:
        raise ValueError(
            f"mounted {ROMAN_CULTURE} does not resolve through {dialect}"
        )
    if f"{language} = {{" not in language_script or f"\t\t{dialect} = {{ }}" not in language_script:
        raise ValueError(f"mounted language layer lacks {language}/{dialect}")
    return language, dialect


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
    priority_locations = {
        row["location"].strip()
        for row in rows(PRIORITY)
        if row["location"].strip() and row["location"].strip() not in roman
    }
    output.extend(ledger_entries(PRIORITY, "tier2", "priority_proxy", "high-visibility priority", culture_groups, group_languages, installed_locations, seen_locations, roman))
    output.extend(ledger_entries(QUALIFIED, "tier2", "qualified", "reviewed qualified", culture_groups, group_languages, installed_locations, seen_locations, roman))
    output.extend(ledger_entries(TIER2, "tier2", "tier2", "bounded Tier-2", culture_groups, group_languages, installed_locations, seen_locations, roman))
    output.extend(ledger_entries(TIER2_WIDE, "tier2", "tier2", "wide Tier-2", culture_groups, group_languages, installed_locations, seen_locations, roman))
    output.extend(ledger_entries(TIER2_REMOTE, "tier2", "tier2_remote", "remote Tier-2", culture_groups, group_languages, installed_locations, seen_locations, roman))
    output.extend(ledger_entries(TIER2_FAR, "tier2", "tier2_far", "far Tier-2", culture_groups, group_languages, installed_locations, seen_locations, roman))
    output.extend(ledger_entries(TIER2_ULTRA, "tier2", "tier2_ultra", "ultra-far Tier-2", culture_groups, group_languages, installed_locations, seen_locations, roman))
    output.extend(ledger_entries(TIER3, "tier3", "tier3", "retained-label Tier-3", culture_groups, group_languages, installed_locations, seen_locations, roman | priority_locations))
    corrections = correction_locations()
    output = [entry for entry in output if entry["location"] not in corrections]
    frontier = {row["location"]: row for row in rows(FRONTIER)}
    matched_frontier: set[str] = set()
    for entry in output:
        alias = frontier.get(entry["location"])
        if alias is None:
            continue
        if entry["culture"] != alias["local_culture"]:
            raise ValueError(
                f"{entry['location']}: frontier culture drift "
                f"{entry['culture']} != {alias['local_culture']}"
            )
        entry["historical_name"] = alias["local_name"]
        entry["source"] = f"{entry['source']};FRONTIER-LANGUAGE"
        entry["note"] = f"{entry['note']} {alias['note']}"
        matched_frontier.add(entry["location"])
    missing_frontier = set(frontier) - matched_frontier
    if missing_frontier:
        raise ValueError(
            "frontier aliases lack dynamic local entries: "
            + ", ".join(sorted(missing_frontier))
        )
    # Tier-3 was originally an installed-label compatibility layer.  Round 5
    # supplies a researched AD 1 root for every field, so letting those culture
    # adapters retain their old names would silently resurrect vanilla labels.
    # Frontier local forms use that researched root only when they merely echo
    # the installed fallback; independently reviewed ancient local forms remain
    # available beside the Roman political exonym.
    geography = r5_root_overrides()
    installed_fallbacks = {
        row["location"].strip(): row["historical_name"].strip()
        for row in rows(TIER3_MAP)
    }
    for entry in output:
        location = entry["location"]
        frontier_is_installed_fallback = (
            location in frontier
            and location in installed_fallbacks
            and comparable_name(entry["historical_name"])
            == comparable_name(installed_fallbacks[location])
        )
        if entry["anchor_kind"] == "tier3" or frontier_is_installed_fallback:
            if location not in geography:
                raise ValueError(f"{location}: dynamic fallback lacks Round 5 geography")
            entry["historical_name"] = geography[location]
            entry["source"] = f"{entry['source']};R5-GEOGRAPHY"
            entry["note"] = (
                f"{entry['note']} Round 5 researched geography replaces the "
                "installed-label fallback."
            )
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
    for location, name in r5_root_overrides().items():
        if location in roots:
            roots[location] = name
    return sorted(roots.items())


def localization(entries_: list[dict[str, str]], roots: list[tuple[str, str]], language: str) -> str:
    roman_language, roman_dialect = roman_resolver_keys()
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
    for alias in rows(FRONTIER):
        name = esc(alias["roman_name"])
        lines.append(f" antq_roman_{alias['location']}: \"{name}\"")
        lines.append(f" {alias['location']}.{roman_dialect}: \"{name}\"")
        lines.append(f" {alias['location']}.{roman_language}: \"{name}\"")
    return "\n".join(lines) + "\n"


def owner_effect() -> str:
    """Render owner-change renames without changing the local culture."""
    lines = [
        "# Generated by generate_dynamic_names.py --write.",
        "# Roman political exonyms for reviewed frontier fields; local names return under non-Roman rule.",
        "",
        "antq_frontier_owner_name_effect = {",
    ]
    for alias in sorted(rows(FRONTIER), key=lambda row: row["location"]):
        location = alias["location"]
        marker = f"antq_frontier_name_{location}"
        lines.extend(
            [
                "\tif = {",
                "\t\tlimit = {",
                "\t\t\tOR = {",
                f"\t\t\t\tthis = location:{location}",
                f"\t\t\t\thas_variable = {marker}",
                "\t\t\t}",
                "\t\t}",
                "\t\tif = {",
                "\t\t\tlimit = {",
                "\t\t\t\tscope:winner ?= {",
                f"\t\t\t\t\tculture ?= culture:{ROMAN_CULTURE}",
                "\t\t\t\t}",
                "\t\t\t}",
                f"\t\t\tset_variable = {marker}",
                f"\t\t\trename_location = antq_roman_{location}",
                "\t\t}",
                "\t\telse = {",
                f"\t\t\trename_location = {location}",
                f"\t\t\tremove_variable = {marker}",
                "\t\t}",
                "\t}",
            ]
        )
    lines.append("}")
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
    result: dict[Path, tuple[str, str]] = {
        REPORT: (report(selected), "utf-8-sig"),
        OWNER_EFFECT: (owner_effect(), "utf-8-sig"),
    }
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
    if OWNER_HOOK not in ON_ACTIONS.read_text(encoding="utf-8-sig"):
        print("dynamic_names: FAIL")
        print(f"  - {ON_ACTIONS.relative_to(ROOT)} lacks the owner-change rename hook")
        return 1
    selected = entries()
    capitals = sum(entry["anchor_kind"] == "capital" for entry in selected)
    curated = sum(entry["anchor_kind"] == "curated" for entry in selected)
    roman_identity = sum(entry["anchor_kind"] == "roman_identity" for entry in selected)
    tier2 = sum(entry["anchor_kind"] in {"priority_proxy", "qualified", "tier2", "tier2_remote", "tier2_far", "tier2_ultra"} for entry in selected)
    remote = sum(entry["anchor_kind"] == "tier2_remote" for entry in selected)
    far = sum(entry["anchor_kind"] == "tier2_far" for entry in selected)
    ultra = sum(entry["anchor_kind"] == "tier2_ultra" for entry in selected)
    tier3 = sum(entry["anchor_kind"] == "tier3" for entry in selected)
    print(f"dynamic_names: PASS ({capitals} capital + {curated} curated + {roman_identity} Roman identity + {tier2} non-Roman Tier-2 ({remote} remote, {far} far, {ultra} ultra-far) + {tier3} non-Roman Tier-3 anchors; {len(CLIENT_LANGUAGES)} mirrored localizations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

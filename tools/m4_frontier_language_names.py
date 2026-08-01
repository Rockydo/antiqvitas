#!/usr/bin/env python3
"""Generate local/Latin aliases for likely Roman frontier acquisitions."""

from __future__ import annotations

import argparse
import csv
import json
import re
from io import StringIO
from pathlib import Path

from generate_m4_tier3_names import installed_names
from generate_dynamic_names import (
    CLIENT_LANGUAGES,
    LOC_ROOT,
    ON_ACTIONS,
    OWNER_EFFECT,
    OWNER_HOOK,
    roman_resolver_keys,
)
from m4_priority_location_names import effective_entries, leaves, rows


ROOT = Path(__file__).resolve().parents[1]
HIERARCHY = ROOT / "docs/vanilla_symbols/geography_hierarchy.json"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
LANGUAGES = ROOT / "docs/m4/languages.csv"
OUTPUT = ROOT / "docs/m4/frontier_language_names.csv"
SCOPES = (
    "north_german_region",
    "south_german_region",
    "france_region",
    "great_britain_region",
    "balkan_region",
)
FIELDS = (
    "location",
    "opening_owner",
    "local_culture",
    "local_language",
    "local_name",
    "roman_name",
    "source",
    "confidence",
    "note",
)
ROMAN_ADMINISTRATIVE = re.compile(
    r"^(?:Ad\s|Aquae\b|Arae\b|Augusta\b|Caesaro|Castra\b|Col\.\s|"
    r"Colonia\b|Concordia\b|Constantia\b|Forum\b|Iulio|Municipium\b|"
    r"Phoebiana\b|Portus\b|Vicus\b)",
    re.IGNORECASE,
)


def ownership() -> dict[str, str]:
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        return {
            row["location"]: row["tag"]
            for row in csv.DictReader(
                line for line in handle if not line.startswith("#")
            )
        }


def generated_rows() -> list[dict[str, str]]:
    hierarchy = json.loads(HIERARCHY.read_text(encoding="utf-8-sig"))
    target = set().union(*(leaves(scope, hierarchy) for scope in SCOPES))
    effective = effective_entries()
    owners = ownership()
    labels = installed_names()
    culture_groups = {row["key"]: row["group"] for row in rows(CULTURES)}
    group_languages = {row["group"]: row["key"] for row in rows(LANGUAGES)}
    output: list[dict[str, str]] = []
    for location in sorted(target):
        entry = effective.get(location)
        culture = (entry or {}).get("culture", "")
        source = (entry or {}).get("source", "")
        if (
            not entry
            or entry.get("layer") == "capital"
            or owners.get(location) == "ROM"
            or not culture
            or "|" in culture
            or culture == "antq_latin"
            or ("PLE:" not in source and "PLN:" not in source)
        ):
            continue
        group = culture_groups.get(culture)
        language = group_languages.get(group or "")
        if not language:
            raise ValueError(f"{location}: no language for {culture}")
        roman_name = entry["historical_name"].strip()
        local_name = (
            labels.get(location, location.replace("_", " ").title())
            if ROMAN_ADMINISTRATIVE.search(roman_name)
            else roman_name
        )
        output.append(
            {
                "location": location,
                "opening_owner": owners.get(location, ""),
                "local_culture": culture,
                "local_language": language,
                "local_name": local_name,
                "roman_name": roman_name,
                "source": source,
                "confidence": entry["confidence"],
                "note": (
                    "Pleiades-derived Roman-view alias on the existing reviewed "
                    "engine-field proxy; overt Roman administrative forms retain "
                    "a transparent local cartographic label."
                ),
            }
        )
    if len(output) < 100:
        raise ValueError(f"frontier alias union unexpectedly small: {len(output)}")
    if len({row["location"] for row in output}) != len(output):
        raise ValueError("frontier alias union contains duplicate locations")
    return output


def render() -> str:
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(generated_rows())
    return stream.getvalue()


def validate_resolver_localizations(values: list[dict[str, str]]) -> None:
    """Require every frontier alias under the culture's actual mounted keys."""
    roman_language, roman_dialect = roman_resolver_keys()
    failures: list[str] = []
    for client in CLIENT_LANGUAGES:
        path = LOC_ROOT / client / f"antq_m4_location_names_l_{client}.yml"
        text = path.read_text(encoding="utf-8-sig")
        if ".antq_latin_dialect:" in text or ".antq_latin_language:" in text:
            failures.append(f"{path.relative_to(ROOT)} retains nonexistent antq_latin resolver keys")
        for row in values:
            location = row["location"]
            if f" antq_roman_{location}:" not in text:
                failures.append(
                    f"{path.relative_to(ROOT)} lacks antq_roman_{location}"
                )
            for resolver in (roman_dialect, roman_language):
                if f" {location}.{resolver}:" not in text:
                    failures.append(
                        f"{path.relative_to(ROOT)} lacks {location}.{resolver}"
                    )
    if failures:
        raise ValueError("\n".join(failures))


def validate_owner_adapter(values: list[dict[str, str]]) -> None:
    """Keep each political exonym reversible after rename_location mutates its tag."""
    raw = OWNER_EFFECT.read_bytes()
    if not raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"{OWNER_EFFECT.relative_to(ROOT)} lacks the required UTF-8 BOM")
    text = raw.decode("utf-8-sig")
    failures: list[str] = []
    for row in values:
        location = row["location"]
        marker = f"antq_frontier_name_{location}"
        required = (
            f"this = location:{location}",
            f"has_variable = {marker}",
            f"set_variable = {marker}",
            f"rename_location = antq_roman_{location}",
            f"rename_location = {location}",
            f"remove_variable = {marker}",
        )
        for contract in required:
            if text.count(contract) != 1:
                failures.append(
                    f"{OWNER_EFFECT.relative_to(ROOT)} requires exactly one {contract}"
                )
    if OWNER_HOOK not in ON_ACTIONS.read_text(encoding="utf-8-sig"):
        failures.append(f"{ON_ACTIONS.relative_to(ROOT)} lacks the owner-change hook")
    if failures:
        raise ValueError("\n".join(failures))


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        values = generated_rows()
        expected = render()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"m4_frontier_language_names: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8-sig", newline="\n")
        print(
            "m4_frontier_language_names: wrote "
            f"{len(values)} local/Latin frontier aliases"
        )
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != expected:
        print("m4_frontier_language_names: FAIL\n  - stale or missing ledger")
        return 1
    try:
        validate_resolver_localizations(values)
        validate_owner_adapter(values)
    except (OSError, ValueError) as exc:
        print(f"m4_frontier_language_names: FAIL\n  - {exc}")
        return 1
    local_overrides = sum(
        row["local_name"] != row["roman_name"] for row in values
    )
    print(
        "m4_frontier_language_names: PASS "
        f"({len(values)} aliases; {local_overrides} overt Roman forms localized)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

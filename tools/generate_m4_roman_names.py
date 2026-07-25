#!/usr/bin/env python3
"""Generate reviewed AD 1 Roman-realm location-name adapters.

This generator consumes an explicit identity-review ledger.  It does not infer
ancient names from nearest map points: every row binds one installed location
to one Pleiades place and one period-valid Pleiades name resource.  Ambiguous,
late, reconstructed, or merely nearby candidates belong in the companion
exclusion ledger and remain on vanilla localization.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELECTIONS = ROOT / "docs/m4/roman_location_name_selections.csv"
QUALIFIED = ROOT / "docs/m4/roman_location_name_qualified.csv"
EXCLUSIONS = ROOT / "docs/m4/roman_location_name_exclusions.csv"
OUTPUT = ROOT / "docs/m4/roman_location_name_overrides.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
CURATED = ROOT / "docs/m4/dynamic_location_name_overrides.csv"
CORRECTIONS = ROOT / "docs/m4/location_name_corrections.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
ENGINE_LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
PLEIADES_NAMES = ROOT / ".cache/pleiades/pleiades-names-latest.csv.gz"

SELECTION_FIELDS = (
    "location",
    "culture",
    "historical_name",
    "pleiades_id",
    "name_id",
    "match_basis",
    "offset_px",
    "note",
)
EXCLUSION_FIELDS = ("location", "pleiades_id", "candidate_name", "reason")
OUTPUT_FIELDS = ("location", "culture", "historical_name", "source", "confidence", "note")
ALLOWED_MATCH_BASIS = {"reviewed_exact_identity", "reviewed_explicit_modern_identity"}


def rows(path: Path, fields: tuple[str, ...], *, comments: bool = False) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        lines = (line for line in handle if not comments or not line.startswith("#"))
        reader = csv.DictReader(lines)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path.relative_to(ROOT)} must use header {','.join(fields)}")
        return [
            {field: str(row.get(field) or "").strip() for field in fields}
            for row in reader
        ]


def roman_locations() -> set[str]:
    fields = ("tag", "engine_tag", "location", "tenure", "source", "confidence", "note")
    result = {
        row["location"]
        for row in rows(OWNERSHIP, fields, comments=True)
        if row["tag"] == "ROM"
    }
    if not result:
        raise ValueError("ownership_resolved.csv contains no Roman locations")
    return result


def excluded_pairs() -> tuple[set[str], set[str]]:
    exclusions = rows(EXCLUSIONS, EXCLUSION_FIELDS)
    locations: set[str] = set()
    place_ids: set[str] = set()
    failures: list[str] = []
    for number, row in enumerate(exclusions, start=2):
        if any(not row[field] for field in EXCLUSION_FIELDS):
            failures.append(f"{EXCLUSIONS.relative_to(ROOT)}:{number}: blank required field")
            continue
        if row["location"] in locations:
            failures.append(f"{EXCLUSIONS.relative_to(ROOT)}:{number}: duplicate location {row['location']}")
        if row["pleiades_id"] in place_ids:
            failures.append(f"{EXCLUSIONS.relative_to(ROOT)}:{number}: duplicate Pleiades place {row['pleiades_id']}")
        locations.add(row["location"])
        place_ids.add(row["pleiades_id"])
    if failures:
        raise ValueError("\n".join(failures))
    return locations, place_ids


def verify_name_resources(selected: list[dict[str, str]]) -> None:
    """Validate selected name IDs when the documented Pleiades cache exists."""
    if not PLEIADES_NAMES.is_file():
        return
    wanted = {(row["pleiades_id"], row["name_id"]) for row in selected}
    found: set[tuple[str, str]] = set()
    invalid_period: list[str] = []
    with gzip.open(PLEIADES_NAMES, "rt", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            place_id = str(row.get("pid") or "").rstrip("/").split("/")[-1]
            name_id = str(row.get("id") or "").rstrip("/").split("/")[-1]
            key = (place_id, name_id)
            if key not in wanted:
                continue
            found.add(key)
            try:
                period_valid = float(row["minDate"]) <= 1 <= float(row["maxDate"])
            except (KeyError, TypeError, ValueError):
                period_valid = False
            if not period_valid:
                invalid_period.append(f"{place_id}/{name_id}")
    missing = sorted(f"{place_id}/{name_id}" for place_id, name_id in wanted - found)
    if missing or invalid_period:
        failures = [*(f"missing Pleiades name resource {item}" for item in missing)]
        failures.extend(f"Pleiades name resource does not span AD 1: {item}" for item in sorted(invalid_period))
        raise ValueError("\n".join(failures))


def render() -> str:
    selected = rows(SELECTIONS, SELECTION_FIELDS)
    qualified = rows(QUALIFIED, OUTPUT_FIELDS)
    if not selected:
        raise ValueError(f"{SELECTIONS.relative_to(ROOT)} has no reviewed selections")

    roman = roman_locations()
    installed = set(json.loads(ENGINE_LOCATIONS.read_text(encoding="utf-8-sig")))
    cultures = {row["key"] for row in rows(CULTURES, tuple(rows_header(CULTURES)))}
    curated = {row["location"] for row in rows(CURATED, OUTPUT_FIELDS)}
    corrections = {row["location"] for row in rows(CORRECTIONS, OUTPUT_FIELDS)}
    excluded_locations, excluded_place_ids = excluded_pairs()

    output: list[dict[str, str]] = []
    locations: set[str] = set()
    place_ids: set[str] = set()
    name_resources: set[tuple[str, str]] = set()
    failures: list[str] = []
    for number, row in enumerate(selected, start=2):
        if any(not row[field] for field in SELECTION_FIELDS):
            failures.append(f"{SELECTIONS.relative_to(ROOT)}:{number}: blank required field")
            continue
        location = row["location"]
        place_id = row["pleiades_id"]
        resource = (place_id, row["name_id"])
        if location in locations:
            failures.append(f"{SELECTIONS.relative_to(ROOT)}:{number}: duplicate location {location}")
        if place_id in place_ids:
            failures.append(f"{SELECTIONS.relative_to(ROOT)}:{number}: reused Pleiades place {place_id}")
        if resource in name_resources:
            failures.append(
                f"{SELECTIONS.relative_to(ROOT)}:{number}: reused Pleiades name {place_id}/{row['name_id']}"
            )
        locations.add(location)
        place_ids.add(place_id)
        name_resources.add(resource)
        if location not in roman:
            failures.append(f"{SELECTIONS.relative_to(ROOT)}:{number}: {location} is not Roman-owned at AD 1")
        if location not in installed:
            failures.append(f"{SELECTIONS.relative_to(ROOT)}:{number}: unknown installed location {location}")
        if location in curated:
            failures.append(f"{SELECTIONS.relative_to(ROOT)}:{number}: {location} already has a direct curated name")
        if location in corrections:
            failures.append(f"{SELECTIONS.relative_to(ROOT)}:{number}: {location} belongs to the correction layer")
        if location in excluded_locations or place_id in excluded_place_ids:
            failures.append(f"{SELECTIONS.relative_to(ROOT)}:{number}: selected excluded candidate {location}/{place_id}")
        if row["culture"] not in cultures:
            failures.append(f"{SELECTIONS.relative_to(ROOT)}:{number}: unknown M4 culture {row['culture']}")
        if row["match_basis"] not in ALLOWED_MATCH_BASIS:
            failures.append(f"{SELECTIONS.relative_to(ROOT)}:{number}: unsupported match basis {row['match_basis']}")
        try:
            offset = float(row["offset_px"])
        except ValueError:
            failures.append(f"{SELECTIONS.relative_to(ROOT)}:{number}: invalid offset {row['offset_px']}")
        else:
            if not 0 <= offset <= 50:
                failures.append(f"{SELECTIONS.relative_to(ROOT)}:{number}: offset outside reviewed bound: {offset}")
        output.append(
            {
                "location": location,
                "culture": row["culture"],
                "historical_name": row["historical_name"],
                "source": f"PLE:{place_id};PLN:{place_id}/{row['name_id']};R2",
                "confidence": "tier2",
                "note": row["note"],
            }
        )
    qualified_resources: list[dict[str, str]] = []
    for number, row in enumerate(qualified, start=2):
        if any(not row[field] for field in OUTPUT_FIELDS):
            failures.append(f"{QUALIFIED.relative_to(ROOT)}:{number}: blank required field")
            continue
        location = row["location"]
        source_parts = row["source"].split(";")
        place_parts = [part[4:] for part in source_parts if part.startswith("PLE:")]
        name_parts = [part[4:] for part in source_parts if part.startswith("PLN:")]
        if len(place_parts) != 1 or len(name_parts) != 1 or "/" not in name_parts[0]:
            failures.append(f"{QUALIFIED.relative_to(ROOT)}:{number}: malformed PLE/PLN source")
            continue
        place_id = place_parts[0]
        name_place, name_id = name_parts[0].split("/", 1)
        if name_place != place_id:
            failures.append(f"{QUALIFIED.relative_to(ROOT)}:{number}: mismatched PLE/PLN place")
        if location in locations:
            failures.append(f"{QUALIFIED.relative_to(ROOT)}:{number}: duplicate location {location}")
        if place_id in place_ids:
            failures.append(f"{QUALIFIED.relative_to(ROOT)}:{number}: reused Pleiades place {place_id}")
        locations.add(location)
        place_ids.add(place_id)
        if location not in roman:
            failures.append(f"{QUALIFIED.relative_to(ROOT)}:{number}: {location} is not Roman-owned at AD 1")
        if location not in installed:
            failures.append(f"{QUALIFIED.relative_to(ROOT)}:{number}: unknown installed location {location}")
        if location in curated or location in corrections:
            failures.append(f"{QUALIFIED.relative_to(ROOT)}:{number}: {location} collides with a higher layer")
        if location in excluded_locations or place_id in excluded_place_ids:
            failures.append(f"{QUALIFIED.relative_to(ROOT)}:{number}: selected excluded candidate {location}/{place_id}")
        if row["culture"] not in cultures:
            failures.append(f"{QUALIFIED.relative_to(ROOT)}:{number}: unknown M4 culture {row['culture']}")
        if row["confidence"] != "tier2" or "proxy" not in row["note"].lower():
            failures.append(f"{QUALIFIED.relative_to(ROOT)}:{number}: qualified row must declare a tier2 proxy")
        output.append(row)
        qualified_resources.append({"pleiades_id": place_id, "name_id": name_id})
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    verify_name_resources([*selected, *qualified_resources])
    output.sort(key=lambda row: row["location"])
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(output)
    return stream.getvalue()


def rows_header(path: Path) -> tuple[str, ...]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return tuple(csv.DictReader(handle).fieldnames or ())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        expected = render()
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f"m4_roman_names: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8-sig", newline="")
        print(f"m4_roman_names: wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != expected:
        print(f"m4_roman_names: FAIL\n  - stale or missing {OUTPUT.relative_to(ROOT)}")
        return 1
    print(f"m4_roman_names: PASS ({max(0, len(expected.splitlines()) - 1)} reviewed identities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

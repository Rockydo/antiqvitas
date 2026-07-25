#!/usr/bin/env python3
"""Generate the exhaustive AD 1 Roman-realm location-name audit.

Every field owned by Rome is classified as either a reviewed override or an
intentional vanilla pass-through.  Generic proximity adapters and synthetic
Tier-3 labels are forbidden in the Roman audit boundary.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
DYNAMIC = ROOT / "docs/m4/dynamic_location_names.csv"
ROMAN_OVERRIDES = ROOT / "docs/m4/roman_location_name_overrides.csv"
EXCLUSIONS = ROOT / "docs/m4/roman_location_name_exclusions.csv"
OUTPUT = ROOT / "docs/m4/roman_location_name_audit.csv"
SUMMARY = ROOT / "docs/m4/roman_location_name_audit_summary.json"

OWNERSHIP_FIELDS = (
    "tag",
    "engine_tag",
    "location",
    "tenure",
    "source",
    "confidence",
    "note",
)
DYNAMIC_FIELDS = (
    "location",
    "anchor_kind",
    "tag",
    "historical_name",
    "culture",
    "language",
    "dialect",
    "source",
    "confidence",
    "note",
)
ROMAN_OVERRIDE_FIELDS = (
    "location",
    "culture",
    "historical_name",
    "source",
    "confidence",
    "note",
)
EXCLUSION_FIELDS = ("location", "pleiades_id", "candidate_name", "reason")
OUTPUT_FIELDS = (
    "location",
    "historical_name",
    "layer",
    "anchor_kind",
    "culture",
    "source",
    "confidence",
    "decision",
    "audit_flags",
    "note",
)
ALLOWED_ROMAN_ANCHORS = {"capital", "curated", "roman_identity"}
ROMAN_SOURCE_RE = re.compile(r"PLE:(\d+);PLN:\1/[^;]+;R2")


def rows(
    path: Path,
    expected_fields: tuple[str, ...],
    *,
    comments: bool = False,
) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        lines = (line for line in handle if not comments or not line.startswith("#"))
        reader = csv.DictReader(lines)
        if tuple(reader.fieldnames or ()) != expected_fields:
            raise ValueError(
                f"{path.relative_to(ROOT)} must use header {','.join(expected_fields)}"
            )
        return [
            {field: str(row.get(field) or "").strip() for field in expected_fields}
            for row in reader
        ]


def unique_rows(
    path: Path,
    expected_fields: tuple[str, ...],
    *,
    comments: bool = False,
) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    failures: list[str] = []
    for number, row in enumerate(
        rows(path, expected_fields, comments=comments),
        start=2,
    ):
        location = row["location"]
        if not location:
            failures.append(f"{path.relative_to(ROOT)}:{number}: blank location")
        elif location in result:
            failures.append(
                f"{path.relative_to(ROOT)}:{number}: duplicate location {location}"
            )
        else:
            result[location] = row
    if failures:
        raise ValueError("\n".join(failures))
    return result


def roman_locations() -> list[str]:
    ownership = rows(OWNERSHIP, OWNERSHIP_FIELDS, comments=True)
    locations = [row["location"] for row in ownership if row["tag"] == "ROM"]
    if not locations or any(not location for location in locations):
        raise ValueError("ownership_resolved.csv contains invalid Roman ownership rows")
    duplicates = sorted(
        location for location, count in Counter(locations).items() if count > 1
    )
    if duplicates:
        raise ValueError("duplicate Roman ownership rows: " + ", ".join(duplicates))
    return sorted(locations)


def validate_identity_sources(
    overrides: dict[str, dict[str, str]],
) -> tuple[set[str], list[str]]:
    place_ids: set[str] = set()
    violations: list[str] = []
    for location, row in sorted(overrides.items()):
        match = ROMAN_SOURCE_RE.fullmatch(row["source"])
        if not match:
            violations.append(
                f"{location}: malformed Roman identity source {row['source']!r}"
            )
            continue
        place_id = match.group(1)
        if place_id in place_ids:
            violations.append(f"{location}: reused Roman Pleiades place {place_id}")
        place_ids.add(place_id)
        if row["confidence"] != "tier2":
            violations.append(
                f"{location}: Roman identity confidence must be tier2"
            )
    return place_ids, violations


def build() -> tuple[list[dict[str, str]], dict[str, object]]:
    roman = roman_locations()
    roman_set = set(roman)
    dynamic = unique_rows(DYNAMIC, DYNAMIC_FIELDS)
    overrides = unique_rows(ROMAN_OVERRIDES, ROMAN_OVERRIDE_FIELDS)
    exclusions = unique_rows(EXCLUSIONS, EXCLUSION_FIELDS)

    violations: list[str] = []
    place_ids, source_violations = validate_identity_sources(overrides)
    violations.extend(source_violations)
    if not set(overrides).issubset(roman_set):
        violations.append(
            "Roman identity ledger contains non-Roman locations: "
            + ", ".join(sorted(set(overrides) - roman_set))
        )
    if not set(exclusions).issubset(roman_set):
        violations.append(
            "Roman exclusion ledger contains non-Roman locations: "
            + ", ".join(sorted(set(exclusions) - roman_set))
        )
    excluded_place_ids = {row["pleiades_id"] for row in exclusions.values()}
    selected_excluded = sorted(place_ids & excluded_place_ids)
    if selected_excluded:
        violations.append(
            "excluded Pleiades places selected at runtime: "
            + ", ".join(selected_excluded)
        )

    output: list[dict[str, str]] = []
    for location in roman:
        entry = dynamic.get(location)
        if entry is None:
            output.append(
                {
                    "location": location,
                    "historical_name": "",
                    "layer": "vanilla_passthrough",
                    "anchor_kind": "",
                    "culture": "",
                    "source": "",
                    "confidence": "",
                    "decision": "vanilla_passthrough",
                    "audit_flags": "insufficient_secure_identity",
                    "note": (
                        "No sufficiently secure AD 1 identity; EU5 vanilla "
                        "localization retained."
                    ),
                }
            )
            continue

        anchor = entry["anchor_kind"]
        if anchor not in ALLOWED_ROMAN_ANCHORS:
            violations.append(
                f"{location}: forbidden Roman runtime layer {anchor or '<blank>'}"
            )
        if anchor == "roman_identity":
            layer = "reviewed_identity"
            if location not in overrides:
                violations.append(
                    f"{location}: runtime Roman identity missing from source ledger"
                )
        elif anchor == "curated":
            layer = "reviewed_direct"
        else:
            layer = "reviewed_capital"
        output.append(
            {
                "location": location,
                "historical_name": entry["historical_name"],
                "layer": layer,
                "anchor_kind": anchor,
                "culture": entry["culture"],
                "source": entry["source"],
                "confidence": entry["confidence"],
                "decision": "reviewed_override",
                "audit_flags": "",
                "note": entry["note"],
            }
        )

    runtime_identities = {
        row["location"] for row in output if row["anchor_kind"] == "roman_identity"
    }
    missing_runtime_identities = sorted(set(overrides) - runtime_identities)
    if missing_runtime_identities:
        violations.append(
            "reviewed Roman identities absent from runtime output: "
            + ", ".join(missing_runtime_identities)
        )

    excluded_overridden = sorted(
        location
        for location in exclusions
        if next(row for row in output if row["location"] == location)["decision"]
        != "vanilla_passthrough"
    )
    if excluded_overridden:
        violations.append(
            "excluded Roman locations still overridden: "
            + ", ".join(excluded_overridden)
        )

    decisions = Counter(row["decision"] for row in output)
    layers = Counter(row["layer"] for row in output)
    confidence = Counter(row["confidence"] for row in output if row["confidence"])
    summary: dict[str, object] = {
        "roman_locations": len(output),
        "reviewed_overrides": decisions["reviewed_override"],
        "vanilla_passthrough": decisions["vanilla_passthrough"],
        "layers": dict(sorted(layers.items())),
        "confidence": dict(sorted(confidence.items())),
        "decisions": dict(sorted(decisions.items())),
        "exclusion_rules": len(exclusions),
        "excluded_passthrough": len(exclusions) - len(excluded_overridden),
        "violations": sorted(set(violations)),
    }
    if len(output) != len(roman_set):
        summary["violations"].append(
            f"audit row count {len(output)} does not match Roman ownership {len(roman_set)}"
        )
    return output, summary


def render_csv(values: list[dict[str, str]]) -> str:
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(values)
    return stream.getvalue()


def outputs() -> tuple[str, str, dict[str, object]]:
    values, summary = build()
    audit_csv = render_csv(values)
    summary_json = json.dumps(
        summary,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    return audit_csv, summary_json, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        audit_csv, summary_json, summary = outputs()
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f"m4_roman_location_name_audit: FAIL\n  - {exc}")
        return 1

    violations = list(summary["violations"])
    if violations:
        print("m4_roman_location_name_audit: FAIL")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    if args.write:
        OUTPUT.write_text(audit_csv, encoding="utf-8-sig", newline="")
        SUMMARY.write_text(summary_json, encoding="utf-8", newline="")
        print(
            "m4_roman_location_name_audit: wrote "
            f"{OUTPUT.relative_to(ROOT)} and {SUMMARY.relative_to(ROOT)}"
        )
        return 0

    failures: list[str] = []
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != audit_csv:
        failures.append(f"stale or missing {OUTPUT.relative_to(ROOT)}")
    if not SUMMARY.is_file() or SUMMARY.read_text(encoding="utf-8") != summary_json:
        failures.append(f"stale or missing {SUMMARY.relative_to(ROOT)}")
    if failures:
        print("m4_roman_location_name_audit: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        "m4_roman_location_name_audit: PASS "
        f"({summary['reviewed_overrides']} reviewed overrides + "
        f"{summary['vanilla_passthrough']} vanilla pass-throughs = "
        f"{summary['roman_locations']} Roman locations)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

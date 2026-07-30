#!/usr/bin/env python3
"""Audit ANTIQVITAS cultural affinity and plural-imperial integration paths."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from generate_country_definitions import (
    IntegrationProfile,
    load_engine_tags,
    load_integration_profiles,
)
from generate_m4_definitions import cultural_opinions
from popcheck import parse_records


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
SYMBOLS = ROOT / "docs/m4/definition_symbols.json"
POP_FILE = ROOT / "main_menu/setup/start/06_pops.txt"
START_COUNTRIES = ROOT / "main_menu/setup/start/10_countries.txt"
COUNTRY_DEFINITIONS = ROOT / "in_game/setup/countries/antq_00_world.txt"
CULTURE_DEFINITIONS = ROOT / "in_game/common/cultures/antq_m4_cultures.txt"
LOCAL_PATHS = ROOT / "config/local_paths.json"
AUDIT_CSV = ROOT / "docs/m4/cultural_integration_audit.csv"
AUDIT_MD = ROOT / "docs/m4/CULTURAL_INTEGRATION_AUDIT.md"

CONTROLLED_PAIRS = (
    (
        "close",
        "antq_zhongyuan_han",
        "antq_qin_han",
        "kindred",
        "shared commandery core",
    ),
    (
        "related",
        "antq_latin",
        "antq_greek_koine",
        "positive",
        "Roman public-culture bridge",
    ),
    (
        "distant",
        "antq_latin",
        "antq_zhongyuan_han",
        "neutral",
        "no invented transcontinental affinity",
    ),
    (
        "hostile",
        "antq_zhongyuan_han",
        "antq_xiongnu",
        "negative",
        "bounded opening court rivalry",
    ),
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def owners() -> dict[str, str]:
    result: dict[str, str] = {}
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(line for line in handle if not line.startswith("#")):
            location = row["location"].strip()
            tag = row["tag"].strip()
            if location in result:
                raise ValueError(f"duplicate owner for {location}")
            result[location] = tag
    return result


def resident_cultures() -> dict[str, set[str]]:
    location_owners = owners()
    result: defaultdict[str, set[str]] = defaultdict(set)
    for record in parse_records(POP_FILE):
        location = record.get("location", "")
        culture = record.get("culture", "")
        if location in location_owners and culture:
            result[location_owners[location]].add(culture)
    return dict(result)


def expected_status(
    profile: IntegrationProfile,
    resident: set[str],
) -> tuple[set[str], set[str]]:
    accepted = set(profile.accepted_cultures)
    if profile.tolerated_mode == "resident_remainder":
        tolerated = (
            resident | set(profile.tolerated_cultures)
        ) - accepted - {profile.primary_culture}
    elif profile.tolerated_mode == "explicit":
        tolerated = set(profile.tolerated_cultures)
    else:
        tolerated = set()
    return accepted, tolerated


def parse_start_status() -> dict[str, dict[str, set[str]]]:
    result: dict[str, dict[str, set[str]]] = {}
    current = ""
    tag_line = re.compile(r"^\t\t([A-Z0-9]{3}) = \{")
    list_line = re.compile(
        r"^\t\t\t(accepted_cultures|tolerated_cultures) = \{\s*(.*?)\s*\}$"
    )
    for line in START_COUNTRIES.read_text(
        encoding="utf-8-sig", errors="replace"
    ).splitlines():
        match = tag_line.match(line)
        if match:
            current = match.group(1)
            result[current] = {"accepted": set(), "tolerated": set()}
            continue
        match = list_line.match(line)
        if current and match:
            key = "accepted" if match.group(1) == "accepted_cultures" else "tolerated"
            result[current][key] = set(match.group(2).split())
    return result


def parse_country_primaries() -> dict[str, str]:
    result: dict[str, str] = {}
    current = ""
    block = re.compile(r"^([A-Z0-9]{3}) = \{")
    primary = re.compile(r"^\tculture_definition = (\S+)")
    for line in COUNTRY_DEFINITIONS.read_text(
        encoding="utf-8-sig", errors="replace"
    ).splitlines():
        match = block.match(line)
        if match:
            current = match.group(1)
            continue
        match = primary.match(line)
        if current and match:
            result[current] = match.group(1)
    return result


def parse_cultural_opinions() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    current = ""
    in_opinions = False
    culture = re.compile(r"^(antq_\S+) = \{")
    opinion = re.compile(
        r"^\t\t(antq_\S+) = (enemy|negative|neutral|positive|kindred)$"
    )
    for line in CULTURE_DEFINITIONS.read_text(
        encoding="utf-8-sig", errors="replace"
    ).splitlines():
        match = culture.match(line)
        if match:
            current = match.group(1)
            result[current] = {}
            in_opinions = False
            continue
        if line == "\topinions = {":
            in_opinions = True
            continue
        if in_opinions and line == "\t}":
            in_opinions = False
            continue
        match = opinion.match(line)
        if current and in_opinions and match:
            result[current][match.group(1)] = match.group(2)
    return result


def engine_contracts() -> tuple[list[str], list[str]]:
    failures: list[str] = []
    notes: list[str] = []
    config = json.loads(LOCAL_PATHS.read_text(encoding="utf-8"))
    game = Path(config["game_dir"]) / "game/in_game"
    contracts = (
        (
            game / "common/cabinet_actions/promote_culture.txt",
            (
                "cultural_view = {",
                "reverse_cultural_view = {",
                "value > neutral",
                "local_pop_assimilation_speed = 0.04",
            ),
            "promotion requires mutual positive affinity and applies +0.04 local assimilation",
        ),
        (
            game / "common/estates/00_default.txt",
            ("has_accepted_culture", "has_tolerated_culture"),
            "estates distinguish primary, accepted, and tolerated cultures",
        ),
        (
            game / "common/subject_types/dominion.txt",
            ("reverse_cultural_view", "value = kindred"),
            "dominion integration queries kindred affinity",
        ),
        (
            game / "common/rebel_demands/999_default_rebel_demands.txt",
            ("has_accepted_culture", "add_accepted_culture"),
            "nationalist concessions promote the demanding culture",
        ),
    )
    for path, needles, note in contracts:
        if not path.is_file():
            failures.append(f"missing installed engine contract {path}")
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        missing = [needle for needle in needles if needle not in text]
        if missing:
            failures.append(
                f"{path.name}: missing engine contract {', '.join(missing)}"
            )
        else:
            notes.append(note)
    return failures, notes


def audit_rows() -> tuple[list[dict[str, str]], list[str], list[str]]:
    failures: list[str] = []
    profiles = load_integration_profiles()
    roster_tags = {row["tag"] for row in rows(ROSTER)}
    cultures = set(json.loads(SYMBOLS.read_text(encoding="utf-8"))["cultures"])
    residents = resident_cultures()
    engine_tags = load_engine_tags()
    start = parse_start_status()
    primaries = parse_country_primaries()
    output: list[dict[str, str]] = []
    for tag, profile in profiles.items():
        if tag not in roster_tags:
            failures.append(f"{tag}: integration profile is absent from the roster")
        referenced = (
            {profile.primary_culture}
            | set(profile.accepted_cultures)
            | set(profile.tolerated_cultures)
        )
        unknown = sorted(referenced - cultures)
        if unknown:
            failures.append(f"{tag}: unknown cultures {', '.join(unknown)}")
        if len(profile.accepted_cultures) != len(set(profile.accepted_cultures)):
            failures.append(f"{tag}: duplicate accepted culture")
        if len(profile.tolerated_cultures) != len(set(profile.tolerated_cultures)):
            failures.append(f"{tag}: duplicate tolerated culture")
        resident = residents.get(tag, set())
        accepted, tolerated = expected_status(profile, resident)
        overlap = accepted & tolerated
        if profile.primary_culture in accepted | tolerated:
            failures.append(f"{tag}: primary culture repeats in a status list")
        if overlap:
            failures.append(f"{tag}: accepted/tolerated overlap {sorted(overlap)}")
        unrecognized = resident - accepted - tolerated - {profile.primary_culture}
        if unrecognized:
            failures.append(
                f"{tag}: resident cultures lack a status: {', '.join(sorted(unrecognized))}"
            )
        engine_tag = engine_tags[tag]
        found = start.get(engine_tag)
        if found is None:
            failures.append(f"{tag}/{engine_tag}: missing generated start country")
        else:
            if found["accepted"] != accepted:
                failures.append(
                    f"{tag}: accepted drift; expected {sorted(accepted)}, "
                    f"found {sorted(found['accepted'])}"
                )
            if found["tolerated"] != tolerated:
                failures.append(
                    f"{tag}: tolerated drift; expected {sorted(tolerated)}, "
                    f"found {sorted(found['tolerated'])}"
                )
        if primaries.get(engine_tag) != profile.primary_culture:
            failures.append(
                f"{tag}: primary drift; expected {profile.primary_culture}, "
                f"found {primaries.get(engine_tag, 'missing')}"
            )
        future = (accepted | tolerated) - resident
        output.append(
            {
                "design_tag": tag,
                "engine_tag": engine_tag,
                "path": profile.path,
                "primary_culture": profile.primary_culture,
                "resident_cultures": "|".join(sorted(resident)),
                "accepted_cultures": "|".join(sorted(accepted)),
                "tolerated_cultures": "|".join(sorted(tolerated)),
                "future_path_cultures": "|".join(sorted(future)),
                "source": profile.source,
                "confidence": profile.confidence,
            }
        )
    return output, failures, sorted(cultures)


def view_audit(cultures: set[str]) -> tuple[list[str], dict[str, dict[str, str]]]:
    failures: list[str] = []
    expected = cultural_opinions(cultures)
    actual = parse_cultural_opinions()
    for culture in cultures:
        if actual.get(culture, {}) != expected.get(culture, {}):
            failures.append(f"{culture}: generated cultural opinions drifted")
    for source, targets in expected.items():
        for target, view in targets.items():
            if expected.get(target, {}).get(source) != view:
                failures.append(
                    f"{source}/{target}: non-reciprocal {view} relationship"
                )
    for label, source, target, expected_view, _note in CONTROLLED_PAIRS:
        actual_view = expected.get(source, {}).get(target, "neutral")
        if actual_view != expected_view:
            failures.append(
                f"{label} pair {source}/{target}: expected {expected_view}, "
                f"found {actual_view}"
            )
    return failures, expected


def csv_payload(audit: list[dict[str, str]]) -> str:
    fields = (
        "design_tag",
        "engine_tag",
        "path",
        "primary_culture",
        "resident_cultures",
        "accepted_cultures",
        "tolerated_cultures",
        "future_path_cultures",
        "source",
        "confidence",
    )
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(audit)
    return stream.getvalue()


def md_payload(
    audit: list[dict[str, str]],
    opinions: dict[str, dict[str, str]],
    contract_notes: list[str],
) -> str:
    lines = [
        "# Cultural Integration Audit",
        "",
        "Generated by `tools/s2_cultural_integration.py`; local engine build "
        + json.loads(LOCAL_PATHS.read_text(encoding="utf-8"))["game_build_id"]
        + ".",
        "",
        "| Tag | Path | Residents | Accepted | Tolerated | Future paths |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in audit:
        count = lambda field: len([item for item in row[field].split("|") if item])
        lines.append(
            f"| {row['design_tag']} | {row['path']} | "
            f"{count('resident_cultures')} | {count('accepted_cultures')} | "
            f"{count('tolerated_cultures')} | {count('future_path_cultures')} |"
        )
    lines.extend(
        (
            "",
            "## Controlled affinity pairs",
            "",
            "| Class | Source | Target | View | Boundary |",
            "|---|---|---|---|---|",
        )
    )
    for label, source, target, _expected, note in CONTROLLED_PAIRS:
        view = opinions.get(source, {}).get(target, "neutral")
        lines.append(f"| {label} | {source} | {target} | {view} | {note} |")
    lines.extend(("", "## Locally verified engine effects", ""))
    lines.extend(f"- {note}." for note in contract_notes)
    lines.extend(
        (
            "",
            "Primary, accepted, tolerated, and unrecognized cultures are therefore "
            "not interchangeable: they feed estate satisfaction, promotion access, "
            "assimilation, subject integration, and nationalist concessions through "
            "the installed engine contracts above.",
            "",
        )
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        audit, failures, culture_list = audit_rows()
        view_failures, opinions = view_audit(set(culture_list))
        contract_failures, contract_notes = engine_contracts()
        failures.extend(view_failures)
        failures.extend(contract_failures)
        expected_csv = csv_payload(audit)
        expected_md = md_payload(audit, opinions, contract_notes)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_cultural_integration: FAIL\n  - {exc}", file=sys.stderr)
        return 1
    if args.write:
        AUDIT_CSV.write_text(expected_csv, encoding="utf-8", newline="\n")
        AUDIT_MD.write_text(expected_md, encoding="utf-8", newline="\n")
        print(
            f"s2_cultural_integration: wrote {len(audit)} paths and "
            f"{sum(len(targets) for targets in opinions.values())} directed views"
        )
    else:
        for path, expected in ((AUDIT_CSV, expected_csv), (AUDIT_MD, expected_md)):
            if not path.is_file():
                failures.append(f"missing generated audit {path.relative_to(ROOT)}")
            elif path.read_text(encoding="utf-8-sig") != expected:
                failures.append(f"stale generated audit {path.relative_to(ROOT)}")
    if failures:
        print("s2_cultural_integration: FAIL", file=sys.stderr)
        for failure in sorted(set(failures)):
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print(
        "s2_cultural_integration: PASS "
        f"({len(audit)} paths; "
        f"{sum(len(targets) for targets in opinions.values())} directed views; "
        "4 controlled affinity classes)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

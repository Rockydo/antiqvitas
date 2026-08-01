#!/usr/bin/env python3
"""Audit opening visibility for the complete reusable-building union."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from pathlib import Path

from m12_system_quarantine import TOP_LEVEL_KEY, brace_delta, structural_code
from m5_regional_buildings import (
    FAMILY_CULTURE_GROUP_GATES,
    FAMILY_EXACT_TAG_GATES,
    ROMAN_ECONOMY_FAMILIES,
    engine_tags,
    load,
)
from m8_knowledge import building_content_profiles, research_profile_maps


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
REPORT = ROOT / "docs/m5/building_visibility.csv"
SCRIPT = ROOT / "in_game/common/building_types/00_antiquitas_regional_buildings.txt"
TAG_RE = re.compile(r"\bhas_or_had_tag\s*=\s*([A-Z0-9]{3})")
GROUP_RE = re.compile(
    r"\bhas_culture_group\s*=\s*culture_group:([a-z][a-z0-9_]*)"
)
ROMAN_INSTITUTION_RE = re.compile(
    r"\bhas_embraced_institution\s*=\s*"
    r"institution:antq_roman_law_engineering\b"
)
COUNTRY_POTENTIAL_RE = re.compile(r"\bcountry_potential\s*=")
ROMAN_GROUPS = frozenset({
    "antq_italic_group", "antq_iberian_group", "antq_balkan_group",
})
FOREIGN_LABEL_TOKENS = (
    "fullonica", "scriptorium", "amphora", "garum", "monetal", "tegula",
    "hypocaust", "macellum", "mensores", "caravanserai", "cordwainer",
    "chandlery", "tesserae", "materia medica", "ironmongery",
)


def rows(path: Path, *, comments: bool = False) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        lines = handle.readlines()
    if comments:
        lines = [line for line in lines if not line.startswith("#")]
    return list(csv.DictReader(lines))


def script_blocks(path: Path) -> dict[str, str]:
    blocks: dict[str, str] = {}
    key = ""
    captured: list[str] = []
    depth = 0
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        code = structural_code(line)
        match = TOP_LEVEL_KEY.match(code) if depth == 0 else None
        if match:
            key = match.group("key")
            captured = [line]
        elif key:
            captured.append(line)
        depth += brace_delta(line)
        if key and depth == 0:
            if key in blocks:
                raise ValueError(f"{path.relative_to(ROOT)} repeats {key}")
            blocks[key] = "\n".join(captured)
            key = ""
            captured = []
    if depth or key:
        raise ValueError(f"{path.relative_to(ROOT)} has an unterminated block")
    return blocks


def expected_report() -> tuple[str, list[str], dict[str, int]]:
    failures: list[str] = []
    families, seeds = load()
    family_rows = {row["key"]: row for row in families}
    family_keys = set(family_rows)
    blocks = script_blocks(SCRIPT)
    tags = engine_tags()
    if len(family_keys) != 200:
        failures.append(
            f"regional reusable-building union is {len(family_keys)}, expected 200"
        )
    if set(blocks) != family_keys:
        failures.append("rendered regional-building union differs from its ledger")

    gated = (
        set(FAMILY_EXACT_TAG_GATES)
        | set(FAMILY_CULTURE_GROUP_GATES)
        | set(ROMAN_ECONOMY_FAMILIES)
    )
    for key, row in family_rows.items():
        block = blocks.get(key, "")
        rendered_tags = frozenset(TAG_RE.findall(block))
        rendered_groups = frozenset(GROUP_RE.findall(block))
        has_institution = bool(ROMAN_INSTITUTION_RE.search(block))
        has_gate = bool(COUNTRY_POTENTIAL_RE.search(block))
        if key in FAMILY_EXACT_TAG_GATES:
            expected_tags = frozenset(
                tags[tag] for tag in FAMILY_EXACT_TAG_GATES[key]
            )
            if (
                rendered_tags != expected_tags
                or rendered_groups
                or has_institution
                or not has_gate
            ):
                failures.append(f"exact country gate drift: {key}")
        elif key in FAMILY_CULTURE_GROUP_GATES:
            expected_groups = frozenset(FAMILY_CULTURE_GROUP_GATES[key])
            if (
                rendered_groups != expected_groups
                or rendered_tags
                or has_institution
                or not has_gate
            ):
                failures.append(f"culture-group gate drift: {key}")
        elif key in ROMAN_ECONOMY_FAMILIES:
            if (
                rendered_groups != ROMAN_GROUPS
                or rendered_tags
                or not has_institution
                or not has_gate
            ):
                failures.append(f"Roman adoption gate drift: {key}")
        elif has_gate or rendered_tags or rendered_groups or has_institution:
            failures.append(f"neutral reusable family gained a regional gate: {key}")

        if key not in gated:
            label = row["name"].casefold()
            bad = [token for token in FOREIGN_LABEL_TOKENS if token in label]
            if bad:
                failures.append(
                    f"ungated family retains foreign institutional label {key}: "
                    f"{','.join(bad)}"
                )

    roster = {row["tag"]: row for row in rows(ROSTER)}
    owners = {row["location"]: row["tag"] for row in rows(OWNERSHIP, comments=True)}
    tag_profiles, tag_cultures, culture_groups = research_profile_maps()
    tag_groups = {
        tag: culture_groups.get(tag_cultures.get(tag, ""), "")
        for tag in roster
    }
    for seed in seeds:
        family = seed["family"]
        tag = owners.get(seed["location"], "")
        if not tag:
            failures.append(f"building seed has no AD 1 owner: {seed['key']}")
            continue
        if (
            family in FAMILY_EXACT_TAG_GATES
            and tag not in FAMILY_EXACT_TAG_GATES[family]
        ):
            failures.append(
                f"exact family seeded under unauthorized {tag}: {family}"
            )
        if (
            family in FAMILY_CULTURE_GROUP_GATES
            and tag_groups[tag] not in FAMILY_CULTURE_GROUP_GATES[family]
        ):
            failures.append(
                f"culture family seeded under unauthorized {tag}: {family}"
            )
        if (
            family in ROMAN_ECONOMY_FAMILIES
            and roster[tag]["region"] != "Rome"
        ):
            failures.append(f"Roman family seeded outside Rome: {family}")

    profiles_by_building = building_content_profiles(tag_profiles)
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow((
        "design_tag", "engine_tag", "name", "culture", "culture_group",
        "research_profiles", "visible_regional_count", "neutral_count",
        "culture_gated_count", "exact_gated_count", "roman_count",
        "visible_regional_buildings",
    ))
    visible_counts: list[int] = []
    exact_counts: list[int] = []
    roman_counts: list[int] = []
    for tag in sorted(roster):
        profiles = set(tag_profiles[tag])
        group = tag_groups[tag]
        visible: list[str] = []
        neutral: list[str] = []
        culture_gated: list[str] = []
        exact: list[str] = []
        roman: list[str] = []
        for key in sorted(family_keys):
            building_profiles = profiles_by_building[key]
            if "shared" not in building_profiles and not (
                profiles & building_profiles
            ):
                continue
            if key in FAMILY_EXACT_TAG_GATES:
                if tag not in FAMILY_EXACT_TAG_GATES[key]:
                    continue
                exact.append(key)
            elif key in FAMILY_CULTURE_GROUP_GATES:
                if group not in FAMILY_CULTURE_GROUP_GATES[key]:
                    continue
                culture_gated.append(key)
            elif key in ROMAN_ECONOMY_FAMILIES:
                # Institution-based adoption is a later dynamic path. This
                # report proves only unadopted opening visibility.
                if group not in ROMAN_GROUPS:
                    continue
                roman.append(key)
            else:
                neutral.append(key)
            visible.append(key)
        if set(exact) - {
            key for key, allowed in FAMILY_EXACT_TAG_GATES.items()
            if tag in allowed
        }:
            failures.append(f"{tag} sees a foreign exact-country building")
        if tag == "SUE" and (exact or roman):
            failures.append("Suebi opening building cards include named foreign families")
        visible_counts.append(len(visible))
        exact_counts.append(len(exact))
        roman_counts.append(len(roman))
        writer.writerow((
            tag, tags[tag], roster[tag]["name"], tag_cultures[tag], group,
            "|".join(sorted(profiles)), len(visible), len(neutral),
            len(culture_gated), len(exact), len(roman), "|".join(visible),
        ))

    if len(visible_counts) != 463:
        failures.append(
            f"building visibility report has {len(visible_counts)} tags, expected 463"
        )
    metrics = {
        "countries": len(visible_counts),
        "families": len(family_keys),
        "exact": len(FAMILY_EXACT_TAG_GATES),
        "culture": len(FAMILY_CULTURE_GROUP_GATES),
        "roman": len(ROMAN_ECONOMY_FAMILIES),
        "minimum": min(visible_counts, default=0),
        "maximum": max(visible_counts, default=0),
        "exact_maximum": max(exact_counts, default=0),
        "roman_maximum": max(roman_counts, default=0),
    }
    return output.getvalue(), failures, metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        rendered, failures, metrics = expected_report()
        if args.write:
            REPORT.parent.mkdir(parents=True, exist_ok=True)
            REPORT.write_text(rendered, encoding="utf-8", newline="\n")
        if not REPORT.is_file():
            failures.append(f"missing generated report: {REPORT.relative_to(ROOT)}")
        elif REPORT.read_text(encoding="utf-8-sig") != rendered:
            failures.append(f"stale generated report: {REPORT.relative_to(ROOT)}")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        failures = [str(exc)]
        metrics = {}
    if failures:
        print("s3_building_isolation: FAIL")
        for failure in sorted(set(failures)):
            print(f"  - {failure}")
        return 1
    print(
        "s3_building_isolation: PASS "
        f"({metrics['countries']} countries; {metrics['families']} families; "
        f"{metrics['exact']} exact, {metrics['culture']} culture, and "
        f"{metrics['roman']} Roman-adoption gates; visible "
        f"{metrics['minimum']}-{metrics['maximum']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

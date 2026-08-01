#!/usr/bin/env python3
"""Audit the complete ancient estate-privilege visibility union."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from pathlib import Path

from m12_system_quarantine import MARKER, TOP_LEVEL_KEY, brace_delta, structural_code
from m6_power import estate_privileges, load_power_data, pipe_values
from s2_estate_orders import (
    country_item_key,
    country_privileges,
    item_key,
    privileges_by_profile,
    profiles,
)


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
REPORT = ROOT / "docs/m6/privilege_visibility.csv"
SCRIPT = ROOT / "in_game/common/estate_privileges/00_antiquitas_m6_core.txt"
ADVANCE_TREE = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
PRIVILEGE_DIR = ROOT / "in_game/common/estate_privileges"
MANIFEST = ROOT / "docs/m12/system_quarantine_manifest.json"
REFORM_RE = re.compile(r"\bhas_reform\s*=\s*government_reform:([a-z][a-z0-9_]*)")
TAG_RE = re.compile(r"\bhas_or_had_tag\s*=\s*([A-Z0-9]{3})")
ALWAYS_NO_RE = re.compile(r"\balways\s*=\s*no\b")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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
                raise ValueError(f"{path.relative_to(ROOT)} repeats top-level key {key}")
            blocks[key] = "\n".join(captured)
            key = ""
            captured = []
    if depth or key:
        raise ValueError(f"{path.relative_to(ROOT)} has an unterminated top-level block")
    return blocks


def expected_profile_contracts() -> tuple[
    dict[str, str], dict[str, frozenset[str]], dict[str, str]
]:
    profile_by_reform: dict[str, str] = {}
    profile_reforms: dict[str, frozenset[str]] = {}
    privilege_profiles: dict[str, str] = {}
    grouped = privileges_by_profile()
    for profile in profiles():
        slug = str(profile["slug"])
        reforms = frozenset(str(value) for value in profile["reforms"])
        profile_reforms[slug] = reforms
        for reform in reforms:
            if reform in profile_by_reform:
                raise ValueError(f"estate reform belongs to two profiles: {reform}")
            profile_by_reform[reform] = slug
        for privilege in grouped[slug]:
            privilege_profiles[item_key(profile, privilege)] = slug
    return profile_by_reform, profile_reforms, privilege_profiles


def expected_report() -> tuple[str, list[str], dict[str, int]]:
    failures: list[str] = []
    data = load_power_data()
    privilege_by_key = {row["key"]: row for row in data.privileges}
    profile_by_reform, profile_reforms, privilege_profiles = expected_profile_contracts()
    country_contracts = {
        country_item_key(row): row for row in country_privileges()
    }

    if len(privilege_by_key) != 376:
        failures.append(f"custom privilege union is {len(privilege_by_key)}, expected 376")
    if len(privilege_profiles) != 270:
        failures.append(f"profile privilege union is {len(privilege_profiles)}, expected 270")
    if len(country_contracts) != 60:
        failures.append(f"country privilege union is {len(country_contracts)}, expected 60")

    for key, slug in privilege_profiles.items():
        row = privilege_by_key.get(key)
        if row is None:
            failures.append(f"profile privilege missing from power data: {key}")
            continue
        reforms = frozenset(pipe_values(
            row["potential_reforms"], f"{key} potential reforms"
        )) if row["potential_reforms"] else frozenset()
        tags = frozenset(pipe_values(
            row["potential_tags"], f"{key} potential tags"
        )) if row["potential_tags"] else frozenset()
        if reforms != profile_reforms[slug] or tags:
            failures.append(f"profile privilege gate drift: {key}")

    advance_text = ADVANCE_TREE.read_text(encoding="utf-8-sig")
    profile_unlocks = sorted(
        key for key in privilege_profiles
        if re.search(
            rf"^\s*unlock_estate_privilege\s*=\s*{re.escape(key)}\s*$",
            advance_text,
            re.MULTILINE,
        )
    )
    if profile_unlocks:
        failures.append(
            "baseline profile privileges are incorrectly research-locked: "
            + ",".join(profile_unlocks)
        )

    for key, contract in country_contracts.items():
        row = privilege_by_key.get(key)
        if row is None:
            failures.append(f"country privilege missing from power data: {key}")
            continue
        reforms = frozenset(pipe_values(
            row["potential_reforms"], f"{key} potential reforms"
        )) if row["potential_reforms"] else frozenset()
        tags = frozenset(pipe_values(
            row["potential_tags"], f"{key} potential tags"
        )) if row["potential_tags"] else frozenset()
        if reforms or tags != {contract["engine_tag"]}:
            failures.append(f"country privilege gate drift: {key}")

    core_keys = set(privilege_by_key) - set(privilege_profiles) - set(country_contracts)
    if len(core_keys) != 46:
        failures.append(f"core privilege union is {len(core_keys)}, expected 46")
    for key in sorted(core_keys):
        row = privilege_by_key[key]
        if row["potential_reforms"] or not row["potential_tags"]:
            failures.append(f"core privilege must use exact country gates only: {key}")

    rendered_blocks = script_blocks(SCRIPT)
    if set(rendered_blocks) != set(privilege_by_key):
        missing = sorted(set(privilege_by_key) - set(rendered_blocks))
        extra = sorted(set(rendered_blocks) - set(privilege_by_key))
        failures.append(
            "rendered custom privilege union differs "
            f"(missing={','.join(missing)}; extra={','.join(extra)})"
        )
    for key, row in privilege_by_key.items():
        block = rendered_blocks.get(key, "")
        rendered_reforms = frozenset(REFORM_RE.findall(block))
        rendered_tags = frozenset(TAG_RE.findall(block))
        declared_reforms = frozenset(pipe_values(
            row["potential_reforms"], f"{key} potential reforms"
        )) if row["potential_reforms"] else frozenset()
        declared_tags = frozenset(pipe_values(
            row["potential_tags"], f"{key} potential tags"
        )) if row["potential_tags"] else frozenset()
        if rendered_reforms != declared_reforms or rendered_tags != declared_tags:
            failures.append(f"rendered privilege widens or loses declared gates: {key}")

    legacy_count = 0
    for path in sorted(PRIVILEGE_DIR.glob("*.txt")):
        if path == SCRIPT:
            continue
        for key, block in script_blocks(path).items():
            legacy_count += 1
            if MARKER not in block or not ALWAYS_NO_RE.search(block):
                failures.append(
                    f"installed privilege is not permanently quarantined: "
                    f"{path.name}:{key}"
                )
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_count = int(manifest["totals"]["estate_privileges"])
    if legacy_count != manifest_count or legacy_count != 261:
        failures.append(
            f"installed privilege union is {legacy_count}; manifest={manifest_count}; expected=261"
        )

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow((
        "design_tag", "engine_tag", "kind", "government_source", "reform",
        "estate_profile", "visible_privilege_count", "profile_privilege_count",
        "exact_privilege_count", "visible_privileges",
    ))
    government_rows = data.governments
    visible_counts: list[int] = []
    profile_counts: list[int] = []
    exact_counts: list[int] = []
    for polity in rows(ROSTER):
        design_tag = polity["tag"]
        engine_tag = data.tags[design_tag]
        if design_tag in government_rows:
            reform = government_rows[design_tag]["reform"]
            government_source = "sourced"
        else:
            reform = (
                "antq_advanced_chiefdom"
                if polity["kind"] == "sop"
                else "antq_regional_kingship"
            )
            government_source = "fallback"
        profile = profile_by_reform.get(reform, "")
        if not profile:
            failures.append(f"{design_tag} reform has no estate profile: {reform}")
        visible: list[str] = []
        visible_profile: list[str] = []
        visible_exact: list[str] = []
        for key, privilege in privilege_by_key.items():
            reforms = set(privilege["potential_reforms"].split("|")) if privilege["potential_reforms"] else set()
            tags = set(privilege["potential_tags"].split("|")) if privilege["potential_tags"] else set()
            if reform not in reforms and engine_tag not in tags:
                continue
            visible.append(key)
            if key in privilege_profiles:
                visible_profile.append(key)
                if privilege_profiles[key] != profile:
                    failures.append(
                        f"{design_tag} sees foreign {privilege_profiles[key]} privilege {key}"
                    )
            else:
                visible_exact.append(key)
        expected_profile = sorted(
            key for key, slug in privilege_profiles.items() if slug == profile
        )
        if sorted(visible_profile) != expected_profile:
            failures.append(f"{design_tag} does not see exactly its six profile privileges")
        if len(visible_profile) != 6:
            failures.append(
                f"{design_tag} sees {len(visible_profile)} profile privileges, expected 6"
            )
        visible_counts.append(len(visible))
        profile_counts.append(len(visible_profile))
        exact_counts.append(len(visible_exact))
        writer.writerow((
            design_tag, engine_tag, polity["kind"], government_source, reform,
            profile, len(visible), len(visible_profile), len(visible_exact),
            "|".join(sorted(visible)),
        ))
    if len(visible_counts) != 463:
        failures.append(f"visibility report has {len(visible_counts)} countries, expected 463")
    metrics = {
        "countries": len(visible_counts),
        "custom": len(privilege_by_key),
        "legacy": legacy_count,
        "minimum": min(visible_counts, default=0),
        "maximum": max(visible_counts, default=0),
        "profile_minimum": min(profile_counts, default=0),
        "profile_maximum": max(profile_counts, default=0),
        "exact_maximum": max(exact_counts, default=0),
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
        if SCRIPT.read_text(encoding="utf-8-sig") != estate_privileges(load_power_data()):
            failures.append(f"stale generated script: {SCRIPT.relative_to(ROOT)}")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        failures = [str(exc)]
        metrics = {}
    if failures:
        print("s3_privilege_isolation: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s3_privilege_isolation: PASS "
        f"({metrics['countries']} countries; {metrics['custom']} custom and "
        f"{metrics['legacy']} quarantined installed privileges; visible "
        f"{metrics['minimum']}-{metrics['maximum']}; six profile grants each)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

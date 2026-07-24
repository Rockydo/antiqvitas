#!/usr/bin/env python3
"""Merge source-led PRO culture batches and regenerate their checked outputs.

The normal M4 generator depends on a local EU5 installation for compatibility
mirrors.  This focused generator changes only the culture catalogue, culture
atlas, country and regional culture profiles, culture-derived runtime files,
and the already-generated AD 1 pop mirror. It is safe in CI and deliberately
leaves religion/language compatibility files untouched.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Callable

from generate_country_definitions import (
    COUNTRIES as COUNTRY_DEFINITIONS,
    country_definitions,
    load_engine_tags,
    load_rows as load_polity_rows,
)
from generate_m4_definitions import (
    COMMON,
    CULTURES,
    LOCALIZATION_LANGUAGES,
    LOC_ROOT,
    M4_LANGUAGES,
    RELIGIONS,
    ROOT,
    Definition,
    brace_delta,
    definitions,
    languages,
    render_cultures,
    render_localization,
    render_named_colors,
)

CULTURE_REMAP = ROOT / "docs/culture_remap.csv"
TAG_PROFILES = ROOT / "docs/m4/tag_profiles.csv"
REGIONAL_PROFILES = ROOT / "docs/m4/regional_profiles.csv"
SYMBOLS = ROOT / "docs/m4/definition_symbols.json"
START_POPS = ROOT / "main_menu/setup/start/06_pops.txt"
README = ROOT / "README.md"
CULTURE_DOC = ROOT / "docs/cultures.md"
HIERARCHY = ROOT / "docs/vanilla_symbols/geography_hierarchy.json"
VALID_SYMBOLS = {
    "area": ROOT / "docs/vanilla_symbols/areas.json",
    "province": ROOT / "docs/vanilla_symbols/provinces.json",
    "location": ROOT / "docs/vanilla_symbols/locations.json",
    "region": ROOT / "docs/vanilla_symbols/regions.json",
}
CULTURE_BATCHES = (
    ROOT / "docs/m4/pro_master_plan_cultures.csv",
    ROOT / "docs/m4/pro_britain_ireland_cultures.csv",
)
REMAP_BATCHES = (
    ROOT / "docs/m4/pro_master_plan_remap.csv",
    ROOT / "docs/m4/pro_britain_ireland_remap.csv",
)
TAG_PROFILE_BATCHES = (
    ROOT / "docs/m4/pro_master_plan_tag_profiles.csv",
    ROOT / "docs/m4/pro_britain_ireland_tag_profiles.csv",
)
REGIONAL_PROFILE_BATCHES = (
    ROOT / "docs/m4/pro_master_plan_regional_profiles.csv",
    ROOT / "docs/m4/pro_britain_ireland_regional_profiles.csv",
)
CULTURE_FIELDS = ("key", "name", "group", "language", "source", "confidence", "note")
REMAP_FIELDS = ("selector_type", "selector", "culture", "source", "confidence", "note")
TAG_PROFILE_FIELDS = ("tag", "culture", "religion", "source", "confidence", "note")
REGIONAL_PROFILE_FIELDS = ("region", "culture", "religion", "source", "confidence", "note")
SPECIFICITY = {"region": 0, "area": 1, "province": 2, "location": 3}
# The installed AD 1 setup intentionally leaves the source-appropriate Na-Dene
# northwest outside all controlled locations. Keep the culture fully defined
# for scripted settlement and later atlas work rather than falsifying a pop
# placement in Puebloan, Inuit, or Pacific-coast cells.
DEFINITION_ONLY_CULTURES = {"antq_na_dene"}


def read_rows(path: Path, fields: tuple[str, ...], *, optional: bool = False) -> list[dict[str, str]]:
    if optional and not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path.relative_to(ROOT)} must use header {','.join(fields)}")
        rows = [{field: (row.get(field) or "").strip() for field in fields} for row in reader]
    for number, row in enumerate(rows, start=2):
        if any(not row[field] for field in fields):
            raise ValueError(f"{path.relative_to(ROOT)}:{number}: blank required field")
    return rows


def merge_rows(
    base_path: Path,
    batch_paths: tuple[Path, ...],
    fields: tuple[str, ...],
    identity: Callable[[dict[str, str]], object],
) -> tuple[list[dict[str, str]], set[str]]:
    rows = read_rows(base_path, fields)
    positions: dict[object, int] = {}
    for number, row in enumerate(rows, start=2):
        key = identity(row)
        if key in positions:
            raise ValueError(f"{base_path.relative_to(ROOT)}:{number}: duplicate identity {key!r}")
        positions[key] = len(positions)

    touched_cultures: set[str] = set()
    for batch_path in batch_paths:
        for row in read_rows(batch_path, fields, optional=True):
            key = identity(row)
            if fields == CULTURE_FIELDS:
                touched_cultures.add(row["key"])
            else:
                touched_cultures.add(row["culture"])
            if key in positions:
                rows[positions[key]] = row
            else:
                positions[key] = len(rows)
                rows.append(row)
    return rows, touched_cultures


def csv_text(rows: list[dict[str, str]], fields: tuple[str, ...]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def controlled_locations(text: str) -> set[str]:
    return set(re.findall(r"(?m)^\t([A-Za-z0-9_]+)\s*=\s*\{\s*$", text))


def leaf_locations(selector: str, hierarchy: dict[str, list[str]], trail: tuple[str, ...] = ()) -> set[str]:
    if selector in trail:
        raise ValueError(f"cyclic geography selector {' -> '.join((*trail, selector))}")
    children = hierarchy.get(selector)
    if not children:
        return {selector}
    leaves: set[str] = set()
    for child in children:
        if child == selector:
            leaves.add(child)
        else:
            leaves.update(leaf_locations(child, hierarchy, (*trail, selector)))
    return leaves


def resolve_remaps(
    rows: list[dict[str, str]],
    culture_keys: set[str],
    controlled: set[str],
) -> dict[str, dict[str, str]]:
    hierarchy: dict[str, list[str]] = json.loads(HIERARCHY.read_text(encoding="utf-8-sig"))
    valid = {
        kind: set(json.loads(path.read_text(encoding="utf-8-sig")))
        for kind, path in VALID_SYMBOLS.items()
    }
    seen: set[tuple[str, str]] = set()
    resolved: dict[str, dict[str, str]] = {}
    failures: list[str] = []
    for number, row in enumerate(rows, start=2):
        kind = row["selector_type"]
        selector = row["selector"]
        identity = (kind, selector)
        if identity in seen:
            failures.append(f"culture_remap.csv:{number}: duplicate selector {kind} {selector}")
            continue
        seen.add(identity)
        if kind not in valid:
            failures.append(f"culture_remap.csv:{number}: invalid selector type {kind}")
            continue
        if selector not in valid[kind]:
            failures.append(f"culture_remap.csv:{number}: unknown {kind} {selector}")
            continue
        if row["culture"] not in culture_keys:
            failures.append(f"culture_remap.csv:{number}: unknown culture {row['culture']}")
            continue
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"culture_remap.csv:{number}: invalid confidence {row['confidence']}")
            continue
        selected = leaf_locations(selector, hierarchy) & controlled
        if not selected:
            failures.append(f"culture_remap.csv:{number}: {kind} {selector} has no controlled AD 1 locations")
            continue
        for location in selected:
            existing = resolved.get(location)
            if existing:
                current_rank = SPECIFICITY[kind]
                existing_rank = SPECIFICITY[existing["selector_type"]]
                if current_rank == existing_rank:
                    failures.append(
                        f"culture_remap.csv:{number}: equally-specific overlap at {location} from "
                        f"{existing['selector_type']} {existing['selector']}"
                    )
                    continue
                if current_rank < existing_rank:
                    continue
            resolved[location] = row
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return resolved


def patch_start_pops(text: str, remaps: dict[str, dict[str, str]]) -> str:
    output: list[str] = []
    current_location: str | None = None
    depth = 0
    location_open = re.compile(r"^\t([A-Za-z0-9_]+)\s*=\s*\{\s*$")
    culture_token = re.compile(r"(\bculture\s*=\s*)([A-Za-z0-9_]+)")
    for line in text.splitlines(keepends=True):
        if current_location is None:
            match = location_open.match(line.rstrip("\r\n"))
            if match:
                current_location = match.group(1)
                depth = 0
        if current_location is not None and current_location in remaps and "define_pop" in line:
            desired = remaps[current_location]["culture"]
            line = culture_token.sub(lambda match: f"{match.group(1)}{desired}", line)
        if current_location is not None:
            depth += brace_delta(line)
            if depth <= 0:
                current_location = None
                depth = 0
        output.append(line)
    result = "".join(output)
    if result and not result.endswith("\n"):
        result += "\n"
    return result


def culture_doc(
    culture_count: int,
    selector_count: int,
    resolved_count: int,
    mapped_count: int,
) -> str:
    return f"""# Cultures and Languages

This is the checked M4 culture-tree foundation. The canonical definitions live
in `docs/m4/cultures.csv`; source-labelled geographic assignments live in
`docs/culture_remap.csv`. Generated runtime definitions, colors, localization,
symbols, and AD 1 pop culture fields must match those two ledgers.

The catalogue currently contains **{culture_count} culture definitions**. The
atlas uses **{selector_count} selectors** resolving **{resolved_count}
controlled locations** across **{mapped_count} explicitly mapped cultures**.
Selectors are implementation frames, not claims of homogeneous populations or
exact ancient frontiers.

`culture_remap.csv` accepts only installed area, province, location, or region
selectors. Precedence is location > province > area > region. Unknown symbols,
empty selectors, duplicate selectors, and equally specific overlaps fail the
generator rather than being silently resolved.

The language column records the closest engine-valid adapter. It is not a
historical language claim where a culture note explicitly identifies a
technical fallback.

## Completion ledgers

- `docs/m4/pro_master_plan_cultures.csv`, its remap ledger, and its profile
  ledgers separate cultures that the master plan named but the earlier atlas
  collapsed into broader frames.
- `docs/m4/pro_britain_ireland_cultures.csv`, its remap ledger, and its tag
  profiles provide the detailed Britain and Ireland pass.
- `tools/generate_pro_culture_expansion.py --check` rejects drift between those
  source ledgers and generated output.
"""


def expected_outputs() -> tuple[dict[Path, tuple[str, str]], dict[str, object]]:
    culture_rows, culture_batch_keys = merge_rows(
        CULTURES, CULTURE_BATCHES, CULTURE_FIELDS, lambda row: row["key"]
    )
    remap_rows, remap_batch_keys = merge_rows(
        CULTURE_REMAP,
        REMAP_BATCHES,
        REMAP_FIELDS,
        lambda row: (row["selector_type"], row["selector"]),
    )
    tag_profile_rows, tag_profile_batch_cultures = merge_rows(
        TAG_PROFILES, TAG_PROFILE_BATCHES, TAG_PROFILE_FIELDS, lambda row: row["tag"]
    )
    regional_profile_rows, regional_profile_batch_cultures = merge_rows(
        REGIONAL_PROFILES,
        REGIONAL_PROFILE_BATCHES,
        REGIONAL_PROFILE_FIELDS,
        lambda row: row["region"],
    )
    language_rows = languages()
    language_groups = {row.group for row in language_rows}
    language_keys = {row.fallback for row in language_rows} | {row.key for row in language_rows}
    culture_keys = [row["key"] for row in culture_rows]
    if len(culture_keys) != len(set(culture_keys)):
        raise ValueError("merged culture catalogue has duplicate keys")
    for row in culture_rows:
        if row["group"] not in language_groups:
            raise ValueError(f"{row['key']}: unknown culture group {row['group']}")
        if row["language"] not in language_keys:
            # Existing culture rows point at installed language keys rather than
            # only M4 roots, so validate syntax here and let the established
            # M4 validator retain the full installed-symbol check.
            if not re.fullmatch(r"[A-Za-z0-9_]+", row["language"]):
                raise ValueError(f"{row['key']}: invalid language adapter {row['language']}")
        if row["confidence"] not in {"secure", "contested"}:
            raise ValueError(f"{row['key']}: invalid confidence {row['confidence']}")

    start_text = START_POPS.read_text(encoding="utf-8")
    controlled = controlled_locations(start_text)
    if not controlled:
        raise ValueError("could not identify any locations in main_menu/setup/start/06_pops.txt")
    resolved = resolve_remaps(remap_rows, set(culture_keys), controlled)
    expected_start = patch_start_pops(start_text, resolved)
    start_cultures = set(re.findall(r"\bculture\s*=\s*([A-Za-z0-9_]+)", expected_start))
    batch_keys = culture_batch_keys | remap_batch_keys
    unknown_definition_only = sorted(DEFINITION_ONLY_CULTURES - set(culture_keys))
    if unknown_definition_only:
        raise ValueError(f"unknown definition-only PRO cultures: {', '.join(unknown_definition_only)}")
    absent = sorted((batch_keys - DEFINITION_ONLY_CULTURES) - start_cultures)
    if absent:
        raise ValueError(f"PRO culture batches have no AD 1 population presence: {', '.join(absent)}")

    cultures = [Definition(**row) for row in culture_rows]
    religions = definitions(RELIGIONS)
    religion_keys = {row.key for row in religions}
    for ledger, rows in (("tag profile", tag_profile_rows), ("regional profile", regional_profile_rows)):
        for row in rows:
            if row["culture"] not in set(culture_keys):
                raise ValueError(f"{ledger} {row.get('tag', row.get('region'))}: unknown culture {row['culture']}")
            if row["religion"] not in religion_keys:
                raise ValueError(f"{ledger} {row.get('tag', row.get('region'))}: unknown religion {row['religion']}")
            if row["confidence"] not in {"secure", "contested"}:
                raise ValueError(f"{ledger} {row.get('tag', row.get('region'))}: invalid confidence {row['confidence']}")
    dialects = {row.group: row.key.replace("_language", "_dialect") for row in language_rows}

    symbols = json.loads(SYMBOLS.read_text(encoding="utf-8"))
    symbols["cultures"] = culture_keys
    index_text = json.dumps(symbols, indent=2) + "\n"

    readme = README.read_text(encoding="utf-8")
    readme, replacements = re.subn(
        r"(?m)^- \d+ cultures, 37 religions,",
        f"- {len(cultures)} cultures, 37 religions,",
        readme,
    )
    if replacements != 1:
        raise ValueError("README culture-count line was not uniquely identified")

    mapped_cultures = {row["culture"] for row in resolved.values()}
    files: dict[Path, tuple[str, str]] = {
        CULTURES: (csv_text(culture_rows, CULTURE_FIELDS), "utf-8"),
        CULTURE_REMAP: (csv_text(remap_rows, REMAP_FIELDS), "utf-8"),
        TAG_PROFILES: (csv_text(tag_profile_rows, TAG_PROFILE_FIELDS), "utf-8"),
        REGIONAL_PROFILES: (csv_text(regional_profile_rows, REGIONAL_PROFILE_FIELDS), "utf-8"),
        COMMON / "cultures/antq_m4_cultures.txt": (
            render_cultures(cultures, dialects),
            "utf-8-sig",
        ),
        ROOT / "main_menu/common/named_colors/antq_m4_colors.txt": (
            render_named_colors(cultures, religions, language_rows),
            "utf-8-sig",
        ),
        SYMBOLS: (index_text, "utf-8"),
        START_POPS: (expected_start, "utf-8"),
        README: (readme, "utf-8"),
        CULTURE_DOC: (
            culture_doc(len(cultures), len(remap_rows), len(resolved), len(mapped_cultures)),
            "utf-8",
        ),
    }
    for language in LOCALIZATION_LANGUAGES:
        files[LOC_ROOT / language / f"antq_m4_people_l_{language}.yml"] = (
            render_localization(cultures, religions, language_rows, language),
            "utf-8-sig",
        )

    summary = {
        "cultures": len(cultures),
        "selectors": len(remap_rows),
        "resolved_locations": len(resolved),
        "mapped_cultures": len(mapped_cultures),
        "batch_cultures": len(batch_keys),
        "profile_batch_cultures": len(tag_profile_batch_cultures | regional_profile_batch_cultures),
    }
    return files, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        files, summary = expected_outputs()
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f"pro_culture_expansion: FAIL\n  - {exc}")
        return 1

    if args.write:
        for path, (content, encoding) in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding, newline="\n")
        country_text = country_definitions(load_polity_rows(), load_engine_tags())
        COUNTRY_DEFINITIONS.parent.mkdir(parents=True, exist_ok=True)
        COUNTRY_DEFINITIONS.write_text(country_text, encoding="utf-8-sig", newline="\n")
        print(
            "pro_culture_expansion: wrote "
            f"{summary['cultures']} cultures, {summary['selectors']} selectors, "
            f"{summary['resolved_locations']} resolved locations"
        )
        return 0

    failures: list[str] = []
    for path, (content, encoding) in files.items():
        if not path.is_file():
            failures.append(f"missing generated output {path.relative_to(ROOT)}")
        elif path.read_text(encoding=encoding) != content:
            failures.append(f"stale generated output {path.relative_to(ROOT)}")
    expected_country = country_definitions(load_polity_rows(), load_engine_tags())
    if not COUNTRY_DEFINITIONS.is_file():
        failures.append(f"missing generated output {COUNTRY_DEFINITIONS.relative_to(ROOT)}")
    elif COUNTRY_DEFINITIONS.read_text(encoding="utf-8-sig") != expected_country:
        failures.append(f"stale generated output {COUNTRY_DEFINITIONS.relative_to(ROOT)}")
    if failures:
        print("pro_culture_expansion: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print(
        "pro_culture_expansion: PASS "
        f"({summary['cultures']} cultures; {summary['selectors']} selectors; "
        f"{summary['resolved_locations']} resolved locations; "
        f"{summary['batch_cultures']} PRO cultures)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

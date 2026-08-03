#!/usr/bin/env python3
"""Merge and validate source-led Round 5 AD 1 geography research shards."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/r5"
OUTPUT = DOCS / "geography_names.csv"
COVERAGE = DOCS / "geography_name_coverage.json"
CONFIG = ROOT / "config/local_paths.json"
SYMBOLS = ROOT / "docs/vanilla_symbols"
FIELDS = (
    "granularity", "key", "parent", "kind", "ad1_name", "language",
    "method", "source", "confidence", "note", "unchanged_verified",
)
LEVELS = (
    ("continent", "continents.json"),
    ("subcontinent", "subcontinents.json"),
    ("region", "regions.json"),
    ("area", "areas.json"),
    ("province", "provinces.json"),
    ("location", "locations.json"),
)
ASSIGNED_SHARD = re.compile(r"^names_(areas|provinces|locations)_(\d+)_(\d+)\.csv$")
LOC_LINE = re.compile(r'^\s*([^#\s][^:]*):(?:\d+)?\s+"(.*)"\s*$')


def expected_sets() -> dict[str, tuple[str, ...]]:
    return {
        level: tuple(json.loads((SYMBOLS / filename).read_text(encoding="utf-8-sig")))
        for level, filename in LEVELS
    }


def expected_parents(expected: dict[str, tuple[str, ...]]) -> dict[tuple[str, str], str]:
    hierarchy = json.loads(
        (SYMBOLS / "geography_hierarchy.json").read_text(encoding="utf-8-sig")
    )
    parents: dict[tuple[str, str], str] = {
        ("continent", key): "world" for key in expected["continent"]
    }
    for index in range(1, len(LEVELS)):
        level = LEVELS[index][0]
        parent_level = LEVELS[index - 1][0]
        allowed = set(expected[level])
        for parent in expected[parent_level]:
            for child in hierarchy.get(parent, []):
                if child in allowed:
                    token = (level, child)
                    if token in parents:
                        raise ValueError(f"multiple {level} parents for {child}")
                    parents[token] = parent
        missing = sorted(key for key in allowed if (level, key) not in parents)
        if missing:
            raise ValueError(f"missing {level} parents: {missing[:12]}")
    return parents


def read_shard(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError(f"{path.name}: schema {reader.fieldnames} != {FIELDS}")
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def shard_assignment(path: Path, expected: dict[str, tuple[str, ...]]) -> set[tuple[str, str]] | None:
    if path.name == "names_coarse_continents_subcontinents.csv":
        return {
            (level, key)
            for level in ("continent", "subcontinent")
            for key in expected[level]
        }
    if path.name == "names_regions_a.csv":
        return {("region", key) for key in sorted(expected["region"])[:41]}
    if path.name == "names_regions_b.csv":
        return {("region", key) for key in sorted(expected["region"])[41:]}
    match = ASSIGNED_SHARD.match(path.name)
    if match:
        plural, first, last = match.groups()
        level = plural[:-1] if plural.endswith("s") else plural
        keys = sorted(expected[level])[int(first) - 1:int(last)]
        return {(level, key) for key in keys}
    return None


def installed_names() -> dict[tuple[str, str], str]:
    game = Path(json.loads(CONFIG.read_text(encoding="utf-8-sig"))["game_dir"]) / "game"
    english = game / "main_menu/localization/english"
    paths = [
        (("continent", "subcontinent", "region"), english / "region_names_l_english.yml"),
        (("area",), english / "area_l_english.yml"),
        (("province",), english / "province_names_l_english.yml"),
        (("location",), *sorted((english / "location_names").glob("*.yml"))),
    ]
    values: dict[tuple[str, str], str] = {}
    for levels, *level_paths in paths:
      for path in level_paths:
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = LOC_LINE.match(line)
            if match:
                for level in levels:
                    values[(level, match.group(1))] = match.group(2)
    return values


def canonical_rows() -> tuple[list[dict[str, str]], dict[str, object]]:
    expected = expected_sets()
    parents = expected_parents(expected)
    vanilla = installed_names()
    source_catalog = (ROOT / "docs/world_1ad/SOURCES.md").read_text(encoding="utf-8-sig")
    level_order = {level: index for index, (level, _filename) in enumerate(LEVELS)}
    rows_by_token: dict[tuple[str, str], dict[str, str]] = {}
    failures: list[str] = []
    shard_files = sorted(
        path for path in DOCS.glob("names_*.csv")
        if path.name != OUTPUT.name and not path.name.startswith("names_holy")
    )
    for path in shard_files:
        rows = read_shard(path)
        tokens = {(row["granularity"], row["key"]) for row in rows}
        assigned = shard_assignment(path, expected)
        if assigned is None:
            failures.append(f"unrecognized research shard filename: {path.name}")
        elif tokens != assigned:
            failures.append(
                f"{path.name}: assigned-set mismatch missing={len(assigned - tokens)} "
                f"extra={len(tokens - assigned)}"
            )
        for row in rows:
            token = (row["granularity"], row["key"])
            if token in rows_by_token:
                failures.append(f"duplicate researched token {token} in {path.name}")
                continue
            if row["granularity"] not in expected or row["key"] not in expected.get(row["granularity"], ()):
                failures.append(f"{path.name}: unknown geography token {token}")
                continue
            canonical_parent = parents[token]
            if row["parent"] != canonical_parent:
                failures.append(
                    f"{path.name}: {token} parent {row['parent']!r} != {canonical_parent!r}"
                )
            for field in ("kind", "ad1_name", "language", "method", "source", "confidence", "note"):
                if not row[field]:
                    failures.append(f"{path.name}: {token} lacks {field}")
            if row["confidence"].lower() not in {"high", "medium", "low"}:
                failures.append(f"{path.name}: {token} has invalid confidence")
            unchanged = row["unchanged_verified"].lower() in {"1", "true", "yes"}
            if token in vanilla and row["ad1_name"].casefold() == vanilla[token].casefold():
                if not unchanged:
                    failures.append(f"{path.name}: unexplained vanilla-equal name for {token}")
            elif unchanged:
                failures.append(f"{path.name}: false unchanged_verified flag for {token}")
            source_tokens = [part.strip() for part in row["source"].split(";")]
            if not all(
                part.startswith(("http://", "https://", "installed:"))
                or part == "GEO-PROXY"
                or re.search(rf"`{re.escape(part)}`|^- `{re.escape(part)}`:", source_catalog, re.MULTILINE)
                for part in source_tokens
            ):
                failures.append(f"{path.name}: unresolved source token for {token}")
            row["parent"] = canonical_parent
            row["unchanged_verified"] = "true" if unchanged else "false"
            rows_by_token[token] = row

    siblings: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for (level, key), row in rows_by_token.items():
        siblings[(level, row["parent"], row["ad1_name"].casefold())].append(key)
    for (level, parent, name), keys in siblings.items():
        if len(keys) > 1:
            failures.append(f"sibling collision {level}/{parent}/{name}: {sorted(keys)}")
    if failures:
        raise ValueError("\n  - ".join(["geography research validation failed", *failures]))

    rows = sorted(
        rows_by_token.values(),
        key=lambda row: (level_order[row["granularity"]], row["key"]),
    )
    counts = Counter(row["granularity"] for row in rows)
    total_expected = sum(len(values) for values in expected.values())
    report: dict[str, object] = {
        "complete": len(rows) == total_expected,
        "researched_rows": len(rows),
        "expected_rows": total_expected,
        "distinct_researched_keys": len({row["key"] for row in rows}),
        "expected_distinct_keys": len({key for values in expected.values() for key in values}),
        "levels": {
            level: {"researched": counts[level], "expected": len(expected[level])}
            for level, _filename in LEVELS
        },
        "shards": [path.name for path in shard_files],
    }
    return rows, report


def csv_bytes(rows: list[dict[str, str]]) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("utf-8-sig")


def coverage_bytes(report: dict[str, object]) -> bytes:
    return (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write() -> None:
    rows, report = canonical_rows()
    OUTPUT.write_bytes(csv_bytes(rows))
    COVERAGE.write_bytes(coverage_bytes(report))
    print(f"r5_geography_names: merged {len(rows)}/{report['expected_rows']} sourced rows")


def check() -> None:
    rows, report = canonical_rows()
    if not OUTPUT.is_file() or OUTPUT.read_bytes() != csv_bytes(rows):
        raise ValueError(f"stale {OUTPUT.relative_to(ROOT)}")
    if not COVERAGE.is_file() or COVERAGE.read_bytes() != coverage_bytes(report):
        raise ValueError(f"stale {COVERAGE.relative_to(ROOT)}")
    print(
        f"r5_geography_names: PASS ({len(rows)}/{report['expected_rows']} sourced "
        f"hierarchy rows; complete={report['complete']})"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    if args.check or not args.write:
        check()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"r5_geography_names: FAIL\n  - {exc}", file=sys.stderr)
        raise SystemExit(1)

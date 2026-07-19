#!/usr/bin/env python3
"""Generate the M5 full map-template override with audited AD 1 RGO corrections."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
RULES = ROOT / "docs/m5/rgo_rules.csv"
OUTPUT = ROOT / "in_game/map_data/location_templates.txt"
REPORT = ROOT / "docs/m5/rgo_remap_report.csv"
LINE = re.compile(r"^(?P<location>[A-Za-z0-9_]+)\s*=\s*\{(?P<body>.*?\braw_material\s*=\s*)(?P<good>[A-Za-z0-9_]+)(?P<tail>.*)$", re.MULTILINE)


def rows(path: Path, comments: bool = False) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        source = (line for line in handle if not line.startswith("#")) if comments else handle
        return list(csv.DictReader(source))


def rendered() -> tuple[str, str, int]:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    source = Path(config["game_dir"]) / "game/in_game/map_data/location_templates.txt"
    roster_rows = rows(ROSTER)
    roster = {row["tag"]: row for row in roster_rows}
    if len(roster) != len(roster_rows):
        raise ValueError("polity roster has duplicate tags")
    owner_region: dict[str, str] = {}
    for row in rows(OWNERSHIP, comments=True):
        tag = row["tag"]
        if tag not in roster:
            raise ValueError(f"ownership references unknown polity {tag}")
        owner_region[row["location"]] = roster[tag]["region"]
    raw_rules = rows(RULES)
    rules: dict[str, dict[str, str]] = {}
    for rule in raw_rules:
        source_good = rule.get("source_good", "").strip()
        if source_good in rules:
            raise ValueError(f"RGO rules duplicate source good {source_good}")
        rules[source_good] = rule
    valid_goods = set(json.loads((ROOT / "docs/vanilla_symbols/good.json").read_text(encoding="utf-8-sig")))
    valid_regions = {row["region"] for row in roster_rows}
    for source_good, rule in rules.items():
        if source_good not in valid_goods or rule["replacement_good"] not in valid_goods:
            raise ValueError(f"RGO rule has unknown good {source_good}->{rule['replacement_good']}")
        if not all(rule.get(field, "").strip() for field in ("source_good", "replacement_good", "source", "confidence", "note")):
            raise ValueError("RGO rule has blank required field")
        if rule["confidence"] not in {"secure", "contested"}:
            raise ValueError(f"RGO rule has invalid confidence {rule['confidence']}")
        allowed = {item for item in rule.get("allowed_regions", "").split("|") if item}
        unknown_regions = allowed - valid_regions
        if unknown_regions:
            raise ValueError(f"RGO rule for {source_good} has unknown regions {sorted(unknown_regions)}")
    changes: list[tuple[str, str, str, str]] = []
    def replace(match: re.Match[str]) -> str:
        location, good = match["location"], match["good"]
        rule = rules.get(good)
        region = owner_region.get(location)
        if not rule or not region:
            return match.group(0)
        allowed = {item for item in rule.get("allowed_regions", "").split("|") if item}
        if allowed and region in allowed:
            return match.group(0)
        replacement = rule["replacement_good"]
        changes.append((location, region, good, replacement))
        return f"{location} = {{{match['body']}{replacement}{match['tail']}"
    content = LINE.sub(replace, source.read_text(encoding="utf-8"))
    if not changes:
        raise ValueError("RGO rules produced no owned-location corrections")
    counts = Counter((old, new) for _, _, old, new in changes)
    report = ["location,region,source_good,replacement_good"]
    report.extend(",".join(row) for row in sorted(changes))
    report.append("")
    report.append("# counts")
    report.extend(f"# {old}->{new},{count}" for (old, new), count in sorted(counts.items()))
    return content, "\n".join(report) + "\n", len(changes)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        content, report, change_count = rendered()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"rgo_remap: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8", newline="\n")
        REPORT.write_text(report, encoding="utf-8-sig", newline="\n")
        print(f"rgo_remap: wrote {OUTPUT.relative_to(ROOT)} ({change_count} corrections)")
        return 0
    failures = []
    for path, expected, encoding in ((OUTPUT, content, "utf-8"), (REPORT, report, "utf-8-sig")):
        if not path.is_file() or path.read_text(encoding=encoding) != expected:
            failures.append(f"stale or missing {path.relative_to(ROOT)}")
    if failures:
        print("rgo_remap: FAIL\n  - " + "\n  - ".join(failures))
        return 1
    print(f"rgo_remap: PASS ({change_count} corrections)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

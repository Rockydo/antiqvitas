#!/usr/bin/env python3
"""Audit installed culture geography against the M4 ownership/profile layer."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from generate_country_definitions import historical_profile_for

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
EXCEPTIONS = ROOT / "docs/m4/culture_template_exceptions.csv"
OUTPUT = ROOT / "docs/m4/culture_template_inventory.csv"
LOCATION_LINE = re.compile(r"^([A-Za-z0-9_]+)\s*=\s*\{.*?\bculture\s*=\s*([A-Za-z0-9_]+)", re.MULTILINE)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def ownership_rows() -> list[dict[str, str]]:
    with OWNERSHIP.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(line for line in handle if not line.startswith("#")))


def exception_locations() -> set[str]:
    entries = rows(EXCEPTIONS)
    locations = {row.get("location", "") for row in entries}
    if "" in locations or len(locations) != len(entries):
        raise ValueError(f"{EXCEPTIONS.relative_to(ROOT)} has a blank or duplicate location")
    for row in entries:
        if any(not row.get(field, "").strip() for field in ("reason", "source", "confidence", "note")):
            raise ValueError(f"{EXCEPTIONS.relative_to(ROOT)} has a blank required field")
    return locations


def rendered() -> str:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    template = Path(config["game_dir"]) / "game/in_game/map_data/location_templates.txt"
    if not template.is_file():
        raise ValueError(f"missing installed location templates: {template}")
    vanilla = {location: culture for location, culture in LOCATION_LINE.findall(template.read_text(encoding="utf-8-sig"))}
    roster = {row["tag"]: row for row in rows(ROSTER)}
    by_culture: defaultdict[str, list[tuple[str, str, str, str]]] = defaultdict(list)
    exceptions = exception_locations()
    missing: list[str] = []
    for row in ownership_rows():
        location = row["location"]
        tag = row["tag"]
        if location not in vanilla:
            if location not in exceptions:
                missing.append(location)
                continue
            vanilla_culture = "__no_installed_template__"
        else:
            vanilla_culture = vanilla[location]
        profile = historical_profile_for(roster[tag])
        by_culture[vanilla_culture].append((location, tag, roster[tag]["region"], profile.culture))
    if missing:
        raise ValueError(f"{len(missing)} controlled locations have no installed culture template; first={missing[:8]}")
    unused = sorted(exceptions - {entry[0] for entries in by_culture.values() for entry in entries})
    if unused:
        raise ValueError(f"culture-template exceptions are not controlled missing-template locations: {unused}")
    lines = ["vanilla_culture,controlled_locations,m4_profile_candidates,regions,sample_locations"]
    for culture, entries in sorted(by_culture.items(), key=lambda item: (-len(item[1]), item[0])):
        candidates = Counter(entry[3] for entry in entries)
        regions = Counter(entry[2] for entry in entries)
        samples = ";".join(entry[0] for entry in sorted(entries)[:8])
        lines.append(
            ",".join(
                (
                    culture,
                    str(len(entries)),
                    "|".join(f"{key}:{value}" for key, value in sorted(candidates.items())),
                    "|".join(f"{key}:{value}" for key, value in sorted(regions.items())),
                    samples,
                )
            )
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        expected = rendered()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"culture_template_inventory: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8-sig", newline="\n")
        print(f"culture_template_inventory: wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != expected:
        print(f"culture_template_inventory: FAIL\n  - stale or missing {OUTPUT.relative_to(ROOT)}")
        return 1
    print(f"culture_template_inventory: PASS ({len(expected.splitlines()) - 1} active vanilla culture templates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

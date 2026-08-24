#!/usr/bin/env python3
"""Compare country research serialization across a ten-year runtime interval.

This deliberately reads saves rather than trusting generated setup text or UI
counts.  It proves that representative AI/player countries retain their
opening advances, finish new advances, and carry sensible active progress.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import m8_knowledge as m8
from m6_ruler_runtime import GameDate, brace_delta
from save_melt import plaintext_save
from s7_research_pacing import installed_base_cost, point_cost


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TAGS = ("ROM", "HAN", "PAR", "CHL", "XIO", "AES")
ROLES = {
    "ROM": "large Mediterranean imperial/literate",
    "HAN": "large East-Asian imperial/literate",
    "PAR": "large Iranian imperial/mixed-literacy",
    "CHL": "regional settled/literate",
    "XIO": "large pastoral/low-literacy",
    "AES": "small society-of-pops/low-literacy",
}


@dataclass(frozen=True)
class CountryResearch:
    design_tag: str
    engine_tag: str
    name: str
    population_thousands: float
    starting_level: int
    researched: frozenset[str]
    active_slots: tuple[int, ...]
    progress: float


def scalar(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}=([^\s{{}}]+)\s*$", text)
    return match.group(1).strip('"') if match else None


def named_block(text: str, key: str) -> str:
    lines = text.splitlines()
    pattern = re.compile(rf"^\s*{re.escape(key)}=\{{\s*$")
    for index, line in enumerate(lines):
        if not pattern.match(line):
            continue
        depth = brace_delta(line)
        body: list[str] = []
        for child in lines[index + 1:]:
            body.append(child)
            depth += brace_delta(child)
            if depth == 0:
                return "\n".join(body)
    return ""


def tag_maps() -> tuple[dict[str, str], dict[str, str]]:
    data = json.loads((ROOT / "docs/world_1ad/tag_map.json").read_text(encoding="utf-8-sig"))
    design_to_engine = {row["design_tag"]: row["engine_tag"] for row in data["entries"]}
    return design_to_engine, {engine: design for design, engine in design_to_engine.items()}


def parse_save(path: Path, selected: set[str]) -> tuple[GameDate, dict[str, CountryResearch]]:
    _design_to_engine, engine_to_design = tag_maps()
    manager = ""
    manager_depth = 0
    database_depth: int | None = None
    block_depth = 0
    block_lines: list[str] = []
    date: GameDate | None = None
    result: dict[str, CountryResearch] = {}

    def finish(text: str) -> None:
        engine_tag = scalar(text, "definition")
        if not engine_tag:
            return
        design_tag = engine_to_design.get(engine_tag, engine_tag)
        if design_tag not in selected or scalar(text, "country_type") != "Real":
            return
        researched_body = named_block(text, "researched_advances")
        researched = frozenset(re.findall(r"([A-Za-z0-9_]+)=yes", researched_body))
        active_body = named_block(text, "current_research")
        slots_match = re.search(r"(?m)^\s*research=\{([^}]*)\}", active_body)
        active_slots = tuple(int(value) for value in re.findall(r"\d+", slots_match.group(1))) if slots_match else ()
        result[design_tag] = CountryResearch(
            design_tag=design_tag,
            engine_tag=engine_tag,
            name=scalar(text, "country_name") or design_tag,
            population_thousands=float(scalar(text, "last_months_population") or 0),
            starting_level=int(scalar(text, "starting_technology_level") or 0),
            researched=researched,
            active_slots=active_slots,
            progress=float(scalar(active_body, "progress") or 0),
        )

    with path.open(encoding="utf-8-sig", errors="replace") as handle:
        for raw in handle:
            line = raw.rstrip("\r\n")
            stripped = line.strip()
            if date is None and stripped.startswith("date="):
                date = GameDate.parse(stripped.removeprefix("date="))
            if block_lines:
                block_lines.append(line)
                block_depth += brace_delta(line)
                if block_depth == 0:
                    finish("\n".join(block_lines))
                    block_lines = []
                continue
            if not manager:
                if stripped == "countries={":
                    manager = "countries"
                    manager_depth = 1
                    database_depth = None
                continue
            before = manager_depth
            if database_depth is not None and before == database_depth:
                if re.match(r"^\d+=\{$", stripped):
                    block_lines = [line]
                    block_depth = brace_delta(line)
                    continue
            if database_depth is None and stripped == "database={":
                database_depth = before + 1
            manager_depth += brace_delta(line)
            if manager_depth == 0:
                manager = ""
                database_depth = None
            if len(result) == len(selected) and date is not None:
                break
    if date is None:
        raise ValueError(f"save has no date: {path}")
    missing = selected - set(result)
    if missing:
        raise ValueError(f"save {path.name} lacks real selected countries: {sorted(missing)}")
    return date, result


def elapsed_months(start: GameDate, end: GameDate) -> float:
    return (
        (end.year - start.year) * 12
        + end.month - start.month
        + (end.day - start.day) / 30.4375
    )


def compare(
    baseline_path: Path,
    sample_path: Path,
    tags: tuple[str, ...],
    minimum_months: float,
) -> dict[str, object]:
    selected = set(tags)
    with plaintext_save(baseline_path) as baseline_source:
        start_date, baseline = parse_save(baseline_source, selected)
    with plaintext_save(sample_path) as sample_source:
        end_date, sample = parse_save(sample_source, selected)
    months = elapsed_months(start_date, end_date)
    records = {record.key: record for record in m8.advance_records()}
    base_cost = installed_base_cost()
    rows: list[dict[str, object]] = []
    failures: list[str] = []
    if months < minimum_months:
        failures.append(f"interval is only {months:.2f} months; need {minimum_months:.2f}")
    for tag in tags:
        before = baseline[tag]
        after = sample[tag]
        added = sorted(after.researched - before.researched)
        removed = sorted(before.researched - after.researched)
        known_added = [key for key in added if key in records]
        completed_points = sum(float(point_cost(records[key], base_cost)) for key in known_added)
        active = bool(after.active_slots) and after.progress >= 0
        if removed:
            failures.append(f"{tag} lost researched advances: {removed}")
        if months >= minimum_months and not added:
            failures.append(f"{tag} completed no advance across the required interval")
        if not active:
            failures.append(f"{tag} has no valid active research at sample date")
        rows.append({
            "tag": tag,
            "role": ROLES.get(tag, "selected comparison polity"),
            "engine_tag": after.engine_tag,
            "opening_population_thousands": before.population_thousands,
            "sample_population_thousands": after.population_thousands,
            "starting_technology_level": before.starting_level,
            "opening_researched_count": len(before.researched),
            "sample_researched_count": len(after.researched),
            "completed_count": len(added),
            "completed_advances": added,
            "completed_known_point_cost": completed_points,
            "removed_advances": removed,
            "sample_active_slots": list(after.active_slots),
            "sample_active_progress": after.progress,
            "status": "pass" if added and not removed and active else "fail",
        })
    return {
        "status": "PASS" if not failures else "FAIL",
        "baseline_save": str(baseline_path.resolve()),
        "sample_save": str(sample_path.resolve()),
        "start_date": str(start_date),
        "end_date": str(end_date),
        "elapsed_months": months,
        "minimum_months": minimum_months,
        "countries": rows,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("sample", type=Path)
    parser.add_argument("--tags", default=",".join(DEFAULT_TAGS))
    parser.add_argument("--minimum-months", type=float, default=120.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        tags = tuple(tag.strip().upper() for tag in args.tags.split(",") if tag.strip())
        if not tags or len(tags) != len(set(tags)):
            raise ValueError("--tags must contain distinct design tags")
        result = compare(args.baseline, args.sample, tags, args.minimum_months)
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print(rendered, end="")
        return 0 if result["status"] == "PASS" else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"s7_research_runtime: FAIL\n  - {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

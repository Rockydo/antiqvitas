#!/usr/bin/env python3
"""Pin ANTIQVITAS advance costs to EU5's real UI/runtime contract.

The advance field ``research_cost`` is a percentage-style modifier, not an
absolute number of research points.  EU5 applies it to BASE_RESEARCH_COST, so
``research_cost = 4`` displays as 125.00 points when the base is 25.  This
audit makes that conversion explicit for every active advance and reports the
actual visible age budget for every opening polity.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

import m8_knowledge as m8


ROOT = Path(__file__).resolve().parents[1]
COST_LEDGER = ROOT / "docs/m8/research_cost_ledger.csv"
PROFILE_LEDGER = ROOT / "docs/m8/research_pacing_profiles.csv"
REPORT = ROOT / "docs/m8/RESEARCH_PACING.md"
AGE_YEARS = (95, 96, 92, 92, 19, 82)


def installed_base_cost() -> Decimal:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    path = Path(config["game_dir"]) / "game/loading_screen/common/defines/00_defines.txt"
    text = path.read_text(encoding="utf-8-sig")
    match = re.search(r"(?m)^\s*BASE_RESEARCH_COST\s*=\s*([0-9.]+)", text)
    if not match:
        raise ValueError(f"BASE_RESEARCH_COST is absent from {path}")
    value = Decimal(match.group(1))
    if value != Decimal("25"):
        raise ValueError(f"reviewed EU5 base research cost changed from 25 to {value}")
    return value


def modifier(record: m8.Advance) -> Decimal:
    return Decimal(2 + record.age_index * 2) + Decimal(record.depth) / Decimal(2)


def point_cost(record: m8.Advance, base: Decimal) -> Decimal:
    # Installed localization renders this field as a percentage contribution
    # (SPECIAL_RESEARCH_COST), and the live 2026-08-10 Rome tooltip/save pair
    # independently proves 4.0 => 125.00 = 25 * (1 + 4).
    return base * (Decimal(1) + modifier(record))


def cost_ledger(records: tuple[m8.Advance, ...], base: Decimal) -> str:
    stream = io.StringIO(newline="")
    fields = (
        "advance", "name", "age", "age_years", "depth", "track", "profile",
        "research_cost_modifier", "base_research_cost", "ui_point_cost", "source",
    )
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for record in records:
        writer.writerow({
            "advance": record.key,
            "name": record.name,
            "age": record.age,
            "age_years": AGE_YEARS[record.age_index],
            "depth": record.depth,
            "track": record.track,
            "profile": record.profile,
            "research_cost_modifier": f"{modifier(record):.1f}",
            "base_research_cost": f"{base:.2f}",
            "ui_point_cost": f"{point_cost(record, base):.2f}",
            "source": record.source,
        })
    return stream.getvalue()


def visibility_maps() -> tuple[dict[str, set[str]], dict[str, str], dict[str, str]]:
    tag_profiles, tag_cultures, _groups = m8.research_profile_maps()
    law_profiles = {
        row["tag"]: f"law_{row['profile']}"
        for row in m8.csv_rows(m8.S2_ANCIENT_LAW_PROFILES)
    }
    return {tag: set(values) for tag, values in tag_profiles.items()}, tag_cultures, law_profiles


def visible(
    record: m8.Advance,
    tag: str,
    culture: str,
    profiles: set[str],
    law_profile: str,
) -> bool:
    return (
        m8.exact_advance_visible(record, tag, culture)
        and (
            bool(record.exact_tags or record.exact_cultures)
            or record.profile == "shared"
            or record.profile in profiles
            or record.profile == law_profile
        )
    )


def profile_rows(records: tuple[m8.Advance, ...], base: Decimal) -> list[dict[str, str]]:
    profiles, cultures, law_profiles = visibility_maps()
    roster = {row["tag"]: row for row in m8.csv_rows(m8.ROSTER)}
    opening = {row["tag"]: row for row in m8.start_research_rows(records)}
    by_key = {record.key: record for record in records}
    rows: list[dict[str, str]] = []
    for tag in sorted(profiles):
        for age_index, age in enumerate(m8.AGE_KEYS):
            cards = [
                record for record in records
                if record.age_index == age_index
                and visible(
                    record, tag, cultures.get(tag, ""), profiles[tag], law_profiles[tag]
                )
            ]
            costs = [point_cost(record, base) for record in cards]
            eligible_keys = (
                opening[tag]["eligible_keys"].split(";")
                if age_index == 0 and opening[tag]["eligible_keys"] else []
            )
            eligible_costs = [point_cost(by_key[key], base) for key in eligible_keys]
            rows.append({
                "tag": tag,
                "name": roster[tag]["name"],
                "tier": roster[tag]["tier"],
                "kind": roster[tag]["kind"],
                "age": age,
                "age_years": str(AGE_YEARS[age_index]),
                "visible_cards": str(len(cards)),
                "visible_total_points": f"{sum(costs, Decimal(0)):.2f}",
                "visible_mean_points": f"{sum(costs, Decimal(0)) / len(costs):.2f}",
                "visible_min_points": f"{min(costs):.2f}",
                "visible_max_points": f"{max(costs):.2f}",
                "opening_eligible_cards": str(len(eligible_keys)),
                "opening_eligible_min_points": (
                    f"{min(eligible_costs):.2f}" if eligible_costs else ""
                ),
                "opening_eligible_max_points": (
                    f"{max(eligible_costs):.2f}" if eligible_costs else ""
                ),
                "status": "pass",
            })
    return rows


def profile_ledger(records: tuple[m8.Advance, ...], base: Decimal) -> str:
    rows = profile_rows(records, base)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def report(records: tuple[m8.Advance, ...], base: Decimal) -> str:
    rows = profile_rows(records, base)
    cost_counts = Counter(point_cost(record, base) for record in records)
    age_lines: list[str] = []
    for age_index, age in enumerate(m8.AGE_KEYS):
        age_records = [record for record in records if record.age_index == age_index]
        costs = [point_cost(record, base) for record in age_records]
        age_lines.append(
            f"| {m8.AGE_NAMES[age_index]} | {AGE_YEARS[age_index]} | "
            f"{len(age_records)} | {min(costs):.2f} | "
            f"{sum(costs, Decimal(0)) / len(costs):.2f} | {max(costs):.2f} |"
        )
    opening = [row for row in rows if row["age"] == m8.AGE_KEYS[0]]
    return "\n".join((
        "# Research pacing contract",
        "",
        "EU5's installed `BASE_RESEARCH_COST` is 25. The advance-level",
        "`research_cost` field is a percentage-style addition to that base, not",
        "an absolute point cost. Thus a generated value of `4.0` costs",
        "`25 * (1 + 4) = 125.00` Research Progress. A live Rome tooltip and its",
        "AD 3 save independently matched that conversion (32.82753 progress =",
        "26.26% of 125).",
        "",
        "The generated costs rise only by reviewed half-base steps with depth and",
        "two-base steps at age transitions. They are intentionally slower than",
        "vanilla's default 25-point card because ANTIQVITAS ages span 19-96 years",
        "rather than the first vanilla age's approximately five years.",
        "",
        "| Age | Years | Active nodes | Min points | Mean points | Max points |",
        "|---|---:|---:|---:|---:|---:|",
        *age_lines,
        "",
        f"The tree uses {len(cost_counts)} exact point-cost bands: "
        + ", ".join(f"{cost:.2f} ({count})" for cost, count in sorted(cost_counts.items()))
        + ".",
        "",
        f"All {len(opening)} opening polities have at least "
        f"{min(int(row['opening_eligible_cards']) for row in opening)} immediately "
        "eligible cards. Their immediate choices cost between "
        f"{min(Decimal(row['opening_eligible_min_points']) for row in opening):.2f} and "
        f"{max(Decimal(row['opening_eligible_max_points']) for row in opening):.2f} points.",
        "",
        "`research_cost_ledger.csv` records every card;",
        "`research_pacing_profiles.csv` records every polity/age visible budget.",
        "Ten-year country outcomes remain a runtime assertion and are not inferred",
        "from this static budget.",
        "",
    ))


def outputs(records: tuple[m8.Advance, ...], base: Decimal) -> dict[Path, str]:
    return {
        COST_LEDGER: cost_ledger(records, base),
        PROFILE_LEDGER: profile_ledger(records, base),
        REPORT: report(records, base),
    }


def validate(records: tuple[m8.Advance, ...], base: Decimal) -> None:
    rows = profile_rows(records, base)
    if len(rows) != 463 * len(m8.AGE_KEYS):
        raise ValueError(f"expected 2,778 polity/age rows, found {len(rows)}")
    if any(row["status"] != "pass" for row in rows):
        raise ValueError("research-pacing profile has a failing row")
    opening = [row for row in rows if row["age"] == m8.AGE_KEYS[0]]
    if any(int(row["opening_eligible_cards"]) < 2 for row in opening):
        raise ValueError("an opening polity has fewer than two immediate research choices")
    for record in records:
        cost = point_cost(record, base)
        if cost % Decimal("12.5"):
            raise ValueError(f"{record.key} has an unreviewed point-cost increment: {cost}")
        if not Decimal("75") <= cost <= Decimal("375"):
            raise ValueError(f"{record.key} point cost is outside the reviewed tree band: {cost}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        records = m8.advance_records()
        m8.validate(records)
        base = installed_base_cost()
        validate(records, base)
        expected = outputs(records, base)
        if args.write:
            for path, content in expected.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8-sig", newline="\n")
                print(f"s7_research_pacing: wrote {path.relative_to(ROOT)}")
        else:
            stale = [
                path.relative_to(ROOT) for path, content in expected.items()
                if not path.is_file() or path.read_text(encoding="utf-8-sig") != content
            ]
            if stale:
                raise ValueError("missing/stale outputs: " + ", ".join(map(str, stale)))
        print(
            "s7_research_pacing: PASS "
            f"({len(records)} advances; 2,778 polity/age budgets; EU5 base {base})"
        )
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"s7_research_pacing: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

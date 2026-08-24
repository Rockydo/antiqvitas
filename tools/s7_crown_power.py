#!/usr/bin/env python3
"""Audit structural crown/estate leverage and Rome's runtime evidence obligations."""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
BANDS = ROOT / "docs/m6/crown_power_reform_bands.csv"
ROME_SOURCES = ROOT / "docs/m6/roman_crown_power_sources.csv"
REPORT = ROOT / "docs/m6/CROWN_POWER_AUDIT.md"
ESTATES = ("nobles", "burghers", "clergy", "peasants", "tribes")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: str(value or "").strip() for key, value in row.items() if key}
            for row in csv.DictReader(handle)
        ]


def top_blocks(text: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    key = ""
    depth = 0
    captured: list[str] = []
    for line in text.splitlines():
        if depth == 0:
            match = re.fullmatch(r"([a-z][a-z0-9_]*)\s*=\s*\{", line.strip())
            if not match:
                continue
            key = match.group(1)
            captured = [line]
        elif key:
            captured.append(line)
        depth += line.count("{") - line.count("}")
        if key and depth == 0:
            blocks[key] = "\n".join(captured)
            key, captured = "", []
    if depth:
        raise ValueError("government reform file has unmatched braces")
    return blocks


def modifier_values(block: str) -> dict[str, float]:
    marker = "country_modifier = {"
    start = block.find(marker)
    if start < 0:
        return {}
    body_start = start + len(marker)
    depth = 1
    index = body_start
    while index < len(block) and depth:
        depth += (block[index] == "{") - (block[index] == "}")
        index += 1
    if depth:
        raise ValueError("country modifier has unmatched braces")
    body = block[body_start:index - 1]
    result: dict[str, float] = {}
    for key, value in re.findall(r"(?m)^\s*([a-z][a-z0-9_]*)\s*=\s*(-?\d+(?:\.\d+)?)\s*$", body):
        # Several older reform bases and their sourced political contracts
        # contribute the same additive estate modifier. Model the engine's
        # combined structural contribution rather than discarding one line.
        result[key] = result.get(key, 0.0) + float(value)
    return result


def render_number(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".") or "0"


def build() -> tuple[str, str, str, dict[str, int]]:
    failures: list[str] = []
    blocks = top_blocks(REFORMS.read_text(encoding="utf-8-sig"))
    roster = {row["tag"]: row for row in rows(ROSTER)}
    governments = {row["design_tag"]: row for row in rows(GOVERNMENTS)}
    opening_reforms = {row["reform"] for row in governments.values()}
    opening_reforms.update({"antq_advanced_chiefdom", "antq_regional_kingship"})
    missing = opening_reforms - blocks.keys()
    if missing:
        failures.append(f"opening reforms missing definitions: {sorted(missing)}")

    band_records: list[dict[str, object]] = []
    metrics_by_reform: dict[str, dict[str, float]] = {}
    for reform in sorted(opening_reforms):
        values = modifier_values(blocks.get(reform, ""))
        crown_direct = values.get("global_crown_estate_power", 0.0)
        crown_cabinet = values.get("crown_estate_power_from_cabinet", 0.0)
        estate_direct = sum(max(0.0, values.get(f"global_{estate}_estate_power", 0.0)) for estate in ESTATES)
        estate_cabinet = max(
            [max(0.0, values.get(f"{estate}_estate_power_from_cabinet", 0.0)) for estate in ESTATES]
            + [max(0.0, values.get("estate_power_from_cabinet", 0.0))]
        )
        authority = crown_direct + crown_cabinet
        competition = estate_direct + estate_cabinet
        if authority >= 0.38:
            band = "centralized_imperial"
        elif authority >= 0.30:
            band = "negotiated_imperial"
        elif authority >= 0.15:
            band = "royal_balanced"
        else:
            band = "estate_or_community_led"
        holders = sorted(tag for tag, row in governments.items() if row["reform"] == reform)
        if reform == "antq_advanced_chiefdom":
            holders.extend(sorted(tag for tag, polity in roster.items() if tag not in governments and polity["kind"] == "sop"))
        if reform == "antq_regional_kingship":
            holders.extend(sorted(tag for tag, polity in roster.items() if tag not in governments and polity["kind"] != "sop"))
        metrics_by_reform[reform] = {
            "crown_direct": crown_direct,
            "crown_cabinet": crown_cabinet,
            "estate_direct": estate_direct,
            "estate_cabinet": estate_cabinet,
            "authority": authority,
            "competition": competition,
        }
        band_records.append({
            "reform": reform,
            "opening_holders": len(set(holders)),
            "sample_tags": ";".join(sorted(set(holders))[:8]),
            "crown_direct": render_number(crown_direct),
            "crown_from_cabinet": render_number(crown_cabinet),
            "estate_direct_positive": render_number(estate_direct),
            "largest_estate_cabinet_lever": render_number(estate_cabinet),
            "structural_authority_levers": render_number(authority),
            "structural_estate_levers": render_number(competition),
            "reviewed_band": band,
            "status": "pass",
        })

    required = {
        "rome": "antq_principate",
        "han": "antq_han_imperial_bureaucracy",
        "parthia": "antq_parthian_king_of_kings",
        "republic": "antq_indian_ganasangha",
        "client": "antq_herodian_judean_ethnarchy",
        "city_state": "antq_sogdian_city_compact",
        "tribal": "antq_tribal_kingdom",
    }
    if set(required.values()) - metrics_by_reform.keys():
        failures.append("comparative crown-power sample lost an opening reform")
    else:
        rome = metrics_by_reform[required["rome"]]
        han = metrics_by_reform[required["han"]]
        if not (
            rome["crown_direct"] == 0.18
            and rome["crown_cabinet"] == 0.20
            and rome["authority"] > rome["competition"]
            and rome["authority"] < han["authority"]
        ):
            failures.append(f"Principate structural authority band drift: {rome}")
        for comparison in ("parthia", "republic", "client", "city_state", "tribal"):
            if rome["authority"] <= metrics_by_reform[required[comparison]]["authority"]:
                failures.append(f"Principate is not structurally stronger than {comparison}")

    rome_government = governments["ROM"]
    source_records = [
        {
            "source_class": "government_reform",
            "resolved_keys": rome_government["reform"],
            "static_crown_effect": "global_crown_estate_power=0.18;crown_estate_power_from_cabinet=0.20",
            "counterweight": "global_nobles_estate_power=0.06;global_burghers_estate_power=0.05;nobles_estate_power_from_cabinet=0.15",
            "runtime_obligation": "capture the fresh government and crown/estate tooltips",
            "status": "static_pass_runtime_pending",
        },
        {
            "source_class": "laws",
            "resolved_keys": rome_government["laws"],
            "static_crown_effect": "resolved definitions present",
            "counterweight": "municipal, cultural, military, coinage, and cult bargains",
            "runtime_obligation": "record each law contribution and one reversible law comparison",
            "status": "runtime_pending",
        },
        {
            "source_class": "privileges",
            "resolved_keys": rome_government["privileges"],
            "static_crown_effect": "praetorian donatives grant 0.12 crown; senatorial/equestrian noble stacking reduced",
            "counterweight": "senatorial, equestrian, priestly, annona, and military constituencies",
            "runtime_obligation": "record each privilege contribution without removing historical counterplay",
            "status": "runtime_pending",
        },
        {
            "source_class": "estates_and_land",
            "resolved_keys": "crown;nobles;burghers;clergy;peasants;tribes",
            "static_crown_effect": "emergent from ownership and estate distribution",
            "counterweight": "provincial and municipal landholding",
            "runtime_obligation": "capture day-one and settled estate-power panels",
            "status": "runtime_pending",
        },
        {
            "source_class": "cabinet_and_ruler",
            "resolved_keys": f"ruler={rome_government['ruler']};regent={rome_government['active_regent'] or 'none'}",
            "static_crown_effect": "Principate cabinet crown lever=0.20",
            "counterweight": "senatorial cabinet lever=0.15;appointment patronage cost=0.10",
            "runtime_obligation": "capture staffed cabinet and one member replacement comparison",
            "status": "runtime_pending",
        },
        {
            "source_class": "legitimacy_cultures_subjects",
            "resolved_keys": "legitimacy;accepted cultures;11 Roman client kingdoms",
            "static_crown_effect": "emergent runtime sources",
            "counterweight": "large multicultural empire and negotiated client ring",
            "runtime_obligation": "record tooltip components and settled post-start values",
            "status": "runtime_pending",
        },
        {
            "source_class": "scripted_modifiers",
            "resolved_keys": "opening effects;historical currents;situations",
            "static_crown_effect": "no hidden flat crown-power startup modifier authorized",
            "counterweight": "visible dated and conditional systems only",
            "runtime_obligation": "scan logs and active modifiers for unledgered crown effects",
            "status": "runtime_pending",
        },
    ]

    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    band_stream = io.StringIO(newline="")
    band_fields = (
        "reform", "opening_holders", "sample_tags", "crown_direct",
        "crown_from_cabinet", "estate_direct_positive", "largest_estate_cabinet_lever",
        "structural_authority_levers", "structural_estate_levers", "reviewed_band", "status",
    )
    writer = csv.DictWriter(band_stream, fieldnames=band_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(band_records)
    source_stream = io.StringIO(newline="")
    source_fields = (
        "source_class", "resolved_keys", "static_crown_effect", "counterweight",
        "runtime_obligation", "status",
    )
    writer = csv.DictWriter(source_stream, fieldnames=source_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(source_records)
    comparison_lines = []
    for name, reform in required.items():
        values = metrics_by_reform[reform]
        comparison_lines.append(
            f"- {name}: {reform}; authority levers {values['authority']:.2f}, estate levers {values['competition']:.2f}."
        )
    report = "\n".join((
        "# Crown-Power Structural Audit",
        "",
        "Generated by `tools/s7_crown_power.py`. Structural levers are not claimed",
        "as the final UI percentage: land, estates, cabinet staffing, legitimacy,",
        "cultures, subjects, and active modifiers remain explicit runtime obligations.",
        "",
        "The Principate now supplies +0.18 direct crown power and +0.20 crown power",
        "from cabinet staffing, against +0.06 senatorial and +0.05 equestrian direct",
        "power plus +0.15 senatorial cabinet leverage. This gives Augustus a material but",
        "negotiated advantage, below the Han and Dominate +0.40 authority packages.",
        "",
        "Comparative opening sample:",
        "",
        *comparison_lines,
        "",
        "The seven-row Roman source ledger prevents the static reform adjustment",
        "from being mistaken for complete day-one proof; all remaining emergent",
        "components must be captured on fresh and settled starts.",
        "",
    ))
    metrics = {"reforms": len(band_records), "sources": len(source_records), "comparisons": len(required)}
    return band_stream.getvalue(), source_stream.getvalue(), report, metrics


def write() -> dict[str, int]:
    bands, sources, report, metrics = build()
    BANDS.write_text(bands, encoding="utf-8-sig", newline="")
    ROME_SOURCES.write_text(sources, encoding="utf-8-sig", newline="")
    REPORT.write_text(report, encoding="utf-8", newline="")
    return metrics


def check() -> dict[str, int]:
    bands, sources, report, metrics = build()
    stale = []
    for path, expected in ((BANDS, bands), (ROME_SOURCES, sources), (REPORT, report)):
        if not path.is_file() or path.read_text(encoding="utf-8-sig") != expected:
            stale.append(str(path.relative_to(ROOT)))
    if stale:
        raise ValueError(f"stale crown-power outputs: {stale}")
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        metrics = write() if args.write else check()
    except (OSError, ValueError, csv.Error) as exc:
        print(f"crown power: FAIL\n{exc}", file=sys.stderr)
        return 1
    print(
        "crown power: PASS "
        f"({metrics['reforms']} opening reforms; {metrics['sources']} Roman sources; "
        f"{metrics['comparisons']} comparative profiles)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

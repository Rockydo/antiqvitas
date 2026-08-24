#!/usr/bin/env python3
"""Prove opening production reachability and isolate dated late-good demand."""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from collections import defaultdict
from pathlib import Path

from economy_chains import (
    ARMY_STAPLE_GOODS,
    CULTIVATOR_CONSTRUCTION_PACKAGE,
    OPENING_CUSTOM_CULTIVATORS,
    OPENING_STAPLE_BUILDINGS,
    PACKAGE_GOODS,
    UPKEEP_GOODS,
    construction_package,
)
from m5_regional_buildings import (
    FAMILY_CULTURE_GROUP_GATES,
    FAMILY_EXACT_TAG_GATES,
    PRODUCTION_RECIPES,
    ROMAN_ECONOMY_FAMILIES,
    expanded_seed_rows,
)
from s3_cultivator_buildings import load as load_cultivators, opening_seed_rows as cultivator_seeds
from m8_knowledge import (
    advance_records,
    building_content_profiles,
    content_unlocks,
    exact_advance_visible,
    research_profile_maps,
    technology_level,
)


ROOT = Path(__file__).resolve().parents[1]
ACTIVE = ROOT / "docs/m5/active_goods_audit.csv"
RGO = ROOT / "docs/m5/global_rgo_audit.csv"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
MARKETS = ROOT / "docs/m5/markets.csv"
FAMILIES = ROOT / "docs/m5/regional_building_families.csv"
LATER = ROOT / "docs/m5/later_antique_goods.csv"
GOODS_DEFINITIONS = ROOT / "in_game/common/goods/00_antiquitas_raw_goods.txt"
POP_DEMANDS = ROOT / "in_game/common/goods_demand/pop_demands.txt"
CONSTRUCTION_DEMANDS = ROOT / "in_game/common/goods_demand/01_antiquitas_s2_construction_demands.txt"
OPENING_OUTPUT = ROOT / "docs/m5/opening_goods_reachability.csv"
POLITY_OUTPUT = ROOT / "docs/m5/opening_polity_production_matrix.csv"
LATER_OUTPUT = ROOT / "docs/m5/later_goods_demand_audit.csv"
REPORT = ROOT / "docs/m5/OPENING_GOODS_REACHABILITY.md"
ROMAN_GROUPS = {"antq_italic_group", "antq_iberian_group", "antq_balkan_group"}


def rows(path: Path, *, comments: bool = False) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        lines = handle.readlines()
    if comments:
        lines = [line for line in lines if not line.startswith("#")]
    return [
        {key: str(value or "").strip() for key, value in row.items() if key}
        for row in csv.DictReader(lines)
    ]


def csv_text(fieldnames: tuple[str, ...], records: list[dict[str, object]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
    return stream.getvalue()


def opening_model() -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    active_rows = rows(ACTIVE)
    active = {row["good"] for row in active_rows}
    roster = {row["tag"]: row for row in rows(ROSTER)}
    owners = {
        row["location"]: row["tag"] for row in rows(OWNERSHIP, comments=True)
    }
    market_locations = {row["location"] for row in rows(MARKETS)}
    family_rows = {row["key"]: row for row in rows(FAMILIES)}
    later_rows = {row["good"]: row for row in rows(LATER)}
    later_buildings = {row["building"] for row in later_rows.values()}
    rgo_locations: dict[str, set[str]] = defaultdict(set)
    rgo_tags: dict[str, set[str]] = defaultdict(set)
    for row in rows(RGO):
        good, location = row.get("ad1_good", ""), row.get("location", "")
        if good and location:
            rgo_locations[good].add(location)
            if row.get("tag"):
                rgo_tags[good].add(row["tag"])

    seeded_families: set[str] = set()
    seeded_market_families: set[str] = set()
    seeded_tags_by_family: dict[str, set[str]] = defaultdict(set)
    for seed in expanded_seed_rows() + cultivator_seeds():
        family = seed["family"]
        seeded_families.add(family)
        if seed["location"] in market_locations:
            seeded_market_families.add(family)
        owner = owners.get(seed["location"])
        if owner:
            seeded_tags_by_family[family].add(owner)

    tag_profiles, tag_cultures, culture_groups = research_profile_maps()
    family_profiles = building_content_profiles(tag_profiles)
    records = advance_records()
    unlocks = content_unlocks(records)
    unlock_records: dict[str, list[object]] = defaultdict(list)
    for record in records:
        for field, target in unlocks.get(record.key, ()):
            if field == "unlock_building":
                unlock_records[target].append(record)
    missing_unlocks = set(family_rows) - unlock_records.keys()
    if missing_unlocks:
        failures.append(f"building families lack research unlocks: {sorted(missing_unlocks)}")

    opening_by_tag: dict[str, set[str]] = defaultdict(set)
    for tag, polity in roster.items():
        profiles = set(tag_profiles[tag])
        culture = tag_cultures.get(tag, "")
        group = culture_groups.get(culture, "")
        level = technology_level(polity)
        for family, family_unlocks in unlock_records.items():
            intended = family_profiles[family]
            if "shared" not in intended and not profiles.intersection(intended):
                continue
            if family in FAMILY_EXACT_TAG_GATES and tag not in FAMILY_EXACT_TAG_GATES[family]:
                continue
            if family in FAMILY_CULTURE_GROUP_GATES and group not in FAMILY_CULTURE_GROUP_GATES[family]:
                continue
            if family in ROMAN_ECONOMY_FAMILIES and group not in ROMAN_GROUPS:
                continue
            for record in family_unlocks:
                if record.age_index != 0 or min(4, record.depth + 1) > level:
                    continue
                if not exact_advance_visible(record, tag, culture):
                    continue
                opening_by_tag[tag].add(family)
                break

    opening_tags_by_family: dict[str, set[str]] = defaultdict(set)
    for tag, families in opening_by_tag.items():
        for family in families:
            opening_tags_by_family[family].add(tag)

    recipes = dict(PRODUCTION_RECIPES)
    for row in load_cultivators():
        recipes[row["key"]] = (
            row["good"],
            row["output"],
            (("lumber", "0.15"), ("tools", "0.05"), ("livestock", "0.24")),
        )
    construction_inputs = {
        family: {
            good for good, _amount in PACKAGE_GOODS[
                construction_package(
                    family,
                    family_rows[family]["category"] if family in family_rows else "basic_industry_category",
                )
            ]
        }
        for family in recipes
    }
    recipe_inputs = {
        family: {good for good, _amount in recipe[2]}
        for family, recipe in recipes.items()
    }
    output_families: dict[str, set[str]] = defaultdict(set)
    for family, recipe in recipes.items():
        output_families[recipe[0]].add(family)

    reachable = set(rgo_locations)
    proven_families: set[str] = set()
    seeded_proven: set[str] = set()
    constructible_proven: set[str] = set()
    changed = True
    while changed:
        changed = False
        for family, recipe in recipes.items():
            if family in later_buildings:
                continue
            inputs_ready = recipe_inputs[family] <= reachable
            seeded_ready = family in seeded_families and inputs_ready
            build_ready = (
                bool(opening_tags_by_family[family])
                and inputs_ready
                and construction_inputs[family] <= reachable
            )
            if not (seeded_ready or build_ready):
                continue
            if seeded_ready:
                seeded_proven.add(family)
            if build_ready and family not in constructible_proven:
                constructible_proven.add(family)
                changed = True
            if family in proven_families:
                continue
            proven_families.add(family)
            output = recipe[0]
            if output not in reachable:
                reachable.add(output)
                changed = True

    ordinary = active - set(later_rows)
    unreachable = ordinary - reachable
    if unreachable:
        failures.append(f"opening economy has unreachable goods: {sorted(unreachable)}")
    package_goods = {good for values in PACKAGE_GOODS.values() for good, _ in values}
    unreachable_packages = package_goods - reachable
    if unreachable_packages:
        failures.append(f"construction packages contain unreachable goods: {sorted(unreachable_packages)}")

    universal_families = {
        family for family, tags in opening_tags_by_family.items()
        if len(tags) == len(roster)
    }
    # Every map location is assigned to a market by the engine. An RGO or a
    # functioning seeded producer therefore constitutes an opening market
    # source even when it is not itself the market-center location. A newly
    # constructible producer is likewise a valid recovery path; the separate
    # polity matrix does not pretend that every country owns that source.
    market_source: set[str] = set(rgo_locations)
    market_source.update(
        recipes[family][0]
        for family in seeded_proven
        if family in recipes
    )
    market_source.update(
        recipes[family][0]
        for family in constructible_proven
        if family in recipes
    )

    # Opening staples must be recoverable by every polity even if the good is
    # not initially sold in its current market. A seeded workshop is not a
    # constructibility proof.
    missing_staples = sorted(
        family for family in OPENING_STAPLE_BUILDINGS
        if family not in universal_families or family not in constructible_proven
    )
    if missing_staples:
        failures.append(
            "opening staples are not universally day-one constructible: "
            + ", ".join(missing_staples)
        )
    chain_goods = {
        good
        for values in list(PACKAGE_GOODS.values()) + list(UPKEEP_GOODS.values())
        for good, _amount in values
    } | set(ARMY_STAPLE_GOODS)
    for good in sorted(chain_goods):
        if good in rgo_locations:
            continue
        families = output_families.get(good, set())
        if not any(
            family in universal_families and family in constructible_proven
            for family in families
        ):
            failures.append(
                f"construction/upkeep/army good {good} is not universally constructible"
            )

    # Find unresolved dependency cycles, not merely individual missing inputs.
    graph: dict[str, set[str]] = defaultdict(set)
    for family, recipe in recipes.items():
        output = recipe[0]
        graph[output].update(recipe_inputs[family] | construction_inputs[family])
    unresolved_cycles: list[set[str]] = []
    index = 0
    indices: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = low[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for neighbor in graph.get(node, set()):
            if neighbor not in graph:
                continue
            if neighbor not in indices:
                visit(neighbor)
                low[node] = min(low[node], low[neighbor])
            elif neighbor in on_stack:
                low[node] = min(low[node], indices[neighbor])
        if low[node] != indices[node]:
            return
        component: set[str] = set()
        while stack:
            member = stack.pop()
            on_stack.remove(member)
            component.add(member)
            if member == node:
                break
        cyclic = len(component) > 1 or node in graph.get(node, set())
        if cyclic and not component <= reachable:
            unresolved_cycles.append(component)

    for good in sorted(graph):
        if good not in indices:
            visit(good)
    if unresolved_cycles:
        failures.append(
            "unresolved production/construction cycles: "
            + "; ".join(",".join(sorted(group)) for group in unresolved_cycles)
        )

    return ({
        "active_rows": active_rows,
        "active": active,
        "roster": roster,
        "rgo_locations": rgo_locations,
        "rgo_tags": rgo_tags,
        "seeded_families": seeded_families,
        "seeded_tags_by_family": seeded_tags_by_family,
        "opening_by_tag": opening_by_tag,
        "opening_tags_by_family": opening_tags_by_family,
        "universal_families": universal_families,
        "recipe_inputs": recipe_inputs,
        "construction_inputs": construction_inputs,
        "output_families": output_families,
        "reachable": reachable,
        "proven_families": proven_families,
        "seeded_proven": seeded_proven,
        "constructible_proven": constructible_proven,
        "market_source": market_source,
        "later_rows": later_rows,
        "later_buildings": later_buildings,
        "unlock_records": unlock_records,
        "unresolved_cycles": unresolved_cycles,
    }, failures)


def build_outputs() -> tuple[str, str, str, str, dict[str, int]]:
    model, failures = opening_model()
    active_rows: list[dict[str, str]] = model["active_rows"]  # type: ignore[assignment]
    later_rows: dict[str, dict[str, str]] = model["later_rows"]  # type: ignore[assignment]
    rgo_locations: dict[str, set[str]] = model["rgo_locations"]  # type: ignore[assignment]
    output_families: dict[str, set[str]] = model["output_families"]  # type: ignore[assignment]
    opening_tags_by_family: dict[str, set[str]] = model["opening_tags_by_family"]  # type: ignore[assignment]
    reachable: set[str] = model["reachable"]  # type: ignore[assignment]
    seeded_proven: set[str] = model["seeded_proven"]  # type: ignore[assignment]
    constructible_proven: set[str] = model["constructible_proven"]  # type: ignore[assignment]
    market_source: set[str] = model["market_source"]  # type: ignore[assignment]
    unlock_records: dict[str, list[object]] = model["unlock_records"]  # type: ignore[assignment]

    opening_records: list[dict[str, object]] = []
    for row in sorted(active_rows, key=lambda item: item["good"]):
        good = row["good"]
        families = output_families[good]
        seeded = families & seeded_proven
        constructible = families & constructible_proven
        modes: list[str] = []
        if rgo_locations[good]:
            modes.append("rgo")
        if seeded:
            modes.append("seeded")
        if constructible:
            modes.append("constructible")
        if good in later_rows:
            modes.append("later_locked")
        issues: list[str] = []
        if not rgo_locations[good] and not families:
            issues.append("zero_producer")
        elif good not in reachable and good not in later_rows:
            if families and not any(family in seeded_proven for family in families):
                issues.append("locked_producer")
            issues.append("unreachable_input")
        if good not in market_source and good not in later_rows:
            issues.append("market_isolated")
        if (
            row["period_role"].startswith("processed")
            and good not in later_rows
            and not rgo_locations[good]
            and not constructible
        ):
            issues.append("seeded_only_not_constructible")
        opening_records.append({
            "good": good,
            "period_role": row["period_role"],
            "source_modes": ";".join(modes) or "none",
            "rgo_locations": len(rgo_locations[good]),
            "producer_families": ";".join(sorted(families)),
            "seeded_producers": ";".join(sorted(seeded)),
            "day_one_constructible_producers": ";".join(sorted(constructible)),
            "constructible_polities": len(set().union(*(opening_tags_by_family[f] for f in constructible))) if constructible else 0,
            "opening_reachable": "yes" if good in reachable else "no",
            "market_source": "yes" if good in market_source else "no",
            "audit_flags": ";".join(issues) or "pass",
        })
    flagged = [row for row in opening_records if row["audit_flags"] != "pass" and "later_locked" not in row["source_modes"]]
    if flagged:
        failures.append(
            "opening goods retain audit flags: "
            + ", ".join(f"{row['good']}[{row['audit_flags']}]" for row in flagged)
        )

    roster: dict[str, dict[str, str]] = model["roster"]  # type: ignore[assignment]
    rgo_tags: dict[str, set[str]] = model["rgo_tags"]  # type: ignore[assignment]
    seeded_tags_by_family: dict[str, set[str]] = model["seeded_tags_by_family"]  # type: ignore[assignment]
    opening_by_tag: dict[str, set[str]] = model["opening_by_tag"]  # type: ignore[assignment]
    polity_records: list[dict[str, object]] = []
    for tag in sorted(roster):
        for good in sorted(model["active"]):  # type: ignore[arg-type]
            families = output_families[good]
            own_seed = any(
                family in seeded_proven and tag in seeded_tags_by_family[family]
                for family in families
            )
            own_build = any(
                family in constructible_proven and family in opening_by_tag[tag]
                for family in families
            )
            if tag in rgo_tags[good]:
                mode = "owned_rgo"
            elif own_seed:
                mode = "owned_seeded_producer"
            elif own_build:
                mode = "day_one_constructible"
            elif good in later_rows:
                mode = "dated_later_unlock"
            elif good in market_source:
                mode = "opening_market_network"
            elif good in reachable:
                mode = "opening_world_source_runtime_market_probe"
            else:
                mode = "unavailable"
            polity_records.append({
                "tag": tag,
                "name": roster[tag]["name"],
                "good": good,
                "source_mode": mode,
                "status": "pass" if mode != "unavailable" else "fail",
            })
    unavailable = [row for row in polity_records if row["status"] == "fail"]
    if unavailable:
        failures.append(f"polity/good matrix has {len(unavailable)} unavailable opening cells")

    definitions = GOODS_DEFINITIONS.read_text(encoding="utf-8-sig")
    pop_demands = POP_DEMANDS.read_text(encoding="utf-8-sig")
    construction_demands = CONSTRUCTION_DEMANDS.read_text(encoding="utf-8-sig")
    later_records: list[dict[str, object]] = []
    for good, row in sorted(later_rows.items()):
        building = row["building"]
        records = unlock_records[building]
        ages = sorted({record.age_index for record in records})
        input_users = sorted(
            family for family, inputs in model["recipe_inputs"].items()  # type: ignore[union-attr]
            if good in inputs
        )
        expected_age = int(row["age_index"])
        block_match = re.search(
            rf"(?ms)^{re.escape(good)}\s*=\s*\{{(?P<body>.*?)^\}}",
            definitions,
        )
        supply_gated = bool(
            block_match
            and re.search(r"\bno_demand_if_no_market_availability\s*=\s*yes\b", block_match.group("body"))
        )
        checks = {
            "no_ad1_rgo": not rgo_locations[good],
            "no_ad1_seed": building not in model["seeded_families"],  # type: ignore[operator]
            "exact_first_unlock_age": ages == [expected_age],
            "not_recipe_input": not input_users,
            "not_construction_input": not re.search(rf"\b{re.escape(good)}\s*=", construction_demands),
            "supply_gated_pop_demand": good in pop_demands and supply_gated,
            "not_opening_reachable": good not in reachable,
        }
        status = "pass" if all(checks.values()) else "fail"
        if status == "fail":
            failures.append(
                f"{good}: late-demand isolation failed "
                + ",".join(name for name, passed in checks.items() if not passed)
            )
        later_records.append({
            "good": good,
            "building": building,
            "first_age_index": min(ages) if ages else "",
            "expected_age_index": expected_age,
            "profiles": row["profile"],
            "rgo_locations": len(rgo_locations[good]),
            "seeded_at_ad1": "yes" if building in model["seeded_families"] else "no",  # type: ignore[operator]
            "recipe_input_users": ";".join(input_users),
            "construction_input": "yes" if re.search(rf"\b{re.escape(good)}\s*=", construction_demands) else "no",
            "pop_demand_gate": "market_availability" if supply_gated else "missing",
            "opening_reachable": "yes" if good in reachable else "no",
            "status": status,
        })

    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    opening_text = csv_text((
        "good", "period_role", "source_modes", "rgo_locations",
        "producer_families", "seeded_producers", "day_one_constructible_producers",
        "constructible_polities", "opening_reachable", "market_source", "audit_flags",
    ), opening_records)
    polity_text = csv_text(("tag", "name", "good", "source_mode", "status"), polity_records)
    later_text = csv_text((
        "good", "building", "first_age_index", "expected_age_index", "profiles",
        "rgo_locations", "seeded_at_ad1", "recipe_input_users", "construction_input",
        "pop_demand_gate", "opening_reachable", "status",
    ), later_records)
    modes: dict[str, int] = defaultdict(int)
    for row in polity_records:
        modes[str(row["source_mode"])] += 1
    report = "\n".join((
        "# Opening Goods Reachability",
        "",
        "Generated by `tools/s7_goods_reachability.py`. This is an unlock-aware",
        "fixed-point proof over RGOs, AD 1 seeds, productive recipes, and each",
        "building's construction basket. A producer counts only after both its",
        "operating inputs and, when unbuilt, construction inputs are reachable.",
        "",
        f"- {len(opening_records)} active goods audited; {len(model['reachable'])} are opening-reachable and {len(later_records)} are deliberately dated.",
        f"- {len(model['proven_families'])} productive families participate in the opening fixed point.",
        f"- {len(model['universal_families'])} building families are day-one constructible by every polity.",
        f"- {len(polity_records)} polity/good cells cover all {len(roster)} opening polities.",
        "- Opening staple workshops use raw-material construction baskets and",
        "  universally owned Age-I depth-zero unlocks. A seeded producer never",
        "  satisfies constructibility, and construction/upkeep goods must be",
        "  RGOs or universally constructible.",
        "- Later specialties have no AD 1 RGO, seed, recipe-input, or construction",
        "  demand. Population demand is inert until market availability exists.",
        "",
        "Per-polity source modes:",
        "",
        *(f"- {key}: {modes[key]}" for key in sorted(modes)),
        "",
        "`opening_world_source_runtime_market_probe` is deliberately not a claim",
        "about live market membership. It identifies globally reachable supply whose",
        "specific market connection remains a runtime gate obligation.",
        "",
    ))
    metrics = {
        "goods": len(opening_records),
        "reachable": len(model["reachable"]),  # type: ignore[arg-type]
        "later": len(later_records),
        "polities": len(roster),
        "matrix_cells": len(polity_records),
        "families": len(model["proven_families"]),  # type: ignore[arg-type]
    }
    return opening_text, polity_text, later_text, report, metrics


def write() -> dict[str, int]:
    opening, polity, later, report, metrics = build_outputs()
    OPENING_OUTPUT.write_text(opening, encoding="utf-8-sig", newline="")
    POLITY_OUTPUT.write_text(polity, encoding="utf-8-sig", newline="")
    LATER_OUTPUT.write_text(later, encoding="utf-8-sig", newline="")
    REPORT.write_text(report, encoding="utf-8", newline="")
    return metrics


def check() -> dict[str, int]:
    opening, polity, later, report, metrics = build_outputs()
    expected = {
        OPENING_OUTPUT: opening,
        POLITY_OUTPUT: polity,
        LATER_OUTPUT: later,
        REPORT: report,
    }
    stale = [str(path.relative_to(ROOT)) for path, text in expected.items() if not path.is_file() or path.read_text(encoding="utf-8-sig") != text]
    if stale:
        raise ValueError(f"stale reachability outputs: {stale}")
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
        print(f"goods reachability: FAIL\n{exc}", file=sys.stderr)
        return 1
    print(
        "goods reachability: PASS "
        f"({metrics['goods']} goods; {metrics['reachable']} opening; "
        f"{metrics['later']} dated; {metrics['polities']} polities; "
        f"{metrics['matrix_cells']} matrix cells)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

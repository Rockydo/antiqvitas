#!/usr/bin/env python3
"""Audit systemic stability, estates, civil wars, and AI/script errors from a save."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from m6_ruler_runtime import GameDate, brace_delta, default_save
from save_melt import plaintext_save


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_STARTING_POLITIES = 463
BLOCK_START = re.compile(r"^(\d+)=\{$")
VANILLA_AI_BASELINE = ROOT / "docs/playtests/V108_VANILLA_WARTIME_COMMAND_BASELINE.json"
EXPECTED_BASELINE_VERSION = "1.3.11 (Pavia)"
ANCIENT_UNIT_TYPES = ROOT / "in_game/common/unit_types/00_antiquitas_m7_units.txt"
NATIVE_BASELINED_COMMANDS = frozenset({
    "change_trade_capacity",
    "diplomaticactioncommand",
    "merge_army",
    "move_unit",
    "perform_generic_action",
    "set_unit_activity",
    "toggle_can_attach_to",
    "transfer_occupation",
})
EXPECTED_PORTABLE_MERCENARY_ALTERNATIVES = frozenset({
    "antq_hired_horse_company",
    "antq_local_retainer_company",
})
EXPECTED_MERCENARY_CLASSES = frozenset({
    "a_age_1_traditions_heavy_infantry",
    "a_age_1_traditions_light_infantry",
    "a_age_1_traditions_light_cavalry",
})
EXPECTED_LIVE_REGIONAL_MERCENARY_GROUPS = {
    "germanic": frozenset({"antq_germanic_bodyguards"}),
    "mediterranean": frozenset({
        "antq_cretan_archers", "antq_dacian_falxmen",
        "antq_galatian_swordsmen", "antq_thracian_peltasts",
    }),
    "indic": frozenset({
        "antq_deccan_spear_company", "antq_indian_longbow_company",
    }),
    "african": frozenset({"antq_sahel_javelin_company"}),
    "american": frozenset({"antq_mesoamerican_atlatl_company"}),
    "iranian_steppe": frozenset({"antq_armenian_horse", "antq_saka_horse"}),
}


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("cannot calculate a percentile of an empty sample")
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def mercenary_audit(path: Path) -> dict[str, object]:
    """Audit the instantiated production-save mercenary army manager.

    Static availability cannot prove what EU5 instantiates. Version 1.3.11
    anchors ordinary cells by combat class, then substitutes an eligible
    regional company for the universal representative of that same class.
    Recording class coverage and the winning regional representatives prevents
    a superficially valid roster from hiding missing roles or a depleted manager.
    """
    in_manager = False
    manager_depth = 0
    in_army = False
    army_depth = 0
    in_availability = False
    availability_depth = 0
    current: dict[str, int] = {}
    cells: list[dict[str, int]] = []
    cell_leaders: list[int | None] = []
    current_leader: int | None = None
    states: Counter[str] = Counter()
    manager_found = False
    army_found = False

    with path.open(encoding="utf-8-sig", errors="strict") as handle:
        for raw in handle:
            line = raw.strip()
            delta = brace_delta(raw)
            if not in_manager:
                if line == "mercenary_manager={":
                    in_manager = True
                    manager_found = True
                    manager_depth = delta
                continue

            manager_depth += delta
            if not in_army:
                if line == "Army={":
                    in_army = True
                    army_found = True
                    army_depth = delta
                if manager_depth == 0:
                    break
                continue

            army_depth += delta
            if not in_availability and line == "availability={":
                in_availability = True
                availability_depth = delta
                current = {}
                continue
            if in_availability:
                availability_depth += delta
                match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_]*)=(\d+)", line)
                if match:
                    current[match.group(1)] = int(match.group(2))
                if availability_depth == 0:
                    cells.append(current)
                    cell_leaders.append(current_leader)
                    current_leader = None
                    in_availability = False
                continue

            leader_match = re.fullmatch(r"leader=(\d+)", line)
            if leader_match:
                current_leader = int(leader_match.group(1))
            state_match = re.fullmatch(r"state=([A-Za-z_]+)", line)
            if state_match:
                states[state_match.group(1)] += 1
            if army_depth == 0:
                in_army = False
            if manager_depth == 0:
                break

    unit_totals: Counter[str] = Counter()
    for cell in cells:
        unit_totals.update(cell)
    depths = [sum(cell.values()) for cell in cells]
    role_counts = [sum(value > 0 for value in cell.values()) for cell in cells]
    live_units = frozenset(unit_totals)
    unit_text = ANCIENT_UNIT_TYPES.read_text(encoding="utf-8-sig")
    unit_classes: dict[str, str] = {}
    for match in re.finditer(
        r"(?ms)^(antq_[a-z0-9_]+)\s*=\s*\{(.*?)(?=^antq_[a-z0-9_]+\s*=\s*\{|\Z)",
        unit_text,
    ):
        base = re.search(r"^\s*copy_from\s*=\s*([A-Za-z0-9_]+)", match.group(2), re.MULTILINE)
        if base:
            unit_classes[match.group(1)] = base.group(1)
    cell_classes = [
        {
            unit_classes.get(unit, "unknown")
            for unit, count in cell.items()
            if count > 0
        }
        for cell in cells
    ]
    missing_class_cells = {
        unit_class: sum(unit_class not in classes for classes in cell_classes)
        for unit_class in sorted(EXPECTED_MERCENARY_CLASSES)
    }
    deficient_cells = [
        {
            "cell_index": index,
            "leader": cell_leaders[index],
            "depth": sum(cells[index].values()),
            "units": cells[index],
            "classes": sorted(classes),
            "missing_classes": sorted(EXPECTED_MERCENARY_CLASSES - classes),
        }
        for index, classes in enumerate(cell_classes)
        if EXPECTED_MERCENARY_CLASSES - classes
    ]
    class_representatives = {
        unit_class: dict(Counter(
            unit
            for cell in cells
            for unit, count in cell.items()
            if count > 0 and unit_classes.get(unit) == unit_class
        ).most_common())
        for unit_class in sorted(EXPECTED_MERCENARY_CLASSES)
    }
    portable_cell_coverage = {
        unit: sum(cell.get(unit, 0) > 0 for cell in cells)
        for unit in sorted(EXPECTED_PORTABLE_MERCENARY_ALTERNATIVES)
    }
    return {
        "manager_found": manager_found,
        "army_pool_found": army_found,
        "cells": len(cells),
        "empty_cells": sum(depth == 0 for depth in depths),
        "one_role_cells": sum(count < 2 for count in role_counts),
        "minimum_cell_depth": min(depths) if depths else 0,
        "median_cell_depth": (
            percentile([float(value) for value in depths], 0.50) if depths else 0
        ),
        "total_subunits": sum(depths),
        "leader_states": dict(states.most_common()),
        "unit_totals": dict(unit_totals.most_common()),
        "missing_portable_alternatives": sorted(
            EXPECTED_PORTABLE_MERCENARY_ALTERNATIVES - live_units
        ),
        "missing_class_cells": {
            unit_class: missing
            for unit_class, missing in missing_class_cells.items()
            if missing
        },
        "deficient_cells": deficient_cells,
        "class_representatives": class_representatives,
        "regional_group_coverage": {
            group: sorted(units & live_units)
            for group, units in EXPECTED_LIVE_REGIONAL_MERCENARY_GROUPS.items()
        },
        "missing_regional_groups": sorted(
            group
            for group, units in EXPECTED_LIVE_REGIONAL_MERCENARY_GROUPS.items()
            if not units & live_units
        ),
        "portable_cell_coverage": portable_cell_coverage,
    }


def manager_audit(path: Path) -> tuple[
    GameDate,
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, int],
    list[dict[str, object]],
    list[dict[str, object]],
    dict[int, dict[str, object]],
    set[int],
    set[int],
]:
    targets = {
        "estate_manager", "countries", "war_manager", "disease_outbreak_manager",
        "construction_manager",
        "building_manager",
        "culture_manager", "religion_manager",
    }
    manager = ""
    manager_depth = 0
    database_depth: int | None = None
    block_id: int | None = None
    block_depth = 0
    block_lines: list[str] = []
    date: GameDate | None = None
    countries: list[dict[str, object]] = []
    estates: list[dict[str, object]] = []
    wars = {"distinct_civil_wars": 0, "active_wars": 0, "active_civil_wars": 0}
    outbreaks: list[dict[str, object]] = []
    constructions: list[dict[str, object]] = []
    buildings: dict[int, dict[str, object]] = {}
    cultures: set[int] = set()
    religions: set[int] = set()

    def scalar(text: str, key: str) -> str | None:
        match = re.search(rf"(?m)^\s*{re.escape(key)}=([^\s{{}}]+)\s*$", text)
        return match.group(1).strip('"') if match else None

    def named_block(text: str, key: str) -> str:
        """Return a complete direct named block, including nested child blocks."""
        lines = text.splitlines()
        start_pattern = re.compile(rf"^\s*{re.escape(key)}=\{{\s*$")
        for index, line in enumerate(lines):
            if not start_pattern.match(line):
                continue
            depth = brace_delta(line)
            body: list[str] = []
            for child in lines[index + 1:]:
                depth += brace_delta(child)
                if depth == 0:
                    return "\n".join(body)
                body.append(child)
            break
        return ""

    def finish_block(identity: int, text: str) -> None:
        if manager == "countries":
            country_type = scalar(text, "country_type")
            province_match = re.search(r"(?m)^\s*provinces=\{([^}]*)\}", text)
            province_count = (
                len(re.findall(r"\d+", province_match.group(1)))
                if province_match else 0
            )
            currency = re.search(
                r"(?ms)^\s*currency_data=\{(?P<body>.*?)^\s*\}", text
            )
            stability = None
            gold = 0.0
            if currency:
                value = scalar(currency.group("body"), "stability")
                stability = float(value) if value is not None else None
                gold = float(scalar(currency.group("body"), "gold") or 0.0)
            economy_body = named_block(text, "economy")

            def economy_float(key: str) -> float:
                value = scalar(economy_body, key)
                return float(value) if value is not None else 0.0

            countries.append({
                "id": identity,
                "name": scalar(text, "country_name"),
                "tag": scalar(text, "definition"),
                "type": country_type,
                "province_count": province_count,
                "stability": stability,
                "gold": gold,
                "great_power": scalar(text, "great_power") == "yes",
                "population_thousands": float(
                    scalar(text, "last_months_population") or 0.0
                ),
                # The economy's ``bankrupt`` scalar is retained as historical
                # metadata after the five-year penalty expires.  The timed
                # modifier is the authoritative active-state contract used by
                # ANTIQVITAS's low-year bankruptcy adapter.
                "bankrupt_at": scalar(text, "bankrupt"),
                "bankruptcy_active": (
                    "modifier=antq_genuine_bankruptcy" in text
                    or "modifier = antq_genuine_bankruptcy" in text
                ),
                "debt": economy_float("total_debt"),
                "loan_capacity": economy_float("loan_capacity"),
                "monthly_income": economy_float("income"),
                "monthly_expense": economy_float("expense"),
                "primary_culture": (
                    int(value) if (value := scalar(text, "primary_culture")) is not None
                    else None
                ),
                "primary_religion": (
                    int(value) if (value := scalar(text, "primary_religion")) is not None
                    else None
                ),
            })
        elif manager == "estate_manager":
            country = scalar(text, "country")
            satisfaction = scalar(text, "satisfaction")
            existence = scalar(text, "existence")
            estate_type = scalar(text, "estate_type")
            if country is not None and satisfaction is not None and existence == "yes":
                estates.append({
                    "id": identity,
                    "country": int(country),
                    "estate_type": estate_type,
                    "satisfaction": float(satisfaction),
                    "culture": (
                        int(value) if (value := scalar(text, "culture")) is not None
                        else None
                    ),
                    "religion": (
                        int(value) if (value := scalar(text, "religion")) is not None
                        else None
                    ),
                })
        elif manager == "war_manager":
            if "CIVIL_WAR_NAME" in text:
                wars["distinct_civil_wars"] += 1
            if "end_date=" not in text:
                wars["active_wars"] += 1
                if "CIVIL_WAR_NAME" in text:
                    wars["active_civil_wars"] += 1
        elif manager == "disease_outbreak_manager":
            disease_type = scalar(text, "type")
            if disease_type and disease_type != "malaria":
                affected = re.search(
                    r"(?m)^\s*locations_ever_affected=(?:\{([^}]*)\}|(\d+))",
                    text,
                )
                affected_ids: set[int] = set()
                if affected:
                    if affected.group(1) is not None:
                        values = [int(value) for value in re.findall(r"\d+", affected.group(1))]
                        # The manager serializes { location presence ... }.
                        affected_ids.update(values[::2])
                    elif affected.group(2) is not None:
                        affected_ids.add(int(affected.group(2)))
                outbreaks.append({
                    "id": identity,
                    "type": disease_type,
                    "outbreak_date": scalar(text, "outbreak_date"),
                    "died_out_date": scalar(text, "died_out_date"),
                    "affected_locations": len(affected_ids),
                })
        elif manager == "construction_manager" and "type=CIVIL" in text:
            spent = named_block(text, "actual_currency_spent")
            constructions.append({
                "id": identity,
                "country": int(scalar(text, "country") or 0),
                "payer": int(scalar(text, "payer") or 0),
                "building": int(scalar(text, "building") or 0),
                "demand": scalar(text, "demand"),
                "location": int(scalar(text, "location") or 0),
                "rgo_upgrade": scalar(text, "upgrade_rgo") == "yes",
                "gold_spent": float(scalar(spent, "gold") or 0.0),
                "progress": float(scalar(text, "progress") or 0.0),
                "total": float(scalar(text, "total") or 0.0),
            })
        elif manager == "building_manager":
            building_type = scalar(text, "type")
            if building_type is not None:
                buildings[identity] = {
                    "type": building_type,
                    "owner": int(scalar(text, "owner") or 0),
                    "location": int(scalar(text, "location") or 0),
                }
        elif manager == "culture_manager":
            if scalar(text, "name") is not None:
                cultures.add(identity)
        elif manager == "religion_manager":
            if scalar(text, "name") is not None:
                religions.add(identity)

    with path.open(encoding="utf-8-sig", errors="replace") as handle:
        for raw in handle:
            line = raw.rstrip("\r\n")
            stripped = line.strip()
            if date is None and stripped.startswith("date="):
                date = GameDate.parse(stripped.removeprefix("date="))

            if block_id is not None:
                block_lines.append(line)
                block_depth += brace_delta(line)
                if block_depth == 0:
                    finish_block(block_id, "\n".join(block_lines))
                    block_id = None
                    block_lines = []
                continue

            if not manager:
                candidate = stripped.removesuffix("={")
                if stripped.endswith("={") and candidate in targets:
                    manager = candidate
                    manager_depth = 1
                    database_depth = None
                continue

            before = manager_depth
            start = BLOCK_START.fullmatch(stripped)
            if start and database_depth is not None and before == database_depth:
                block_id = int(start.group(1))
                block_lines = [line]
                block_depth = brace_delta(line)
                continue
            if stripped == "database={" and database_depth is None:
                database_depth = before + 1
            manager_depth += brace_delta(line)
            if manager_depth == 0:
                manager = ""
                database_depth = None

    if date is None:
        raise RuntimeError(f"no metadata date found in {path}")
    return (
        date, countries, estates, wars, outbreaks, constructions, buildings,
        cultures, religions,
    )


def log_audit(path: Path | None, ai_path: Path | None = None) -> dict[str, object]:
    """Audit both script and AI command logs for runtime-invalid behavior.

    EU5 writes script failures to ``error.log`` but emits the high-volume
    command-validation failures to ``ai.log``.  Treating error.log as the whole
    runtime surface allowed V25's 141,000+ invalid generic-action postings to
    escape the stability gate, so a supplied error log now automatically pulls
    in its sibling AI log unless the caller names another one explicitly.
    """
    if ai_path is None and path is not None:
        ai_path = path.with_name("ai.log")
    script_errors = 0
    ai_errors = 0
    missing_logs = [
        str(candidate)
        for candidate in (path, ai_path)
        if candidate is not None and not candidate.is_file()
    ]
    locations: Counter[str] = Counter()
    invalid_commands: Counter[str] = Counter()
    pending_script = False
    if path is not None and path.is_file():
        with path.open(encoding="utf-8-sig", errors="replace") as handle:
            for raw in handle:
                lower = raw.lower()
                if "script system error!" in lower:
                    script_errors += 1
                    pending_script = True
                elif pending_script and "script location:" in lower:
                    locations[raw.strip().removeprefix("Script location: ")] += 1
                    pending_script = False
                if (
                    ("ai" in lower and "command" in lower and "error" in lower)
                    or "invalid ai command" in lower
                    or "failed to execute ai" in lower
                ):
                    ai_errors += 1
    if ai_path is not None and ai_path.is_file():
        patterns = (
            re.compile(r"AI posting invalid commands?:\s*([^\s.]+)", re.IGNORECASE),
            re.compile(
                r"AI tried to execute invalid command:\s*([^\s.]+)",
                re.IGNORECASE,
            ),
            re.compile(r"invalid AI command:\s*([^\s.]+)", re.IGNORECASE),
            re.compile(r"failed to execute AI(?: command)?:?\s*([^\s.]*)", re.IGNORECASE),
        )
        with ai_path.open(encoding="utf-8-sig", errors="replace") as handle:
            for raw in handle:
                # Audit can run while EU5 is still writing this log.  Its file
                # buffer is observable at arbitrary byte boundaries (the R27
                # AD2 checkpoint ended at exactly 8192 bytes with
                # ``change_trad``), so the final non-newline fragment is not a
                # record and must not be classified as a distinct command.
                if not raw.endswith(("\n", "\r")) and not raw.rstrip().endswith("."):
                    continue
                for pattern in patterns:
                    match = pattern.search(raw)
                    if not match:
                        continue
                    command = (match.group(1) or "unknown").strip().rstrip(".")
                    invalid_commands[command] += 1
                    ai_errors += 1
                    break
    return {
        "path": str(path) if path else None,
        "ai_path": str(ai_path) if ai_path else None,
        "missing_logs": missing_logs,
        "script_errors": script_errors,
        "ai_command_errors": ai_errors,
        "invalid_ai_commands": dict(invalid_commands.most_common()),
        "locations": dict(locations.most_common()),
    }


def classify_ai_commands(log: dict[str, object], elapsed_years: float) -> dict[str, object]:
    """Separate proven stock-engine warning families from actionable errors.

    The matched unmodified 1.3.11 control emits ``change_trade_capacity`` while
    its automated trade queue adjusts routes and ``diplomaticactioncommand``
    when diplomatic objectives become stale between planning and execution.
    An uninterrupted eleven-year stock wartime control also directly reproduced
    the engine's attach, merge, move-unit, generic-action, unit-activity, and
    occupation-transfer command races.  Mercenary hiring and consolidation did
    not occur in that long control and remain actionable.
    No other command is excused.  Each exact stock rate is scaled by campaign
    length, so a regression or high-volume loop still fails instead of becoming
    a blanket ignore list.
    """
    baseline = json.loads(VANILLA_AI_BASELINE.read_text(encoding="utf-8-sig"))
    if baseline.get("game_version") != EXPECTED_BASELINE_VERSION:
        raise RuntimeError("vanilla AI-command baseline game version drift")
    if baseline.get("mode") != "vanilla" or baseline.get("process_exit_during_sample"):
        raise RuntimeError("vanilla AI-command baseline is not a completed stock control")
    baseline_counts = baseline.get("invalid_ai_commands")
    if not isinstance(baseline_counts, dict):
        raise RuntimeError("vanilla AI-command baseline lacks its command ledger")
    sample_years = float(baseline.get("sample_years", 0))
    if sample_years <= 0:
        raise RuntimeError("vanilla AI-command baseline lacks a positive sample duration")
    observed = Counter({
        str(key): int(value)
        for key, value in dict(log.get("invalid_ai_commands", {})).items()
    })
    limits = {
        command: math.ceil(
            (int(baseline_counts[command]) / sample_years)
            * max(1.0, elapsed_years)
        )
        for command in NATIVE_BASELINED_COMMANDS
    }
    baselined = {
        command: count
        for command, count in observed.items()
        if command in limits and count <= limits[command]
    }
    actionable = {
        command: count
        for command, count in observed.items()
        if command not in baselined
    }
    return {
        "control": str(VANILLA_AI_BASELINE),
        "control_game_version": baseline["game_version"],
        "control_sample_years": sample_years,
        "native_warning_limits": limits,
        "native_baseline_ai_warnings": baselined,
        "actionable_invalid_ai_commands": actionable,
        "actionable_ai_command_errors": sum(actionable.values()),
    }


def audit(
    save: Path,
    error_log: Path | None,
    ai_log: Path | None = None,
) -> tuple[dict[str, object], list[str]]:
    (
        date, countries, estates, wars, outbreaks, constructions, buildings,
        cultures, religions,
    ) = manager_audit(save)
    real = [
        country for country in countries
        if country["type"] == "Real" and country["province_count"] > 0
        and country["stability"] is not None
    ]
    stabilities = [float(country["stability"]) for country in real]
    historical_bankrupt = [country for country in real if country["bankrupt_at"] is not None]
    bankrupt = [country for country in real if bool(country["bankruptcy_active"])]
    major_bankrupt = [
        country for country in bankrupt
        if bool(country["great_power"]) or int(country["province_count"]) >= 25
    ]
    debt_rows: list[dict[str, object]] = []
    for country in real:
        debt = float(country["debt"])
        monthly_income = float(country["monthly_income"])
        if debt <= 0:
            continue
        annual_income = monthly_income * 12
        debt_rows.append({
            "id": country["id"],
            "tag": country["tag"],
            "name": country["name"],
            "province_count": country["province_count"],
            "great_power": country["great_power"],
            "debt": debt,
            "loan_capacity": country["loan_capacity"],
            "monthly_income": monthly_income,
            "monthly_expense": country["monthly_expense"],
            "debt_to_annual_income": (
                debt / annual_income if annual_income > 0 else None
            ),
        })
    debt_rows.sort(key=lambda row: float(row["debt"]), reverse=True)
    major_economies = [
        {
            "id": country["id"],
            "tag": country["tag"],
            "name": country["name"],
            "province_count": country["province_count"],
            "great_power": country["great_power"],
            "population_thousands": country["population_thousands"],
            "gold": country["gold"],
            "debt": country["debt"],
            "loan_capacity": country["loan_capacity"],
            "monthly_income": country["monthly_income"],
            "monthly_expense": country["monthly_expense"],
            "debt_to_annual_income": (
                float(country["debt"]) / (float(country["monthly_income"]) * 12)
                if float(country["debt"]) > 0
                and float(country["monthly_income"]) > 0
                else 0.0
            ),
            "years_of_surplus_to_repay_debt": (
                float(country["debt"])
                / (
                    (float(country["monthly_income"]) - float(country["monthly_expense"]))
                    * 12
                )
                if float(country["debt"]) > 0
                and float(country["monthly_income"]) > float(country["monthly_expense"])
                else (None if float(country["debt"]) > 0 else 0.0)
            ),
            "bankrupt_at": country["bankrupt_at"],
            "bankruptcy_active": country["bankruptcy_active"],
        }
        for country in real
        if bool(country["great_power"]) or int(country["province_count"]) >= 25
    ]
    major_economies.sort(key=lambda row: int(row["province_count"]), reverse=True)
    country_by_id = {int(country["id"]): country for country in real}
    estate_identity_differences: list[dict[str, object]] = []
    estate_identity_failures: list[dict[str, object]] = []
    for estate in estates:
        # Crown is an ownership bucket, not a population estate, and therefore
        # intentionally has no culture/religion identity.  Population estates
        # may legitimately represent a local dominant culture or religion that
        # differs from the state: vanilla's ``pa_accept_estate_culture`` agenda
        # explicitly depends on that distinction.  The runtime invariant is
        # therefore completeness and referential integrity, not forced identity
        # with the country.  Preserve differences as diversity diagnostics.
        if estate["estate_type"] == "crown_estate":
            continue
        country = country_by_id.get(int(estate["country"]))
        if country is None:
            continue
        invalid_fields: list[str] = []
        if estate["culture"] is None or estate["culture"] not in cultures:
            invalid_fields.append("culture")
        if estate["religion"] is None or estate["religion"] not in religions:
            invalid_fields.append("religion")
        if invalid_fields:
            estate_identity_failures.append({
                "estate_id": estate["id"],
                "estate_type": estate["estate_type"],
                "country_id": country["id"],
                "tag": country["tag"],
                "fields": invalid_fields,
                "estate_culture": estate["culture"],
                "estate_religion": estate["religion"],
            })
        difference_fields: list[str] = []
        if estate["culture"] != country["primary_culture"]:
            difference_fields.append("culture")
        if estate["religion"] != country["primary_religion"]:
            difference_fields.append("religion")
        if difference_fields:
            estate_identity_differences.append({
                "estate_id": estate["id"],
                "estate_type": estate["estate_type"],
                "country_id": country["id"],
                "tag": country["tag"],
                "fields": difference_fields,
                "estate_culture": estate["culture"],
                "country_culture": country["primary_culture"],
                "estate_religion": estate["religion"],
                "country_religion": country["primary_religion"],
            })
    construction_by_country: defaultdict[int, list[dict[str, object]]] = defaultdict(list)
    for construction in constructions:
        construction_by_country[int(construction["payer"])].append(construction)
    construction_rows: list[dict[str, object]] = []
    for country_id, projects in construction_by_country.items():
        country = country_by_id.get(country_id)
        if country is None:
            continue
        project_types: Counter[str] = Counter()
        for project in projects:
            if bool(project["rgo_upgrade"]):
                project_types["rgo_upgrade"] += 1
            else:
                building = buildings.get(int(project["building"]))
                project_types[str(building["type"]) if building else "unknown_building"] += 1
        construction_rows.append({
            "id": country_id,
            "tag": country["tag"],
            "name": country["name"],
            "province_count": country["province_count"],
            "great_power": country["great_power"],
            "active_projects": len(projects),
            "rgo_upgrades": sum(bool(project["rgo_upgrade"]) for project in projects),
            "building_projects": sum(not bool(project["rgo_upgrade"]) for project in projects),
            "gold_committed": sum(float(project["gold_spent"]) for project in projects),
            "project_types": dict(project_types.most_common()),
        })
    construction_rows.sort(
        key=lambda row: (int(row["active_projects"]), float(row["gold_committed"])),
        reverse=True,
    )
    estate_by_country: defaultdict[int, list[float]] = defaultdict(list)
    for estate in estates:
        estate_by_country[int(estate["country"])].append(float(estate["satisfaction"]))
    estate_values = [float(estate["satisfaction"]) for estate in estates]
    polity_estate_means = [
        sum(values) / len(values) for values in estate_by_country.values() if values
    ]
    elapsed_years = max(1.0, date.year - 1 + (date.month - 1) / 12 + (date.day - 1) / 365)
    incidence = wars["distinct_civil_wars"] / (
        EXPECTED_STARTING_POLITIES * elapsed_years
    )
    log = log_audit(error_log, ai_log)
    log.update(classify_ai_commands(log, elapsed_years))
    mercenaries = mercenary_audit(save)
    save_year = date.year + (date.month - 1) / 12 + (date.day - 1) / 365
    epidemic_rows: list[dict[str, object]] = []
    for outbreak in outbreaks:
        raw_date = outbreak["outbreak_date"]
        if not isinstance(raw_date, str):
            continue
        outbreak_date = GameDate.parse(raw_date)
        outbreak_year = (
            outbreak_date.year
            + (outbreak_date.month - 1) / 12
            + (outbreak_date.day - 1) / 365
        )
        age_years = max(1 / 365, save_year - outbreak_year)
        affected_locations = int(outbreak["affected_locations"])
        epidemic_rows.append({
            **outbreak,
            "age_years": age_years,
            "affected_locations_per_year": affected_locations / age_years,
        })
    result: dict[str, object] = {
        "save": str(save),
        "date": str(date),
        "real_polities": len(real),
        "stability": {
            "minimum": min(stabilities),
            "p10": percentile(stabilities, 0.10),
            "median": percentile(stabilities, 0.50),
            "p90": percentile(stabilities, 0.90),
            "maximum": max(stabilities),
            "negative_count": sum(value < 0 for value in stabilities),
            "severe_count": sum(value < -5 for value in stabilities),
        },
        "solvency": {
            "bankrupt_count": len(bankrupt),
            "bankrupt_polities": bankrupt,
            "historical_bankrupt_count": len(historical_bankrupt),
            "historical_bankrupt_polities": historical_bankrupt,
            "major_bankrupt_count": len(major_bankrupt),
            "major_bankrupt_polities": major_bankrupt,
            "indebted_count": len(debt_rows),
            "largest_debts": debt_rows[:20],
            "major_economies": major_economies,
        },
        "construction": {
            "active_projects": len(constructions),
            "active_payers": len(construction_rows),
            "busiest_payers": construction_rows[:30],
            # Retain the complete payer ledger for country-specific trend and
            # bankruptcy diagnosis.  A top-N list alone hid the one-province
            # queues that precipitated several AD 6 insolvencies.
            "all_payers": construction_rows,
        },
        "estates": {
            "records": len(estate_values),
            "minimum": min(estate_values),
            "p10": percentile(estate_values, 0.10),
            "median": percentile(estate_values, 0.50),
            "polity_mean_p10": percentile(polity_estate_means, 0.10),
            "below_10_percent": sum(value < 0.10 for value in estate_values),
            "below_25_percent": sum(value < 0.25 for value in estate_values),
            "identity_definition_counts": {
                "cultures": len(cultures),
                "religions": len(religions),
            },
            "identity_failure_count": len(estate_identity_failures),
            "identity_failures": estate_identity_failures,
            "identity_difference_count": len(estate_identity_differences),
            "identity_differences": estate_identity_differences,
        },
        "wars": {
            **wars,
            "elapsed_years": elapsed_years,
            "civil_wars_per_polity_year": incidence,
        },
        "epidemics": {
            "non_endemic_outbreaks": len(epidemic_rows),
            "outbreaks": epidemic_rows,
        },
        "mercenaries": mercenaries,
        "log": log,
    }
    failures: list[str] = []
    if len(real) < 400:
        failures.append(f"only {len(real)} substantive real polities survive")
    if percentile(stabilities, 0.10) < -5:
        failures.append(f"stability p10 is systemically severe: {percentile(stabilities, 0.10):.3f}")
    if sum(value < 0 for value in stabilities) / len(stabilities) > 0.30:
        failures.append("more than 30% of substantive polities have negative stability")
    if sum(value < -5 for value in stabilities) / len(stabilities) > 0.10:
        failures.append("more than 10% of substantive polities have severe stability")
    if major_bankrupt:
        labels = ", ".join(
            f"{country['tag']} ({country['province_count']} provinces)"
            for country in major_bankrupt
        )
        failures.append(f"major polities are bankrupt: {labels}")
    if len(bankrupt) / len(real) > 0.02:
        failures.append(
            f"bankruptcy is systemic: {len(bankrupt)}/{len(real)} substantive polities"
        )
    if percentile(polity_estate_means, 0.10) < 0.20:
        failures.append(
            f"polity estate-mean p10 is below 20%: {percentile(polity_estate_means, 0.10):.3%}"
        )
    if estate_identity_failures:
        failures.append(
            f"{len(estate_identity_failures)} existing population estates have "
            "a missing or unresolved culture/religion identity"
        )
    if incidence > 0.005:
        failures.append(f"civil-war incidence is systemic: {incidence:.4%} per polity-year")
    if wars["active_civil_wars"] > max(5, math.ceil(len(real) * 0.02)):
        failures.append(f"{wars['active_civil_wars']} civil wars are concurrently active")
    # The first-century production gate precedes the scripted Antonine and
    # Cyprian pandemics.  An ordinary outbreak may cross a regional corridor,
    # but hundreds of new locations per year is the modern-style global relay
    # explicitly forbidden by the design contract.
    if date.year <= 100:
        for outbreak in epidemic_rows:
            if (
                float(outbreak["age_years"]) >= 0.25
                and int(outbreak["affected_locations"]) > 200
                and float(outbreak["affected_locations_per_year"]) > 200
            ):
                failures.append(
                    f"{outbreak['type']} outbreak {outbreak['id']} spread to "
                    f"{outbreak['affected_locations']} locations in "
                    f"{float(outbreak['age_years']):.2f} years"
                )
    if int(log["script_errors"]) or int(log["actionable_ai_command_errors"]):
        failures.append(
            f"runtime log has {log['script_errors']} script and "
            f"{log['actionable_ai_command_errors']} actionable AI-command errors"
        )
    if not mercenaries["manager_found"] or not mercenaries["army_pool_found"]:
        failures.append("production save lacks a readable mercenary army manager")
    elif int(mercenaries["cells"]) < 400:
        failures.append(
            f"mercenary manager has only {mercenaries['cells']} geographic cells"
        )
    elif int(mercenaries["empty_cells"]) or int(mercenaries["one_role_cells"]):
        failures.append(
            "mercenary manager contains "
            f"{mercenaries['empty_cells']} empty and "
            f"{mercenaries['one_role_cells']} one-role cells"
        )
    if mercenaries["missing_portable_alternatives"]:
        failures.append(
            "mercenary manager is missing universal portable alternatives: "
            + ", ".join(mercenaries["missing_portable_alternatives"])
        )
    if mercenaries["missing_class_cells"]:
        failures.append(
            "mercenary combat classes do not cover every geographic cell: "
            + ", ".join(
                f"{unit_class} missing in {missing}"
                for unit_class, missing in mercenaries["missing_class_cells"].items()
            )
        )
    if mercenaries["missing_regional_groups"]:
        failures.append(
            "mercenary manager lacks live regional diversity: "
            + ", ".join(mercenaries["missing_regional_groups"])
        )
    if log["missing_logs"]:
        failures.append(f"runtime logs are missing: {', '.join(log['missing_logs'])}")
    return result, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("save", nargs="?", type=Path, help="save; defaults to newest")
    parser.add_argument("--error-log", type=Path, help="log to include in runtime gate")
    parser.add_argument(
        "--ai-log",
        type=Path,
        help="AI log to include; defaults to ai.log beside --error-log",
    )
    parser.add_argument("--json", type=Path, help="optional report output")
    parser.add_argument("--report-only", action="store_true", help="print metrics without enforcing thresholds")
    args = parser.parse_args()
    save = (args.save or default_save()).resolve()
    with plaintext_save(save) as source:
        result, failures = audit(source, args.error_log, args.ai_log)
    result["save"] = str(save)
    result["failures"] = failures
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if failures and not args.report_only:
        print("s7_stability_runtime: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print("s7_stability_runtime: PASS" if not failures else "s7_stability_runtime: REPORT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate Rome's opening bullion access for the Augustan coinage law."""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

from m12_hardcoded_startup import (
    EXPECTED_ROMAN_MINT_RUNTIME_AMOUNTS,
    EXPECTED_ROMAN_MINT_ROUTES,
    EXPECTED_ROMAN_MINT_RUNTIME_SUPPLY,
    roman_mint_route_rows,
)


ROOT = Path(__file__).resolve().parents[1]
ON_START = ROOT / "in_game/common/on_action/_hardcoded.txt"
LAWS = ROOT / "in_game/common/laws/01_antiquitas_s2_profile_laws.txt"
START_COUNTRIES = ROOT / "main_menu/setup/start/10_countries.txt"
OPENING_POPS = ROOT / "main_menu/setup/start/06_pops.txt"
COUNTRY_MONTHLY = ROOT / "in_game/common/on_action/country_monthly.txt"
MIN_BULLION_SOURCE_LABORERS = Decimal("1.000")


def top_level_block(text: str, key: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*\{{", text)
    if match is None:
        raise ValueError(f"missing {key} block")
    depth = 0
    for index in range(match.start(), len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[match.start():index + 1]
    raise ValueError(f"unterminated {key} block")


def main() -> int:
    failures: list[str] = []
    rows, roman_tag = roman_mint_route_rows()
    on_start = ON_START.read_text(encoding="utf-8-sig")
    laws = LAWS.read_text(encoding="utf-8-sig")
    start_countries = START_COUNTRIES.read_text(encoding="utf-8-sig")
    opening_pops = OPENING_POPS.read_text(encoding="utf-8-sig")
    country_monthly = COUNTRY_MONTHLY.read_text(encoding="utf-8-sig")
    try:
        law = top_level_block(laws, "antq_s2_roman_coinage_law")
    except ValueError as exc:
        failures.append(str(exc))
        law = ""
    required = {
        "goods_gold_used_for_minting = yes",
        "silver_used_for_minting = yes",
    }
    if "always = no" in law:
        failures.append("live Roman coinage group is hidden or disabled")
    live_options = (
        "antq_s2_roman_coinage_central",
        "antq_s2_roman_coinage_mediated",
        "antq_s2_roman_coinage_local",
    )
    for option_key in live_options:
        try:
            option = top_level_block(law, option_key)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        for token in required:
            if option.count(token) != 1:
                failures.append(
                    f"active Roman policy {option_key} does not apply {token} exactly once"
                )
        if "copper_used_for_minting = yes" in option:
            failures.append(f"{option_key} weakens the Augustan standard to copper")
    opening_assignment = (
        "antq_s2_roman_coinage_law = antq_s2_roman_coinage_mediated"
    )
    if start_countries.count(opening_assignment) != 1:
        failures.append("XAA's live Roman coinage starting assignment is not singular")
    if "antq_roman_coinage_law = antq_augustan_bimetallic_standard" in start_countries:
        failures.append("startup still relies on the hidden legacy Augustan law group")

    marker = "# ANTIQVITAS S7: bounded internal bullion routes for Augustan coinage."
    if on_start.count(marker) != 1:
        failures.append("Roman mint route startup marker is not singular")
    section = on_start.split(marker, 1)[-1].split(
        "# ANTIQVITAS S2: establish each reform's source-bounded ancient council.", 1
    )[0]
    if section.count(f"c:{roman_tag} = {{") != 1:
        failures.append("Roman mint routes do not use the mapped Roman country scope")
    if len(re.findall(r"(?m)^\s*create_trade\s*=\s*\{", section)) != len(rows):
        failures.append("Roman mint route count does not match the ledger")
    for source, good in EXPECTED_ROMAN_MINT_ROUTES.items():
        tokens = (
            f"from = location:{source}.market",
            "to = location:rome.market",
            "merchant = location:rome.market",
            f"goods = goods:{good}",
            "desired = 1",
            "locked = yes",
        )
        if any(token not in section for token in tokens):
            failures.append(f"incomplete locked {good} route from {source}")
        pop_block = re.search(
            rf"(?ms)^\t{re.escape(source)}\s*=\s*\{{\r?\n"
            rf"(?P<body>.*?)^\t\}}\s*$",
            opening_pops,
        )
        laborers = re.search(
            r"\btype\s*=\s*laborers\s+size\s*=\s*([0-9.]+)",
            pop_block.group("body") if pop_block else "",
        )
        if laborers is None:
            failures.append(f"bullion source {source} has no opening laborers")
        elif Decimal(laborers.group(1)) < MIN_BULLION_SOURCE_LABORERS:
            failures.append(
                f"bullion source {source} has only {laborers.group(1)} opening "
                f"laborers; runtime-proven floor is {MIN_BULLION_SOURCE_LABORERS}"
            )
    if "sell_goods_from_location" in section:
        failures.append("bullion routes fabricate supply instead of using owned AD 1 RGOs")

    monthly_marker = (
        "# ANTIQVITAS S7: bounded monthly Roman bullion-source deliveries; "
        "no RGO mutation."
    )
    if country_monthly.count(monthly_marker) != 1:
        failures.append("Roman mint monthly source marker is not singular")
    try:
        monthly = top_level_block(country_monthly, "antq_roman_mint_monthly_supply")
    except ValueError as exc:
        failures.append(str(exc))
        monthly = ""
    if monthly.count("sell_goods_from_location = {") != len(
        EXPECTED_ROMAN_MINT_RUNTIME_SUPPLY
    ):
        failures.append("Roman mint runtime supply count drift")
    if f"trigger = {{ tag = {roman_tag} }}" not in monthly:
        failures.append("Roman mint monthly delivery lacks the native country-tag trigger")
    if f"this = c:{roman_tag}" in monthly:
        failures.append("Roman mint monthly delivery uses non-firing scope equality")
    for source, good in EXPECTED_ROMAN_MINT_RUNTIME_SUPPLY.items():
        supply_tokens = (
            "location:rome.market = {",
            f"goods = goods:{good}",
            f"amount = {EXPECTED_ROMAN_MINT_RUNTIME_AMOUNTS[source]}",
            f"location = location:{source}",
        )
        if any(token not in monthly for token in supply_tokens):
            failures.append(f"incomplete bounded {good} delivery from {source} to Rome")
    if failures:
        print("s4_roman_mint_supply: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s4_roman_mint_supply: PASS "
        f"({len(rows)} locked staffed owned-RGO routes; "
        f"{len(EXPECTED_ROMAN_MINT_RUNTIME_SUPPLY)} bounded source-attributed "
        "bullion deliveries to Rome (silver 1, gold 2); "
        "all 3 live Roman policies and XAA's opening assignment require gold and silver)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

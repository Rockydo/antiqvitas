#!/usr/bin/env python3
"""Guard the AD 1 opening economy against flat-income and supply regressions."""

from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path

import generate_start_mirror as start
import s3_opening_market_supply as supply


ROOT = Path(__file__).resolve().parents[1]
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
COUNTRIES = ROOT / "main_menu/setup/start/10_countries.txt"
PRE_MARKET = ROOT / "in_game/common/auto_modifiers/00_antiquitas_pre_market_revenue.txt"
STARTUP = ROOT / "in_game/common/on_action/_hardcoded.txt"
PEER_MARKETS = ("alexandria", "baghdad", "luoyang", "patna", "anuradhapura")


def definition(text: str, key: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*\{{", text)
    if not match:
        raise ValueError(f"missing definition {key}")
    depth = 0
    quoted = False
    escaped = False
    for index in range(match.end() - 1, len(text)):
        char = text[index]
        if escaped:
            escaped = False
        elif quoted and char == "\\":
            escaped = True
        elif char == '"':
            quoted = not quoted
        elif not quoted and char == "{":
            depth += 1
        elif not quoted and char == "}":
            depth -= 1
            if depth == 0:
                return text[match.start(): index + 1]
    raise ValueError(f"unclosed definition {key}")


def country_blocks(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for match in re.finditer(r"(?m)^\t\t([A-Z0-9]{3})\s*=\s*\{\s*#", text):
        result[match.group(1)] = definition(text[match.start():], match.group(1))
    return result


def main() -> int:
    failures: list[str] = []
    reforms = REFORMS.read_text(encoding="utf-8-sig")
    principate = definition(reforms, "antq_principate")
    if "monthly_gold_income" in principate or re.search(r"\badd_gold\b", principate):
        failures.append("Principate reform grants direct recurring or lump-sum gold")

    for root in (ROOT / "in_game", ROOT / "main_menu"):
        for path in root.rglob("*.txt"):
            text = path.read_text(encoding="utf-8-sig", errors="strict")
            if re.search(r"(?m)^\s*monthly_gold_income\s*=\s*500(?:\.0+)?\s*(?:#.*)?$", text):
                failures.append(f"flat monthly_gold_income=500 survived in {path.relative_to(ROOT)}")

    bridge = PRE_MARKET.read_text(encoding="utf-8-sig")
    bridge_block = definition(bridge, "antq_pre_market_in_kind_revenue")
    for token in (
        "market_access <= 0",
        "value = country_economical_base",
        "divide = 4",
        "min = 5",
        "max = 200",
        "monthly_gold_income = 1",
        "create_market_cost_modifier = -1",
    ):
        if token not in bridge_block:
            failures.append(f"bounded pre-market bridge lacks {token}")
    if bridge_block.count("monthly_gold_income") != 1:
        failures.append("pre-market bridge income shape drifted")

    startup = STARTUP.read_text(encoding="utf-8-sig")
    food_reserve = re.findall(
        r"every_country\s*=\s*\{\s*every_province\s*=\s*\{\s*"
        r"change_province_food_percentage\s*=\s*([0-9.]+)",
        startup,
        re.S,
    )
    if food_reserve != ["0.50"]:
        failures.append(
            "opening province food reserve is not one capacity-bounded 0.50 seed: "
            f"{food_reserve!r}"
        )
    if startup.count("change_province_food_percentage = 0.50") != 1:
        failures.append("opening food reserve effect duplicated or drifted")

    compatibility = start.culture_presence_cultures()
    _, _, _, _, _, populations = start.population_manager(compatibility)
    tag_map = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(start.TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    blocks = country_blocks(COUNTRIES.read_text(encoding="utf-8-sig"))
    if set(blocks) != set(tag_map.values()):
        failures.append("opening country blocks and tag map do not agree")
    reserve_count = 0
    for design_tag, population in populations.items():
        engine_tag = tag_map[design_tag]
        block = blocks.get(engine_tag, "")
        gold = re.findall(r"currency_data\s*=\s*\{\s*gold\s*=\s*([0-9.]+)\s*\}", block, re.S)
        should_have_reserve = population < start.OPENING_LIQUIDITY_POPULATION_CEILING
        if should_have_reserve:
            reserve_count += 1
            if gold != [str(start.OPENING_LIQUIDITY_FLOOR)]:
                failures.append(f"{design_tag}/{engine_tag}: small-polity reserve is {gold!r}")
        elif gold:
            failures.append(f"{design_tag}/{engine_tag}: major polity received opening gold {gold!r}")
    if reserve_count < 100:
        failures.append(f"opening reserve audit unexpectedly shallow: {reserve_count}")
    if "currency_data" in blocks.get(tag_map["ROM"], ""):
        failures.append("Rome received a flat opening treasury reserve")

    generated = supply.generated_rows()
    totals = supply.coverage(generated)
    # Keep the regression gate aligned with the bounded one-circuit policy.
    # Staffing and realized throughput remain runtime checks; multiplying inert
    # bookmark workshops is neither proof of supply nor a safe crash fix.
    for market in ("rome", *PEER_MARKETS):
        minimum = supply.target(market)
        for output in supply.OUTPUT_ORDER:
            if totals[market][output] < minimum:
                failures.append(
                    f"{market}: {output} producer coverage {totals[market][output]} < {minimum}"
                )

    if failures:
        print("s4_principate_economy: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s4_principate_economy: PASS "
        f"({reserve_count} bounded small-polity reserves; "
        f"50% opening province food stores; Rome and "
        f"{len(PEER_MARKETS)} peer markets have bounded complete circuits)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

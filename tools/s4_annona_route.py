#!/usr/bin/env python3
"""Guard the live-proven AD 1 annona route contract."""

from __future__ import annotations

import re
from pathlib import Path

import m12_hardcoded_startup as startup


ROOT = Path(__file__).resolve().parents[1]
START_MARKETS = ROOT / "main_menu/setup/start/03_markets.txt"
ON_START = ROOT / "in_game/common/on_action/_hardcoded.txt"
COUNTRY_MONTHLY = ROOT / "in_game/common/on_action/country_monthly.txt"


def main() -> int:
    failures: list[str] = []
    try:
        rows, roman_tag = startup.annona_route_rows()
    except (OSError, ValueError) as exc:
        print(f"s4_annona_route: FAIL\n  - {exc}")
        return 1
    market_text = START_MARKETS.read_text(encoding="utf-8-sig")
    on_start = ON_START.read_text(encoding="utf-8-sig")
    country_monthly = COUNTRY_MONTHLY.read_text(encoding="utf-8-sig")
    if "create_trade" in market_text:
        failures.append("pre-country market manager still tries to create annona routes")
    if "c:ROM" in on_start:
        failures.append("unmapped design tag ROM survives in runtime effects")
    marker = "# ANTIQVITAS M5: country-scoped annona routes; live-proven after monthly settlement."
    if on_start.count(marker) != 1:
        failures.append("annona runtime marker is not singular")
    route_section = on_start.split(marker, 1)[-1].split(
        "# ANTIQVITAS S7: bounded internal bullion routes for Augustan coinage.",
        1,
    )[0]
    if len(re.findall(r"(?m)^\s*create_trade\s*=\s*\{", route_section)) != len(rows):
        failures.append("runtime create_trade count does not match the route ledger")
    if route_section.count(f"c:{roman_tag} = {{") != 1:
        failures.append(f"Roman runtime scope does not use mapped tag {roman_tag}")
    for row in rows:
        source_token = f"from = location:{row['source_location']}.market"
        if route_section.count(source_token) != 1:
            failures.append(f"annona source route is not singular: {source_token}")
        delivery_pattern = (
            rf"location:{re.escape(row['destination_location'])}\.market\s*=\s*\{{\s*"
            r"sell_goods_from_location\s*=\s*\{\s*"
            r"goods\s*=\s*goods:wheat\s*"
            r"amount\s*=\s*1\s*"
            rf"location\s*=\s*location:{re.escape(row['source_location'])}\s*\}}"
        )
        if re.search(delivery_pattern, country_monthly) is None:
            failures.append(
                "annona source lacks its safe monthly destination sale: "
                f"{row['source_location']} -> {row['destination_location']}"
            )
    delivery_marker = "# ANTIQVITAS M5: bounded monthly Annona source deliveries; no RGO mutation."
    if country_monthly.count(delivery_marker) != 1:
        failures.append("annona monthly-delivery marker is not singular")
    if country_monthly.count("antq_annona_monthly_supply") != 2:
        failures.append("annona monthly delivery is not both registered and defined exactly once")
    if country_monthly.count(f"trigger = {{ tag = {roman_tag} }}") < 2:
        failures.append("custom Roman monthly actions do not use the native country-tag trigger")
    if f"this = c:{roman_tag}" in country_monthly:
        failures.append("non-firing country-scope equality trigger survives in monthly actions")
    if "change_raw_material" in country_monthly:
        failures.append("annona monthly delivery must not mutate a raw material")
    common_tokens = {
        "Rome destination": "to = location:rome.market",
        "Roman merchant": "merchant = location:rome.market",
        "wheat good": "goods = goods:wheat",
        "desired capacity": "desired = 1",
        "locked route": "locked = yes",
    }
    for label, token in common_tokens.items():
        if route_section.count(token) != len(rows):
            failures.append(f"annona {label} count drift: {route_section.count(token)}")
    if failures:
        print("s4_annona_route: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        f"s4_annona_route: PASS ({len(rows)} locked wheat routes and safe monthly "
        f"source-attributed destination sales; mapped Roman tag {roman_tag}; "
        "post-country runtime timing)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

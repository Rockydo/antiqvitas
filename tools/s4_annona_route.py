#!/usr/bin/env python3
"""Guard the live-proven AD 1 annona route contract."""

from __future__ import annotations

import re
from pathlib import Path

import m12_hardcoded_startup as startup


ROOT = Path(__file__).resolve().parents[1]
START_MARKETS = ROOT / "main_menu/setup/start/03_markets.txt"
ON_START = ROOT / "in_game/common/on_action/_hardcoded.txt"


def main() -> int:
    failures: list[str] = []
    try:
        rows, roman_tag = startup.annona_route_rows()
    except (OSError, ValueError) as exc:
        print(f"s4_annona_route: FAIL\n  - {exc}")
        return 1
    market_text = START_MARKETS.read_text(encoding="utf-8-sig")
    on_start = ON_START.read_text(encoding="utf-8-sig")
    if "create_trade" in market_text:
        failures.append("pre-country market manager still tries to create annona routes")
    if "c:ROM" in on_start:
        failures.append("unmapped design tag ROM survives in runtime effects")
    marker = "# ANTIQVITAS M5: country-scoped annona routes; live-proven after monthly settlement."
    if on_start.count(marker) != 1:
        failures.append("annona runtime marker is not singular")
    route_section = on_start.split(marker, 1)[-1].split("# ANTIQVITAS M6:", 1)[0]
    if len(re.findall(r"(?m)^\s*create_trade\s*=\s*\{", route_section)) != len(rows):
        failures.append("runtime create_trade count does not match the route ledger")
    if route_section.count(f"c:{roman_tag} = {{") != 1:
        failures.append(f"Roman runtime scope does not use mapped tag {roman_tag}")
    for row in rows:
        source_token = f"from = location:{row['source_location']}.market"
        if route_section.count(source_token) != 1:
            failures.append(f"annona source route is not singular: {source_token}")
        seed_pattern = (
            rf"location:{re.escape(row['source_location'])}\s*=\s*\{{\s*"
            r"change_raw_material\s*=\s*goods:wheat\s*"
            r"change_max_raw_material_workers\s*=\s*[1-9][0-9]*\s*\}"
        )
        if re.search(seed_pattern, on_start) is None:
            failures.append(f"annona source lacks a wheat capacity seed: {row['source_location']}")
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
        f"s4_annona_route: PASS ({len(rows)} locked wheat routes; "
        f"mapped Roman tag {roman_tag}; post-country runtime timing)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

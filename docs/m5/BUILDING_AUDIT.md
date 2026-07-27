# M5/M7 building-system audit

The permanent audit counts every mod-seeded M5/M7 building placement, including
named civic sites and M7 frontier-fort proxies. It therefore does not inflate
the result by counting only the reusable guild family definitions.

For the current ledger, 2,016 of 2,790 placements (72.3%) use calibrated productive
guild recipes. The remaining 774 placements are intentionally bounded civic,
religious, infrastructure, service, primary-production, or fort contexts. This
is within the requested 50-80% productive range.

All 2,688 regional-family placements render as non-special, repeatable guild
buildings with `guild_max_level`. The 102 named historic/civic or fort proxies
are the sole one-level exception set, leaving 96.3% of all
placed M5/M7 buildings scalable. `tools/m5_building_audit.py` enforces both
ratios during `make validate`.

The same gate now enforces geographic breadth: 1,432 distinct settlement-ranked
locations cover all 292 starting polities, every polity has productive opening
capacity, and the top ten locations contain 7.2% of regional placements.
Ordinary locations are capped at six. The only higher-density exceptions are
the fifteen source-reviewed Roman provincial profiles, capped at 32.

This is an economy balance guard, not a reconstruction of ancient output,
prices, workforce, municipal law, or building stock. Individual historical
claims remain bounded in their source ledgers.

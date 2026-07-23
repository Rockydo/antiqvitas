# M5/M7 building-system audit

The permanent audit counts every mod-seeded M5/M7 building placement, including
named civic sites and M7 frontier-fort proxies. It therefore does not inflate
the result by counting only the reusable guild family definitions.

For the current ledger, 210 of 327 placements (64.2%) use calibrated productive
guild recipes: wine, pottery, cloth, glass, dyes, tools, or naval supplies.
The remaining 117 placements are intentionally bounded civic, religious,
infrastructure, service, primary-production, or fort contexts. This is within
the requested 50-80% productive range.

All 262 regional-family placements render as non-special, repeatable guild
buildings with `guild_max_level`. The 61 named historic/civic placements and
four M7 fort proxies are the sole one-level exception set, leaving 80.1% of all
placed M5/M7 buildings scalable. `tools/m5_building_audit.py` enforces both
ratios during `make validate`.

This is an economy balance guard, not a reconstruction of ancient output,
prices, workforce, municipal law, or building stock. Individual historical
claims remain bounded in their source ledgers.

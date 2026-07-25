# M5/M7 building-system audit

The permanent audit counts every mod-seeded M5/M7 building placement, including
named civic sites and M7 frontier-fort proxies. It therefore does not inflate
the result by counting only the reusable guild family definitions.

For the current ledger, 1,799 of 2,421 placements (74.3%) use calibrated productive
guild recipes. The remaining 622 placements are intentionally bounded civic,
religious, infrastructure, service, primary-production, or fort contexts. This
is within the requested 50-80% productive range.

All 2,313 regional-family placements render as non-special, repeatable guild
buildings with `guild_max_level`. The 108 named historic/civic or fort proxies
are the sole one-level exception set, leaving 95.5% of all
placed M5/M7 buildings scalable. `tools/m5_building_audit.py` enforces both
ratios during `make validate`.

This is an economy balance guard, not a reconstruction of ancient output,
prices, workforce, municipal law, or building stock. Individual historical
claims remain bounded in their source ledgers.

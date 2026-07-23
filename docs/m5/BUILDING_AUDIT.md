# M5/M7 building-system audit

The permanent audit counts every mod-seeded M5/M7 building placement, including
named civic sites and M7 frontier-fort proxies. It therefore does not inflate
the result by counting only the reusable guild family definitions.

For the current ledger, 1,137 of 1,513 placements (75.1%) use calibrated productive
guild recipes. The remaining 376 placements are intentionally bounded civic,
religious, infrastructure, service, primary-production, or fort contexts. This
is within the requested 50-80% productive range.

All 1,444 regional-family placements render as non-special, repeatable guild
buildings with `guild_max_level`. The 69 named historic/civic or fort proxies
are the sole one-level exception set, leaving 95.4% of all
placed M5/M7 buildings scalable. `tools/m5_building_audit.py` enforces both
ratios during `make validate`.

This is an economy balance guard, not a reconstruction of ancient output,
prices, workforce, municipal law, or building stock. Individual historical
claims remain bounded in their source ledgers.

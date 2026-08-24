# Research pacing contract

EU5's installed `BASE_RESEARCH_COST` is 25. The advance-level
`research_cost` field is a percentage-style addition to that base, not
an absolute point cost. Thus a generated value of `4.0` costs
`25 * (1 + 4) = 125.00` Research Progress. A live Rome tooltip and its
AD 3 save independently matched that conversion (32.82753 progress =
26.26% of 125).

The generated costs rise only by reviewed half-base steps with depth and
two-base steps at age transitions. They are intentionally slower than
vanilla's default 25-point card because ANTIQVITAS ages span 19-96 years
rather than the first vanilla age's approximately five years.

| Age | Years | Active nodes | Min points | Mean points | Max points |
|---|---:|---:|---:|---:|---:|
| Principate | 95 | 323 | 75.00 | 101.08 | 125.00 |
| High Empires | 96 | 222 | 125.00 | 155.18 | 175.00 |
| Crisis | 92 | 303 | 175.00 | 203.80 | 225.00 |
| Dominate | 92 | 222 | 225.00 | 255.18 | 275.00 |
| Federate Age | 19 | 195 | 275.00 | 302.95 | 325.00 |
| Migrations | 82 | 109 | 325.00 | 354.93 | 375.00 |

The tree uses 25 exact point-cost bands: 75.00 (36), 87.50 (78), 100.00 (73), 112.50 (94), 125.00 (52), 137.50 (51), 150.00 (46), 162.50 (67), 175.00 (58), 187.50 (78), 200.00 (73), 212.50 (94), 225.00 (58), 237.50 (51), 250.00 (46), 262.50 (67), 275.00 (53), 287.50 (53), 300.00 (53), 312.50 (59), 325.00 (30), 337.50 (25), 350.00 (25), 362.50 (30), 375.00 (24).

All 463 opening polities have at least 13 immediately eligible cards. Their immediate choices cost between 87.50 and 125.00 points.

`research_cost_ledger.csv` records every card;
`research_pacing_profiles.csv` records every polity/age visible budget.
Ten-year country outcomes remain a runtime assertion and are not inferred
from this static budget.

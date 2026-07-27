# S2 Global Settlement Network — 2026-07-27

## Scope

Rapid acceptance of the worldwide opening settlement/building redistribution.
This follows the reduced test policy: complete static checks, targeted subsystem
audits, and paired menu smoke, without a long observer campaign.

## Generated coverage

- 2,688 scalable regional placements.
- 1,432 settlement-ranked locations.
- 292/292 starting polities with an opening economy and productive capacity.
- 2,016 productive placements among 2,790 total M5/M7 placements (72.3%).
- 96.3% of all placed M5/M7 buildings are scalable.
- Ordinary locations cap at six regional buildings.
- Fifteen reviewed Roman provincial profiles are metropolitan exceptions capped
  at 32; the top ten locations together hold 7.2% of regional placements.
- Ten geographic macros are represented, including Central Asia, Southeast and
  East Asia, West Africa, the Americas, and Oceania.

## Checks

- `s2_global_settlements.py --check`: PASS.
- `m5_regional_buildings.py --check`: PASS.
- `m5_building_audit.py`: PASS.
- `m5_roman_economy_audit.py --check`: PASS.
- `generate_start_mirror.py --check`: PASS; 1,432 urban/settlement nodes and
  2,790 M5/M7 building placements emitted.
- Full validation: PASS, 102/102 commands.
- Paired vanilla/mod smoke: PASS; both reached responsive rendered menus and the
  mod introduced zero new or unique `error.log` lines.

The authoritative ledgers are `docs/m5/regional_building_seeds.csv` and
`docs/m5/global_settlement_audit.csv`.

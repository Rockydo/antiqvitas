# Mainland Southeast Asian Granularity — 2026-07-28

## Accepted scope

- Removed `SEA` and reassigned all 136 locations exactly once.
- Added eleven bounded networks across Arakan, central Vietnam, the upper
  Irrawaddy, northern basins, upper Mekong, Salween-Shweli, and southern
  plateau; Harikela gained only six Chittagong littoral fields.
- Added ten cultures, one plural faith, four direct-art doctrines, four
  reforms, eleven standards, qualified capitals, settlements, and full
  roster-wide integration.

## Deterministic probe

`tools/s2_mainland_sea_granularity.py --check` passes:

- no `SEA` residue in roster, ownership, selectors, or localization;
- eleven exact counts, capitals, cultures, faiths, reforms, and standards;
- 130 new-frame fields plus the six-field Harikela extension equal 136;
- settlements, research, four direct doctrine icons, and eleven clients resolve.

## QA acceptance

- `make validate`: **PASS**, 120 commands.
- Paired vanilla/mod `make smoke`: **PASS**, 197.7 seconds.
- Both launches reached responsive rendered menus.
- Normalized `error.log`: **zero new lines unique to the mod**.

## Evidence boundary

Frames are archaeological or geographic proxies. No Champa, Lanna, Shan,
later Arakan, Tai, Buddhist, or Hindu state/identity is projected into AD 1.
Sources and limits are in `docs/world_1ad/SOURCES.md`,
`docs/ASSUMPTIONS.md`, and `docs/m12/mainland_sea_granularity.csv`.

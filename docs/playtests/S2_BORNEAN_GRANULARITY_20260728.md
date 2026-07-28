# Bornean Granularity - 2026-07-28

## Accepted scope

- Removed `BOR`; reassigned all 110 locations exactly once among ten bounded
  cave, karst, river, littoral, and foothill frames.
- Added ten cultures, one plural faith, four direct-art doctrines, four
  reforms, ten standards, settlements, and roster-wide integration.

## Deterministic probe

`tools/s2_bornean_granularity.py --check` passes exact selectors, counts,
capitals, cultures, faith, reforms, standards, settlements, research, doctrine
icons, and eleven localization clients; no `BOR` residue remains.

## QA acceptance

- `make validate`: **PASS**, 122 commands, 372.1 seconds.
- Paired vanilla/mod `make smoke`: **PASS**, 198.6 seconds.
- Both launches reached responsive rendered menus.
- Normalized `error.log`: **zero new lines unique to the mod**.

## Evidence boundary

Frames are archaeological/geographic proxies, not reconstructed states or
later ethnic borders. Sources and limits are recorded in
`docs/world_1ad/SOURCES.md`, `docs/ASSUMPTIONS.md`, and
`docs/m12/bornean_granularity.csv`.

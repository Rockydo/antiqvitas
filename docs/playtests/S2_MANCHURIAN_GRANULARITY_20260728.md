# Manchurian Granularity - 2026-07-28

## Accepted scope

- Removed `MNC`; reassigned all 125 locations exactly once among six bounded
  Amur, Sakhalin, Ussuri, Mudan, and Okjeo-Tuanjie frames.
- Added six cultures, one plural faith, four direct-art doctrines, four
  reforms, six standards, qualified capitals, settlements, and roster-wide
  integration.

## Deterministic probe

`tools/s2_manchurian_granularity.py --check` passes exact selectors, counts,
capitals, cultures, faiths, reforms, standards, settlements, research, doctrine
icons, and eleven localization clients; no `MNC` player-facing residue remains.

## QA acceptance

- `make validate`: **PASS**, 121 commands.
- Paired vanilla/mod `make smoke`: **PASS**, 197.1 seconds.
- Both launches reached responsive rendered menus.
- Normalized `error.log`: **zero new lines unique to the mod**.

## Evidence boundary

Frames are archaeological or geographic proxies, not reconstructed states,
ethnic borders, or later Jurchen, Nivkh, Ainu, or Korean identities. Sources
and limits are in `docs/world_1ad/SOURCES.md`, `docs/ASSUMPTIONS.md`, and
`docs/m12/manchurian_granularity.csv`.

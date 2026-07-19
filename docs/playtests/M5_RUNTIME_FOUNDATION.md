# M5 Runtime Foundation Report

Run date: 2026-07-19
Game: EU5 1.3.1.1 (Pavia), build 24187685
Mode: enabled ANTIQVITAS playset, debug-mode autonomous driver

## Evidence

1. The driver launched New Game and reached the AD 1 selection map at
   `08:00, 1 January, 1`; see
   `docs/screens/m5_runtime_probe/new_game_timeout.png`.
2. The driver entered Observer Mode and confirmed the irreversible observer
   prompt; see `observer_after_precise.png` in the same session directory.
3. The visible play control advanced the observer to `13:00, 11 January, 1`.
   The resulting frame (`observer_play_check.png`) shows AI notifications for
   new market construction.
4. `make validate` and a subsequent fully rendered `make smoke` passed with
   zero new menu-load `error.log` lines.

## Runtime log assessment

The observed error set contains only these remaining categories:

- invalid or unset `capital`;
- unset `government_type` and its vanilla coat-of-arms trigger fallout;
- invalid or missing `international_organization` and vanilla HRE interaction
  fallout.

There are no `market`, `town_setup`, `entrepot`, `granary`, `raw_material`, or
`road_network` error lines in this run. The M5 market, RGO, and urban-foundation
surfaces therefore load and tick through the first ten observer days. This is
not the M5 milestone gate: roads, development, the wider goods/buildings pass,
and longer trade-flow verification remain pending; the surviving government and
IO failures belong to M6 and M9.

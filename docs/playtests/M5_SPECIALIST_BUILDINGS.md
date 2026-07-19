# M5 specialist buildings probe — 2026-07-19

## Scope

Validate that the source-led specialist market, urban, and building layer loads
into a new AD 1 game and does not emit an economic parser/runtime error. This
is a focused M5 sub-probe, not the M5 trade-flow milestone gate.

## Procedure and evidence

1. Ran `make validate`: green, including the generated 39 markets, 39 urban
   nodes, and 11 specialist buildings.
2. Ran a real `make smoke`: green, zero new `error.log` lines versus the
   accepted baseline.
3. Launched the enabled mod with `tools/gamedriver.py`, selected New Game, and
   waited for the AD 1 country-selection map. `setup_map_ready.png` shows
   `08:00, 1 January, 1` and the intended total-conversion map.
4. Entered Observer Mode and started the game. `observer_day10.png` shows
   Observer Mode active at `16:00, 7 January, 1` with AI market-construction
   notices. The session screenshots are under
   `docs/screens/m5_specialist_buildings/`.
5. Searched the resulting `error.log` for `lighthouse`, `glass_guild`,
   `lacquerware`, `pottery_guild`, `aqueduct`, `minting_office`,
   `building_manager`, and the new anchor locations. There were no matches.

## Result

**Pass for this sub-surface.** The new-game parser accepted the specialist
building manager, including the event-only Pharos entry, and the observer clock
advanced while market AI was active. Existing errors remain limited to the
already tracked absent government/dynasty and international-organization/HRE
systems, which are M6/M9 work and not accepted as an M5 milestone pass.

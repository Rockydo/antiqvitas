# M4 Iberian ethnographic atlas verification

Date: 2026-07-21

## Scope

The batch adds 38 named Iberian ethnographic frames from Strabo and Pliny,
with a modern heterogeneity cross-check. Each frame is mapped through one
installed province selector and refines, rather than replaces, the previously
documented broad regional frame. The ledger uses exact source precedence:
location > province > area > region; same-specificity overlap remains invalid.

## Static evidence

- `tools/generate_m4_definitions.py --write` produced 217 culture definitions
  and 37 religions.
- `tools/generate_start_mirror.py --write` resolved 373 source-labelled
  selectors to 12,037 controlled locations across 196 mapped cultures. The 38
  Iberian selectors cover 208 generated population locations.
- `tools/popcheck.py` passed at 230,000.000 thousand people over 13,552
  populated controlled locations.
- `make validate` passed all project gates, including the M4 definition,
  population, localization, symbol, encoding, and anachronism checks.

## Runtime evidence

The enabled-mod smoke completed at `2026-07-21T18:07:39Z`. Its normalized
error-log delta was empty (`new: []`, `fixed: []`, with two unchanged accepted
baseline lines). EU5 exited cleanly after the normal smoke readiness window.

## Result

The batch is accepted as a clean, source-labelled increment. It does not claim
exact tribal borders, a language census, uniform populations, or political
boundaries. The larger M4 milestone remains open because 217 definitions is
still below the plan's 350-500 culture target.

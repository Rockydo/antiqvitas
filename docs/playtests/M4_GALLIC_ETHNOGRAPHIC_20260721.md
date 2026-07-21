# M4 Gallic ethnographic atlas verification

Date: 2026-07-21

## Scope

The batch adds 47 named Aquitanian, Armorican, Gallic, Belgic, Alpine, and
Narbonensian frames from Strabo and Pliny, cross-checked against the *Oxford
Classical Dictionary*. Each uses a single installed province selector to refine
an existing broad regional frame. It is an explicitly contested campaign-start
proxy, not an exact tribal polygon, language census, or political boundary.

## Static evidence

- M4 generation produced 264 culture definitions and 37 religions.
- The 420 source-labelled selectors resolve 12,037 controlled locations across
  243 mapped cultures; the 47 new selectors cover 231 generated population
  locations.
- `tools/popcheck.py` passed: 230,000.000 thousand people in 13,552 populated
  controlled locations.
- `make validate` passed the entire project surface, including generated
  culture definitions, population, localization, symbols, encoding, and
  anachronism checks.

## Runtime evidence

The enabled-mod smoke completed at `2026-07-21T18:18:26Z` with an empty
normalized error-log delta (`new: []`, `fixed: []`; two unchanged baseline
lines). EU5 exited cleanly after the normal smoke readiness window.

## Result

The batch is accepted as a green, source-labelled increment. The M4 milestone
remains open because 264 definitions remains below the plan's 350-500 target.

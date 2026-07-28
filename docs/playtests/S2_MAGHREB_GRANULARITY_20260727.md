# S2 Maghreb Granularity Evidence — 2026-07-27

## Scope

This is the first tranche of the global player-facing placeholder-polity
remediation. It replaces the Maghreb-wide Berber/Gaetulian residual with:

- Mauretania, capital Caesarea Mauretaniae (`cherchell`), 128 locations;
- Gaetuli, bounded high-plateau/pre-desert frame at `djelfa`, 19 locations;
- Musulamii, bounded Aures/Hodna frontier frame at `biskra`, 11 locations.

The Gaetulian and Musulamian frames are explicitly societies of peoples, not
claims of centralized AD 1 states or exact borders.

## Static contract

`tools/s2_maghreb_granularity.py` verifies:

- exact display names, collision-safe engine tags, owned capitals, and resolved
  ownership counts;
- the Mauretanian coastal, Gaetulian plateau, and Musulamian Aures/Hodna
  selectors;
- distinct country culture/religion profiles and required culture remaps;
- government/reform wiring and direct sourced presentation standards;
- source/confidence metadata; and
- country/adjective localization in all eleven supported clients.

`tools/s2_placeholder_polity_census.py` separately retains the honest global
baseline: 26 literal placeholder names remain after this tranche.

## QA

- `gmake validate`: PASS, 112/112 commands.
- `gmake smoke`: PASS. Vanilla and ANTIQVITAS both reached responsive rendered
  menus; the mod introduced zero new and zero mod-unique `error.log` lines
  against the accepted baseline.
- Long observer campaigns are intentionally excluded by the reduced QA policy;
  this ownership/content tranche uses static invariants plus the paired
  vanilla/mod load comparison.

## Evidence boundary

The source ledger is in `docs/world_1ad/SOURCES.md`. The Mauretanian kingdom
and Caesarea capital are secure. Gaetulian spatial usage and the exact
Musulamian AD 1 extent are contested; the map frames are reproducible,
source-bounded gameplay proxies.

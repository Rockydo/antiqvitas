# M4 curated dynamic names - 2026-07-21

## Scope

The dynamic-name layer previously rendered only 61 coordinate-verified capital
anchors. This batch adds 24 secure, source-labelled non-capital toponyms through
`docs/m4/dynamic_location_name_overrides.csv`, for 85 reviewed anchors in
total. Every curated row resolves to an installed location, a valid M4 culture
and language contract, a non-empty source/note, and a unique location key.

## Historical method

Classical names use the project Pleiades (`PLE`) pipeline, Han names use the
`BHR` route, and the plan's reviewed market/road anchors constrain the local
map matches. The ledger deliberately excludes near-site and uncertain entries.
Its culture field selects the engine's dynamic-language key; it does not assert
that the city was linguistically homogeneous or that the owner profile proves
local speech.

## Verification

- `tools/generate_dynamic_names.py --write` rendered 85 anchors to English and
  ten exact client mirrors.
- `make validate` passed, including dynamic-name and localization checks.
- Enabled-mod smoke completed at `2026-07-21T20:15:28Z` with zero new
  normalized `error.log` lines.

## Result

Pass. The M4 dynamic-name task is complete. Current Culture/Religion map-mode
acceptance remains separately blocked by the documented observer renderer
crash; this batch does not claim to have produced that unavailable visual gate.

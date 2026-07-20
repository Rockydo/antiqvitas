# M5 Second Temple start and transformation

Run date: 2026-07-20
Game: EU5 1.3.1.1, build 24187685
Mode: enabled ANTIQVITAS playset and debug-mode autonomous driver

## Result

Added the engine-valid `temple` building at Jerusalem for the plan-required
Second Temple. Jerusalem enters the building renderer through a separate,
validated historic-site ledger because it is not one of the forty market nodes.

The first-century current renderer now emits the AD 70 `Destruction of the
Second Temple` event. It checks for the building before applying the locally
harvested location-scoped `destroy_building` contract, so an earlier player
removal does not produce a false effect or runtime error.

`make validate` passed with 28 first-century currents. A fresh enabled-mod
`make smoke` reached the rendered menu and reported zero new `error.log` lines
against the accepted baseline.

## Scope

The generic engine temple is a technical representation of the Second Temple,
not a reconstruction of its form, priesthood, ritual practice, or the full
post-70 Rabbinic transformation. The AD 70 date is a year-level historical
current, not a claim to a precise day.

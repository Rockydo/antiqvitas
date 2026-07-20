# M5 Muza trade roadstead

Run date: 2026-07-20
Game: EU5 1.3.1.1, build 24187685
Mode: enabled ANTIQVITAS playset and debug-mode autonomous driver

## Result

Added the engine-valid `market_warehouse` at Al Mukha, the existing reviewed
Muza proxy and M5 market node. Casson's translation of *Periplus Maris
Erythraei* sections 21-24 identifies Muza as a legally limited port of trade,
commercially active with a good roadstead.

The source equally states that Muza had no harbor. The implementation therefore
uses a market-infrastructure proxy and deliberately does not place a
`protected_harbor` there.

`make validate` passed. A fresh enabled-mod `make smoke` reached the rendered
menu and reported zero new `error.log` lines against the accepted baseline.

## Scope

The Al Mukha mapping remains the pre-existing contested geographic proxy for
Muza. The building represents no excavated warehouse, harborwork, capacity,
or uniform customs regime.

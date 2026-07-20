# M5 Ancient Harbor Infrastructure

Run date: 2026-07-20
Game: EU5 1.3.1.1, build 24187685
Mode: enabled ANTIQVITAS playset and debug-mode autonomous driver

## Result

Added six `protected_harbor` buildings through the locally verified start
building-manager contract: Gades, Massilia, Panyu, Barygaza (Khambat proxy),
Muziris (Kodungallur proxy), and Adulis (Massawa proxy). Each row is attached
to an existing reviewed M5 market/urban anchor and retains its source and
proxy qualification in `docs/m5/special_buildings.csv`.

`make validate` passed. A fresh enabled-mod `make smoke` reached the rendered
menu and reported zero new `error.log` lines against the accepted baseline.

## Scope

This adds the plan's harbor-tier economy surface only. It does not claim an
archaeological harbor plan, throughput measure, universal monsoon-route
regularity, or runtime proof of the still-blocked RGO remap. The pre-existing
observer-modal limitation remains unchanged and was not retried.

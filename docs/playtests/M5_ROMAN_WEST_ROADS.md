# M5 Roman western road corridor

Run date: 2026-07-20
Game: EU5 1.3.1.1, build 24187685
Mode: enabled ANTIQVITAS playset and debug-mode autonomous driver

## Result

The generated AD 1 road manager now has 36 source-labelled segments. Seven
new links provide a conservative western continuation from Massilia to Arelate,
Nemausus, Narbo, the Pyrenean approach, Gerunda, Barcino, and Tarraco.

The Arelate-Nemausus-Narbo sequence is grounded in the Oxford Classical
Dictionary's Via Domitia entry. The Spanish Atlas supports the broad Via
Augusta Barcino/Tarraco corridor. The Massilia-Arelate link and two
installed-map crossing links are explicitly marked `contested`: they are
high-level connectors, not claimed archaeological traces.

`make validate` passed. A fresh enabled-mod `make smoke` reached the rendered
menu and found zero new `error.log` lines against the accepted baseline.

## Scope

The manager uses the installed base-road endpoint syntax only. This is a
connectivity layer for the plan's ancient-market economy; it does not recreate
roadbeds, stations, distances, maintenance, or legal status.

# M4 Iberian period-name pass — rapid validation record

Date: 2026-07-23

Scope: nineteen direct, secure Roman-period city labels in the curated dynamic
name ledger. The generator resolved all 148 curated anchors plus 61 capital
anchors and mirrored the display strings to all supported clients.

`make validate` passed, including dynamic-name, localization, syntax, and
anachronism checks. `make smoke` passed: vanilla and ANTIQVITAS both reached
the menu-ready heuristic, and the mod added zero new `error.log` lines. The
four archived-baseline delta line types in the vanilla control were not unique
to the mod.

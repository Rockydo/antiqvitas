# M7 core and mercenary roster expansion — 2026-07-23

## Scope

This rapid subsystem check expands the AD 1 role roster by twelve bounded
adapters: three Roman, two Parthian, two Germanic, and five mercenary-company
types. The scripts deliberately avoid named detachments, force totals, and
orders of battle.

## Automated result

`make validate` passed after regenerating the exact start mirror. The M7 gate
reports 44 ancient unit types and confirms that M8 retains ownership of the
complete advance replacement.

## Smoke criterion

The reduced game-visible check is limited to vanilla/mod menu launch and a
zero-new-lines comparison of `error.log` against the accepted baseline. It
does not claim an extended observer playthrough.

## Smoke result

`make smoke` passed on 2026-07-23. Vanilla and ANTIQVITAS each reached the
menu-ready heuristic; the comparison found zero new `error.log` line types
unique to the mod.

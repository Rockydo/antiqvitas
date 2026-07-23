# M5 Argentoratum frontier-camp probe - 2026-07-23

## Scope

This rapid building-subsystem gate adds one direct, source-qualified AD 1
frontier special: `Castrum Argentoratum` at installed `strasbourg`. The
University of Strasbourg thesis source dates its legionary-city foundation to
Drusus in 12 BC. The implementation is deliberately restricted to the existing
low timber-and-earth stockade contract.

## Static gate

`gmake validate` passed. In particular, the Roman-building ledger reports 40
named buildings with direct icon contracts; the M5/M7 audit reports 456
placements, 319 productive (70.0%), and 388 scalable (85.1%); the exact start
mirror reports 456 M5/M7 buildings including four M7 forts. The new 128px RGBA
master and its BC7 DDS were independently inspected before ledger generation.

## Menu smoke

The bounded `gmake smoke` control reached the vanilla menu, then reached the
ANTIQVITAS menu with the enabled playset. The normalized error-log comparison
reported:

`smoketest: PASS (zero new lines; 0 baseline line types absent)`

No observer chronology was run. The change is a checked start-time building,
its source-managed localization, and a direct icon, so static generation plus
the paired menu/log smoke is the project-approved rapid verification scope.

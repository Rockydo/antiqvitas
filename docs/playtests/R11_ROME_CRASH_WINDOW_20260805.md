# R11 Rome crash-window regression — 2026-08-05

## Scope

Fresh non-debug 1920x1080 ANTIQVITAS campaign as Roman Imperium. This is the
player path reported to crash around April, not an Observer substitute.

## Repair under test

- The sixteen custom bilateral regional actions reject AI self-targets in
  their executable allow scopes.

An experimental late government-law overlay was rejected because it made the
engine crash seconds after unpausing. It is not part of this repair.

## Result

The Roman player campaign remained alive and responsive through the reported
failure period:

| Evidence | In-game date | Result |
|---|---:|---|
| rome_april_crossed.png | 19:00, 5 April AD 1 | Alive; normal Coming of Age popup only |
| rome_june.png | 18:00, 9 June AD 1 | Alive; normal New Market popup only |

Screens: docs/screens/R11_PLAYER_ROME_SUCCESSION_FIX_20260805/.

## Remaining distinction

The independent non-debug Observer stress path still reached an FSR
access-violation without a new script assertion. It is not treated as proof
that the player Rome crash is resolved globally; it remains a separate
AI/Observer renderer investigation.

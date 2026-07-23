# M10 historical currents acceptance report

Date: 2026-07-24
Build: EU5 1.3.1.1 / Steam build 24187685
Scope: static chronology contracts, menu/log smoke, and one bounded driver probe;
no centuries-long observer campaign.

## Acceptance evidence

- The current `make validate` is green.  Its five M10 renderers validate all
  84 historical currents: 28 for AD 1--96, 19 for AD 97--199, 10 for AD
  200--299, 14 for AD 300--399, and 13 for AD 400--476.  This includes each
  date, recipient, dynamic tag, location seed, localization binding, and
  event-art reference.
- The same validation confirms that all 84 currents use the shared
  `tools/dates.py` contract.  The M11 checks additionally confirm direct
  event-art files and 557 player-facing direct UI-asset chains.
- A fresh enabled-mod `make smoke` reached menu-ready state and reported zero
  new `error.log` lines against the accepted baseline.
- The five earlier batch records remain the detailed implementation evidence:
  `M10_001_096.md`, `M10_097_199.md`, `M10_200_299.md`, `M10_300_399.md`, and
  `M10_400_476.md`.

## Bounded driver probe

On 2026-07-24 the automated driver launched the enabled mod, passed the
rendered-menu readiness check, and attempted the recorded New Game-to-Observer
sequence twice.  Both attempts returned to the menu rather than showing the
live-observer pause banner.  The retained screenshots are
`../screens/M10_targeted_probe/m10_menu_ready.png`,
`../screens/M10_targeted_probe/manual_selection_start_attempt1.png`, and
`../screens/M10_targeted_probe/manual_selection_start_attempt2.png`.

The resulting log tail contains only the pre-existing DX12 feature assertion
and store-backend DLC messages; smoke's vanilla control confirms that neither
line type is unique to ANTIQVITAS.  The game was then stopped by the driver.
This is therefore a documented observer-UI coverage limitation, not evidence
of an M10 content failure.

## Result

**PASS.** All historical-current contracts validate and the enabled-mod menu
has no new diagnostics.  In accordance with the reduced test protocol in
plan section 22, no full AD 1--476 observer run is required.  The driver
sequence may be revisited after a material UI/renderer change, but it is not a
ship blocker for M10.

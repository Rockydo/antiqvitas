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

On 2026-07-24 the first automated invocation attempted Observer before the
New Game country-selection screen; it consequently returned to the menu.  The
driver was then run through its required sequence: enabled menu, New Game,
AD 1 country selection, Observer selection, and the live paused map.  The
retained evidence is `../screens/M10_targeted_probe_repaired/`, in particular
`m10_country_selection_wait.png` and `manual_selection_live.png`.

The installed console reference documents `event [eventid] [target]`.  From
that live Observer session the driver dispatched the generated first-current
event with its generated Armenian recipient:
`event antq_m10.1000 XAO`.  It produced no new M10 error-log entry; country
events addressed to an AI country in Observer mode resolve without a player
event popup.  `m10_event_targeted_armenian.png` retains the immediately
following paused-map state.  The error tail contains only the separately
tracked AD 1 no-pop diagnostics and the pre-dispatch Observer-without-country
probe; neither names an M10 content identifier.

## Result

**PASS.** All historical-current contracts validate, the enabled-mod menu has
no new diagnostics, and the first generated current accepts its explicit
country target in a live AD 1 session.  In accordance with the reduced test
protocol in plan section 22, no full AD 1--476 observer run is required.

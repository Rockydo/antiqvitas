# R21 Roman opening-ruler runtime — 2026-08-08

## Defect and root cause

Fresh candidate 36 exposed a random 25-year-old Roman ruler on the first
playable frame. The sourced age-63 Augustus already existed in the living-court
bootstrap, but `antq_m6.1` deliberately waited until the next date: replacing
the bookmark-generated ruler on 1 January makes EU5 1.3.11 create overlapping
same-day ruler terms.

EU5 assigns the generated opening ruler character ID `0`. That ID is a valid
government and ruler-term reference, but it is also the null sentinel for a
persisted character variable. Candidate 37 and candidate 38 proved that both a
saved event scope and a direct `value = ruler` serialize as a typed character
variable without an identity. The solution therefore validates the actual AD 1
government/character records rather than pretending an ID-zero variable exists.

## Repair

`tools/m6_power.py` now transforms the existing single-term Roman holder during
`on_game_start`: Augustus's localized name, Latin culture, Religio Romana,
Julio-Claudian dynasty, noble estate, mortality guard, and marriage to Livia are
all present before player control. The distinct sourced age-63 character remains
under a non-player-facing placeholder name until the already-proven 2 January
handoff. The handoff renames him Augustus, installs him as ruler on the new date,
retires the ID-zero holder, restores the Livia marriage from a captured event
scope, persists `antq_m6_roman_augustus`, and removes its temporary variables.

`tools/m6_ruler_runtime.py` now treats 1 January as an explicit strict phase. It
requires the active named Augustus, Gaius heir, Livia consort, no regent, one
active term, matching court culture/religion/dynasty, mortality protection, and
a distinct living age-63 placeholder handoff target. From 2 January onward the
normal persisted Augustus identity is mandatory.

## Fresh runtime proof

Candidate 42 was generated from a fresh 1920x1080 New Game and entered as player
Rome while paused:

- `docs/screens/candidate42_ruler/candidate42_augustus_ad1.png` shows Princeps
  Augustus Julio-Claudian as the active ruler on 1 January AD 1;
- `docs/playtests/M6_RULER_RUNTIME_CANDIDATE42_AD1.json` passes the saved AD 1
  contract with ruler `0`, Gaius `6109`, Livia `6142`, no regent, active term
  `2`, and distinct age-63 target `6093`;
- `docs/screens/candidate42_ruler/candidate42_augustus_handoff.png` shows the
  sourced age-63 Augustus with Livia on 2 January;
- `docs/playtests/M6_RULER_RUNTIME_CANDIDATE42_HANDOFF.json` passes with ruler
  `6093`, Gaius `6109`, Livia `6142`, no regent, and exactly one active term
  (`465`).

The final log is 995 bytes / 11 lines: ten store-backend messages and the known
AudioArena environment line. It contains zero script-system, ruler-term,
assertion, construction, formatter, or crash diagnostics.

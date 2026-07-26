# ANTIQVITAS BLOCKERS

## 2026-07-26 - Optional eastern live-selector probe did not enter Observer

Status: automation-only QA limitation; does not block continued work.

After the complete 97-check validation and paired vanilla/mod menu smoke passed,
the game driver enabled Observer and dismissed the selection popup, but two
bounded attempts to start the campaign returned to the ANTIQVITAS main menu
without a pause banner. The evidence is retained under
`docs/screens/evidence/runtime/eastern_granularity_20260726/`.

The affected content is covered by the new deterministic
`s2_eastern_granularity.py` gate, including exact ownership, capital, culture,
government, agenda, localization, and art contracts. Per the reduced QA policy,
this optional selector capture is not replaced with a long observer campaign;
future driver work can revisit the main-menu transition independently.

## 2026-07-26 - Hardcoded absent-HRE country-selection notice

Status: engine constraint; does not block continued work.

Two attempts removed all reachable script causes: the HRE yearly pulse and all
installed HRE/curia/international-organization interactions and generic actions
are false-gated with optional object scopes. A repeated AD 1 country-selection
probe now reports zero Jomini script-system errors, but EU5 1.3.11 still emits
`initialize_from_bookmark.cpp:320: HRE doesn't exists in game` from hardcoded
bookmark initialization.

Creating a dummy Holy Roman Empire would silence the engine but would reintroduce
a medieval institution into AD 1 state and risks player-facing leakage. The
notice is therefore documented rather than “fixed” through an anachronistic
object. Standard paired smoke remains green; focused probes distinguish this
hardcoded notice from mod script errors.

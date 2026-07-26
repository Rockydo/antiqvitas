# ANTIQVITAS BLOCKERS

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

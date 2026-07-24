# M12 final-gate status

Date: 2026-07-22
Build: EU5 1.3.11 / local Steam build 24187685

## Current green gate

`make full` passed again on the current tree after the M6 current-ruler repair
and M7 observer-war retest. It includes all static/generated
validators, a 350-culture and 37-religion M4 definition check, 416 historical
current events, the 230,000.000-thousand population target, and an enabled-mod
smoke run with zero new normalized `error.log` lines.

This establishes the present release baseline: the mod parses, the generated
contracts agree, the active playset launches, and the menu-ready smoke path is
clean.

## 2026-07-21 resume audit

A fresh autonomous `make full` rerun also passed after the recorded M7 retest.
It again reached the settled enabled-mod menu with zero new normalized
`error.log` lines. The installed Steam build remains 24187685 and the RTX 3080
driver remains 591.86, matching the renderer-blocker environment; therefore no
additional high-speed observer retry was performed.

## Tagged release gate

The revised plan accepts `make full`, a fresh AD 1 start, static finale
validation, and rapid high-risk subsystem probes. The AD 1-to-476 observer
run and finale screenshot are optional evidence, not a release gate. The
24 July additive-presence repair removed every fresh culture/religion no-pop
diagnostic while preserving the exact 230,000.000-thousand target; the final
smoke and fresh-selection probe are recorded in
`docs/playtests/M12_CULTURE_PRESENCE_20260724.md`. M12 is tagged `M12-done`.

The observer renderer failure remains documented optional evidence in
`docs/playtests/M12_OBSERVER_RETRY_20260721.md`,
`docs/playtests/M12_RENDER_SCALE70_20260721.md`, and `BLOCKERS.md`.

# M12 final-gate status

Date: 2026-07-21
Build: EU5 1.3.11 / local Steam build 24187685

## Current green gate

`make full` passed on the current tree. It includes all static/generated
validators, a 350-culture and 37-religion M4 definition check, 416 historical
current events, the 230,000.000-thousand population target, and an enabled-mod
smoke run with zero new normalized `error.log` lines.

This establishes the present release baseline: the mod parses, the generated
contracts agree, the active playset launches, and the menu-ready smoke path is
clean.

## Release gate not accepted

M12 is not tagged. The plan requires observer-based pacing measurements and an
autonomous AD 1-to-476 run with decade screenshots and finale evidence. Two
material renderer-profile attempts reproduce the FSR renderer failure during
sustained play. A fresh observer initialization is clean, but that cannot
substitute for a completed timeline run.

Evidence and recovery conditions are in
`docs/playtests/M12_OBSERVER_RETRY_20260721.md`,
`docs/playtests/M12_RENDER_SCALE70_20260721.md`, and `BLOCKERS.md`. Resume this
gate only after a material renderer, driver, or installed-game change.

# M2 — Time itself

Date: 2026-07-19  
Game: EU5 1.3.1.1 (Pavia), build 24187685  
Result: **PASS**

## Acceptance evidence

- `tools/dates.py --write-m2` is the sole generator for the active
  `1.1.1`–`476.9.4` defines, five playable ages, M8 scaffold advances, and
  BOM-safe mirrored localization.
- `make full` passed with the active calendar: static validation passed and
  the real-game smoke reported **zero new `error.log` lines**. In particular,
  the former 868 year-one vanilla ruler-term errors are absent because M3 now
  mirrors every start-manager filename.
- The driver reached a new-game screen at `08:00, 1 January, 1`, entered
  observer mode, and showed the `Age of Principate` header in
  `M2_mirror_observer_started.png`.
- The driver issued `save antq_m2_mirror`; the resulting relocated-user-dir
  save was 32,525,746 bytes. A fresh game process loaded it through the UI;
  `M2_mirror_reloaded_result.png` again visibly reads `08:00, 1 January, 1`.

## Scope judgment

The political map is intentionally blank in this report: M3 has removed the
vanilla 1337 setup but has not yet written AD 1 ownership and countries into
the start manager. This is not a calendar failure. The clean empty mirror makes
the M2 evidence stronger by isolating dates/ages/save compatibility from the
historical-map work still in progress.

## Curated visual evidence

- `docs/screens/M2_retry/M2_mirror_observer_started.png`
- `docs/screens/M2_retry/M2_mirror_reloaded_result.png`

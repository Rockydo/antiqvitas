# M2 Runtime Probe

Date: 2026-07-19
Game: EU5 1.3.1.1 (Pavia), checksum 3794
Result: **calendar/save-reload PASS; clean-runtime closure deferred to M3**

## What was proven

- `tools/dates.py --write-m2` generated `START_DATE = "1.1.1"` and
  `END_DATE = "476.9.4"`, five campaign ages, five unavailable placeholder
  advances, and English-mirrored localization.
- The driver selected New Game, waited through generation, and reached the
  country-selection map. `M2_gameplay_map.png` visibly reads `08:00, 1 January,
  1`; `M2_observer_running.png` also visibly reads `Age of Principate`.
- The observer game was saved with the in-game `save antq_m2_calendar` command.
  The console confirmed success and the 320 MB file was written beneath the
  relocated user directory.
- A fresh process used Load Game, selected the AD 1 save, confirmed loading,
  and reached `M2_reloaded_map.png`, which again visibly reads
  `08:00, 1 January, 1`.

## Runtime constraint and recovery

The retained vanilla 1337 setup loads at the new date but emits 868 distinct
`ruler_term_container.cpp:109` errors: old ruler histories are all validated
against year one. This is an M3 setup-mirror dependency, not a calendar parsing
failure. The generated M2 files were removed before commit, and a subsequent
`make full` passed with zero new error lines. See `BLOCKERS.md` for the two
attempts and re-enable procedure.

## Curated visual evidence

- `docs/screens/M2/M2_observer_running.png`
- `docs/screens/M2/M2_reloaded_map.png`

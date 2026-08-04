# R5 population runtime — 2026-08-03

- Normal AD 1 start/end saves: `1.1.1` to `1.5.30.12`.
- World tribesmen: 24.419% to 24.381%; all eight strata parsed from saves.
- Speed-five calibration completed 120 seconds without pause recovery.
- Full-year retries reproduced EU5 1.3.11 `C0000005` at
  `ffxFsr2ResourceIsNull`; no content frame appears in the stack.
- A repaired non-debug recovery waited for visible save-load completion, but
  the engine reset the explicit `1.5.30` checkpoint to `1.1.1` before Observer;
  both recovery entries exited in the same renderer family.
- Console-load follow-up: the installed `load [file name]` command rejects both
  `r5_population_normal_end.eu5` and the quoted absolute path with its own
  `File doesn't exist` response. The fail-closed probe retains captures and
  never accepts a loading plate without an exact re-saved date match.
- Static population targets, capacity, and bookmark mirrors pass. One-year and
  `leavepops` visual proof remain blocked per `BLOCKERS.md`.

## 2026-08-04 high-resolution `-leavepops` control

- Fresh non-debug player Rome at 1920x1080 reached the full live opening UI,
  including the Principate agenda and seeded market list. Evidence:
  `docs/screens/R5_LEAVEPOPS_1080/leavepops_live_1080.png`.
- The expected `Culture has no pops in the setup` diagnostics occur under
  `-leavepops`; no claim is made for one-year stability. The continuous normal
  and `-leavepops` gates remain governed by the FSR renderer blocker.

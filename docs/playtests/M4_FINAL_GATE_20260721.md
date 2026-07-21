# M4 final gate attempt

Date: 2026-07-21

## Evidence

- `make full` passed: M4 definitions reported 179 cultures and 37 religions;
  the start mirror retained 13,552 populated controlled locations and
  230,000.000 thousand people.
- The enabled-mod smoke completed at `2026-07-21T17:45:00Z` with zero new
  normalized `error.log` lines against the accepted baseline.
- A fresh visible driver launch reached the responsive main menu (evidence:
  `docs/screens/20260721_193500/m4_final_audit_timeout_20260721.png`) and, via
  the scripted New Game to Observer sequence, the paused AD 1 screen at 08:00,
  1 January, 1 (evidence:
  `docs/screens/20260721_193639/m4_final_generating_20260721.png`).

## Driver observation

The direct probe was deliberately given `--max-cpu 10`. It timed out after
eight minutes because the fully rendered menu sustained about 110 percent
aggregate CPU after log quiescence. The screenshot establishes that the UI was
ready; a normal smoke run without that optional threshold passed. This is a
readiness-heuristic observation, not an M4 content error.

## Gate result

Engine and UI evidence is green, but the milestone is **not accepted**. The
source-led ledger has 335 selectors and 12,037 resolved locations across 158
mapped cultures, with a 179-culture definition catalogue. This remains below
the plan's specified 350-500 culture target. `M4-done` is withheld; the
historical-evidence blocker is recorded in `BLOCKERS.md`.

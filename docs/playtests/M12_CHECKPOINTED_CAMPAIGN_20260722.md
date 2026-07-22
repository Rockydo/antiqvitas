# M12 checkpointed campaign — 22 July 2026

## Scope

This run tested the newly committed crash-resilient Observer driver against a
longer normal-renderer interval. It was intentionally stopped when a new
runtime error violated the project's zero-new-error rule; it is not a completed
AD 1--476 campaign.

## Procedure

`gamedriver.py observer-recover --seconds 4800 --maximum-speed
--max-restarts 10` was launched from the latest autosave. The driver launched
the configured exact EU5 installation, waited for the local load and cache log
markers, entered Observer without a launcher click, recorded the autosave
fingerprint, and began its sixty-second evidence cadence.

## Observed result

- The recovered live Observer screenshot is `08:00, 1 January, 39`.
- The first periodic frame is `08:00, 25 April, 41`; the renderer remained
  alive and no crash-recovery cycle was needed.
- The runtime log then added `Getting relation with itself` and an
  `XDP` overlapping ruler-term warning. The campaign controller and exact EU5
  process were stopped immediately to avoid treating an erroring run as valid
  chronology evidence.

The screenshots are under
`docs/screens/20260722_m12_checkpointed_campaign/`. The controller's stdout
and stderr are retained on G: under `baselines/runtime/`.

## Verdict

**Fail for long-run acceptance; pass for checkpointed launch/reload.** The
recovery driver is functioning, but M5's market-relation contract is not clean
beyond the early game. No balance, decade, or renderer-recovery claim is made
from this aborted run.

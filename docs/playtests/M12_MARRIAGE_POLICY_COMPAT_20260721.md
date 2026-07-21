# AD 1 Government-Law Compatibility - 21 July 2026

## Change

M8 now carries the installed law-category and court-policy unlock contracts
that the AD 1 historical government adapters retain after vanilla advances are
disabled. M4's historically named religion families use compatible native
mechanics groups, and `tools/m12_marriage_policy_guard.py` renders a
checksum-guarded exact overlay of the installed `01_common.txt` to extend
marriage-policy availability for the Buddhist, Dharmic, Iranian, and
Manichaean groups. No overlay assigns a policy or changes the game install.

## Verification

`make validate` passed. A fresh driver-run New Game -> Observer -> paused AD 1
map session then reported:

- 0 removed invalid laws;
- 0 missing-advance diagnostics;
- 0 invalid-policy removals, including `polygyny` and
  `aristocratic_court_policy`.

The live paused-state evidence is
`docs/screens/m12_marriage_policy_probe/observer_runtime.png`. The enabled
playset then completed `make smoke` with zero new error-log lines against the
accepted baseline.

## Boundary

This verifies initialization compatibility only. It does not exercise AI
research, long-running diplomacy, or later history because the renderer crash
after play remains the controlling observer blocker.

# R20 Fresh-World Building Efficiency Runtime — 2026-08-08

## Failure and root cause

Candidate 33 was a genuinely fresh 1920x1080 world. Before Rome was allowed to
advance from 1 January AD 1, its error log added 13 `building_type.cpp`
efficiency warnings for inherited barracks, naval, trade-company, dockyard, and
order buildings. These definitions were already quarantined with impossible
availability, but EU5 validates their capacity per employee during new-world
initialization anyway.

The quarantine generator had retained four irrelevant output forms:
`local_manpower`, `local_sailors`, `manpower_to_building_owner`, and
`sailors_to_building_owner`. Candidate 34 confirmed the direct-output fix by
removing 11 warnings and isolating the last pair to the owner-directed trade
company form. The final generator removes all four forms from every inactive
legacy definition. It does not alter any of the 412 active ANTIQVITAS building
types.

## Passing candidate 35

- Fresh process PID 33164 started with game-visible fingerprint
  `e0658fb9feea3031be0da0af9dbffac0b028805340c40fdf46ae953ca055f6a4`.
- Entered the actual *Generating New Game* path and reached the country selector
  on 1 January AD 1 at 1920x1080.
- Final `error.log`: 995 bytes / 11 lines.
- Relevant counts: efficiency 0, construction context 0, formatter 0, script 0,
  assertion 0.
- The remaining lines are the established DLC store-backend and AudioArena
  environment baseline, with no content definition warning.
- `m5_building_quarantine.py --check`, `s3_building_isolation.py --check`, and
  `pdxlint.py` all pass.

## Evidence

- `docs/screens/20260808_165444/candidate35_selector.png`
- `docs/m5/building_quarantine_manifest.json`
- `tools/m5_building_quarantine.py`

Candidate 35 is a focused fresh-generation proof only. The changed tree still
requires the complete validate/smoke pair and a restarted AD 1–100 Rome gate.

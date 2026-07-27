# S2 Ancient Politics Focused Probe — 2026-07-27

## Scope

This is a reduced-QA subsystem probe, not a long observer playthrough. It
checks registry compilation, opening assignment, visible Roman council/state
office content, direct art, and paired log cleanliness.

## Static and smoke results

- `python tools/s2_ancient_politics.py --check`: PASS — 9 councils, 45 cabinet
  actions, 27 issues, 27 agendas, and 54 unique direct icons.
- `python tools/p4_manual_regression.py --check`: PASS — 108 ancient political
  entries are present in the manual-symptom regression report.
- `make smoke`: PASS — zero new `error.log` lines against the accepted
  baseline after the new definitions, localization, and textures were mounted.

## Focused live result

The game driver entered a fresh AD 1 observer start, switched to Rome, opened
Government > State Offices, and expanded the available administrative
programmes. The selector showed only the five Roman entries:

1. Census Rolls
2. Provincial Dispatches
3. Aerarium Accounts
4. Annona Contracts
5. Legionary Rosters

All five displayed distinct direct icons, descriptions, costs, and effects.
No vanilla cabinet action appeared. The probe also reconfirmed Rome's solvent
opening state: 10.96K reserve and +8.51/month in this observer context.

Evidence:

- `docs/screens/evidence/s2_politics_probe_20260727/rome_government.png`
- `docs/screens/evidence/s2_politics_probe_20260727/rome_cabinet.png`
- `docs/screens/evidence/s2_politics_probe_20260727/rome_cabinet_actions.png`
- `docs/screens/evidence/s2_politics_probe_20260727/observer_live.png`

## Issue found and corrected

The live panel proved that fixed engine chrome still used the generic words
“Parliament” and “Cabinet” even though the active content was Roman. Checked
eleven-client overrides now present the neutral shared surfaces as “Council,”
“State Offices,” and “Administrative Programme.” The active type itself remains
profile-specific, such as Roman Senate or Han Court Conference.

## Runtime boundary

After the useful screenshots were captured, EU5 exited through the already
documented `ffxFsr2ResourceIsNull` / `NVSDK_NGX_D3D12_Shutdown1` renderer
access-violation family. The crash was not triggered by opening the new action
selector and produced no new mod script error. Under the reduced-QA policy,
static profile assignment, clean paired smoke, and the successful Roman live
probe replace repetitive Han and Iranian panel cycling in this tranche.

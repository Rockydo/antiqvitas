# M8 Knowledge Runtime Report

Run date: 2026-07-20  
Game: EU5 1.3.1.1 (Pavia), build 24187685  
Mode: enabled ANTIQVITAS playset, debug-mode autonomous driver

## Automated checks

- `tools/m8_knowledge.py --check` passed: 250 advances, 50 in each of the five
  campaign ages, nine ancient institution entries, and M3-derived technology
  tiers of 60/8/86/3 for levels 1/2/3/4.
- The generator verifies every requirement exists and is in its own age (EU5
  rejects cross-age advance requirements), verifies the 25 per-age strand
  roots/leaves, strips every vanilla unit/levy unlock, and rejects the banned
  post-antique military tokens from the M8 tree.
- `make validate` passed. A fully rendered enabled-mod `make smoke` passed
  with zero new `error.log` lines after the M8 source-preserving disables were
  corrected.

## Driver evidence

The enabled mod reached the AD 1 country selector at `08:00, 1 January, 1`;
the worldwide political surface is visible in
[`m8_selector_ready_retry.png`](../screens/M8_knowledge_probe/m8_selector_ready_retry.png).
This follows the clean menu launch in
[`m8_menu_ready.png`](../screens/M8_knowledge_probe/m8_menu_ready.png).

The historical confirmation finding is now superseded. The exact-name
country-change overlay enters Observer Mode, and the 2026-07-22 M7 replay
reached maximum speed in a live AI-war session. That material retest then hit
the existing `ffxFsr2ResourceIsNull` / `NVSDK_NGX_D3D12_Shutdown1` renderer
crash before a periodic capture. AI research behavior therefore still cannot
be observed; the M8 milestone gate remains open. The static research-graph and
anachronism checks, together with the clean real-game menu load, remain green.
See `docs/playtests/M7_WAR.md` and `BLOCKERS.md` for the current retry boundary.

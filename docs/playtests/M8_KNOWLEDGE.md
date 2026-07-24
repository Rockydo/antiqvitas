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

On 2026-07-24 a bounded player-session probe replaced the obsolete AI-playback
gate. The driver entered a live AD 1 session, used the generated engine tag
map to inspect Rome and the Iceni, then opened the installed Advances panel
through its verified `top_left_8` input contract. Rome rendered the complete
high-tier Age of Principate counter (`50/50 Advances`). Iceni rendered a
coherent lower starting surface (`45/50 Advances`, empty research queue) with
the visible source-led strands **Standing Administration**, **Principate
Warfare**, **Principate Exchange**, and **Principate Learning**. Evidence is
retained in `../screens/M8_research_probe_repaired/m8_advances_panel_repaired.png`
and `m8_iceni_starting_tree.png`.

The previous FSR observer crash is irrelevant to this prompt screen and is
still documented for M7/M12; it is not a reason to require an AI research
campaign. The live interaction emitted no M8 advance, institution, or asset
identifier in `error.log`.

## Result

**PASS.** The static tree/institution contracts and the bounded research-panel
probe meet the reduced M8 acceptance criterion. No long AI research campaign
is required.

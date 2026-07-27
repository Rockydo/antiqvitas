# S2 Major Reform Branches - 2026-07-27

## Scope

This focused pass adds two constitutional alternatives for each of the four
bespoke state profiles:

- Xiongnu: Left and Right Wing Command; Chanyu Gift Circuit.
- Goguryeo: Fortress-Lineage Kingship; Royal Granary Court.
- Meroitic Kush: Dual Royal Household; Temple-Domain Stewardship.
- Anuradhapura Lanka: Reservoir Stewardship Kingship; Sangha Endowment Court.

## Deterministic checks

- `m6_power.py --check`: PASS - 45 political contracts, including 19 opening
  or dated core reforms and 26 alternatives.
- Alternative-family guard: PASS - exactly two alternatives for each of 13
  profiles.
- Reform potential: PASS - every new path is reachable only from its opening
  reform or a sibling in the same profile.
- Council inheritance: PASS - activating each path selects its dedicated
  Xiongnu, Goguryeo, Meroitic, or Anuradhapura council.
- `m8_knowledge.py --check`: PASS - all eight paths are attached to deeper
  matching Age-I branches; 611 ancient-system unlocks and all 292 opening
  profiles remain researchable.
- Localization and anachronism checks: PASS - eleven client files, zero
  missing keys, and zero prohibited player-facing terms.
- Full `run_checks.py validate`: PASS - 102/102 commands.

## Runtime smoke

Paired smoke launched the installed game with the vanilla control playset and
then with ANTIQVITAS. Both sessions reached a responsive rendered menu. The
comparison found zero mod-unique `error.log` line types and zero new lines
against the accepted baseline.

The reduced QA policy treats the generated potential/council/unlock contracts
as the focused subsystem proof; no long observer campaign is required to test
eight equivalent reform definitions.

## Result

PASS. The four profiles now retain bespoke identity across their first player
reform choices. Other major-state subdivisions and later-century successor
forms remain open.

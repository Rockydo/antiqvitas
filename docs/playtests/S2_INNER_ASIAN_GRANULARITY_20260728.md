# S2 Inner Asian Granularity Gate - 2026-07-28

## Scope

This gate covers the removal of `OAS` (Inner Asian Oasis Societies), the
reviewed reassignment of its 302 locations, eleven new bounded opening frames,
and the connected culture, religion, government, diplomacy, settlement, art,
and localization changes.

No multi-year observer campaign was run. The accepted reduced QA policy uses
full deterministic validation, a paired vanilla/mod menu smoke, and focused
subsystem checks.

## Deterministic checks

- `gmake validate`: PASS, 117/117 commands.
- `tools/s2_inner_asian_granularity.py --check`: PASS.
- Ownership: 13,549 controlled locations, 348 tags, no `OAS` owner or selector.
- New frames: 11 tags controlling 120 locations; each has a pinned capital,
  culture/religion profile, opening reform, direct standard, research unlock,
  laws, estates, buildings, history, agenda, rank, and 11-client localization.
- Revised neighbours: Dayuan, Sogdian Cities, Kangju, Wusun, Yuezhi,
  Margiana, Khotan, Kucha, Kashgar, Loulan, Turfan, Altai, and Xiongnu have
  pinned post-audit ownership counts.
- Diplomacy: 35 start dependencies; thirteen Han Western Regions tributaries;
  Aria is Arsacid-facing; Sogdian Cities is a Kangju tributary and organization
  member.
- Belief art: two new direct religion badges and eight unique direct doctrine
  illustrations. The global UI ledger covers 1,357 direct asset chains.
- Research: all 348 opening profiles can research; all ten new reforms have
  opening unlocks.

## Paired smoke

Command: `gmake smoke`

Result: PASS in 197.9 seconds.

- Vanilla control reached a responsive rendered menu.
- ANTIQVITAS reached a responsive rendered menu.
- The normalized log comparison found zero mod-only new `error.log` lines.
- Four archived-baseline delta line types were present in the current vanilla
  control and therefore were not attributed to the mod.
- Both launched sessions were stopped automatically by the driver.

## Evidence boundary

The gate validates implementation consistency, not exact ancient borders.
Hanshu/Hou Hanshu political names and distances, archaeological horizons, and
regional histories are translated onto installed EU5 geography with contested
status recorded in `docs/ASSUMPTIONS.md`. Tributary or hegemonic relations are
not converted into cultural identity or direct annexation.

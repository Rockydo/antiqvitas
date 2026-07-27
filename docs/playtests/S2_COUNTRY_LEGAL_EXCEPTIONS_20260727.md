# S2 Country Legal Exceptions - 2026-07-27

## Scope

This focused pass adds one unique legal option for each of twelve major or
high-priority opening states: Rome, Han, Parthia, Armenia, Xiongnu, Goguryeo,
Anuradhapura, Satavahana, Kush, Nabataea, Himyar, and the Cherusci.

## Deterministic checks

- `s2_ancient_laws.py --check`: PASS - 182 groups and 584 total options,
  including 26 dated and 12 country-only options.
- Tag resolution: PASS - all twelve readable design tags resolve through
  `tag_map.json` to their collision-safe engine tags.
- Profile containment: PASS - every tag belongs to the legal profile of the
  parent law group.
- Availability: PASS - every exceptional option is `unique` and uses
  `has_or_had_tag`; no regional neighbor can satisfy the gate merely by
  sharing culture, geography, government, or religion.
- Effect and evidence quality: PASS - twelve distinct packages with at least
  three harvested modifiers, valid estate preferences, descriptions, source
  routes, confidence, and bounded notes.
- Group shape: PASS - 38 enriched groups have four options and the other 144
  retain three; no group receives accidental duplicate additions.
- Full `run_checks.py validate`: PASS - 102/102 commands.

## Runtime smoke

Paired smoke launched the installed game with the vanilla control playset and
then with ANTIQVITAS. Both sessions reached a responsive rendered menu. The
comparison found zero mod-unique `error.log` line types and zero new lines
against the accepted baseline.

The reduced QA policy uses exact tag/profile inspection and real-game loading
instead of twelve repetitive panel clicks.

## Result

PASS. The first major-state exceptional-law tranche is complete. Additional
country/culture-specific privileges with direct art remain open.

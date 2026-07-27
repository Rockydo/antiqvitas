# S2 Dated Legal Options - 2026-07-27

## Scope

This focused pass adds two later developments to each of the 13 legal
profiles. They are fourth options inside selected existing groups, leaving all
14 opening selections per tag unchanged.

## Engine verification

The installed `in_game/common/laws/01_legal_system.txt` uses option-level
`potential` and `current_year` gates. Installed event scripts also verify the
full `current_date >= Y.M.D` comparator. ANTIQVITAS uses that more precise
form, rendering every threshold through `AntqDate`.

## Deterministic checks

- `s2_ancient_laws.py --check`: PASS - 13 profiles, 292 tags, 182 law groups,
  572 options, and 26 dated options.
- Profile distribution: PASS - exactly two dated options per profile.
- Package uniqueness: PASS - every dated option has a distinct set of at least
  three locally harvested modifiers.
- Date safety: PASS - all 26 thresholds validate inside AD 1-476 through
  `tools/dates.py`.
- Availability shape: PASS - exactly 26 groups have four options and the
  remaining 156 groups retain three.
- Localization and evidence: PASS - 11 client files, non-empty descriptions,
  source routes, confidence, and bounded historical notes.
- Full `run_checks.py validate`: PASS - 102/102 commands.

## Runtime smoke

Paired smoke launched the installed game with the vanilla control playset and
then with ANTIQVITAS. Both sessions reached a responsive rendered menu. The
comparison found zero mod-unique `error.log` line types and zero new lines
against the accepted baseline.

The reduced QA policy uses static date/potential inspection plus the real-game
load for this data-only tranche; advancing 382 years solely to expose the last
option would add no proportional coverage.

## Result

PASS. Later legal development now exists across every profile. Bespoke
country-only exceptional options and further privilege breadth remain open.

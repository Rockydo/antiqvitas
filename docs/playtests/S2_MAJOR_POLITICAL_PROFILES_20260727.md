# S2 Major Political Profiles - 2026-07-27

## Scope

This focused pass replaces broad opening political fallbacks for Xiongnu,
Goguryeo, Meroitic Kush, and Anuradhapura Lanka. Each profile is generated as a
single contract spanning its base reform, council, six social-order names, six
privileges, five cabinet actions, three issues, three agendas, direct art, and
research routing.

## Deterministic checks

- `s2_estate_orders.py --check`: PASS - 13 profiles, 78 grants, 78 direct
  privilege icons, and 78 polity-aware social-order names.
- `s2_ancient_politics.py --check`: PASS - 13 councils, 65 cabinet actions,
  39 issues, 39 agendas, and 78 direct political icons.
- `m6_power.py --check`: PASS - 124 total privileges, 227 law groups, and 37
  reforms; the four dedicated base reforms select their matching councils.
- `m8_knowledge.py --check`: PASS - 603 ancient-system unlocks and all 292
  opening profiles researchable.
- `m11_ui_asset_ledger.py --check`: PASS - 808 direct UI asset chains.
- `p4_manual_regression.py --check`: PASS - the exact 13-profile, 78-grant
  breadth is now a permanent regression floor.
- Full `run_checks.py validate`: PASS - 102/102 commands.

## Visual review

Eight 1536x1024 source atlases were reviewed as 3x2 archaeological object
sheets before cropping. The generated icon families use centered objects,
dark charcoal-blue backgrounds, controlled edge lighting, and no textual or
medieval elements. A first Kushite court sheet was rejected and regenerated
because decorative marks resembled invented writing. The accepted asset
contact sheet contains 808 distinct direct chains.

## Runtime smoke

Paired smoke launched the installed game first with the vanilla control
playset and then with ANTIQVITAS. Both sessions reached a responsive rendered
menu. The log comparison found zero mod-unique `error.log` line types and zero
new lines against the accepted baseline.

The user's reduced QA policy does not require repetitive live clicks through
four structurally generated profiles when startup assignments, availability
gates, localization, art chains, and research reachability are covered by the
same deterministic profile tables. A future political-panel probe can sample
one of these states when that screen is already under focused UI test.

## Result

PASS. This closes the four-state tranche only. Additional reform branches and
later-century legal development remain open under S2-P4.

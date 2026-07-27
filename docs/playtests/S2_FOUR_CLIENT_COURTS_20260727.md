# S2 Four Roman Client Courts — 2026-07-27

## Scope

This focused tranche replaces the shared political fallback for Herodian
Judea, Cappadocia, Odrysian Thrace, and the Bosporan Kingdom. It covers opening
reforms, research alternatives, councils, state-office programmes,
issue/agenda pairs, social-order names, privileges, direct art, localization,
and start-research reachability.

## Deterministic checks

- `m6_power --check`: 31 core reforms, 50 alternatives, 220 privileges, and
  227 laws across 199 opening governments.
- `s2_ancient_politics --check`: 25 councils, 125 programmes, 75 issues, 75
  agendas, and 150 direct political icons.
- `s2_estate_orders --check`: 25 profiles, 174 generated profile/country
  privileges, 174 direct privilege icons, and 150 polity-aware order names.
- `m8_knowledge --check`: 360 advances, 743 ancient-system unlocks, all 292
  opening profiles researchable, and no vanilla unlocks.
- `m11_privilege_icons --check`: all 220 active ancient privileges have direct
  icons.
- `m11_ui_asset_ledger --check`: 916 direct UI chains.
- `p4_manual_regression --check`: the permanent floor requires the complete
  25-profile political union.
- `make validate`: PASS, 103/103 commands.

## Art review

Eight exact 1536×1024 six-cell source atlases were reviewed before integration:
four for councils/programmes and four for order privileges. All accepted cells
use centered archaeological objects on a dark blue field with no people,
heraldry, modern or medieval material, or writing. Three first-pass seal cells
showed pseudo-inscription and were rejected; regenerated unmarked versions are
the pinned sources.

## Runtime smoke

The paired driver launched the installed game first with the vanilla playset
and then with ANTIQVITAS, using the relocated user directory. Both runs reached
a responsive rendered menu and were terminated by the driver.

Result: PASS. The mod run produced zero new `error.log` lines and no
mod-unique line types relative to the current vanilla control.

This follows the reduced QA policy: deterministic subsystem checks and paired
startup smoke replace a long observer campaign for this content tranche.

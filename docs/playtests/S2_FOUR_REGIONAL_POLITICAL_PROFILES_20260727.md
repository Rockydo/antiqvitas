# S2 Four Regional Political Profiles — 27 July 2026

## Scope

This focused acceptance covers the new Catuvellaunian, Marcomannic, Sabaean,
and Mauretanian political contracts. It uses the reduced project QA rule:
generated subsystem checks, one complete static regression, normal
paired-control menu smoke, and paired-control `-leavepops` smoke. No extended
observer campaign was run.

## Generated subsystem evidence

- `s2_ancient_politics.py --check`: PASS — 21 councils, 105 cabinet actions,
  63 issues, 63 agendas, and 126 direct political icons.
- `s2_estate_orders.py --check`: PASS — 21 profiles, 150 profile-plus-country
  privileges, 150 direct privilege icons, and 126 polity-aware order names.
- `m6_power.py --check`: PASS — 69 political contracts and 196 total ancient
  privileges inside a green 199-government opening roster.
- `m8_knowledge.py --check`: PASS — 360 advances, 707 ancient-system unlocks,
  no vanilla unlocks, and all 292 opening profiles researchable.
- `generate_start_mirror.py --check`: PASS — 292 verified-capital countries and
  13,550 controlled/populated locations.
- UI ledger/contact sheet: PASS — 880 direct asset chains across eight
  player-facing surfaces.
- Anachronism audit: PASS — 61,670 English player-facing entries and zero
  prohibited terms.

The first broad pass correctly failed on a duplicate Sabaean localization key
shared by an administrative programme and a privilege. The programme was
renamed to **Incense Caravan Dispatches**, its old action-only master/texture
was removed, all generated outputs were refreshed, and the localization audit
then passed with 65,596 unique quoted entries and zero stubs.

## Full static regression

`make validate`: **PASS (102/102)** after the localization correction.

Relevant whole-project protections also passed:

- 13,550 audited RGO assignments and 652 reviewed corrections.
- 2,790 opening building placements across all 292 polities.
- 265/265 active building icons style-compliant.
- 311 legacy units unavailable and all 52 active ancient units directly
  illustrated.
- 18 legacy institutions removed and no vanilla advance unlocks.
- 196/196 ancient privileges directly illustrated.

## Runtime smoke

### Standard paired control

- Vanilla control reached the rendered menu.
- Mod launch reached the rendered menu.
- Four assertion fragments differed from the archived baseline but appeared in
  the current vanilla control as well.
- Result: **PASS — zero mod-unique `error.log` lines**.

### `-leavepops` paired control

- Vanilla control reached the rendered menu.
- Mod launch reached the rendered menu with raw population adjustment disabled.
- The same four current-vanilla fragments were excluded as non-mod deltas.
- Result: **PASS — zero mod-unique `error.log` lines**.

Runtime reports were written under `<REPO_DIR>_runtime\`; these machine-local
logs are intentionally not committed.

## Verdict

PASS. All four starting states select dedicated opening reforms and councils;
their two alternatives are reachable through the ancient research graph; their
programmes, issues, agendas, order names, privileges, localization, and direct
art resolve without a generic political fallback or new runtime errors.

# S2 estate orders — focused acceptance, 2026-07-27

## Scope

This is a reduced-QA acceptance pass for the polity-aware social-order tranche.
It uses generated-content audits, direct-art inspection, research reachability,
and paired menu smoke. It deliberately does not use a long observer campaign.

## Content under test

- Nine reform-driven estate identity profiles, each resolving all six stable
  engine estate slots to period-specific social orders.
- Fifty-four profile-locked grants, six per profile, with reciprocal
  exclusivity where two grants represent competing bargains.
- More than thirty distinct modifier packages across administration, cult,
  trade, production, household obligations, food security, mobilization, and
  elite power.
- Fifty-four direct source-crop/master/BC7 art chains. Together with the
  previously accepted tranche, all 100 active ANTIQVITAS privileges have direct
  illustrations.
- Regional Age-I advance integration for all fifty-four grants.

## Static and focused checks

- `make validate`: PASS, 100/100 commands.
- `s2_estate_orders.py --check`: PASS, 9 profiles, 54 privileges, 54 direct
  icons, and 54 polity-aware order names.
- `m8_knowledge.py --check`: PASS, 360 advances, 379 ancient-system unlocks,
  292 opening profiles researchable, and no vanilla unlocks.
- `m11_privilege_icons.py --check`: PASS, 100 direct privilege icons and zero
  remaining aliases.
- `m11_ui_asset_ledger.py --check`: PASS, 784 direct UI asset chains.
- `m11_localization.py --check`: PASS, all 11 client languages mirrored and
  zero stubs.
- `m12_anachronism_audit.py --check`: PASS, zero prohibited terms.
- `p4_manual_regression.py --check`: PASS, all 20 reported symptom families and
  27 mandatory validators covered.

## Smoke result

The first paired smoke reached menu-ready in both control and mod sessions but
reported duplicate localization definitions for the new privileges. The cause
was dual generator ownership: the estate-order generator and power-system
generator both emitted the same grant labels and descriptions.

The estate-order generator now owns only dynamic social-order labels, while the
power-system generator is the sole owner of privilege labels and descriptions.
After regeneration and targeted lint, the paired smoke was rerun:

- Vanilla control: responsive, rendered, menu-ready.
- ANTIQVITAS: responsive, rendered, menu-ready.
- Final comparator: PASS, zero mod-unique new `error.log` lines.

## Acceptance

Accepted for this tranche. The remaining S2-P4 work is deeper political weights,
delegates/seats, appointments, costs, AI behavior, additional major-country
profiles, and broader laws/reforms—not correction of this accepted grant set.

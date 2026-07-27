# S2 reform paths — focused acceptance, 2026-07-27

## Scope

Rapid static and menu-smoke acceptance for the first branching government
reform expansion. No observer campaign was run.

## Coverage

- Thirty-seven ancient reforms: nineteen prior core/successor definitions and
  eighteen new alternatives.
- Exactly two alternatives for each of nine political profiles.
- Thirty or more distinct political/appointment packages.
- Profile-family potential gates, matching council and social-order identity,
  source notes, descriptions, and all eleven localization mirrors.
- Eighteen regional Age-I research unlocks; all 292 opening profiles remain
  researchable.

## Defect found and fixed

The first paired smoke found one duplicate localization key because an Iranian
reform initially reused the key of an existing law option. The reform was
renamed `antq_iranian_great_house_reform`, all generated references were
rebuilt, and a global duplicate-key assertion was added to
`m11_localization.py`. The guard now checks all 62,872 quoted English entries
for uniqueness before runtime.

## Results

- `m6_power.py --check`: PASS.
- `s2_estate_orders.py --check`: PASS.
- `s2_ancient_politics.py --check`: PASS.
- `m8_knowledge.py --check`: PASS, 397 ancient-system unlocks and no vanilla
  unlocks.
- `m11_localization.py --check`: PASS, 62,872 unique quoted entries.
- `pdxlint.py`: PASS.
- `make validate`: PASS, 100/100 commands.
- Final paired smoke: responsive rendered vanilla and mod menus; zero
  mod-unique new `error.log` lines.

## Acceptance

Accepted. The next S2-P4 work is narrower major-country reform subdivision and
broader ancient law groups.

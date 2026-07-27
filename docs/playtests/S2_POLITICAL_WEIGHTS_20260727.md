# S2 political weights — focused acceptance, 2026-07-27

## Scope

This is a rapid acceptance pass for reform-level political weights, office
appointment economics, and council participant influence. It uses installed
engine-contract inspection, deterministic validators, and paired menu smoke.
No long observer campaign is required for this data-only tranche.

## Engine contract verified

- Installed `parliament_types/readme.txt`: parliament types accept a country
  modifier block.
- Installed parliament types: delegate behavior is expressed through
  `*_can_participate_in_parliament`, `*_agenda_impact`, and
  `parliament_base_support`.
- Installed government reforms and modifier definitions: order power,
  `*_estate_power_from_cabinet`, `estate_power_from_cabinet`,
  `set_cabinet_member_cost_modifier`, and
  `replace_cabinet_member_cost_modifier` are valid country modifiers.
- No separate programmable council seat-count field is present in the local
  parliament-type contract.

## Content under test

- Nineteen core reform contracts, including the dated Dominate and Sasanian
  successors.
- At least fifteen distinct power/appointment packages.
- Nine distinct council support-and-influence profiles.
- Twenty-seven agenda-impact entries, exactly one for each participating
  social order across the nine councils.

## Results

- `m6_power.py --check`: PASS.
- `s2_ancient_politics.py --check`: PASS.
- `pdxlint.py`: PASS.
- `p4_manual_regression.py --check`: PASS.
- `make validate`: PASS, 100/100 commands.
- Paired smoke: vanilla control and ANTIQVITAS both responsive, rendered, and
  menu-ready; zero mod-unique new `error.log` lines.

## Acceptance

Accepted. Remaining S2-P4 depth is additional major-country reform families,
broader ancient law groups, and focused panel samples—not repair of these
political-weight contracts.

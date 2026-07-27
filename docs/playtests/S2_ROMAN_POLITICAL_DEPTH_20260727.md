# S2 focused probe — Roman political depth

Date: 2026-07-27
Scope: Roman reforms, councils, state offices, debates, agendas, privileges,
research unlocks, and direct UI art.

## Implemented contract

- Early Roman Senate: 11 administrative programmes, 9 issues, and 9 agendas.
- Late Imperial Consistory: 5 administrative programmes, 3 issues, and 3
  agendas, with its own six social-order names and six profile privileges.
- Successor reforms:
  - Age I: Flavian Imperial Settlement.
  - Age II: Antonine Provincial Principate.
  - Age III: Severan Military Principate.
  - Age IV: Tetrarchic Collegium and Constantinian Consistory.
  - Age V: Late Imperial Twin Courts.
- Six new exact-Rome privileges form three symmetric exclusive pairs.
- Four reviewed 1536x1024 source atlases provide 24 new direct icon chains.

## Art review

Accepted atlases:

- `roman_state_offices_ii_atlas.png` —
  `44cd5ed49cdf7b2c31f7f8744db2424335f0d80e531b624dec9d1c606b822a6a`
- `late_roman_consistory_atlas.png` —
  `f0cdfa119856f3cc36736a23966bc19b20d2b7a2b8d39d31a4d2bf3948c65329`
- `late_roman_orders_atlas.png` —
  `d274269d261318a67697b177ceab786bcdfecb4102a98162c67af1fade4bd18b`
- `roman_major_privileges_ii_atlas.png` —
  `447f09066a075492ee347720f2fbf10a461a0e02fac790cb54546a1eccdf9012`

Review checked centered circular/portrait-safe compositions, distinct material
subjects, small-size legibility, and absence of people, writing,
pseudo-writing, heraldry, modern objects, and medieval material.

The global UI contact sheet was extended to include council and state-office
art. It now contains 1,138 direct assets across nine surfaces.

## Deterministic focused probe

`python tools/s2_roman_politics_depth.py`

Result: PASS.

The permanent probe verifies:

- exact 11+5 programme and 9+3 issue/agenda counts;
- Senate activation for all six early reforms;
- Consistory activation for all four late reforms;
- unique age-correct advance unlocks for all six successors;
- exact `XAA` gating and symmetric exclusion for the three new privilege
  pairs;
- complete direct art for every Roman/late-Roman council, programme, and new
  privilege.

## Validation and runtime smoke

- Full static validation: PASS, initially 103/103; the focused Roman validator
  is now registered as command 6, raising the permanent suite to 104 commands.
- M8: PASS, 797 ancient-system unlocks; all 292 opening profiles researchable;
  no vanilla unlocks.
- Paired vanilla/mod smoke: PASS. Both sessions reached responsive rendered
  menus; the mod added zero new and zero mod-unique `error.log` lines.

Per the reduced QA policy, this tranche uses a deterministic registry probe and
paired menu smoke. It does not spend time on a long observer campaign.

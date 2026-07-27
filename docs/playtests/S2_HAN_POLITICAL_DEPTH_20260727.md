# S2 focused probe - Han political depth

Date: 2026-07-27
Scope: Han reforms, councils, state offices, debates, agendas, privileges,
research unlocks, and direct UI art.

## Implemented contract

- Western Han Court Conference: 11 administrative programmes, 9 issues, and 9
  agendas.
- Eastern Han Imperial Secretariat: 5 administrative programmes, 3 issues,
  and 3 agendas, with six separate social-order names and six profile
  privileges.
- Successor reforms:
  - Age I: Xin State Reorganization and Guangwu Restoration Court.
  - Age II: Eastern Han Imperial Secretariat and Affinal Regency Court.
  - Age III: Provincial Inspectorate Commands and Three Kingdoms Chancellery.
  - Age IV: Jin Reunification Court.
- Six new exact-Han privileges form three symmetric exclusive pairs.
- Four reviewed 1536x1024 source atlases provide 24 new direct icon chains.

## Art review

Accepted atlases:

- `han_state_offices_ii_atlas.png` -
  `b74874ce120568b763746a7c0ae809318885e4ee9ff918e5c524237e9d376e95`
- `late_han_secretariat_atlas.png` -
  `9bff557047681d86fe076b3272b199a26677568f00f6b2d557c0bc3d6b6ea7f0`
- `late_han_orders_atlas.png` -
  `a05af9c3a91bb718d652631f3ea067f61b91aa13ed04573728583229c7b2cd94`
- `han_major_privileges_ii_atlas.png` -
  `d08bba199a80f5f393d400971a01cd76989bce48913d853c044ff31164895d19`

Review checked centered circular/portrait-safe compositions, distinct material
subjects, small-size legibility, and absence of people, writing,
pseudo-writing, heraldry, modern objects, and medieval material.

The global UI contact sheet now contains 1,162 direct assets across nine
surfaces.

## Deterministic focused probe

`python tools/s2_han_politics_depth.py`

Result: PASS.

The permanent probe verifies:

- exact 11+5 programme and 9+3 issue/agenda counts;
- Western court activation for all four Western Han/Xin reforms;
- Eastern Secretariat activation for all six restored/later successor reforms;
- unique age-correct advance unlocks for all seven successors;
- exact `XAR` gating and symmetric exclusion for the three new privilege
  pairs;
- complete direct art for every Han council, programme, and new privilege.

## Validation and runtime smoke

- Full static validation: PASS, 105/105 commands.
- M6: PASS, 106 political contracts, 268 privileges, and 227 laws.
- M8: PASS, 816 ancient-system unlocks; all 292 opening profiles researchable;
  no vanilla unlocks.
- Focused Han and Roman depth probes: PASS.
- Paired vanilla/mod smoke: PASS. Both sessions reached responsive rendered
  menus; the mod added zero new and zero mod-unique `error.log` lines.

Per the reduced QA policy, this tranche uses deterministic registry checks and
one paired menu smoke after full validation. It does not use a long observer
campaign.

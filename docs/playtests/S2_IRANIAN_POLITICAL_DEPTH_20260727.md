# S2 focused probe - Arsacid and Sasanian political depth

Date: 2026-07-27
Scope: Iranian reforms, councils, state offices, debates, agendas, privileges,
research unlocks, and direct UI art.

## Implemented contract

- Arsacid Great-House Council: 11 administrative programmes, 9 issues, and 9
  agendas.
- Sasanian Royal Council: 5 administrative programmes, 3 issues, and 3 agendas,
  with six separate social-order names and six profile privileges.
- Successor reforms:
  - Age I: Vologasid Dynastic Settlement.
  - Age II: Arsacid Regional-Court Compact.
  - Age III: Late Arsacid House Mobilization, Ardashir's Unification Court,
    and Shapur's Imperial Settlement.
  - Age IV: Shahrdar and Marzban Order.
  - Age VI: Yazdegerd's Concordat Court and Bahram's Great-House Settlement.
- Six new exact-Arsacid privileges form three symmetric exclusive pairs.
- Four reviewed 1536x1024 source atlases provide 24 new direct icon chains.

## Art review

Accepted atlases:

- `arsacid_state_offices_ii_atlas.png` -
  `48c033de6c0ecf548d271007dd1fac131af723a5a3324e26e3955d2e98875330`
- `sasanian_royal_council_atlas.png` -
  `d5a17faa93bc77d2595f1525473c4b2ad730f6599ad47be57dec1643f00489ce`
- `sasanian_orders_atlas.png` -
  `04fa40340dc454300e5dff17eb924468ae2729fad3e5aa65ba8442f003ccaa3f`
- `arsacid_major_privileges_ii_atlas.png` -
  `19fdf86d85af7583308eaf02be7a5998526756f988736a8474d0b85e3cb39ecc`

Review checked centered circular/portrait-safe compositions, distinct material
subjects, small-size legibility, and absence of people, readable or
pseudo-writing, heraldry, modern objects, and medieval material. An initial
Sasanian order atlas was rejected because figurative seal motifs could read as
portraits; the accepted replacement is fully aniconic.

The global UI contact sheet now contains 1,186 direct assets across nine
surfaces.

## Deterministic focused probe

`python tools/s2_iranian_politics_depth.py`

Result: PASS.

The permanent probe verifies:

- exact 11+5 programme and 9+3 issue/agenda counts;
- Arsacid council activation for all eight Arsacid-family reforms;
- Sasanian council activation for all six Sasanian reforms;
- unique age-correct advance unlocks for all eight successors;
- exact `XAH` gating and symmetric exclusion for the three new Arsacid
  privilege pairs;
- six Sasanian profile privileges and complete direct art for every affected
  council, programme, and privilege.

## Validation and runtime smoke

- Full static validation: PASS, 106/106 commands.
- M6: PASS, 114 political contracts, 280 privileges, and 227 laws.
- M8: PASS, 836 ancient-system unlocks; all 292 opening profiles researchable;
  no vanilla unlocks.
- Focused Iranian, Han, and Roman depth probes: PASS.
- Paired vanilla/mod smoke: PASS. Both sessions reached responsive rendered
  menus; the mod added zero new and zero mod-unique `error.log` lines.

Per the reduced QA policy, this tranche uses deterministic registry checks and
one paired menu smoke after full validation. It does not use a long observer
campaign.

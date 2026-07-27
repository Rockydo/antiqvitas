# S2 focused probe - Xiongnu and Xianbei political depth

Date: 2026-07-27
Scope: Xiongnu/Xianbei reforms, councils, state offices, debates, agendas,
privileges, research unlocks, and direct UI art.

## Implemented contract

- Xiongnu Wing Council: 11 administrative programmes, 9 issues, and 9 agendas.
- Xianbei Chiefly Assembly: 5 administrative programmes, 3 issues, and 3
  agendas, with six separate social-order names and six profile privileges.
- Dated successors:
  - Age I: Southern Xiongnu Frontier Court, Northern and Western Xiongnu
    Confederacy, and Southern Xiongnu Commandery Settlement.
  - Age II: Tanshihuai's Three Divisions and Xianbei Successor Federations.
  - Age III: Five Xiongnu Divisions Order.
  - Age IV: Han-Zhao Chanyu Court, Murong Frontier Court, and Tuoba Dai
    Confederacy.
  - Age VI: Rouran Khaganate.
- Six new exact-Xiongnu privileges form three symmetric exclusive pairs.
- Four reviewed 1536x1024 source atlases provide 24 new direct icon chains.

## Art review

Accepted atlases:

- `xiongnu_state_offices_ii_atlas.png` -
  `ce9be47311990f525ae76b0665903e94017e3aadbd41c14ad39844f587d75fcd`
- `xianbei_chiefly_council_atlas.png` -
  `d2e1f5e05f34c9ed04ecbca830465b3b96f84fc506a9e0732165c67232c55ac5`
- `xianbei_orders_atlas.png` -
  `d6a140da2d62355e9376de9116bde5c284963546dcc5aa307f508792c5921a14`
- `xiongnu_major_privileges_ii_atlas.png` -
  `0c5c55a3a08b10d457144d709dc229039fa3042e38e82899aaf62d6afc1b1787`

Review checked centered circular/portrait-safe compositions, distinct
archaeological material subjects, small-size legibility, and absence of
people, readable writing, heraldry, modern objects, and later Turkic, Mongol,
or medieval motifs. Plain bands and incisions function only as tally material,
not pseudo-script.

The global UI contact sheet now contains 1,210 direct assets across nine
surfaces.

## Deterministic focused probe

`python tools/s2_steppe_politics_depth.py`

Result: PASS.

The permanent probe verifies:

- exact 11+5 programme and 9+3 issue/agenda counts;
- Xiongnu council activation for all eight Xiongnu-family reforms;
- Xianbei council activation for all six Xianbei-family reforms;
- unique age-correct advance unlocks for all ten dated successors;
- exact `XIO` gating and symmetric exclusion for three Xiongnu privilege pairs;
- six Xianbei profile privileges and complete direct art for every affected
  council, programme, and privilege.

## Validation and runtime smoke

- Full static validation: PASS, 107/107 commands.
- M6: PASS, 125 political contracts, 292 privileges, and 227 laws.
- M8: PASS, 859 ancient-system unlocks; all 292 opening profiles researchable;
  no vanilla unlocks.
- Focused Xiongnu/Xianbei, Iranian, Han, and Roman depth probes: PASS.
- Paired vanilla/mod smoke: PASS. Both sessions reached responsive rendered
  menus; the mod added zero new and zero mod-unique `error.log` lines.

Per the reduced QA policy, this tranche uses deterministic registry checks and
one paired menu smoke after full validation. It does not use a long observer
campaign.

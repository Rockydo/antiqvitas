# M5 economy acceptance report

Date: 2026-07-24  
Build: EU5 1.3.1.1 / Steam build 24187685  
Scope: bounded M5 node and market verification; no long observer campaign

## Acceptance evidence

- Static M5 checks pass in the current full validation: five custom ancient
  goods, 328 runtime RGO corrections, 78 named Roman buildings with direct
  icon contracts, 154 direct-art regional families, and 1,910 total M5/M7
  placements (1,497 productive; 1,804 scalable).
- The M11 direct-art ledger confirms the player-facing M5 surfaces have their
  own checked DDS chains: all 78 named Roman buildings and all 154 regional
  families; the project-wide UI inventory is 557 direct chains.
- The enabled-mod menu smoke on 2026-07-24 reached menu-ready state and
  reported zero new `error.log` lines versus the accepted baseline.
- The short live AD 1 observer probe recorded in `M5_TRADE_FLOW.md` reached
  May AD 1. It demonstrated localized custom production and actual pepper and
  incense imports, while the source-led annona nodes produced wheat. This is
  positive trade evidence, not an inferred route claim.

## Roman building scope

Rome's 78 source-bounded civic, cultic, commercial, water, military-supply,
and frontier specials are listed in `docs/m5/roman_buildings.csv`; the
regional system provides the scalable production layer. The 24 July loading
screen batch also adds dedicated Roman Forum, Ostia, and Campus Martius civic
art without changing any M5 data contract.

## Bounded limitation

The exact installed market-route contract has not yielded a reproducible
Faiyum-to-Roma wheat import, and the live market can assert on a long observer
run. This is recorded in `M5_TRADE_FLOW.md`. It does not invalidate the
verified RGO application, direct building contracts, or positive localized
trade evidence; no unsupported grain-route claim is made. Per the reduced
test protocol, a centuries-long observer is not an M5 requirement.

## Result

**PASS.** M5 satisfies the source-led building/UI-art and rapid
market/building-probe acceptance criteria. The unresolved market semantics
remain a documented engine limitation for future targeted investigation.

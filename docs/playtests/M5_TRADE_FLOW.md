# M5 trade-flow probe — 2026-07-22

## Scope

Test the M5 economy in a live AD 1 Observer session using the installed build's
`export_goods_by_market` console output. This is an acceptance probe, not a
milestone pass.

## Runtime RGO recovery

The previous 19 July probe remains valid: the static
`in_game/map_data/location_templates.txt` override is parsed but is not read
when the installed build instantiates an AD 1 game. Local `script_docs` instead
documents `change_raw_material` in location scope. A disposable console change
from Roma's wheat to clay changed the live ledger, proving that effect's
runtime contract.

`tools/m12_hardcoded_startup.py` now injects all 328 source-led corrections
after the exact installed `setup_area_preferences = yes` startup anchor. Custom
goods also require entries in the exact installed `pop_demands.txt` registry;
the generated mirror adds the five ANTIQVITAS raw-good keys and gives each
custom anchor one worker level. In the fresh observer export Alexandria alone
produced `1.09371` papyrus, which confirms a localized custom RGO rather than
the rejected global base-production experiment.

The source-led annona anchors are Faiyum, Sousse, Syracuse, and Cagliari. They
receive only transparent capacity seeds; the values are technical limits, not
historical yield measurements. Their historical rationale and uncertainty are
recorded in `docs/m5/annona_grain_anchors.csv` and `ASSUMPTIONS.md`.

## Procedure and live results

1. Ran `make validate` and the enabled-mod `make smoke`. Both were green; the
   smoke comparison reported zero new normalized `error.log` lines.
2. Started a new game, entered Observer Mode, let the live clock reach May AD
   1, and saved captures under `docs/screens/20260722_m5_annona/`.
3. Exported wheat, pepper, incense, and silk from the live debug console. The
   May TSVs in the configured user directory are the authoritative readback.
   Pepper showed Kodungallur production `29.04223`, Khambat imports `7.64863`,
   and Attock imports `5.58147`. Incense showed Al-Mukha production `3.24144`,
   Massawa production `2.12655`, and Meroe imports `2.06148`. Silk was produced
   at Luoyang, Chengdu, Panyu, and Chang'an but had no westward import in this
   short run.
4. The annona anchors executed: Tunis produced `4.26409` wheat and Alexandria
   produced `2.97279` wheat. Roma nevertheless had no wheat import row.
5. Tested the locally documented country-scoped `create_trade` effect twice in
   the disposable Observer game: a locked Faiyum-to-Roma wheat order, then the
   same order after a temporary Faiyum-market wheat stockpile. Neither produced
   a Roma import row. This isolates the remaining failure to the installed
   build's market/merchant-route semantics, not the raw-material renderer or
   source-market supply.

## Result

**Deferred: M5 remains untagged.** Runtime RGO application and localized custom
goods are now demonstrated, and the pepper and incense legs have real import
evidence. The required grain-to-Roma, silk-westward, incense-north, and
pepper-to-Egypt acceptance pattern is not yet fully substantiated. The two
bounded annona-route attempts are recorded in `BLOCKERS.md`; do not claim a
trade result until a materially different local market-route contract is
demonstrated.

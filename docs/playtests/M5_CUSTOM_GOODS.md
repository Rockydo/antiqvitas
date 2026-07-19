# M5 dedicated ancient-goods probe — 2026-07-19

## Scope

Verify that five new raw goods and their generated UI/modifier contracts load
in an AD 1 observer game: papyrus, silphium, naphtha/bitumen, jade, and camels.
This is a focused M5 sub-probe, not the longer trade-flow milestone gate.

## Procedure and evidence

1. Ran `make validate`: green, including the five-source input, 326 audited
   RGO corrections, generated modifier contracts, all client localizations,
   and DDS dimension/mipmap checks.
2. Ran a real `make smoke`: green, zero new `error.log` lines versus the
   accepted baseline.
3. The autonomous driver reached the AD 1 new-game selector at `08:00,
   1 January, 1`, entered Observer Mode, and started the observer session.
4. Its play-control retry reached `11:00, 3 January, 1`; the resulting frame
   visibly shows active Observer Mode and the AD 1 campaign. Screenshots are
   retained under `docs/screens/m5_custom_goods/`.
5. Searched the post-run `error.log` for every `antq_` good key, its icon
   names, the raw-goods file, and generated modifier-type references. There
   were no matches.

## Result

**Pass for this sub-surface.** The real game accepts all five raw-good,
modifier, localization, and streamed-texture contracts at menu and early
observer runtime. Trade balancing, date-gating, and extended flow observation
remain M5 work.

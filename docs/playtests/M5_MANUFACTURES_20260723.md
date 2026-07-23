# M5 manufacture expansion rapid probe — 23 July 2026

## Scope

This bounded verification covers the direct-art regional manufacture expansion:
twelve reusable workshop families, twenty-four AD 1 market-proxy placements,
their generated start mirror, localization, and 128px BC7 DDS icons. It is a
rapid menu/log-diff check, not an observer campaign or a claim about long-run
market flow.

## Static result

`make validate` passed. In particular, `m5_regional_buildings` reports 22
direct-art families and 288 regional AD 1 placements; the permanent whole-M5/M7
audit reports 234 productive placements of 354 (66.1%) and 288 scalable
placements (81.4%). The start mirror resolves 72 M5 markets, 72 urban nodes,
and all 354 M5/M7 building placements.

## Real-game rapid result

The first vanilla control launch encountered the recorded transient DX12
options-8 startup assertion and exited before rendering. A clean retry started
Steam's vanilla control, reached the menu, then started ANTIQVITAS and reached
the menu. `smoketest` found zero new `error.log` line types versus the accepted
baseline; its four vanilla-control deltas were all archived baseline deltas and
none were unique to the mod.

## Judgment

**PASS for this batch.** The new game-visible building definitions, assets,
localization, and start-state placements load cleanly at the menu. The separate
runtime market self-relation assertion remains documented in `BLOCKERS.md`; it
was neither exercised nor broadened by this rapid probe.

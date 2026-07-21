# M4 Germanic, Baltic, and Fennian atlas batch - 2026-07-21

## Scope

This source-led M4 batch adds 36 explicitly contested culture definitions and
selectors for named Germanic, Baltic, and Fennian contexts from the Lower Rhine,
Oder, Jutland, the Baltic shore, interior central Europe, Scandinavia, and one
controlled Karelia location. Every selector is a reproducible campaign-boundary
proxy, not a tribal polygon, language census, or political boundary.

`STR-GER` supplies the near-contemporary Strabo context. `TAC-GER` is a
late-first-century cross-check only, not evidence of exact AD 1 placement.
`OCD-GER` constrains the implementation against treating diverse historical
identities as a uniform Germanic map. Source details and limitations are in
`docs/world_1ad/SOURCES.md` and `docs/ASSUMPTIONS.md`.

## Generated evidence

- Catalogue: 350 cultures and 37 religions.
- Ledger: 506 source-labelled selectors resolving 12,058 controlled locations
  across 329 mapped cultures; 36 definitions/selectors belong to this batch.
- The initial `savolax_province` Fennian selection was rejected by the start
  generator because the AD 1 setup controls no locations there. It was replaced
  with controlled `shuya_karelia`, preserving a visible and reviewable
  approximation rather than fabricating an empty-population scope.
- `tools/generate_m4_definitions.py --write`,
  `tools/generate_start_mirror.py --write`,
  `tools/m12_anachronism_audit.py --write`, and `tools/popcheck.py` completed.
- `make validate` passed all static and generated contracts.

## Runtime result

Enabled-mod smoke completed at 18:42 UTC. `baselines/runtime/last_smoke.json`
reports zero new normalized `error.log` lines (two actual and two accepted
unique lines). This batch is runtime-green.

## Status

Pass for the batch's source, generator, static, and menu-load gates. Reaching
the plan's 350-culture lower bound unlocks the still-pending current M4 full
and driver-observer/map-mode acceptance gate; it does not convert the contested
frames into exact historical tribal borders.

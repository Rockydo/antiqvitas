# M4 Africa culture-atlas batch

Date: 2026-07-21

## Scope

This sixth source-led batch adds 13 non-overlapping selectors to
`docs/culture_remap.csv`. It resolves 533 more controlled locations, lifting
the audited atlas to 174 selectors, 6,199 locations, and 85 mapped cultures.
Eight generated definitions raise the M4 catalogue from 112 to 120 cultures:
Gaetulian, Garamantian, Cushitic, Equatorial Bantu, Kongo Bantu, Great Lakes
Bantu, Eastern Bantu, and Southern Bantu.

The batch uses the locally harvested installed region hierarchy for the
explicitly source-qualified Bantu-frontier frames. The resolver expands each
region to exact controlled locations and rejects unknown symbols, empty
coverage, and any overlap with a prior selector. All culture rows remain
contested regional proxies rather than homogeneous ethnic claims.

## Verification

- `make validate` passed; `m4_definitions` reports 120 cultures and 37
  religions, while `start_mirror` and `popcheck` retain all 13,552 populated
  locations and the 230,000.000-thousand population target.
- The enabled-mod `make smoke` passed with zero new normalized error-log lines.
- The region-selector capability is checked against the local harvested symbol
  inventory and geography hierarchy during every `start_mirror` validation.

## Boundary

This is a smoke checkpoint, not a claim that the global M4 culture atlas is
finished. A later fresh Observer map checkpoint will inspect the Africa labels;
the current batch preserves the project rule that every broad region remains a
source-qualified, contestable representation.

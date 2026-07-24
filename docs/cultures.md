# Cultures and Languages

This is the checked M4 culture-tree foundation. The canonical definitions live
in `docs/m4/cultures.csv`; source-labelled geographic assignments live in
`docs/culture_remap.csv`. Generated runtime definitions, colors, localization,
symbols, country definitions, and AD 1 pop culture fields are products of the
canonical project generators and must not be edited independently.

The catalogue currently contains **423 culture definitions**. The
atlas uses **627 selectors** resolving **12179 controlled
locations** across **397 explicitly mapped cultures**. Selectors are
implementation frames, not claims of homogeneous populations or exact ancient
frontiers.

`culture_remap.csv` accepts only installed area, province, location, or region
selectors. Precedence is location > province > area > region. Unknown symbols,
empty selectors, duplicate selectors, and equally specific overlaps fail the
canonical start generator rather than being silently resolved.

The language column records the closest engine-valid adapter. It is not a
historical language claim where a culture note explicitly identifies a
technical fallback.

## Completed coverage passes

- The master-plan completion is integrated directly into the canonical culture,
  remap, tag-profile, and regional-profile ledgers.
- The Britain and Ireland pass provides 34 detailed British and 16 Hibernian
  cultures, with source-qualified province frames and narrow location overrides.
- `tools/generate_m4_definitions.py --check`,
  `tools/generate_country_definitions.py --check`,
  `tools/m12_culture_presence.py --check`, and
  `tools/generate_start_mirror.py --check` remain the sole output owners and
  drift checks for this data.

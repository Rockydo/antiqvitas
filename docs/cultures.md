# Cultures and Languages

This is the checked M4 culture-tree foundation. The canonical definitions live
in `docs/m4/cultures.csv`; source-labelled geographic assignments live in
`docs/culture_remap.csv`. Generated runtime definitions, colors, localization,
symbols, and AD 1 pop culture fields must match those two ledgers.

The catalogue currently contains **373 culture definitions**. The
atlas uses **535 selectors** resolving **12179
controlled locations** across **349 explicitly mapped cultures**.
Selectors are implementation frames, not claims of homogeneous populations or
exact ancient frontiers.

`culture_remap.csv` accepts only installed area, province, location, or region
selectors. Precedence is location > province > area > region. Unknown symbols,
empty selectors, duplicate selectors, and equally specific overlaps fail the
generator rather than being silently resolved.

The language column records the closest engine-valid adapter. It is not a
historical language claim where a culture note explicitly identifies a
technical fallback.

## Completion ledgers

- `docs/m4/pro_master_plan_cultures.csv`, its remap ledger, and its profile
  ledgers separate cultures that the master plan named but the earlier atlas
  collapsed into broader frames.
- `docs/m4/pro_britain_ireland_cultures.csv`, its remap ledger, and its tag
  profiles provide the detailed Britain and Ireland pass.
- `tools/generate_pro_culture_expansion.py --check` rejects drift between those
  source ledgers and generated output.

# R5 dynamic geography-name regression repair — 2026-08-04

## Scope

The map location keyed `stuttgart` rendered the reviewed root label but could
still render the installed modern label through its Suebian/Germanic dynamic
adapters. The source settlement name postdates the campaign start.

## Repair

- The reviewed R5 location ledger now labels the field **Nicer Valley**, using
  the ancient *Nicer* hydronym for the Neckar as a transparent geographic
  proxy; its provenance and scope note are recorded in
  `docs/r5/names_locations_23201_23600.csv`.
- `tools/m4_priority_location_names.py` now uses reviewed R5 location roots for
  every priority Tier-3 adapter, preventing a high-visibility overlay from
  reviving a vanilla cartographic label.

## Verification

- `tools/r5_geography_names.py --check`: 33,801/33,801 hierarchy rows;
  eleven exact client mirrors.
- `tools/m4_priority_location_names.py --check` and
  `tools/generate_dynamic_names.py --check`: pass.
- English root, Germanic dialect, and Germanic language entries each render
  `Nicer Valley`; no `: "Stuttgart"` display value remains in the M4 English
  location surface.
- `make validate`: 171/171 pass.
- Paired `make smoke`: zero new lines at
  `485b3bdd72fa559a3fc93d4eaf3d407472557f24aa82f24e8e1405505c483052`.

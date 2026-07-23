# M5 second productive-building pass — rapid validation record

Date: 2026-07-23

Scope: twelve directly illustrated reusable antique workshop families and 168
contested city-and-hinterland seeds at fourteen already reviewed AD 1 anchors.

Rapid checks before the full gate:

- `tools/m5_regional_buildings.py --write`: PASS — 34 direct-art families,
  29 calibrated productive and 5 maintenance families, 556 regional AD 1
  placements.
- `tools/generate_start_mirror.py --write`: PASS — all generated start files
  refreshed from the ledger.
- `tools/m5_building_audit.py`: PASS — 624 M5/M7 placements, 473 productive
  (75.8%), 556 scalable (89.1%).

Full gate result:

- `make validate`: PASS.
- `make smoke`: PASS — vanilla and ANTIQVITAS both reached the menu-ready
  heuristic and the mod added zero new `error.log` lines; the vanilla control's
  four archived-baseline delta line types were not unique to the mod.

No long observer campaign is required for this asset-and-start-data batch.

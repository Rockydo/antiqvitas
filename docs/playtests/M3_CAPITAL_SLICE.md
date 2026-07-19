# M3 Capital-Control Slice

Date: 2026-07-19  
Scope: first generated political-state slice, not the M3 milestone gate

`tools/generate_start_mirror.py` now emits 50 AD 1 country entries for roster
polities whose capitals have direct, verified EU5 location-key matches. Each
entry owns and controls its mapped capital; this is deliberately narrower than
the eventual sourced global ownership map. The current engine-safe generic
government template and random ruler are transitional M3 scaffolding, to be
replaced by M6's historical government and character data.

Validation: `make validate` passed and real-game smoke reported zero new error
lines. The autonomous new-game map in `M3_capital_slice_map.png` visibly shows
the initial 34-state capital-control surface at AD 1; the same smoke-clean
generator has since expanded that set to 50 after geographic review. Unassigned
land and the remaining 83 unmapped-capital polities remain the next M3 tasks.

Curated evidence: `docs/screens/M3_capital_slice/M3_capital_slice_map.png`.

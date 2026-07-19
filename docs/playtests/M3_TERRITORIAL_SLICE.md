# M3 Territorial Political-Map Slice

Date: 2026-07-19  
Scope: sourced imperial-core ownership pass; not the M3 milestone gate

`ownership_areas.csv` names reviewed EU5 geography-hierarchy keys and records
the relevant plan/scholarly source for each. `tools/ownership_map.py` expands
them against the locally harvested hierarchy, filters broad areas to locations
proven ownable in the installed setup, rejects overlaps, and writes the checked
`ownership_resolved.csv`. Direct location rows remain explicit and reviewed.

This pass paints 4,153 locations under 56 roster polities: the Roman,
Parthian, and Western Han cores are multi-location data; the smaller reviewed
polities retain their conservative capital-control seeds. It deliberately does
not claim that unassigned edge areas, SoP extents, or subject territories are
finished. Those remain the M3 research backlog.

Validation: `make validate` passed; a real-game `make smoke` returned zero new
error lines. The autonomous new-game selector reaches `08:00, 1 January, 1`
and visibly shows the Roman and Parthian territorial surfaces. This run also
exposed false modern-key textual matches: `edessa` was Macedonian Edessa,
`susa` Italian Susa, and `khwar` a Rey-area location. Osroene was corrected to
Urfa, Elymais to Shush, and Khwarazm was returned to `TBD` pending a genuine
capital mapping.

Curated evidence: `docs/screens/M3_territorial_slice/M3_territories_start_select_retry.png`.

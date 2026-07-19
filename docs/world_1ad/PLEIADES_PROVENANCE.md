# Pleiades coordinate source

The mapping pipeline cached `pleiades-places-latest.csv.gz` on 2026-07-19 in
the G:-drive build cache (not committed). It was downloaded from the official
Pleiades CSV dump URL documented by the project:
`https://atlantides.org/downloads/pleiades/dumps/pleiades-places-latest.csv.gz`.

Pleiades is the plan's `PLE` source and distributes the dataset under CC-BY.
`tools/pleiades_capital_candidates.py` records the relevant title, coordinate,
precision, temporal range, and permanent path in a committed review report;
only reviewed coordinates then enter `capital_coordinates.csv` and only
reviewed local-map proxies enter `polities.csv`.

# Pleiades AD 1 name-review queue

`tools/pleiades_name_candidates.py` turns the checked local Pleiades snapshot
and the installed map projection into a conservative review queue. Its 656
rows are not a renaming import: map locations can represent a district, while
a Pleiades point can be a nearby settlement, port, or archaeological site.

Each candidate is limited to a precisely located Pleiades settlement point
whose declared date range includes AD 1 and whose projection lies within 3.25
pixels of the nearest installed location key. Existing capital and curated
dynamic-name anchors are excluded. The queue records the source ID, period
range, coordinate, feature type, vanilla display name, and offset so later
passes can reject false matches before adding a secure ledger row.

Run:

```powershell
.venv\Scripts\python.exe tools\pleiades_name_candidates.py --write
```

The committed `pleiades_name_candidates.csv` is an evidence worklist. Secure,
reviewed rows in `dynamic_location_name_overrides.csv` remain the Tier-1
runtime source. `tools/generate_m4_tier2_names.py` separately selects a
bounded subset (nearest AD 1 settlement, no more than 1.50 pixels away), rejects
uncertain and archaeological title forms, and records its lower-confidence
proxy status in `tier2_location_name_overrides.csv`. It never edits Tier-1.

`tools/generate_m4_tier2_wide_names.py` promotes a distinct light-review set
from the same queue only at 1.50--3.25 pixels. It rejects obvious site labels,
uses `tier2` confidence, and remains below all direct entries.

`tools/generate_m4_tier2_remote_names.py` reads the same pinned Pleiades
snapshot directly and adds a separately labelled remote Tier-2 layer at
3.25--6.00 pixels. It remains a precise, AD 1-active settlement source, but
the greater map distance means every row is explicitly a remote proxy (`T2R`),
never a claim of exact local identity. Direct, bounded, and wide Tier-2 layers
always win over it.

`tools/generate_m4_tier3_names.py` is a separate coverage fallback for every
remaining populated AD 1 map field. It copies the installed label only as an
explicit, culture-bound placeholder with `tier3` confidence and no historical
identity claim; its companion root ledger covers all named map fields. Direct
research always supersedes either fallback.

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

The committed `pleiades_name_candidates.csv` is an evidence worklist. Only a
reviewed row in `dynamic_location_name_overrides.csv` is game-visible.

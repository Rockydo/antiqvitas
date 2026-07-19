# AD 1 World Roster Sources

The roster records a source code on every row. `P8.x` means the historical
requirements in the corresponding section of the ANTIQVITAS master plan; those
requirements are cross-checked against the following research pipeline before
a row reaches `implemented` status.

- `CAH-XI`: *The Cambridge Ancient History*, Volume XI, especially Roman
  imperial, Parthian, Germanic, and demographic syntheses.
- `OCD`: *Oxford Classical Dictionary*, polity, ruler, and chronology entries.
- `BHR`: *Book of Han* geography/census tradition, read with Hans Bielenstein
  for the AD 2 commandery population allocation.
- `PLE`: Pleiades ancient places dataset, used for classical capital and
  toponym matching; credit/license review is retained for the M4 naming pass.
- `ORB`: Stanford ORBIS network model, used only for route/market sanity.
- `CHG`: China Historical GIS Han-era layers, subject to its attribution and
  non-commercial license review before data import.
- `PER`: *Periplus of the Erythraean Sea* and modern scholarship for Indian
  Ocean ports and trade polities.
- `SAM`: *Samguk Sagi* conventional dates, explicitly marked contested where
  modern archaeology does not confirm a date.

Rows marked `contested` have a corresponding entry in `docs/ASSUMPTIONS.md`.
`TBD` map capitals are historical roster records awaiting a verified mapping to
the installed EU5 location key; they are not silently guessed.

`capital_coordinates.csv` holds only conservative Pleiades/CHGIS-style
gazetteer coordinates used to generate review candidates. The coordinate
projection is fitted against directly matched local-map anchors, and a nearest
location is never promoted into `polities.csv` without an explicit geographic
judgment.

`ownership_areas.csv` uses the P8 historical requirements with CAH-XI and BHR
as applicable. It does not import borders from an external game or silently
turn coordinate proximity into territory: `tools/ownership_map.py` expands
only the installed EU5 geography hierarchy, filters broad rows through the
installed ownable-location surface, and makes the final location list reviewable
in `ownership_resolved.csv`.

`subjects.csv` likewise records only source-backed AD 1 relationships. P8.1
supplies the Roman client ring, P8.2 the Arsacid sub-kings, and P8.3 the Han
Western Regions. The M3 engine-contract label is technical scaffolding and is
not used as a historical source claim.

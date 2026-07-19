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

All 133 roster rows now have a reviewed local-map capital anchor. For an
attested city, the anchor is a direct local match or a conservative geometry
proxy with coordinate evidence; for a society of peoples or broad regional
polity, it is an explicitly documented geographic seed. Capital anchoring is
not evidence of a final border, formal capital, or population distribution.
Those claims require the separate ownership/SoP and M4 population source passes.

The Indian Ocean ownership expansion records P8.3/P8.4/P8.9 and, where useful,
CAH-XI or *Periplus* on every area row. It captures coarse reviewed frames only;
all such rows are explicitly `contested` rather than silently treating the
installed area geometry as a period border.

The Barbaricum expansion likewise uses P8.1/P8.2/P8.7 with CAH-XI. Its rows
are deliberately marked `contested`: broad regional labels are a visible
political-map scaffold, never an assertion that a present map-area boundary was
an AD 1 frontier.

The Han-world expansion records P8.1–P8.3/P8.8 with CAH-XI, CHGIS, or *Samguk
Sagi* as appropriate. Multi-capital regions are deliberately retained for the
residual SoP/source pass rather than being silently collapsed to one owner.

P8.5 and CAH-XI support the explicit African SoP families. Their map anchors
are documented geographic handles, not claimed state capitals; every broad
ownership row remains `contested` until the population-map phase.

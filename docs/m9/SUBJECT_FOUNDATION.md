# M9 Subject-Contract Foundation

`tools/m9_diplomacy.py` generates the first M9 diplomatic surface:

- `antq_client_kingdom` for the sourced Roman client ring;
- `antq_satrapy` for the Arsacid sub-king network;
- `antq_tributary` for the Han Western Regions relationship ledger;
- `antq_foederati`, unavailable until 382.1.1; and
- `antq_autonomous_city` for later city-charter use.

The historical membership list is not duplicated here: the generated start
manager reads `docs/world_1ad/subjects.csv`, whose individual rows carry
confidence and source labels. The mapping is `ROM` to client kingdom, `PAR` to
satrapy, and `HAN` to tributary. It covers the ledger's 25 AD 1 dependencies.

The legal/economic values are intentionally technical adapters rather than
claims about standardized antique treaties. Their field vocabulary was checked
against the installed 1.3.1.1 `subject_types/vassal.txt` and
`subject_types/tributary.txt`, then accepted by an enabled-mod smoke test.
Historical basis: plan sections 8.1-8.3 and 16.2; row-level `OCD`, `PLE`,
`CAH-XI`, and `CHG` citations in `docs/world_1ad/SOURCES.md`. The foederati
threshold is the plan's 382 foedus sequence (sections 10 and 16.2), rendered
through `tools/dates.py`'s `AntqDate` gateway.

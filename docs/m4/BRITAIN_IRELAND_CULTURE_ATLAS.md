# [PRO] Britain and Ireland culture atlas

## Scope

This pass replaces the three-culture Britain-and-Ireland scaffold with **50 new
culture definitions**: 34 British and 16 Hibernian. It adds **92 audited
selectors**—79 complete province frames and 13 narrow location overrides—while
retaining `antq_caledonian` only for twelve deliberately unresolved northern
locations.

The resulting global catalogue contains **423 cultures**. All source
rows are integrated directly into `docs/m4/cultures.csv`,
`docs/culture_remap.csv`, and `docs/m4/tag_profiles.csv`.

## Britain

The detailed pass includes the Catuvellauni, Trinovantes, Iceni, Brigantes,
British Atrebates, Silures, Ordovices, Dumnonii, Cantiaci, Regni, British
Belgae, Durotriges, Dobunni, Corieltauvi, Cornovii, British Parisii, Carvetii,
Demetae, Deceangli, Votadini, Selgovae, Novantae, Damnonii, Venicones, Taexali,
Epidii, Vacomagi, Decantae, Caereni, Creones, Carnonacae, northern Lugi,
Smertae, and Caithness Cornavii.

All **237 controlled British locations** resolve away from the generic
`antq_brittonic` scaffold. The twelve residual northern locations use
`antq_caledonian` because Ptolemy's geometry and later reassessments do not
support a defensible narrower assignment.

## Ireland

The pass represents all sixteen peoples in Ptolemy's Hibernian list: Vennicnii,
Rhobogdii, Erdini, Nagnatae, Autini, Gangani, Velabri, Iverni, Usdiae, Irish
Brigantes, Coriondi, Manapii, Cauci, Eblani, Voluntii, and Darini. All **95
controlled Irish locations** resolve away from the generic `antq_gaelic`
scaffold.

These are contested campaign-scale proxies. Ptolemy's relative ordering does not
license exact AD 1 ethnic borders, uniform populations, or modern county
equivalences. Source contracts are recorded in
`docs/world_1ad/SOURCES.md`.

## Verification

- 50 unique new culture keys and 92 unique selectors.
- No unknown or empty geographic selector.
- No equal-specificity overlap.
- Every new Britain-and-Ireland culture has a controlled AD 1 presence.
- The superseded broad `antq_brittonic` and `antq_gaelic` symbols, plus the
  definition-only `antq_na_dene`, are retained only through the canonical M12
  non-historical initializer-presence ledger.
- Population-location overrides remain higher priority than culture remaps.
- Runtime files are regenerated exclusively by the canonical project
  generators.

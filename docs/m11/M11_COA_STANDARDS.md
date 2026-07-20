# M11 AD 1 CoA standards

The generated `main_menu/common/coat_of_arms/coat_of_arms/antq_00_coa_standards.txt`
now supplies a layered CoA for every one of the 157 AD 1 roster polities. It
replaces the former solid-field placeholder file rather than relying on
alphabetical file precedence.

The three direct country reviews in `core_coas.csv` take priority for Rome,
Han, and Parthia. The remaining countries resolve through the 34 reviewed
regional entries in `coa_theme_catalog.csv`. Both ledgers require an installed
`ce_*.dds` colored-emblem texture, a valid roster region or tag, and a
`secure`/`contested` confidence label before the generator writes a CoA.

These are period-inspired map/UI identity standards, not reconstructions of
flags, vexilla, royal banners, sacred symbols, seals, or state standards. The
regional motifs distinguish the game map while preserving that uncertainty in
every row's note. Direct historical claims remain in the source-labelled roster
and M4 culture/religion ledgers, not in the visual motif itself.

Local verification: the renderer validated all 157 source entries against the
installed colored-emblem catalogue; `make validate` and enabled-mod `make
smoke` passed with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1-8.10 and 20; the source fields in
`docs/world_1ad/polities.csv`; local EU5 CoA definitions and texture catalogue.

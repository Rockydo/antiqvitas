# M5 Via Flaminia eastern-branch proxy

The M5 road ledger adds the bare installed-road link `narni = spoleto` as a
high-level proxy for the Via Flaminia's eastern branch. The Italian Ministry of
Culture describes the road as traced in 220-219 BCE and explains that, after
Narni, one branch crossed Terni and Spoleto before rejoining the western branch
at Forum Flaminii. The installed map has Narni and Spoleto under Roman AD 1
control but lacks the necessary Terni and intermediate anchors, so the link is
explicitly contested rather than presented as a surveyed reconstruction.

`tools/generate_start_mirror.py` verifies both endpoints against the installed
location catalogue and AD 1 ownership before writing the vanilla bare
`origin = destination` contract. This is connectivity only; it does not
resolve the separate runtime-effective RGO/trade-flow blocker.

Sources: ANTIQVITAS master plan sections 8.1 and 12.2; Stanford ORBIS route
sanity; Italian Ministry of Culture, ["Archeologia Via
Flaminia"](https://sabapumbria.cultura.gov.it/archeologia-e-territorio/archeologia-via-flaminia/).

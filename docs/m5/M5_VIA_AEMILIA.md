# M5 Via Aemilia corridor

The M5 road ledger adds four bare installed-road links for the Via Aemilia:
`rimini = bologna`, `bologna = modena`, `modena = parma`, and
`parma = piacenza`. The Italian Ministry of Culture's Roman-Rimini catalogue
identifies the Via Aemilia as the 187 BCE route from Rimini to Piacenza, while
the Ministry's Modena archive records its Bologna-Modena-Reggio Emilia axis.

The installed AD 1 map contains Roman-controlled Rimini, Bologna, Modena, Parma,
and Piacenza but not Reggio Emilia or the smaller intermediate stations. The
Rimini-Bologna and Modena-Parma links are consequently labelled contested
high-level proxies; the other two join available corridor endpoints. None is a
claim to a survey-grade reconstruction.

`tools/generate_start_mirror.py` validates the endpoints and emits the locally
verified vanilla bare `origin = destination` contract. This adds connectivity
only and does not resolve the separate runtime-effective RGO/trade-flow blocker.

Sources: ANTIQVITAS master plan sections 8.1 and 12.2; Stanford ORBIS route
sanity; Italian Ministry of Culture, ["Città romana di Ariminum /
Rimini"](https://catalogo.cultura.gov.it/detail/ibc/ArchaeologicalProperty/261525)
and ["La storia infinita della via
Emilia"](https://asmo.cultura.gov.it/mostre/archivio-mostre/la-storia-infinita-della-via-emilia).

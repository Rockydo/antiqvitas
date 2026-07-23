# Roman-world dynamic-name expansion

This 22 July 2026 batch extends the curated M4 name ledger with twenty-eight
Italian and Sicilian AD 1 forms. The Pleiades CSV snapshot in the project
cache supplies each direct ancient point, historical title, date range, and
permanent place path. The local affine-plus-residual projection check was used
only to reject a bad map-key match; it does not turn a game location into an
archaeological city polygon.

| Installed key | AD 1 display form | Pleiades place | Point | Local-match result |
| --- | --- | --- | --- | --- |
| aosta | Augusta Praetoria | 383579 | 45.73744, 7.31617 | direct local key retained |
| arezzo | Arretium | 413032 | 43.47127, 11.86305 | direct local key retained |
| bari | Barium | 442500 | 41.12922, 16.87033 | direct local key retained |
| benevento | Beneventum | 432721 | 41.13044, 14.78116 | direct local key retained |
| bergamo | Bergomum | 383589 | 45.69491, 9.66995 | direct local key retained |
| brescia | Brixia | 383603 | 45.53977, 10.22314 | direct local key retained |
| cagliari | Caralis | 471899 | 39.21489, 9.10952 | direct local key retained |
| como | Comum | 383627 | 45.81192, 9.08578 | direct local key retained |
| florence | Florentia | 413138 | 43.76980, 11.25564 | direct local key retained |
| lecce | Lupiae | 442642 | 40.35215, 18.17243 | direct local key retained |
| lucca | Luca | 403234 | 43.84184, 10.50703 | direct local key retained |
| milano | Mediolanum | 383706 | 45.46375, 9.18806 | direct local key retained |
| messina | Messana | 462538 | 38.19225, 15.55663 | direct local key retained |
| naples | Neapolis | 433014 | 40.84000, 14.25287 | direct local key retained |
| pavia | Ticinum | 383798 | 45.18590, 9.15656 | direct local key retained |
| perugia | Perusia | 413248 | 43.11119, 12.38991 | direct local key retained |
| pesaro | Pisaurum | 413256 | 43.91208, 12.91577 | direct local key retained |
| reggiocal | Regium | 452416 | 38.10928, 15.64393 | direct local key retained |
| reggioem | Regium Lepidum | 383755 | 44.69814, 10.63072 | direct local key retained |
| rimini | Ariminum | 393379 | 44.05896, 12.56319 | direct local key retained |
| salerno | Salernum | 433075 | 40.67799, 14.76592 | direct local key retained |
| siena | Saena | 413293 | 43.31862, 11.33108 | direct local key retained |
| syracuse | Syracusae | 462503 | 37.07008, 15.28334 | direct local key retained |
| trento | Tridentum | 383804 | 46.06677, 11.11914 | direct local key retained |
| trieste | Tergeste | 187578 | 45.64915, 13.77170 | direct local key retained |
| turin | Augusta Taurinorum | 383580 | 45.07178, 7.68600 | direct local key retained |
| vicenza | Vicetia | 393513 | 45.54577, 11.54028 | direct local key retained |

The source notation `PLE:<id>` in
`dynamic_location_name_overrides.csv` resolves to
`https://pleiades.stoa.org/places/<id>`. Naples, Messana, Syracusae, Lupiae,
and Regium retain a direct period form under the Latin dynamic-language adapter;
the adapter is an engine lookup and does not claim a monolingual local speech
community.

## 2026-07-23 - Exact northern and central Italian pass

Nine further installed city keys have a Pleiades settlement point whose recorded
life includes AD 1 and whose coordinate falls directly on the modern local-key
anchor. The conservative display forms are recorded below. They are direct
toponym replacements only: neither a settlement polygon nor any assertion about
local language, civic rank, population, or ownership follows from this pass.

| Installed key | AD 1 display form | Pleiades place | Point |
| --- | --- | --- | --- |
| ancona | Ancona | 413014 | 43.61899, 13.51607 |
| belluno | Bellunum | 187311 | 46.14003, 12.21739 |
| cesena | Caesena | 393397 | 44.13511, 12.24180 |
| cosenza | Consentia | 452308 | 39.29539, 16.25361 |
| cremona | Cremona | 383628 | 45.13364, 10.02615 |
| matera | Matera | 442650 | 40.66889, 16.60628 |
| parma | Parma | 383737 | 44.80151, 10.32797 |
| treviso | Tarvisium | 393503 | 45.66625, 12.24206 |
| verona | Verona | 383816 | 45.44215, 10.99572 |

The Pleiades IDs resolve through `https://pleiades.stoa.org/places/<id>` and the
project's cached CC-BY CSV snapshot, described in
`docs/world_1ad/PLEIADES_PROVENANCE.md`.

## 2026-07-23 - Exact Upper-Rhine, Norican, and Pannonian pass

Six further Roman-controlled installed city keys have Pleiades settlement points
whose temporal ranges include AD 1 and whose coordinate matches are no farther
than 0.61 km from the local city anchor. The pass excludes nearby rather than
direct candidates such as Iuvavum and Veldidena.

| Installed key | AD 1 display form | Pleiades place | Point | Point offset |
| --- | --- | --- | --- | --- |
| besancon | Vesontio | 177657 | 47.23724, 6.02792 | 0.29 km |
| ljubljana | Emona | 197258 | 46.05143, 14.50596 | 0.61 km |
| ptuj | Poetovio | 197446 | 46.41998, 15.86998 | 0.02 km |
| sopron | Scarbantia | 197501 | 47.68489, 16.58304 | 0.37 km |
| szombathely | Savaria | 197498 | 47.23514, 16.62192 | 0.49 km |
| vienna | Vindobona | 128537 | 48.20741, 16.37387 | 0.09 km |

The Latin dynamic-language adapter is an engine display lookup only. It does
not assert uniform local speech, settlement extent, provincial boundary,
citizenship, or urban rank.

## 2026-07-23 - Exact Gallic city pass

Fourteen further Roman-controlled city keys have a Pleiades settlement point
active at AD 1 and no farther than 0.62 km from the installed local anchor.
`Divodurum/Mettis` at Metz was already present and was not duplicated.

| Installed key | AD 1 display form | Pleiades place | Point offset |
| --- | --- | --- | --- |
| agen | Aginnum | 138169 | 0.22 km |
| amiens | Samarobriva Ambianorum | 109321 | 0.16 km |
| bourges | Avaricum | 138207 | 0.18 km |
| cahors | Divona | 138329 | 0.51 km |
| chartres | Autricum | 108778 | 0.28 km |
| clermont | Augustonemetum | 138202 | 0.19 km |
| limoges | Augustoritum | 138203 | 0.62 km |
| orleans | Cenabum | 138281 | 0.31 km |
| perigueux | Vesunna | 138650 | 0.02 km |
| poitiers | Limonum | 138422 | 0.57 km |
| reims | Durocortorum | 108945 | 0.49 km |
| rouen | Rotomagus | 109287 | 0.33 km |
| saintes | Mediolanum | 138458 | 0.25 km |
| toulouse | Tolosa | 246694 | 0.10 km |

The Pleiades source/master records are retained in the documented project
cache. As with every curated dynamic row, these are display labels alone, not
claims of a settlement polygon, local demography, language uniformity, civic
rank, or provincial boundary.

## 2026-07-23 - Exact Adriatic and Pannonian pass

Four Roman-controlled installed city keys have exact Pleiades settlement points
active at AD 1: Naissus, Siscia, Spalatum, and Sirmium. Their offsets from the
local-key anchor range from 0.23 km to 0.57 km. The display names are direct
point labels only and assert no municipal rank, language uniformity, city
extent, provincial boundary, citizenship, or population.

| Installed key | AD 1 display form | Pleiades place | Point offset |
| --- | --- | --- | --- |
| nis | Naissus | 207303 | 0.53 km |
| sisak | Siscia | 197504 | 0.57 km |
| split | Spalatum | 197524 | 0.23 km |
| sremska_mitrovica | Sirmium | 207447 | 0.57 km |

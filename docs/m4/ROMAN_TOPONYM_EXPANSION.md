# Roman-world dynamic-name expansion

This 22 July 2026 batch extends the curated M4 name ledger with seventeen
Italian and Sicilian AD 1 forms. The Pleiades CSV snapshot in the project
cache supplies each direct ancient point, historical title, date range, and
permanent place path. The local affine-plus-residual projection check was used
only to reject a bad map-key match; it does not turn a game location into an
archaeological city polygon.

| Installed key | AD 1 display form | Pleiades place | Point | Local-match result |
| --- | --- | --- | --- | --- |
| aosta | Augusta Praetoria | 383579 | 45.73744, 7.31617 | direct local key retained |
| bari | Barium | 442500 | 41.12922, 16.87033 | direct local key retained |
| benevento | Beneventum | 432721 | 41.13044, 14.78116 | direct local key retained |
| florence | Florentia | 413138 | 43.76980, 11.25564 | direct local key retained |
| lecce | Lupiae | 442642 | 40.35215, 18.17243 | direct local key retained |
| lucca | Luca | 403234 | 43.84184, 10.50703 | direct local key retained |
| messina | Messana | 462538 | 38.19225, 15.55663 | direct local key retained |
| naples | Neapolis | 433014 | 40.84000, 14.25287 | direct local key retained |
| pavia | Ticinum | 383798 | 45.18590, 9.15656 | direct local key retained |
| perugia | Perusia | 413248 | 43.11119, 12.38991 | direct local key retained |
| reggiocal | Regium | 452416 | 38.10928, 15.64393 | direct local key retained |
| reggioem | Regium Lepidum | 383755 | 44.69814, 10.63072 | direct local key retained |
| rimini | Ariminum | 393379 | 44.05896, 12.56319 | direct local key retained |
| salerno | Salernum | 433075 | 40.67799, 14.76592 | direct local key retained |
| siena | Saena | 413293 | 43.31862, 11.33108 | direct local key retained |
| syracuse | Syracusae | 462503 | 37.07008, 15.28334 | direct local key retained |
| turin | Augusta Taurinorum | 383580 | 45.07178, 7.68600 | direct local key retained |

The source notation `PLE:<id>` in
`dynamic_location_name_overrides.csv` resolves to
`https://pleiades.stoa.org/places/<id>`. Naples, Messana, Syracusae, Lupiae,
and Regium retain a direct period form under the Latin dynamic-language adapter;
the adapter is an engine lookup and does not claim a monolingual local speech
community.

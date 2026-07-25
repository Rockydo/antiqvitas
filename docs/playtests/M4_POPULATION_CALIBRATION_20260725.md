# M4 population calibration — 2026-07-25

## Result

PASS under the reduced rapid-test policy.

- Static truth: 230.000m world population; all 12 macro totals exact; Roman
  Empire 47.500m; Italy 7.500m across seven sourced gameplay partitions.
- City audit: 47 rows, 45 fixed map targets, explicit proper/agglomeration/game
  uncertainty bands, and no untargeted location above 75k.
- Italy culture cross-table: Latin 2.500m, Cisalpine Gallic 1.510m,
  Oscan-Umbrian 1.243m, Etruscan 0.707m, Venetic 0.591m, Greek Koine 0.500m,
  Nuragic 0.250m, Ligurian 0.199m.
- Live `-leavepops` population map: Rome 1.000m, Alexandria 0.500m,
  Jingzhao 0.650m, Ctesiphon 0.350m, Pataliputra 0.300m, Antioch 0.220m,
  Ephesus 0.180m. Rome's surrounding untargeted locations respect the 75k cap.
- The Observer-lobby start control was unreliable in this session. The bounded
  fallback used a random playable start, `discover all`, population map mode,
  and direct city `goto` commands; no long simulation was run.
- The first live start exposed the post-period `legacy_of_genghis` reform
  resolving an absent Borjigin dynasty. An exact-name invisible adapter removed
  that error family; a second fresh start confirmed it did not recur.
- Validation: 73/73 PASS. Paired normal and `-leavepops` smoke: zero mod-unique
  error-log lines.

Evidence:

- `docs/m4/population_audit.csv`
- `docs/screens/M4_population_20260725/population_major_cities_contact.png`
- `docs/screens/M4_population_20260725/population_rome_discovered.png`
- `baselines/runtime/population_validate.stdout.log`
- `baselines/runtime/population_leavepops_smoke.stdout.log`
- `baselines/runtime/population_normal_smoke.stdout.log`

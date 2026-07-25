# M3 political-granularity rapid probe - 2026-07-25

Status: PASS under the reduced rapid-subsystem policy.

## Scope

The canonical roster increased from 157 to 229. All 72 additions are Tier-3
peoples, archaeological horizons, or community frames with sourced confidence,
owned capitals, explicit culture/faith profiles, generated governments and AI,
diplomacy discovery profiles, regional CoAs, localization, agendas, and start
manager coverage.

| Target | Old residual | New residual | New starts | Largest addition |
| --- | ---: | ---: | ---: | --- |
| Germania and Scandinavia | 639 | 72 | 31 | Naristi, 77 |
| Venedi-facing eastern Europe | 997 | 56 | 7 | Dnieper, 101 |
| Finnic, Uralic, western Siberian | 337 | 36 | 14 | Upper Volga, 109 |
| Yayoi Japan and Ryukyu | 342 | 9 | 9 | Northern Honshu, 61 |
| West Africa | 367 | 24 | 11 | Middle Niger, 78 |

The machine-readable evidence is `docs/m3/political_granularity.csv`. The older
157-country overview is `docs/screens/M3_global_coverage/M3_global_map.png`.
Focused after-captures are
`docs/screens/M3_granularity_20260725/after_goto_berlin.png`,
`west_africa_after.png`, `ural_siberia_after.png`, and `japan_after.png`.

## Checks

- `tools/run_checks.py validate`: PASS, 74/74.
- Paired vanilla/mod `tools/run_checks.py smoke`: PASS, zero mod-only normalized
  lines.
- Fresh enabled New Game reached the AD 1 country-selection map. Focused log
  scans returned zero `has no pops of its primary culture`, zero
  discriminated-estate culture diagnostics, and zero Sagala/Sialkot errors.
- The native bookmark loader still emits the accepted repeated missing-HRE
  diagnostic family. It predates this batch and contains none of the new polity,
  culture, or capital keys.

The automated Observer click path failed to enter a live observer twice, so the
rapid acceptance route used the fully initialized country-selection political
map instead. No long campaign or extreme playthrough was required.

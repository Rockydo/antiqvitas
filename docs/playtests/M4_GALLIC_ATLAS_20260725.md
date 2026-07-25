# M4 Gallic Atlas - 2026-07-25

## Static result

- `tools/m4_gallic_atlas.py --check`: 503 locations, 63 cultures, 15,512.038k
  people, zero generic `antq_gallic`.
- Full validation: 75/75 checks pass.
- Paired vanilla/mod smoke: zero mod-only `error.log` lines.

## Focused runtime result

- Fresh AD 1 New Game selector reached successfully.
- Culture-map review shows granular Gallic/Belgic regional blocks:
  `docs/screens/20260725_051347/gallic_culture_map.png`,
  `docs/screens/20260725_051420/gallic_culture_paris.png`, and
  `docs/screens/20260725_051444/gallic_culture_detail.png`.
- Final selector capture after removing the compatibility definition:
  `docs/screens/20260725_052919/gallic_final_selector.png`.
- Final log counts: zero `antq_gallic`, `Culture has no pops`, or
  `has no pops of its primary culture` lines; zero errors naming any of the
  twelve new culture keys.

Result: PASS. Repeated hardcoded HRE diagnostics remain accepted native noise and
are not unique to the mod.

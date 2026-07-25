# M5 Roman Economy Probe - 2026-07-25

## Scope

Reduced-QA probe of the first P3 economy tranche: registry load, Rome start,
initial market formation, short tick stability, and focused error classes.

## Evidence

- Static: 23 Roman families; 509 placements; 15 profiles; 177 active regional
  families, of which 143 are productive; 13 custom goods; 31 direct new assets.
- Rome selected and started successfully. The session advanced to 31 January.
- No new invalid/unknown building, missing building type, invalid market link,
  unset market scope, profitability, or unused-variable line appeared.
- `make validate`: PASS, 75/75.
- paired vanilla/mod `make smoke`: PASS, zero mod-only lines.

Screens:

- `docs/screens/M5_roman_economy_quarantine_20260725/tagged_rome.png.png`
- `docs/screens/M5_roman_economy_quarantine_20260725/rome_started.png.png`
- `docs/screens/M5_roman_economy_quarantine_20260725/rome_seven_days.png.png`
- `docs/screens/M5_roman_economy_quarantine_20260725/rome_day_30.png.png`

## Result

PASS for load and short-tick stability. P3 remains open: the bounded run ended
while new markets were still being established, so exported market TSVs were
header-only. A later focused probe must capture established production/export
specialization and one construction choice; no long observer playthrough is
required.

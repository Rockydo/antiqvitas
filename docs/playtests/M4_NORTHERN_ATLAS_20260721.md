# M4 northern culture-atlas batch

Date: 2026-07-21

## Scope

This second source-led batch adds 46 non-overlapping area selectors to
`docs/culture_remap.csv`. It resolves 1,482 more controlled locations, lifting
the audited atlas to 93 selectors, 2,888 locations, and 37 mapped cultures.
The broad contested frames cover Brittonic and Caledonian Britain, Gaelic
Ireland, Germanic/Suebian/Gothic/Vandalic continental and Scandinavian areas,
Uralic Finland/Karelia, Baltic regions, and Venedi/Belgic regional proxies.

The harvested local hierarchy represents some places as a parent containing
itself and sublocations (for example `kilkenny -> cullahill, kilkenny`). The
selector resolver now treats only that direct self member as the place leaf;
any indirect cycle is still rejected. `kola_area` was deliberately excluded
because it resolves to no controlled population location.

## Verification

- `make validate` passed; `start_mirror` and `popcheck` retain all 13,552
  populated locations and the 230,000.000-thousand population target.
- The enabled-mod `make smoke` passed with zero new normalized error-log lines.
- A fresh autonomous New Game -> Observer -> `Cultures (Location)` run reached
  the paused 08:00, 1 January, 1 map. Its visible labels include Gaelic,
  Brittonic, Belgic, Suebian, Baltic, and Uralic. Evidence:
  `docs/screens/m4_north_batch_clean/culture_atlas_north_batch_clean_clear.png`.
- The fresh archive
  `G:\antiqvitas_user_data\logs\error.m4_north_batch_clean_20260721_0349.log`
  has zero `jomini_script_system` and zero `Setting a law` diagnostics after
  the culture-panel interaction.

## Boundary

These are contested regional representations, not a claim that each selected
location shared one identity, language, or political status. The global M4
target and a finer Sami/tribal-cultural pass remain open.

# M4 source-led culture remap batch

Date: 2026-07-21

## Scope

This batch adds `docs/culture_remap.csv`: 47 source-labelled area/province
selectors that resolve through the harvested local geography hierarchy to 1,406
exact controlled locations. It introduces 22 generated culture definitions and
raises the M4 catalogue from 69 to 91 cultures. The selectors cover Italy,
Iberia, Aquitania/Armorica, the Balkans, Greece/Anatolia, the Levant, Punic
coasts, South Arabia, and northeast Africa. Each row retains a source key,
confidence, and a short scope note; none imports a third-party culture-map
dataset.

## Static and menu checks

- `make validate` passed: `m4_definitions` reports 91 cultures and 37
  religions; `start_mirror` and `popcheck` retain 13,552 populated locations
  and 230,000.000 thousand people.
- The enabled-mod `make smoke` passed with zero new normalized `error.log`
  lines against the accepted baseline.

## Paused observer result

- The autonomous New Game -> Observer path reached a live, paused map at
  `08:00, 1 January, 1` after its save-load transition. Evidence:
  `docs/screens/m4_culture_remap_clean_v2/culture_atlas_clean_clear.png`.
- `Cultures (Location)` visibly renders the new Latin, Etruscan,
  Cisalpine-Gallic, Ligurian, Venetic, Lusitanian, Celtiberian, Iberian,
  Thracian, Phrygian, Cappadocian, Phoenician-Punic, and Meroitic frames among
  the existing AD 1 atlas.
- The final fresh-run archive
  `G:\antiqvitas_user_data\logs\error.m4_final_observer_20260721_0321.log`
  has zero `jomini_script_system` and zero `Setting a law` diagnostics. It
  retains inherited engine-template invalid-law/privilege notices, which are a
  separate M8/M12 compatibility surface and are not represented as an M4 pass.

## Boundary

This is a substantial regional atlas increment, not M4 milestone acceptance:
the 350-500-culture global target and additional reviewed dynamic names remain
open. Contested selector notes intentionally mark broad regional proxies rather
than asserting homogeneous identities within every resolved map location.

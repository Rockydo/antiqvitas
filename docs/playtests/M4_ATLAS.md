# M4 atlas observer probe

Date: 2026-07-21

## Scope

A fresh mod-enabled AD 1 Observer start was opened and left paused at
08:00, 1 January, 1. The normal map-mode selector was used to select
`Cultures (Location)` and then `Religions (Location)`. No player tag,
console state change, or time advance was used.

## Result

- `Cultures (Location)` rendered an internally varied atlas with visible
  Celtic, Germanic, Italic, Sarmatian, Uralić, Latin, and Baltic labels.
  Evidence: `docs/screens/m4_atlas_probe/culture_atlas.png`.
- `Religions (Location)` rendered a distinct faith atlas with visible Religio
  Romana, Germanic, Baltic-Slavic, Finnic, Tengri, Catharic, and Sámi
  Shamanist labels. Evidence:
  `docs/screens/m4_atlas_probe/religion_atlas.png`.
- `G:\antiqvitas_user_data\logs\error.m4_atlas_probe_20260721_0428.log`
  contains 2,667 normal startup/UI lines and zero `script_system` diagnostics.

This is a map-mode rendering checkpoint, not M4 milestone acceptance. The
existing 69-culture foundation remains below the design target of 350–500
cultures; that expansion remains blocked on a redistributable reviewed global
culture dataset as recorded in `BLOCKERS.md`.

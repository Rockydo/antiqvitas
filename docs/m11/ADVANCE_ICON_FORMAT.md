# Advance Icon Format

Installed EU5 build 24187685 exposes advance art through 16 calls across
9 GUI contexts. Some add a round mask; the agenda, HUD, messages, and
other contexts do not. The asset itself must therefore be safe everywhere.

## Required master

- 256x256 RGBA PNG; BC7 sRGB DDS with mipmaps.
- Fully transparent square perimeter and corners; visible alpha stays inside a
  3px safe perimeter.
- One compact, centered subject readable at 60px. Preserve useful reviewed art;
  legacy scene art may use the checked circular-alpha retrofit.
- New art must be generated four-up against actual installed EU5 advance
  cutouts, on a flat chroma-key field, then split and keyed locally.
- No baked square backdrop, border, frame, text, watermark, yellow wash,
  modern object, or subject touching the edge.

Run `python tools/m11_advance_format.py --write` after changing advance art, then
`--check`. The generated surface ledger is
`docs/m11/advance_icon_surface_audit.csv`; the contact sheet is reviewed in
actual circular context.

## Targeted replacements

Regional Law Codes, High Empire Administration, Seasonal Markets, and Standing
Administration use one EU5-referenced four-up cutout sheet. The other 361
reviewed illustrations retain their compositions under the deterministic
round-alpha compatibility treatment.

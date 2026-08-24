# Rome monthly crash regression — 2026-08-05

## Result

**Pass for the reported Rome-to-April crash on the fresh compatibility build.**
A new non-debug Rome campaign progressed to **16 May, AD 1**.  It crossed the
reported April failure window after the new recurring Annona supply action had
run at the February, March, April, and May country-monthly pulses.

## Root cause and repair

The reproducible native `C0000005` / `ffxFsr2ResourceIsNull` failure was tied
to assigning altered raw materials at the AD 1 bookmark, whether through
`change_raw_material` or map-template `raw_material` fields.  The active map
now retains the installed raw-material fields.  The four sourced Annona routes
retain their locked wheat deliveries through the native, market-scoped
`sell_goods_from_location` effect, injected into the installed
`monthly_country_pulse`; this changes neither raw-material nor worker state.

## Player-Rome evidence

| Campaign time | Observed state |
| --- | --- |
| 16 January, AD 1 | Live Rome campaign after startup. |
| 1 February, AD 1 | First country-monthly pulse completed; *Immensum Bellum* current displayed. |
| 19 February, AD 1 | Continued after current acknowledgement. |
| 7 April, AD 1 | Passed the reported failure month; coming-of-age event displayed. |
| 16 May, AD 1 | Four monthly pulses later; new-market notification displayed; game remained live. |

Screens: `docs/screens/20260805_013511/`,
`docs/screens/20260805_013633/`, `docs/screens/20260805_013907/`, and
`docs/screens/20260805_014008/`.

## Targeted checks

`tools/m12_hardcoded_startup.py --check` and `tools/s4_annona_route.py` pass.
The latter verifies all four locked Rome wheat routes have exactly one safe
monthly source delivery and that no raw-material mutation remains in that
runtime surface.

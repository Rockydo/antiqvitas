# Rome startup-crash regression — 2026-08-05

## Result

**Pass for the reported Rome-to-April crash.** A fresh non-debug, 1920x1080
Rome campaign ran continuously from AD 1 into **2 May** after the historical
raw-material ledger was removed from all engine-facing start surfaces. It
remained live while the opening market simulation, *Immensum Bellum* current,
a character coming-of-age event, and market-notification event were displayed
and acknowledged.

This is a bounded startup regression, not evidence for the separate required
Rome-to-AD-100 final gate.

## Causal isolation

The prior native `C0000005` in `ffxFsr2ResourceIsNull` reproduced from every
tested altered-RGO delivery route:

- 848 `change_raw_material` operations at `on_game_start`;
- vanilla-good-only and custom-good remap subsets;
- one bookmark-loader `alexandria = { raw_material = antq_papyrus }` probe.

The durable compatibility build therefore keeps the 848-location source ledger
and its audits, but does not emit raw-material changes in either
`common/on_action/_hardcoded.txt` or `in_game/map_data/location_templates.txt`.

## Player-Rome evidence

| Campaign time | Observed state |
| --- | --- |
| 9 January, AD 1 | Rome live; market construction notifications active. |
| 1 February, AD 1 | *Immensum Bellum* current opened with art and response. |
| 3 March, AD 1 | Continued market simulation, no exit. |
| 2 April, AD 1 | Passed the previously reported failure window; character event displayed. |
| 2 May, AD 1 | Continued after event acknowledgement; new-market event displayed. |

Screens: `docs/screens/20260805_005954/`,
`docs/screens/20260805_010123/`, `docs/screens/20260805_010332/`,
`docs/screens/20260805_010503/`, and `docs/screens/20260805_010643/`.

## Regression checks

`tools/generate_rgo_remap.py --check` and
`tools/m12_hardcoded_startup.py --check` both pass on the compatibility build.

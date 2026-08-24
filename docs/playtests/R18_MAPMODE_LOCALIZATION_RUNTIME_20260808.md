# R18 map-mode localization runtime regression — 2026-08-08

## Scope

This probe followed a deterministic 3,092-line formatter burst when a live
Rome campaign first opened Country Market. It was diagnostic evidence only;
the affected AD 21 save is not a final-campaign continuation.

## Root cause

A one-shot debugger breakpoint at the geography-name formatter captured the
UTF-32 source stream for `demena_province`. The visible name
`Tauromenium–Catana` was preceded by an internal `L` style marker produced by
the installed `game_province_definition_struct`. EU5 1.3.11 passed that already
formatted tooltip-backed label through the text formatter again, where the
marker became `Unknown formatting tag 'l'`.

A fresh unmodded 1920x1080 Viennois campaign established the control:

| Map mode | New stock formatter warnings |
| --- | ---: |
| Political | 0 |
| Country Rank | 2,366 |
| Country Market | 58 |

The defect family also affected Area (712), Region (256), Subcontinent (220),
and Continent (212) in the enabled mod before their corresponding structs were
repaired. Culture, language, religion, market, topography, and climate modes
remained clean.

The Proximity map had a separate installed localization fault. Its legend tried
to resolve `local_proximity_source` as a data-system function and emitted three
conversion errors even though that identifier is a building modifier.

## Repair

`tools/m12_engine_loc_workarounds.py` generates exact localization mirrors that:

- retain every installed geography `#TOOLTIP` target;
- omit only the redundant `|L` style that fails on the second formatting pass;
- replace the invalid Proximity data lookup with the equivalent static legend
  text; and
- cover all eleven localization directories under the project's exact-mirror
  contract.

The generator's `--check` mode is part of the canonical validation sequence.

## Fresh-process proof

After a full process restart and save load, the following modes were opened in
sequence at 1920x1080:

`Political`, `Country Rank`, `Country Market`, `Area`, `Region`,
`Subcontinent`, `Continent`, and `Proximity`.

Each mode added zero formatter/proximity errors. From the post-event baseline to
the final Proximity frame, `error.log` remained at 12 lines and 1,084 bytes:
zero total new lines. The Proximity overlay, location labels, location hover
card, legend panel, and map selection remained operational.

Screenshots:

- `docs/screens/20260808_132842/formatter_fix_country_market.png`
- `docs/screens/20260808_133656/formatter_fix_all_geography.png`
- `docs/screens/20260808_134455/engine_loc_workarounds_runtime.png`
- `docs/screens/20260808_134523/proximity_legend_fixed.png`

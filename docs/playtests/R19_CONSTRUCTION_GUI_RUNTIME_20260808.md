# R19 Construction GUI Runtime — 2026-08-08

## Scope

This focused 1920x1080 Rome probe verifies the production build-location UI's
empty and non-empty civil-construction states. It is regression evidence for the
GUI repair, not the final AD 1–100 production gate.

## Root-cause isolation

Candidate 27 first exposed two identical diagnostics on opening Ropewalk with
Roma and Neapolis listed and no queued construction:

```text
[pdx_gui_data_model.h:421]: Could not get datacontext of type Construction from model, index 0 was out of range [0,0]
```

Candidates 28–31 tested progressively narrower header/tooltip hypotheses. They
continued to emit two lines, proving the number tracked visible location rows,
not the single cancel header. Candidate 28 also demonstrated that full GUI hot
reload is unsafe by crashing the disposable process at 15:27; every subsequent
probe loaded its candidate from a fresh executable process.

The installed `build_location_lateralview.gui` row badge used
`datacontext_from_model` with `index = 0` on
`Location.GetCivilConstructions`. Its `visible = DataModelHasItems(...)` check
did not defer context evaluation. The repair replaces only this badge with a
`DataModelFirst(..., 1)` item container. Empty models instantiate no child;
non-empty models retain the original count and `Construction_tooltip`.

## Passing candidate 32

- Fresh process PID 668 started at 16:05 with tree fingerprint
  `b39acf32c3bb1fb5e45eb4bffa11639e864641fa8b1cc1d5c60d8b98d10ba293`.
- Loaded the clean paused Rome AD 2 probe save.
- Baseline `error.log`: 1,084 bytes, 12 known environment lines, zero
  `Construction`, formatter, or script errors.
- Opened Production, searched for Ropewalk, and opened the location selector.
  Roma and Neapolis both had empty civil-construction lists. The log remained
  byte-for-byte unchanged.
- Queued one Ropewalk in Neapolis. The row displayed `(+1)` and the full tooltip
  identified *Ropewalk in Neapolis*, completion on 19 December AD 2, lumber,
  clay, and stone availability, and the one-item location queue.
- Hovered the original cancel header. Its full *Cancel Latest Constructions*
  tooltip listed Neapolis, Ropewalk, 352 days, and the click action.
- Clicked the original cancel action. Neapolis returned from `0(+1)/9` to
  `0/9`; the row badge disappeared and the header returned to its empty state.
- Final `error.log`: unchanged at 1,084 bytes / 12 lines, with zero
  construction, formatter, or script errors.

## Evidence

- `docs/screens/20260808_161332/candidate32_ropewalk_locations2.png`
- `docs/screens/20260808_161409/candidate32_queued_hover_cancel.png`
- `docs/screens/20260808_161439/candidate32_badge_tooltip.png`
- `docs/screens/20260808_161506/candidate32_cancelled.png`
- `tools/m12_construction_gui_guard.py --check`: PASS
- `tools/pdxlint.py`: PASS

No TODO checkbox is cleared by this focused probe. The repaired tree still
requires canonical validation, paired smoke, and the fresh AD 1–100 gate.

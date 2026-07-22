# M12 Finale Verification

## Checked terminal contract

The chronology ledger sets both `odoacer_finale` and the campaign `end` to
4 September 476 through `tools/dates.py`. `tools/m10_final_century.py` renders
the terminal current as `antq_m10_final.5012`, recipient `XAA`, with a
once-only monthly window from 1 January to 4 September 476. Its historical
option changes the Western-Roman cosmetic identity to `ODO`, applies the
bounded prestige effect, and uses the reviewed
`gfx/interface/illustrations/event/antq_odoacer_finale.dds` asset.

`tools/m10_final_century.py --check` validates the ledger, date boundary,
recipient map, generated event, localization, and final-century image mapping
as part of `make validate`. Menu smoke has loaded this contract with zero new
script-error lines.

## Runtime evidence still required

The acceptance criterion is stricter: a driver-run observer campaign must
reach the terminal date and provide a screenshot that visibly shows the finale
firing. Observer entry is no longer blocked: the exact country-change overlay
and the 2026-07-22 M7 Rome-Parthia AI-war replay both entered a live observer
session and reached maximum speed. Sustained play nevertheless still exits in
the documented `ffxFsr2ResourceIsNull` / `NVSDK_NGX_D3D12_Shutdown1` renderer
path. The 22 July non-debug run reached 11:00 on 18 March AD 1 with four
periodic captures before this failure; see
`docs/playtests/M12_NONDEBUG_PACING_20260722.md`. This file must be updated
with a terminal-date session path, finale screenshot, and log-diff result
before M12 can close.

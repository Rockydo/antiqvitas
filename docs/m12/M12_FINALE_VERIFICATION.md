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
firing. That evidence is absent because the observer confirmation control is
still blocked, and repeated post-launch Vulkan-memory exits make long-run
automation unreliable. This file must be updated with the session path, final
date, screenshot filename, and log-diff result before M12 can close.


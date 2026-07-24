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

## Runtime evidence and remaining release work

The revised acceptance criterion requires static finale validation, a clean
fresh AD 1 start, and rapid probes for high-risk systems. It does **not**
require an AD 1-to-476 observer campaign or a screenshot of the finale firing.
The terminal event remains fully date/symbol/localization/image checked by
`tools/m10_final_century.py --check`.

Observer entry works, but sustained play exits in the documented
`ffxFsr2ResourceIsNull` / `NVSDK_NGX_D3D12_Shutdown1` renderer path. The 22
July non-debug run reached 11:00 on 18 March AD 1; the native DX12 fallback
reached 14:00 on 3 March. Their evidence remains useful optional context in
`docs/playtests/M12_NONDEBUG_PACING_20260722.md` and
`docs/playtests/M12_DX12_RENDERER_20260722.md`, but neither is a ship gate.

M12 remains open for the substantive fresh-start diagnostic gap: retained
legacy culture and religion definitions emit no-pop warnings at AD 1. The
source-preserving suppression and definition-removal paths each failed local
engine probes and are recorded in `BLOCKERS.md`. Future M12 work must find an
engine-accepted authored-population or definition contract without weakening
the accepted baseline.

# M9 Diplomacy Foundation Verification

## Static and smoke result

The generated M9 subject, war-contract, IO, and known-world layers pass
`make validate`: five subject contracts, ten casus belli, three peace terms,
four IO types, and discovery profiles for all 157 AD 1 polities. The enabled
playset also passes `make smoke` with zero new error-log lines.

## Paused AD 1 observer inspection - 21 July 2026

The autonomous driver selected New Game, enabled Observer, and started the
paused AD 1 map. The resulting country panels confirm the live diplomatic
surface without advancing time:

- Rome renders as Roman Commonwealth (`XAA`), capital Roma, with eleven
  subjects: `docs/screens/m9_diplomacy_probe/rome_runtime_panel.png`.
- Western Han renders as `XAR`, capital Chang'an, with five subjects:
  `docs/screens/m9_diplomacy_probe/han_runtime_panel2.png`.
- A controlled, paused tag fallback confirms the Xiongnu Confederation Horde
  (`XIO`), Longcheng, its Chanyu, Tengri faith, and Xiongnu culture:
  `docs/screens/m9_diplomacy_probe/xiongnu_player_panel.png`.

The selector and observer-state evidence is retained with those panels. The
initial country-card overlap around Longcheng required the no-time-advance
`tag XIO` fallback; it did not create a save or run the simulation.

That fallback also invokes a separate legacy player-context UI surface that
emits 212 vanilla HRE/Curia/Middle-Kingdom/dynastic scope diagnostics. They do
not occur in plain Observer mode and are recorded, after two bounded attempts,
in `BLOCKERS.md`; they are not evidence against the generated M9 contracts.

## Remaining acceptance work

M9 remains open. The paused panels establish that the generated client,
tributary, and confederation structures render coherently, but cannot prove
war resolution, subject behavior over time, or later foederati gating. The
two documented renderer-profile attempts crash in the FSR stack after play is
pressed, so a third identical autoplay test would not be material evidence.
Retry the M9 speed/war observation only after a verified renderer or driver
change; see `BLOCKERS.md`.

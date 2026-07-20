# M9 Diplomacy Foundation Verification

## Automated result

On 20 July 2026, the enabled ANTIQVITAS playset completed `make validate` and
the real-game `make smoke` after the M9 subject, war-contract, IO, and
known-world layers were generated. The game reached its menu-ready state and
the smoke comparison reported zero new `error.log` lines.

The IO pass required two concrete local-build corrections: one generated
`io_opinion_<type>` bias per organization type, then the matching member-status
localization keys. Both are now generator-owned and covered by `make validate`.

## Remaining gate

The game driver has not yet crossed the existing Observer confirmation modal;
see `BLOCKERS.md`. No third identical click sequence is useful evidence. After
a material driver/UI change, inspect the Han, Xiongnu, and Roman diplomacy
panels and then observe the ancient war/subject rules at speed. The M9
implementation is green; this interactive verification remains open.

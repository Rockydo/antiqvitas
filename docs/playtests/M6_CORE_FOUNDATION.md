# M6 core power foundation — runtime record

Date: 2026-07-19
Build: EU5 1.3.1.1 / Steam build 24187685
Mod mode: enabled `ANTIQVITAS` playset via relocated user directory

## Implemented, checked surface

- `tools/m6_power.py --check` reports three dynasties, nine characters, and
  three government profiles from source-labelled M6 CSV ledgers.
- Generated Rome uses `antq_principate`, Augustus, Livia, and Gaius Caesar as
  heir. Tiberius is present but neither adopted nor heir.
- Generated Western Han uses `antq_han_imperial_bureaucracy`, Emperor Ping,
  Wang Mang's dated regency, and Chang'an through the Jingzhao/Xi'an anchor.
- Generated Parthia uses `antq_parthian_king_of_kings`, Phraates V, and Musa.
- `make validate` and enabled-mod `make smoke` passed after all generated
  outputs were rebuilt; smoke reported zero new `error.log` lines.

## Autonomous observer result

The driver launched an enabled-mod New Game and reached an observer map showing
`08:00, 1 January, 1`: [loaded map screenshot](../screens/M6_core_observer/loaded_new_game.png).
This verifies the generated AD 1 start state reaches a live map instead of
only parsing at the menu.

The run did expose the known M3/M9 missing-system runtime surface (vanilla HRE,
IO, law, formable, and unpopulated-culture evaluations). A targeted scan for
the M6 reform and character identifiers found no new M6-specific line. This is
not an M6 milestone pass: the remaining government/law/estate systems still
need implementation.

## Coverage limitation

The driver attempted direct country selection and twice sent a console command
recorded in `console_history.txt`, but the visible country/console panel did
not follow those inputs reliably under the host's scaled window geometry. The
specific Rome/Han/Parthia UI verification therefore remains open in TODO and
is recorded in `KNOWN_ISSUES.md`; no human action is required or requested.

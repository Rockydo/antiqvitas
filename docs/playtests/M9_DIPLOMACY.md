# M9 Diplomacy Foundation Verification

## Result

**PASS — M9-done foundation gate, 22 July 2026.**

The generated AD 1 diplomatic web renders coherently in a paused Observer
session and matches the reviewed `docs/world_1ad/subjects.csv` ledger exactly.
The required project-wide `make full` gate also passed: all generators and
static contracts validated, and the enabled-mod smoke test found zero new
normalized `error.log` lines.

## Ledger and generated-start audit

`tools/m9_diplomacy.py --check`, run by `make full`, reports five subject
contracts, ten CBs, three peace treaties, four IO types, 157 discovery
profiles, and the 382.1.1 foederati unlock. Its checked subject adapter table
and `main_menu/setup/start/12_diplomacy.txt` render all 25 source-led AD 1
dependencies:

| Senior polity | Contract | Ledger relationships | Live panel |
| --- | --- | ---: | --- |
| Roman Commonwealth (`XAA`) | `antq_client_kingdom` | 11 | 11 |
| Parthia (`XAH`) | `antq_satrapy` | 9 | 9 |
| Western Han (`XAR`) | `antq_tributary` | 5 | 5 |

The generated IO setup separately contains the Han tributary system with the
Han court and its five Western Regions members, the Xiongnu Confederation, and
the Panhellenic Games. The Church type remains deliberately dormant at AD 1.
The 157 known-world profiles retain the generator's enforced Atlantic/Pacific
ocean exclusions.

## Paused live inspection

The autonomous driver selected New Game, enabled Observer, and entered the
paused AD 1 map at `08:00, 1 January, 1`; no simulation time was advanced.

- Rome is retained in the prior clean paused panel as Roman Commonwealth,
  Roma, with **11** subjects:
  `docs/screens/m9_diplomacy_probe/rome_runtime_panel.png`.
- Western Han is retained in the prior clean paused panel as `XAR`, Chang'an,
  with **5** subjects:
  `docs/screens/m9_diplomacy_probe/han_runtime_panel2.png`.
- The fresh current run selected Parthia (`XAH`), Ctesiphon, and displayed
  **9** subjects: `docs/screens/20260722_m9_gate/m9_current_parthia.png`.
- The fresh observer-state capture is retained at
  `docs/screens/20260722_m9_gate/m9_current_observer.png`.

These live counts exactly match the source-led relationship ledger and the
generated dependency manager. No player-context tag fallback was used in this
gate, so its known legacy UI diagnostics are not part of the acceptance run.

## Scope boundary

M9's master-plan acceptance requires coherent diplomacy screens and founding
client/tributary webs matching the AD 1 ledger. It does not claim a resolved
war, a long AI replay, or a future foederati transition: AI war behavior is
M7, dated historical behavior is M10, and sustained observer/finale evidence
is M12. Those later runtime gates remain independently open or renderer-bound
as recorded in their reports and `BLOCKERS.md`.

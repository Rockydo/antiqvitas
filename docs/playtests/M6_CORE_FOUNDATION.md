# M6 core power foundation — runtime record

Date: 2026-07-19
Build: EU5 1.3.1.1 / Steam build 24187685
Mod mode: enabled `ANTIQVITAS` playset via relocated user directory

## Implemented, checked surface

- `tools/m6_power.py --check` reports 79 dynasties, 133 characters, 107
  government profiles, 24 privileges, 23 laws, 31 ruler terms, and 15
  regnal-history rows from source-labelled M6 CSV ledgers.
- Generated Rome uses `antq_principate`, Augustus, Livia, and Gaius Caesar as
  heir. Tiberius is present but neither adopted nor heir.
- Generated Western Han uses `antq_han_imperial_bureaucracy`, Emperor Ping,
  Wang Mang's dated regency, and Chang'an through the Jingzhao/Xi'an anchor.
- Generated Parthia uses `antq_parthian_king_of_kings`, Phraates V, and Musa.
- The start profiles now also render source-labelled estate adapters, laws, and
  direct societal values through the locally verified country-manager syntax.
- Rome now separates senatorial, equestrian, priestly, urban-pleb, and military
  fallback adapters through distinct source-labelled privileges.
- The secondary AD 1 slice adds source-labelled starts for Mauretania,
  Nabataea, Kush, Xiongnu, Goguryeo, Marcomanni, and Catuvellauni; its detailed
  limits are recorded in `docs/m6/SECONDARY_AD1_ROSTER.md`.
- Judea, Galilee-Peraea, and Batanea now have the plan-specified Herodian AD 1
  rulers through the same client-monarchy adapter.
- Cappadocia, Commagene, Odrysian Thrace, and Bosporus now have sourced Roman
  client-court profiles, with the contested mappings labelled in their ledgers.
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

## 2026-07-19 Han minority-regency retest

The new foreground-safe driver selected Western Han in a fresh selector and
captured the country inspector. XAR's territory, capital, population, culture,
faith, M6 reform, and laws loaded, but its regent was the generated `Han Zhang`
rather than Wang Mang, and Emperor Ping was not the nominal ruler. The first
probe used a direct `ruler = antq_emperor_ping`; the second used the exact local
minority-regency shape (Ping as `heir`, no concurrent ruler or current term,
and the native field order). Both produced the same fallback with no new
`error.log` line. The screenshots and recovery are retained in `BLOCKERS.md`.
This is not an M6 acceptance result.

## 2026-07-21 current-term contract and Han retest

Installed start data pairs ordinary named `ruler` values with `ruler_term`.
An open term dated `1.1.1` is rejected as future, but a date-less current term
binds the incumbent without asserting an accession day. The generator now uses
that locally verified form for all 31 non-regency ledger rows. Fresh government
panels show `Augustus Valerii, 35` for ROM and `Count Phraates V Arsacid, 0`
for PAR; the latter age remains the separate no-invented-birth-date issue.
Evidence is retained in
`docs/screens/20260721_m6_termless/termless_rome_government.png` and
`docs/screens/20260721_m6_termless/termless_parthia_panel.png`.

Han was tested twice after this material engine-contract finding. First, Ping
received a date-less current term while retaining the native heir/regency
shape; then he was repeated as both `ruler` and `heir` with that term. Both
fresh XAR Government panels rendered generated `Wang Guangwu, 35`, not Emperor
Ping. The second capture is
`docs/screens/20260721_m6_han_final/han_final_government.png`; the first is
`docs/screens/20260721_m6_termless/termless_han_panel.png`. Each shape passed
static validation and enabled-mod smoke with zero new error-log lines. The
failed Han-only variation was reverted, while the verified non-regency contract
was retained. This remains an M6 acceptance blocker.

## 2026-07-19 Parthian country-panel result

A fresh enabled-mod selector run reached `08:00, 1 January, 1`, selected XAH,
and opened its Country tab. The visible panel identifies Count Phraates V
Arsacid at Ctesiphon with nine subjects; it shows the Parthian profile with one
reform and fifteen laws. Evidence is retained at
`docs/screens/20260719_200913/M6_runtime_parthia/parthia_selected.png` and
`docs/screens/20260719_200939/M6_runtime_parthia/parthia_country_tab.png`.

Phraates renders as age 0 because his source-led record intentionally omits an
unknown birth date. This presentation defect is tracked in `KNOWN_ISSUES.md`;
no invented date was added. The result is a Parthian runtime pass only, not an
M6 milestone pass while the Han regency fallback remains unresolved.

## 2026-07-19 Roman government-panel result

A fresh enabled-mod selector run reached `08:00, 1 January, 1`, selected ROM,
and started the paused Roman country session. Its Country tab shows Roma, Latin
culture, one reform, eleven societal values, and nineteen laws. The live
Government panel then rendered all five Roman estate adapters by their
generated names: Senatorial Land Exemption, Equestrian Service, Praetorian
Donatives, Priestly Colleges, and Annona. In particular, the Equestrian Service
and Priestly Colleges tooltips show their intended `+2.50%` cabinet-efficiency
modifier.

Evidence is retained under `docs/screens/20260719_212456/M6_runtime_rome/`,
including `rome_country_tab.png`, `nobility_privilege_two.png`,
`clergy_privilege_one.png`, and `annona_privilege.png`. The player-panel probe
did encounter the already-deferred global AD 1 runtime error surface; a scan
found no Roman M6 profile, privilege, reform, or character identifier in its
`error.log`. This is a Roman runtime pass only. The Han minority-regency
fallback and broader M6 scope still preclude an M6 acceptance result.

## 2026-07-24 Wang Mang officeholder-proxy retest

The final materially distinct Han variation made the documented regent Wang
Mang the generated current officeholder with Emperor Ping retained as heir. It
was deliberately described in the source ledger as a technical presentation
adapter, not an imperial accession or a pre-scripted AD 9 usurpation.

The enabled-mod AD 1 probe selected a disposable country, used the installed
debug `tag XAR` command, and opened Western Han's Government panel. It again
rendered the generated `Han Guangwu, 35` rather than Wang Mang. The panel is
retained at `docs/screens/M6_han_officeholder_proxy/han_proxy_government.png`;
the exact command-state capture is
`docs/screens/M6_han_officeholder_proxy/han_proxy_tag_xar.png`. Static
validation and the short enabled-mod smoke check both passed before the probe,
with zero new error-log lines.

The variation was reverted immediately. This exhausts the third material
engine-shape attempt without claiming a false Han ruler; see `BLOCKERS.md`.

## 2026-07-24 Character-birthplace linkage probe

All installed active-regency characters carry a `birth` location. A fresh
temporary XAR fixture therefore supplied Wang Mang with the Yuancheng
Wang-clan locality, passed M6/start-mirror checks and fresh menu smoke, and
opened the live Government panel. It still rendered `Wang Guangwu, 35`.
The unsupported individual-birthplace claim and all generated output were
reverted; evidence is `docs/screens/M6_han_birthplace_fixture/`.

## 2026-07-24 Emperor Ping father-link probe

The local 28-regency comparison identified one untried common condition: a
named father on nearly every vanilla heir. The source-backed Liu Xing--Emperor
Ping link was rendered through a temporary generated fixture, then passed full
validation and the enabled-mod smoke. A fresh AD 1 Observer start and XAR
Government-panel capture still showed generated `Liu Zhang, 35`. The exact
source-backed fixture, its generic relation renderer, and its generated output
were reverted. The retained evidence is
`docs/screens/M6_han_father_fixture/m6_father_government_menu.png`.

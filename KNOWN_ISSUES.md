# Known Issues

## M6 country-inspector coverage is partial

The foreground-safe driver now selects countries and opens their Country panel
under the host's scaled geometry. Rome's prior run and the new Parthian run
visibly show the intended rulers and their government/law profiles. Han has a
separate, reproducible silent minority-regency fallback and therefore blocks
M6 acceptance; see `BLOCKERS.md` and `docs/playtests/M6_CORE_FOUNDATION.md`.

The Parthian run also included an unrelated `chrome.exe` error modal in the
desktop capture. It did not prevent country selection or the Country tab, but
the driver must continue to capture the actual game window and must not close
or interfere with unrelated desktop applications.

## M6 missing biography dates render as age zero

EU5 renders a source-deliberate blank `birth_date` as age 0 in the live
country panel. The fresh Parthian run displayed Phraates V correctly by name,
government, capital, religion, and subjects but as age 0. The project will not
manufacture a birth date merely to alter this UI value. A later sourced
prosopography pass needs either evidence-qualified ranges or a locally verified
display-safe contract; this does not invalidate the loaded government profile.

## M5 RGO runtime coverage gap

The source-led RGO ledger and generated full location-template file pass static
validation, but two fresh observer probes show that this build retains vanilla
raw materials at runtime. The tested Roma wheat-to-clay correction and custom
papyrus anchor did not affect console market exports. The attempted
file-specific `replace_path` metadata contract was also ineffective and has
been removed. M5 trade-flow acceptance therefore remains open; see the exact
reproduction and recovery route in `BLOCKERS.md` and
`docs/playtests/M5_TRADE_FLOW.md`.

## M3 political-map runtime boundary

The active M3 mirror removes every vanilla 1337 start-manager entry and loads
157 AD 1 roster polities, 13,552 controlled locations, 25 technical dependency
records, and complete installed-ownable coverage (13,535 assigned plus 41
intentional-empty locations). SoPs remain temporary country-shaped scaffolding
until M4's population pass.

The real observer-start test exposes unset market/event links and related
vanilla building, government/law, formable, and HRE interaction evaluations.
They are not accepted baseline lines; M3 remains untagged and the exact
reproduction/recovery plan is in `BLOCKERS.md`. M5, M6, and M9 own the required
system replacements.

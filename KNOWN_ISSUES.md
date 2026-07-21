# Known Issues

## Renderer failures during observer playback

The full event-quarantine build passes a settled enabled-mod menu smoke, and
the live AD 1 Observer map advances through 1 June before exiting with an
`ffxFsr2ResourceIsNull`-stack access violation. The failure reproduced on two
material profiles: supported 1920x1080 at full scale, then the Graphics-UI
verified 70-percent Render Scale with upscaling already disabled. The latest
bundle had 14.6 GB RAM and 17.3 GB pagefile free, so the earlier low-pagefile
observation is insufficient to explain it. Renderer-profile experiments are
therefore paused; this prevents reliable observer playback. The exact evidence
and recovery boundary is in `BLOCKERS.md`.

The two 350-culture M4 startup crashes were resolved by a material generated
start-data repair: open current ruler terms at `1.1.1` were invalid for the
installed parser. The current observer reaches both required map modes; see
`docs/playtests/M4_FINAL_GATE_350_20260721.md`. This does not resolve the
separate M12 playback crash after game time advances.

## Fresh AD 1 startup inherited invalid vanilla government defaults (resolved)

The first successful observer initialization recorded 213 removed laws and
227 removed estate privileges from the installed `east_asia_monarchy` and
`asia_advanced_tribe` templates, including `royal_court_customs_law`,
`medieval_levy_law`, `noble_fortification_licenses`, and
`clergy_literacy_rights`. These were template defaults, not invalid
ANTIQVITAS definition keys. The generated country starts now render their
explicit ANTIQVITAS government block, or a minimal locally verified fallback,
without either template. The fresh paused AD 1 Observer test has zero matches
for both removal diagnostics; see `docs/playtests/AD1_STARTUP_DEFAULTS_20260721.md`.

## M12 observer and renderer reliability remain release blockers

The final observer-to-476 acceptance run has not been achieved. The observer
country-change default is now enabled by a menu-smoked exact-name overlay, but
the current game build exits in an FSR renderer access-violation stack on the
first play action. The full 40-action M11 registry, the resolved M8
institution-birth contracts, and the 7,440-event quarantine all have successful
enabled-mod evidence, so this is not evidence of a message-registry or
event-loader failure. Do not treat this development
build as release-ready for a long observer campaign; see `BLOCKERS.md` and
`docs/m12/M12_FINALE_VERIFICATION.md`.

## The exact message registry is pinned to the installed EU5 build

M11 mirrors the exact `main_menu/gui/messagetypes.txt` filename because the
installed registry does not load additive sibling files. The renderer rejects
a changed game build, SHA-256, or 1,348-entry source inventory. On an EU5
update, regenerate and menu-smoke this guarded overlay before use; do not copy
or edit the game installation.

## M10 all-century observer coverage is deferred

The AD 1-476 layers have clean enabled-mod menu smoke and no new `error.log`
lines, including the generated AD 48 Northern-Xiongnu, AD 192 Champa, AD 370
Hunnic, AD 395 Eastern-Roman, AD 418 Visigothic, and AD 429 Vandal dynamic
country contracts. Their
observer-to-era playback cannot yet be run because the first play action hits
the documented FSR renderer access violation. The country-change confirmation
is no longer the blocker: its exact-name rule overlay is menu-smoked. Retry the
M10 event-window observer route only after a material verified renderer-profile
or driver change, then capture the resulting situations and events. See
`docs/playtests/M10_001_096.md`, `docs/playtests/M10_097_199.md`,
`docs/playtests/M10_200_299.md`, `docs/playtests/M10_300_399.md`,
`docs/playtests/M10_400_476.md`, and `BLOCKERS.md`.

## M6 country-inspector coverage is partial

The foreground-safe driver now selects countries and opens their Country panel
under the host's scaled geometry. Fresh Roman and Parthian probes visibly show
their intended government/law profiles, and the Roman player-panel probe also
confirms all five source-labelled estate adapters. Han has a separate,
reproducible silent minority-regency fallback and therefore blocks M6
acceptance; see `BLOCKERS.md` and `docs/playtests/M6_CORE_FOUNDATION.md`.

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

The real observer-start test exposed generic startup and legacy-country
evaluations. Exact-source startup, CoA, and flag overlays now make absent
IO, government, HRE-status, and capital references safely false for inactive
legacy tags. A fresh AD 1 observer initialization reports zero script-system
errors. M3 remains untagged because M5, M6, and M9 still need their separate
runtime acceptance work; the exact recovery plan is in `BLOCKERS.md`.

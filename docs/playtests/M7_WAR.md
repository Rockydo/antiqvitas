# M7 warfare -- observer acceptance retest

Date: 2026-07-22 (the runtime session crossed local midnight)

Status: **accepted under the reduced rapid-subsystem test policy.**

## Verified route

The menu-smoked `country_change_allowed` overlay supersedes the old Observer
confirmation finding. The driver selected Observer, the menu changed to
`Disable Observer`, and the game began a paused session displaying `You are
currently in Observer Mode`. At maximum speed it advanced from 17:00 on 4
January to 12:00 on 15 March AD 1 in 35 seconds. Evidence is in
`docs/screens/20260721_m7_observer_retest/m7_observer_menu.png`,
`m7_observer_initial.png`, and `m7_running_highspeed.png`.

## Controlled AI war

The console help harvested from this exact build establishes `declarewar`; it
requires an active player context. An observer-scoped invocation left the War
Viewer empty, so the driver started a random country, switched using the
checked engine tag `XAA`, and issued `declarewar XAH`. The live War Viewer
shows the `1st Roman Commonwealth-Parthia War`: Roman Commonwealth attacks
Parthia, Characene, Elymais, Media Atropatene, Adiabene, Osroene, Gordyene,
Sakastan, and Margiana. The driver then issued `observe`, returning both sides
to AI control. Evidence:

- `docs/screens/20260721_m7_player_war/m7_tag_xaa_active_player.png`
- `docs/screens/20260721_m7_player_war/m7_war_created_player_context.png`
- `docs/screens/20260721_m7_player_war/m7_observer_after_war_setup.png`

## Result

The first maximum-speed AI-war interval ended before its periodic capture when
EU5 exited. Crash bundle `Europa Universalis V20260721_221809` reports an
`ffxFsr2ResourceIsNull` / `NVSDK_NGX_D3D12_Shutdown1` access violation. Its
log contains zero matches for the M7 unit types, `unit_manager`, or the
stockade fort proxy. This is the established renderer-family limitation, not
evidence that M7 warfare content fails to load.

`make validate` and enabled-mod `make smoke` were already green on the unchanged
content baseline immediately before this observer-only test. On 24 July, the
M7 validator was strengthened with a generated deployable-role audit: all six
Roman, four Arsacid, and four Marcomannic required types must be both
country-available and present in their AD 1 seed; twelve companies also cover
foot-skirmisher, heavy-foot, and mounted mercenary profiles. The check passes
with 44 ancient types and is recorded in `docs/m7/DIVERSITY_AUDIT.md`.

## Result under the rapid policy

**PASS.** The static roster/seed checks, bounded live war creation, and
zero-new-line enabled-mod smoke demonstrate that M7 loads and exposes its core
ancient warfare surface. The unrelated renderer exit remains a known runtime
limitation, but a long high-speed Observer playback is no longer an M7
acceptance requirement.

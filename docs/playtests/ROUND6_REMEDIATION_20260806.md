# Round 6 remediation evidence — 2026-08-06

This report records only fresh-campaign and generated-union evidence. It does
not close the still-open ten-year research comparison, all-path situation/event
playback, resource-telemetry run past year 5, or continuous Rome run to AD 100.

## Crash and opening-building budget

The two archived user failures remain at:

- `G:\antiqvitas_user_data\crashes\Europa Universalis V20260805_212520`
  (23:25 market-panel failure; Vulkan device-lost/write-AV path);
- `G:\antiqvitas_user_data\crashes\Europa Universalis V20260805_220507`
  (00:05 year-4 failure after system commit fell to roughly 5 MB).

The generated opening was reduced from 6,706 buildings to 2,950, close to the
2,646 installed vanilla opening rather than the prior indiscriminate saturation.
The checked union contains 1,928 productive and 1,022 civic/service/fort
placements; 2,901 (98.3%) are scalable, distributed over 1,874 locations and all
463 opening polities. The top ten polities hold only 4.9% of placements.

A fresh 1920x1080 Rome campaign opened Roma's detailed market panel on 1 January
before time advanced and remained responsive. The same process then ran at
speed 5 through all of AD 4 and reached 1 January AD 5 without a new crash
directory. No forced observer recovery was needed and `error.log` did not grow
during the extended segment. This crosses the user's former April and AD 4
failure windows, but is not the still-required run *past* AD 5 with full RAM,
commit, VRAM, widget, and driver-event telemetry.

Evidence:

- `docs/screens/20260806_024153/R6_DAY1_MARKET_OPEN.png`;
- `docs/screens/20260806_031246/observer_0004.png` (AD 4);
- `docs/screens/20260806_032345/observer_0004.png` (1 January AD 5).

The earlier building-AI null dereference remains separately mitigated by the
narrow proximity-candidate update define. The new administrative buildings do
use bounded proximity/control modifiers, so the define is retained as an engine
safety workaround; it does not disable their local modifiers or ordinary
building, construction, road, city, or market AI.

## Fresh imperial starts

No flat treasury or income modifier was added. Ancient court and diplomatic
obligations are already represented by the mod's household, elite, temple,
municipal, and subject systems, so the inherited generic budget shares were
reduced to two percent for court spending and one percent for diplomatic
spending.

- Rome: the day-one transient was -179.18, February was +120.71, and the settled
  14 March balance was +7.18 (82.14 income / 74.95 expense). Court cost was
  19.01, diplomatic spending 11.90, army 11.51, navy 14.12, forts 3.19, food
  3.13, and buildings 12.05.
- Parthia: settled 14 March balance +19.25 (26.31 / 7.06), with 633.90 reserves.
- Western Han: settled 14 March balance -7.76 (80.76 / 88.52), with 10.03k
  reserves. Its pressure was visible food (36.02) and stability (22.15)
  investment rather than a hidden administrative or culture penalty.

Screens:

- `docs/screens/20260806_035147/R6_FINAL_DAY1_ECONOMY.png`;
- `docs/screens/20260806_035624/R6_FINAL_APRIL_ECONOMY.png`;
- `docs/screens/20260806_035830/R6_PARTHIA_MARCH_ECONOMY_PANEL.png`;
- `docs/screens/20260806_040136/R6_HAN_MARCH_ECONOMY_PANEL.png`.

Rome, Parthia, and Han have opening ropewalks inside their major-market supply
circuits. The market-supply gate verifies 60 major markets and 265 bounded added
workshops; the Principate gate verifies complete circuits for Rome and five peer
markets. Roman accepted-culture capacity is now ten, Iranian peers received
scale-aware capacity, and the fresh log contains no unsupported accepted/tolerated
culture warning. Municipal Lineage Arbitration no longer applies global monthly
control loss. Seeded scriptoria, forum-basilicas, cursus stations, and peer
administrative centers provide local maximum/monthly control and bounded
propagation while remaining staffed service buildings rather than flat map-wide
control grants.

Augustus appears as Rome's active age-63 ruler, Gaius as heir, and no regency is
shown (`docs/screens/20260806_035008/R6_FINAL_ROME_SELECTOR.png`). The engine
cannot serialize BCE birth dates in the year-one bookmark, so an age-zero
placeholder is replaced on game start. Two same-day ruler-term warnings for Rome
and Parthia remain; therefore the ruler-integrity TODO is deliberately still open.
Han's child ruler/regency is historical for Emperor Ping and Wang Mang.

## Identity, situations, events, and names

The reform visibility matrix covers all 463 opening profiles and prevents Rome
from seeing Han or Indo-Scythian forms. The expanded knowledge tree contains
1,374 advances and 1,489 unlocks. Round 6 adds 135 exact-polity nodes across 15
flagship countries and 108 exact-culture nodes across 12 cultures, with early,
middle, and late chains and bounded unit/building/effect unlocks.

All 43 situations now have three themed, material responses (129 total), staged
monthly progression, readable progress variables, and AI registration. Rome,
Armenia, and Parthia are explicit actors in Gaius Caesar's Eastern Settlement.
Fresh runtime displayed distinct initial and follow-up choices through AD 5. The
old “strong setting” implementation phrase is absent from all 11 clients. Full
start/end playback remains open.

The event gate now requires 336 consequential phase events inside the 421-event
corpus. Full runtime playback of every first-century chain remains open.

The North-African descendant audit covers 843 rows across three regions, 20
areas, 95 provinces, and 725 locations. Fifty-nine corrected rows are recorded
in `docs/r5/north_africa_name_corrections.csv`; the scoped Al-/Ar-/El-, Oued,
Jebel/Djebel, Sahara, wadi, erg, hamada, and related lexeme gate reports zero
survivors across the generated hierarchy and all 11 localization clients.

## Focused green gates

- `r5_geography_names`: 33,801/33,801 rows, 11 clients;
- `m5_building_audit`: 2,950 bounded placements;
- `m5_goods_system_audit`: 104 goods, 288 buildings, 151 productive families;
- `m5_regional_buildings`: 200 families, 1,521 regional placements;
- `s3_opening_market_supply`: 60 major markets, 265 workshops;
- `s4_principate_economy`: Rome plus five peer complete circuits;
- `m6_power`: 394 governments and 31 ruler terms;
- `m8_knowledge`: 1,374 advances, 1,489 unlocks, 463 researchable profiles;
- `m10_situation_actions`: 43 situations, 129 themed actions;
- `m11_flavor_events`: 336 consequential phase events, 421 total;
- `s4_structural_audit` and `pdxlint`: pass.

The structural audit was updated to derive the three authored action names from
the situation-action generator. It now rejects stale or missing themed actions
instead of looking for the retired `_relief` and `_mobilize` templates.

The final canonical `make.cmd validate` run completed in 697 seconds and passed
all 172 checks. During the run, the combined settlement audit was corrected to
count the tribal generator's four-building packages, Rome's explicit integration
profile gained a reviewable unrecognized-resident column, both market-creation
popup settings became source-owned, and every affected derived report was
regenerated. No validator was removed or false-gated.

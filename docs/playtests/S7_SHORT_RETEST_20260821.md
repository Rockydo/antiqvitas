# Short retest — remaining S7/S6/S5 runtime checkboxes — 2026-08-21

User instruction: finish the remaining open TODO checkboxes, then a short
retest of the relevant nations (not a hundred-year playthrough). The
uninterrupted Rome century run (PID 31912, 1 January 1 → 1 January 101) stays
the crash/survival gate. This session is the missing UI, construction-queue,
comparative-nation, and Teutoburg-trigger evidence.

## Session

- Fresh player Rome, paused 1 January 1, 1920x1080 debug.
- EU5 PID 37312, tree
  `d5fc5daead74beed40543ea92e917611cf417b571d91e9ee5a34f6b0ee6ddfcc`
  (same game-visible fingerprint as the prior construct and AD 101 sessions).
- Screens: `docs/screens/S7_SHORT_RETEST_20260820/` (shared folder with the
  2026-08-20 probe; numbered 01–40 from that probe, 41–75 from the overlay
  follow-up, 80–134 from this fresh start).
- Nations tagged with engine IDs: XAA Rome, XAH Parthia, XAR Han, XDZ Suebi,
  JUD Herodian Judea, XAO Armenia, CRU Cherusci. Design tag `SUE` is not an
  engine tag.

## S7-P0 Advance-effect scale

Ledger: `docs/m8/ADVANCE_EFFECT_SCALE.md` — 1374 advances, 24/24 modifier
families, 0 zero-display rewards. Validator `tools/m8_knowledge.py --check`.

Runtime, Age of Principate, 29/48 cards, Monthly Research Progress +3.10,
research cost on the hovered card **125.00 Research Progress** (matches
`BASE * (1+4) = 125` in `docs/m8/RESEARCH_PACING.md`):

| Card | Displayed effect | Capture |
| --- | --- | --- |
| Field Boundary Witnesses | Cabinet efficiency **+1.00%** | `93_card_tooltip.png` |
| Gift and Tribute Tallies | Cabinet efficiency **+1.00%** | `58_advances.png` |
| Roman and Italic: Imperial Archives | Tax efficiency **+2.00%** | `58_advances.png` |
| River Crossing Guides | Levy recovery **+2.00%**, unlocks Limited Coastal Transport | `58_advances.png` |

No `0%`, no `+0.06%` generator fingerprints. Unique Advances 3/9.

## S7-P1 Production graph, cordage, tar, later goods

Ledger: `docs/m5/OPENING_GOODS_REACHABILITY.md` — 108 goods, 104 opening-
reachable, 4 dated later specialties, 463 polities, tar/cordage cycle rejected.

**Ropewalk is player-constructible, not seed-only.** Hover of the construct
hammer (`86_ropewalk_hammer_hover.png`): `antq_reg_ropewalk`, production
efficiency +2.00%, construction basket lumber/clay/stone all in surplus in
the Roma market, best locations Bosporan Phanagoria-Sindica / Roma /
Olisipo. Location picker (`86_ropewalk_hammer.png`) titled **Building
Ropewalk**, Roma 1/56 and Neapolis 0/9, Build control, Mass Build Ropewalk.
The unfiltered list then shows **Ropewalk 1 (+2)** queued
(`88_celadon_absent.png`). Downstream cordage users (Navalia Romae, Granary,
Wharf Crane, Horrea) appear under a "Produces Cordage" / "Uses Cordage"
filter (`53_goods_cordage.png`).

**Wood-Tar Kiln** location picker (`87_tar_hammer.png`) titled **Building
Wood-Tar Kiln**, Cancel Last Wood-Tar Kiln Construction (a queue exists),
Roma plus rural alternatives (Albingaunum, Aquila, Arretium, …), Build
control. Forest and town rows are both listed.

**Later goods, zero premature AD 1 demand.** Search "Celadon" on Western Han
shows the filter chip "Produces Yue Celadon" and **No building available
with this search criteria** (`107_han_celadon.png`). Reachability rows for
`antq_yue_celadon`, `antq_bound_codices`, `antq_cage_glass`,
`antq_garnet_cloisonne` are `later_locked` / `opening_reachable=no` / pass.

## S7-P2 Programmes and crown power

Matrix: `docs/m6/ADMINISTRATIVE_PROGRAMME_COVERAGE.md` — 463/463 tags, 5–11
visible programmes, 56 regional overlays.

Runtime **Assign a new Administrative Programme** for Rome
(`130_open_tab.png`, `131_prog1.png`, `132_prog2.png`):

- Aerarium Accounts (burghers power +2.50%, trade through owned land +5.00%)
- Census Rolls (monthly control +0.25%, cabinet +2.50%)
- Client-King Dossiers (prestige, subject loyalty +5.00)
- Fleet Supply Returns (sailors, navy maintenance)
- Annona Contracts (food consumption −1.00%, production +2.50%)
- Imperial Correspondence

Confirm dialog uses censoria potestas flavour, not a cloned stability swap.

Day-one Roman Social Orders (`81_gov.png`): Imperial Household **24% / 21%**,
Senatorial Order 50% / 160K at 100% satisfaction, Public Priesthoods 19%,
Equestrians 1% at 100%, Citizens 4%. Principate structural levers remain
+0.18 crown / +0.20 cabinet crown against senatorial +0.06 and equestrian
+0.05. Two of three cabinet seats are filled (Gaius Fufius Geminus, Lucius
Apronius). Council tab: "The Council was called 2 years ago" with Roman
issues (`84_council.png`).

Comparative day-one cabinets (tag-switch empties AI seats; seat **count**
and admin efficiency are the comparable structural reads):

| Tag | Country | Pops | Markets | Cabinet seats | Admin efficiency | Capture |
| --- | --- | --- | --- | --- | --- | --- |
| XAA | Roman Imperium | 47.490M | 31 | 3, two filled | +27.67% | `81_gov.png` `83_crown_tooltip.png` |
| XAH | Parthian Kingdom of Kings | 6.950M | 8 | 3 | +17.26% | `123_parthia_orders.png` |
| XAR | Western Han | 57.792M | 5 | 3 | +51.24% | `124_han_orders.png` |
| XDZ | People of Suebi | 206K | 1 | 2 | +18.57% | `125_suebi_orders.png` |
| JUD | Kingdom of Herodian Judea | 99,974 | 1 | 2 | +32.50% | `126_judea_orders.png` |

Han is not a copy of Rome; Suebi and Judea have the smaller two-seat
cabinet. Reform bands remain in `docs/m6/crown_power_reform_bands.csv`.

## S7-P3 Teutoburg

Static: 13/13 scenarios in `docs/m10/teutoburg_scenario_matrix.csv`. Chain
titles: Varus and the Germanic Campaign (9.3–9.5) → Strain Along the
Northern Roads → The Forest Corridors Narrow (battle from 9.8.8) → After
the Varian Disaster. Peace fallback `antq_m10.1099` *The Germania Frontier
Policy* (10.1.2–11.1.2) with Rhine consolidation / forward districts /
frontier compacts. Never silently declares war.

**Peace trigger (fresh start, no Germanic war)**
`96b_teutoburg_peace_trigger.png`: `test_event_trigger antq_m11_flavor.6012`
shows Publius Quinctilius Varus alive, Cherusci/Chatti/… exist, and every
`We are at War with <tribe>` row is **false**. The OR of eligible wars does
not fire. Console `event` still bypasses the trigger (captured in the 20
Aug probe); that is not a peace-suppression proof. `test_event_trigger` is.

**War path (20 Aug probe, same tree):** `war_on_player CRU` produced the
Cherusci WAR overlay; the campaign event art and two distinct choices
("Survey the approaches" / "Rely on the frontier commands") were visible
under it (`27_war_cherusci.png`, `28_teutoburg_war_event.png`).

Save/reload continuity is the country variables
`antq_teutoburg_varus`, `antq_teutoburg_opponent`,
`antq_teutoburg_chain_active`, `antq_teutoburg_battle_resolved`,
`antq_teutoburg_aftermath_seen`, `antq_teutoburg_policy_resolved`.

## S6 civil war, cordage, research, situations, events

Civil-war audit: `docs/playtests/S6_CIVIL_WAR_AUDIT_20260821.md`. Year 3/4
did not collapse on the century process. AD 24 nobles war recovered by AD
43. Council pulse, cabinet refill, and praetorian/principate rebalance are
on disk; day-one Senate satisfaction is 100%.

Research pacing: static ages 95/96/92/92/19/82 years, costs 75–375.
Runtime day-one 125-point cards at +3.10/month; the century process entered
Age of High Empires around AD 96 with 29/48 Principate cards already taken
on this fresh start's tree.

Gaius Caesar's Eastern Settlement: three unique choices in
`23_gaius_event.png` (recorded settlement / local compact / mobilize).
Actors XAA/XAO/XAH. Progress variable with monthly 2.5/1.75/0.5 and
25/50/75 milestones; situation actions embassy/client/ultimatum add 16/28/36
progress with distinct costs. 100 AD run showed the same non-cloned pattern
on Claudian Britain and Trajan's Dacian Wars.

## S5 quarantine and century playback

22 inherited vanilla situations remain `always = no` dated past 476
(`western_schism`, `reformation`, `black_death`, …). 100 AD playback:
Immensum Bellum, Claudian Invasion of Britain, Trajan's Dacian Wars, all
with unique directed choices. Renderer crash folders on this host still end
2026-08-11; none in PID 31912 or PID 37312.

## Gates

- Century survival: `docs/playtests/S7_ROME_AD100_20260820.md`.
- This short retest: construction queue, advance tooltips, programme picker,
  comparative nations, Teutoburg peace trigger, later-good absence.
- `make validate`: 185/185 PASS after regenerating the Teutoburg scenario
  ledger (`tools/s7_teutoburg_scenarios.py --write`). Paired smoke last
  passed on this same tree fingerprint
  `d5fc5daead74beed40543ea92e917611cf417b571d91e9ee5a34f6b0ee6ddfcc`; a live
  EU5 session owned the slot during the short retest, so smoke is that prior
  green result rather than a second concurrent launch.

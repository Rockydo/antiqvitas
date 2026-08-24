# S7 Rome runtime — 2026-08-19

Fresh player Rome at 1920x1080, debug build, session
`docs/screens/S7_ROME_LIVE_20260819/` and campaign
`docs/screens/S7_ROME_CAMPAIGN_20260819/`.

## Start route

`start-country` from the branded menu never leaves the lobby. The working
sequence is `capture-new-game-loading` (New Game at 0.14, 0.383) then
`start-country` on the Europe selector. Italy is 0.40, 0.62. The Play button is
dark bronze at about 0.50, 0.866 of the windowed frame; title-bar parking
edge-scrolls the map and makes the Agenda heuristic fire on brown ocean. The
driver now locates the Play control and parks on the left country panel.

## Day-one paused HUD (1 January 1)

- Roman Imperium, Age of Principate, Princeps Augustus Julio-Claudian.
- After the first monthly pulse Augustus is age 63 (41/63/44 then 52/43/53).
- Treasury 10.94K. Paused day-one balance −89.69 (trade expense −146.63). By
  12 April the monthly balance had settled to about +91.
- Roma market opens while paused: food 4498/5850, attraction +7.60%, owned
  trades to Bononia, Alexandria, and Massilia.
- 31 markets listed. Advance cards display +1.00% cabinet efficiency and
  +2.00% tax / levy recovery, not 0% or generator micro-values.
- Government: Imperial Household 18% / 21%, Senatorial Order 56% / 160K,
  Public Priesthoods 19%, Equestrians 1%, Citizens 4%. Council, State Offices,
  and Laws tabs are present.

## Campaign

The session ran at speed 5 from 1 January 1.

- 12 April 1: Immensum Bellum fired with three unique choices (recorded
  settlement / local compact / mobilize), not cloned stability swaps.
- 1 January 43: still Roman Imperium under Princeps Marcus III; capital had
  moved to Antiochia ad Orontem; population 11.520M from 47.490M; 73 rebels;
  empty cabinet; irrigation constructions in queue; Claudian Invasion of
  Britain current visible with unique mobilize text.
- 24 October 47: population 240K; 1st Roman Nobles Civil War and 1st Rebellion
  against Roman Imperium both active; one remaining market (Antiochia).
- 1 April 48: Game Over as Noble Imperium, score 835. Not a renderer crash.
  Latest crash folders predate this run.

## Script defect found in play

`antq_m6.1` saved `antq_m6_opening_ruler_scope` only for Rome, then every
named-head country called `set_new_ruler_no_update` on a null scope. The
generator now saves the opening-ruler scope for every tagged country and
guards the handoff/kill.

## Follow-up applied before the next start

Runtime crown 18% vs Senate 56% with an unfilled cabinet left the 0.20
cabinet-crown lever unused and fed noble civil wars. Principate direct crown
is 0.18, senatorial direct 0.06, and the shared ancient rebel-growth /
join-threshold floor is stronger.

A second start still reached senatorial civil war by AD 28 because three
opening noble privileges stacked +0.30 senate power. Those privileges were
cut, Praetorian Donatives now grant +0.12 crown, Augustan Auctoritas is
applied at start, and three cabinet officers are seated. A third start on
1 January 1 showed Imperial Household 24% and Senatorial Order 50%. Session
`S7_ROME_AD1_SURVIVAL_20260819` is the current uninterrupted 100 AD attempt.

## Survival session — 2026-08-20

Session directory: `docs/screens/S7_ROME_AD1_SURVIVAL_20260819/`.
Lease token `c15456c8266b4531b0611ed04021016d`, EU5 PID 31912, tree
`9ae766bbd130b0e659367c3a923642387e103a98db584c3e58164d327db7b2d6`.

- 1 January 1: Imperial Household 24% / Senatorial Order 50%, Roma, 47.490M,
  31 markets, Augustus 41/63/44.
- By 19 September 24 a nobles civil war had moved the capital to Antiochia,
  cut population to 14.570M and markets to 8, and emptied the cabinet. The
  country remained Roman Imperium under Tiberius.
- 1 January 43: recovered as Roman Imperium, capital Roma, 51.242M, 31
  markets, treasury 25.24K, +68.84/month. Stacked victory/capitulation
  overlays hid the pause banner; the observer's compact-Ok detector did not
  fire (Ok at x=0.516 vs the old 0.53 bound, and a centred death Ok at
  0.482). Time froze for about three hours until the detector was widened.
- After the overlay fix, 20 November 44 is still Roman Imperium at Roma with
  50.667M pops and 31 markets. Claudian Invasion of Britain presented three
  unique situation choices (recorded settlement / local compact / mobilize).
  Estate satisfaction had collapsed to ~0.15% after the civil war; Imperial
  Household 16% / Senate 56%.

The observer now treats compact Go-to/Ok pairs and centred death-report Ok
buttons as `report_ok_*` even when the red pause banner is covered. Do not
close the 100 AD gate until this process reaches 100 without crash or Game
Over.

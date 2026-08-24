# Year-3/4 civil-war audit — 2026-08-21

S6-P0 asked for a separate audit of the year-3/4 civil-war wave and invalid
AI commands, plus a representative stability picture, before the century
gate. The uninterrupted Rome process (PID 31912) already ran 1 January AD 1
through 1 January AD 101. This note records that audit against that run and
the subsequent structural repairs.

## What the year-3/4 wave was not

The successful century process did **not** collapse in years 3–4. There was
no Game Over, no renderer crash, and no invalid-command storm in that
window. Earlier rejected playtests that died around AD 4 were resource /
market-panel / building-AI paths, already closed under the S6-P0 crash
items, not a separate global civil-war epidemic.

## What did fire later

| Date | Observation |
| --- | --- |
| 1 Jan 1 | Imperial Household 24% / 21% equilibrium, Senatorial Order ~50%, Senate and Equestrian satisfaction ~100%. Augustus is ruler. Stability 25. |
| 19 Sep 24 | Nobles civil war. Capital Antiochia, empty cabinet, Tiberius. Still Roman Imperium. |
| 1 Jan 43 | Recovered: Roma, 51.242M, 31 markets. Not a Game Over. |
| 1 Jan 101 | Same process still Roman Imperium at Roma, 35.456M, 31 markets, stability 20. |

The AD 24 nobles war is therefore a **year-24 estate/cabinet defect**, not
the year-3/4 wave. It did not produce accidental systemic collapse: Rome
remained the player tag and recovered the capital.

## Causes isolated in that run

1. **Council never convened.** Vanilla `estate_unhappy_with_lack_of_parliament`
   reached −1107% satisfaction equilibrium after 1227 months because
   `call_parliament` is `ai_tick = never`. That, not only the AD 24 war, is
   why every order sat at 0.01% by the 90s.
2. **Empty cabinet.** Courtiers died; the 0.20 crown-from-cabinet lever went
   unused; Imperial Household fell to 0% by AD 96.
3. **Estate stacking.** Senatorial/equestrian privileges had been adding
   noble power against a 0.18 Principate crown grant.

## Structural repairs now on disk

- Principate: `global_crown_estate_power = 0.18` and
  `crown_estate_power_from_cabinet = 0.20`, against senatorial 0.06 and
  equestrian 0.05 plus 0.15 senatorial cabinet leverage.
- Praetorian donatives: `global_crown_estate_power = 0.12` and
  `global_nobles_estate_power = -0.04`.
- Monthly Rome pulse refills up to three empty cabinet seats.
- `antq_ancient_council_session` silently starts and ends parliament when
  `months_since_last_parliament_called > 36`.
- Regional programme potentials use `dominant_culture ?=`.
- Quarantined disasters drop `has_complacency_effects`.

Day-one of the short retest (paused 1 January 1) showed Senate 100.00% /
103.80% satisfaction, Equestrians 100.00% / 102.63%, Imperial Household
24% / 21%, Public Priesthoods 90.66%, Citizens 97.78%. That is a usable
opening distribution, not an accidental collapse.

## Gate reading

The year-3/4 civil-war wave is rejected as a continuing systemic defect.
The century gate proceeded on one process to 1 January 101. Remaining
estate-council and cabinet emptying are repaired in the monthly pulse
rather than by a hidden crown-power cheat.

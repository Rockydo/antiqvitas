# M4 Korean and northeast-steppe culture-atlas batch

Date: 2026-07-21

## Scope

This fifth source-led batch adds 15 non-overlapping area selectors to
`docs/culture_remap.csv`. It resolves 365 more controlled locations, lifting
the audited atlas to 161 selectors, 5,666 locations, and 74 mapped cultures.
Five generated definitions raise the M4 catalogue from 107 to 112 cultures:
Buyeo-Goguryeoic, Samhan, Wuhuan, Xianbei, and Dingling.

The selected frames cover Goguryeo, Buyeo, Mahan/Byeonhan, Liaodong Wuhuan,
the Xiongnu Gobi and Selenga areas, eastern-steppe Xianbei, and Upper-Yenisei
Dingling areas. Every row is contested and does not settle later state,
ethnolinguistic, or confederation identities.

## Verification

- `make validate` passed; `m4_definitions` reports 112 cultures and 37
  religions, while `start_mirror` and `popcheck` retain all 13,552 populated
  locations and the 230,000.000-thousand population target.
- The enabled-mod `make smoke` passed with zero new normalized error-log lines.
- A fresh autonomous New Game -> Observer -> `Cultures (Location)` run reached
  the paused 08:00, 1 January, 1 map. Its northeast-steppe view visibly shows
  Xiongnu, Xianbei, Wuhuan, and Dingling. Evidence:
  `docs/screens/m4_northeast_batch/culture_northeastasia_probe.png`.
- The map-label probe itself did not require player control. A later exploratory
  country-selection click reproduced the established deferred player-context
  HRE/IO scope errors in
  `G:\antiqvitas_user_data\logs\error.m4_northeast_batch_clean_20260721_0432.log`.
  This known surface is excluded from the enabled-mod smoke baseline and is
  already recorded in `BLOCKERS.md`; no new content-specific signature was
  introduced.

## Boundary

The global M4 density target remains open. The batch does not assert a
homogeneous culture within any current map area or resolve the historical
classification debates around the northern frontier communities.

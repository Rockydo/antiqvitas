# M4 Iran, Caucasus, Central Asia, and Pontic culture-atlas batch

Date: 2026-07-21

## Scope

This fourth source-led batch adds 25 non-overlapping area selectors to
`docs/culture_remap.csv`. It resolves 1,093 more controlled locations, lifting
the audited atlas to 146 selectors, 5,301 locations, and 68 mapped cultures.
Five generated definitions raise the M4 catalogue from 102 to 107 cultures:
Chorasmian, Carmanian, Hyrcanian, Scythian, and Wusun.

The selected frames cover Armenia, Caucasian Albania, the Alanian north
Caucasus, Aorsi/Roxolanian and Crimean Pontic areas, the Iranian and
Mesopotamian Arsacid sphere, Khwarazm, Zhetysu, Bactria, Transoxiana, and
Badakhshan. Every row is contested: these are regional representations rather
than uniform ethnic, linguistic, or political claims.

## Verification

- `make validate` passed; `m4_definitions` reports 107 cultures and 37
  religions, while `start_mirror` and `popcheck` retain all 13,552 populated
  locations and the 230,000.000-thousand population target.
- The enabled-mod `make smoke` passed with zero new normalized error-log lines.
- A fresh autonomous New Game -> Observer -> `Cultures (Location)` run reached
  the paused 08:00, 1 January, 1 map. The inspected Iran/Central Asia view
  visibly renders Wusun, Sogdian, Bactrian, Chorasmian, Parthian, Median,
  Scythian, and Sarmatian frames. Evidence:
  `docs/screens/m4_iran_batch/culture_iran_centralasia_clear.png`.
- The fresh archive
  `G:\antiqvitas_user_data\logs\error.m4_iran_batch_clean_20260721_0420.log`
  has zero `jomini_script_system` and zero `Setting a law` diagnostics after
  culture-map interaction. Its remaining invalid-law/privilege notices are an
  existing M8 compatibility boundary and are not new normalized smoke lines.

## Boundary

The global M4 density target remains open. The Wusun label does not decide a
disputed ethnolinguistic affiliation, and the northern Caucasus, Crimea, and
Transoxiana frames retain deliberate mixed-frontier limits.

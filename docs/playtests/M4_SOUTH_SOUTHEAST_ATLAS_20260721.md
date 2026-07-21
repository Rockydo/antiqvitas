# M4 South and Southeast Asian culture-atlas batch

Date: 2026-07-21

## Scope

This third source-led batch adds 29 non-overlapping area selectors to
`docs/culture_remap.csv`. It resolves 1,320 more controlled locations, lifting
the audited atlas to 121 selectors, 4,208 locations, and 52 mapped cultures.
Eleven generated definitions raise the M4 catalogue from 91 to 102 cultures:
Gandhari, Kalingan, Deccan Prakrit, Proto-Telugu-Kannada, Sinhala, Pyu, Vietic,
Early Malay, Early Javanese, Philippine, and Bornean.

The selected frames cover the northwestern South Asian frontier, Sindh,
Himalayan foothills, Kalinga, the Satavahana Deccan, Tamilakam, Lanka, Jiaozhi,
Pyu/Mon/Proto-Khmer areas, the Malay Peninsula and Sumatra, Java/Lesser Sunda,
the Philippine islands, and Borneo. Every new row is contested: it is a
regional proxy, not a homogeneous identity, language, or political claim.

## Verification

- `make validate` passed; `m4_definitions` reports 102 cultures and 37
  religions, while `start_mirror` and `popcheck` retain all 13,552 populated
  locations and the 230,000.000-thousand population target.
- The enabled-mod `make smoke` passed with zero new normalized error-log lines.
- A fresh autonomous New Game -> Observer -> `Cultures (Location)` run reached
  the paused 08:00, 1 January, 1 map. The South Asian view visibly shows
  Gandhari and Indo-Aryan Prakrit; the Southeast Asian view visibly shows Pyu,
  Mon, Proto-Khmer, and Vietic. Evidence:
  `docs/screens/m4_southsea_batch/culture_india_probe.png` and
  `docs/screens/m4_southsea_batch/culture_southeastasia_clear_v2.png`.
- The fresh archive
  `G:\antiqvitas_user_data\logs\error.m4_southsea_batch_clean_20260721_0408.log`
  has zero `jomini_script_system` and zero `Setting a law` diagnostics after
  culture-map interaction. The remaining 15 invalid-law/privilege notices are
  the existing M8 compatibility boundary; they are not new normalized smoke
  lines.

## Boundary

The global M4 density target remains open. These labels deliberately do not
project later national, standard-language, or court identities backward into
AD 1, and finer local/tribal coverage remains a future source pass.

# R33 rejected at AD 17: mercenary class depletion

R33 was a fresh, non-debug 1920x1080 Rome campaign on fingerprint
`15ea3be5cc6c1d7c4c322d0c60df9874706b3f79bc7bac12dcbb0b9acc10eb88`.
It ran continuously from 1 January AD 1 through AD 17 without a renderer exit.
The run proved the corrected Roman chronology: a persisted AD 6 save retained
Augustus as ruler, removed Gaius Caesar, and designated Tiberius; a persisted
AD 17 save installed Tiberius, created the protected succession reserve, and
had no regency.

The AD 17 strict systemic audit nevertheless failed. Two low-manpower
mercenary cells had each lost one required infantry combat class. Save-history
comparison established the cause rather than merely observing the symptom:
both cells contained one heavy, one light, and one mounted company before
hiring; each hired a full three-class company; the sole hired infantry entry
was removed from availability and had not regenerated years later. The two
active hired contracts themselves each contained heavy infantry, light
infantry, and cavalry, so this was depletion of a one-entry reserve rather than
an unlock or successor-state inheritance error.

The global AD 17 pool was also materially skewed: 6,290 Hired Horse subunits
against 1,565 Local Retainer and 1,166 Caravan Guard subunits. The M7 generator
now uses a 0.10 population multiplier for mercenary infantry and retains 0.05
for cavalry. This creates the smallest supported reserve that lets a normal
three-class hire remove one infantry entry without erasing the class from a
small cell, while avoiding an indiscriminate increase to the already-deep
mounted pool. Generator validation pins the asymmetric density for all four
portable company roles.

R33 is rejected and cannot contribute elapsed years to the final AD 100 gate.
Its retained evidence includes:

- `docs/screens/R33_FINAL_PRODUCTION_ROME_AD1_100/`
- `docs/playtests/R33_M6_POST_AD4.json`
- `docs/playtests/R33_M6_POST_AD14.json`
- `docs/playtests/R33_CHECKPOINT_POST_AD14.json`

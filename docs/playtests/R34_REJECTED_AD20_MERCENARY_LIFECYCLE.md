# R34 rejected at AD 20: multi-hire mercenary lifecycle

R34 was a fresh, non-debug 1920x1080 Rome campaign on fingerprint
`bd7b81141716e5d5d99769fdf0a92facc9809c8889363686639e5a6cdeef48a9`.
The same EU5 process ran continuously from 1 January AD 1 through 6 February
AD 20.  The live and persisted checkpoints proved the corrected Roman ruler
sequence: Augustus survived the AD 4 Gaius transition, Tiberius succeeded him,
the protected reserve heir existed, and neither phase entered a regency.

The strict AD 20 systemic gate nevertheless rejected the run.  Five
mercenary cells lacked at least one required combat class and one had only a
single available role.  Save-history comparison established the complete
lifecycle cause.  A cell led by character 5277 held one heavy, one light, and
one mounted company at AD 6, but retained only its light company at AD 20.
Two live contracts led by characters 8991 and 9543 each consumed the sole
entry for one of their cell's classes.  EU5 returned expired leaders but did
not regenerate any removed availability entry.  Regional companies replace
the universal representative of their combat class, so increasing only the
portable infantry definitions cannot protect all cells.

All generated land-mercenary company definitions now use a 0.50 eligible-pop
multiplier.  This provisions several successive hires in the smallest cells
for the century gate while leaving unit combat strength, contract cost,
duration, and recruitment eligibility unchanged.  Generator validation pins
the reserve on every portable role, and the strict runtime audit continues to
require every live cell to retain heavy infantry, light infantry, and mounted
coverage.  Its report now preserves the exact deficient leader, units, and
classes for future diagnosis rather than only aggregate counts.

R34 also logged one `set_unit_activity` AI command race.  The matched stock
EU5 1.3.11 wartime control produced six occurrences in 11.044 years, so this
exact command family is now classified under the same annualized, rate-capped
native-warning policy as other directly reproduced engine races.  This does
not excuse mercenary hiring or consolidation warnings, which the stock
control explicitly did not reproduce and which remain actionable.

R34 cannot contribute elapsed years to the final AD 100 gate.  Evidence is
retained in:

- `docs/screens/R34_FINAL_PRODUCTION_ROME_AD1_100/`
- `docs/playtests/R34_M6_POST_AD4.json`
- `docs/playtests/R34_M6_POST_AD14.json`
- `docs/playtests/R34_CHECKPOINT_POST_AD17.json`

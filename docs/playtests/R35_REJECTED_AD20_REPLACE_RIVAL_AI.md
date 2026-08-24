# R35 rejected at AD 20: unresolved `replace_rival` AI command

R35 was a fresh, non-debug 1920x1080 Rome campaign on fingerprint
`508fe35a719fef6a300b49ef7465cac5cf2246ee4214e6122e503dc5e98ed89c`.
The same EU5 process ran continuously from 1 January AD 1 through 11 March
AD 20.  Its persisted 1 January checkpoint passed the Roman ruler audit:
Tiberius ruled without a regency and the protected succession reserve was the
designated heir.

The R34 mercenary lifecycle fix passed its decisive runtime retest.  All 447
instantiated cells retained heavy infantry, light infantry, and mounted
coverage; none was empty or one-role; minimum depth was 3, median depth was
86, and aggregate availability was 115,423.  The wider systemic state had
zero bankruptcies and zero civil wars.

The strict gate nevertheless rejected the run because `ai.log` contained one
invalid `replace_rival` command.  This is a hardcoded C++ AI command with no
script callsite.  Its scripted price is five stability, and the engine also
rejects it if the actor enters a war or the old/new rival relation changes
between planning and execution.  The log does not identify the issuing
country or rejection reason.  The existing matched 11.044-year stock 1.3.11
control did not reproduce this exact family, so R35 does not classify it as a
native warning or continue past the failed gate.  A longer matched stock
production control is required before any exact annualized allowance could
be justified.

R35 cannot contribute elapsed years to the final AD 100 gate.  Evidence is
retained in:

- `docs/screens/R35_FINAL_PRODUCTION_ROME_AD1_100/`
- `docs/playtests/R35_M6_AD20.json`
- `docs/playtests/R35_STABILITY_AD20.json`

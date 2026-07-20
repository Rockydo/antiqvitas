# M5 Noricum iron anchor

## Evidence

The Austrian Science Fund's Ferrum Noricum archaeology project identifies the
Hüttenberg area as a centre of Noric iron production. Its archaeological summary
dates production from the second half of the first century BCE through the
middle of the fourth century CE, securely covering the AD 1 start. It supports
an iron-production district, not a quantified output, a single mine location,
or a complete supply-chain reconstruction.

## Engine representation

The installed `friesach` location is a reviewed nearby Carinthian proxy for the
Hüttenberg district. M5 changes its raw material from vanilla marble to the
installed `iron` good. This is a contested map adapter only: it does not assert
that Friesach itself was the mine, the district's production volume, or a
runtime trade-flow result.

## Verification

The RGO renderer reports 328 audited corrections, including the new
`marble -> iron` anchor. `make validate` passed. Enabled-mod `make smoke`
reached the menu and found zero new `error.log` lines against the accepted
baseline.

Sources: `FWF-NORIC`; P8.1; P12.1.

# M5 Forum Romanum anchor

## Evidence

The Parco archeologico del Colosseo's [Roman Forum
record](https://colosseo.it/en/area/the-roman-forum/) identifies the Forum as
Rome's centre of public life, with political, religious, and commercial
buildings. Its historical account also places Caesar's final redesign and the
Augustan completion before AD 1. This establishes enduring civic-commercial
context, not a single building footprint or quantified market throughput.

## Engine representation

The local EU5 building catalogue has no forum- or agora-specific type.
`marketplace` is the verified generic contract selected for the existing Rome
city node. It represents the Forum's intertwined commercial and civic role
without adding a new script key, modelling a specific basilica or temple, or
claiming an archaeological reconstruction.

## Verification

After regeneration, `make validate` passed: the start mirror reports 35
M5/M7 buildings. Enabled-mod `make smoke` reached the menu and reported zero
new `error.log` lines against the accepted baseline.

Sources: `PARC-FORUM`; P12.3.

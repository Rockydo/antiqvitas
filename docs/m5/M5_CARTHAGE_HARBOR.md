# M5 Carthage harbor proxy

## Evidence

UNESCO's [Archaeological Site of Carthage](https://whc.unesco.org/en/list/37/)
identifies Roman Carthage as the capital of the province of Africa, describes
the antique ports as enabling Mediterranean exchange over more than ten
centuries, and records the Roman refoundation after the destruction of 146 BCE.
This establishes a durable port-and-exchange context at the AD 1 boundary; it
does not identify an AD 1 harbor footprint or a modern game-location key.

## Engine representation

The existing reviewed Tunis location is the project's contested Carthago proxy.
`protected_harbor` is a locally verified building-manager type, so
`carthago_harbor` is emitted there at level 1 for the Roman owner. It represents
the city's inherited antique maritime infrastructure and exchange function, not
a claim about the Punic cothon surviving unchanged, its capacity, or a precise
archaeological plan.

## Verification

After regeneration, `make validate` passed: the start mirror reports 32 M5/M7
buildings and all 40 market/urban nodes. Enabled-mod `make smoke` reached the
menu and reported zero new `error.log` lines against the accepted baseline.

Sources: `UNESCO-CAR-HAR`; P8.1; P12.2.

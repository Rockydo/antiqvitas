# M5 Ephesus market and harbor

## Evidence

UNESCO identifies Ephesus as the Roman provincial capital of Asia and an
outstanding Roman harbour city with a sea channel and harbour basin. It records
the Roman-period city as a major administrative, commercial, and urban centre.
The historical city and its ports shifted with the silting Kaystros estuary;
the source therefore does not turn any modern map key into an exact AD 1
footprint.

## Engine representation

The installed `ayasuluk` location is a near-site proxy: the modern Ayasuluk
Hill/Selçuk component lies near, but is not identical to, the Roman city. M5
uses it at city rank as the 41st market node and gives it the verified
`protected_harbor` tier. That preserves Ephesus's plan-required Roman port and
market role while making the mapping approximation explicit.

## Verification

The generated start manager reports 41 M5 markets, 41 urban nodes, and 33
M5/M7 buildings. `make validate` passed. Enabled-mod `make smoke` reached the
menu and found zero new `error.log` lines against the accepted baseline.

Sources: `UNESCO-EPH`; P8.1; P12.2.

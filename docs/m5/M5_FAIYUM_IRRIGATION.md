# M5 Faiyum irrigation anchor

## Evidence

UNESCO's [Oasis of Fayoum, hydraulic remains and ancient cultural
landscapes](https://whc.unesco.org/en/tentativelists/1830/) records the
channelled Bahr Youssef and its irrigation network, continued Roman-period
reclamation, and the canal-fed agricultural villages that made the Greco-Roman
period one of Faiyum's most prosperous. It supports an AD 1 irrigation context,
not a single mapped canal, a fixed production total, or a centralized system.

## Engine representation

`faiyum` is a direct installed, Roman-controlled location. It is added to the
validated historic-site ledger and receives the locally verified level-one
`irrigation_systems` building. The generic building is an agricultural-hydraulic
proxy only; it does not model every Faiyum canal, estate, settlement, labor
arrangement, or the region's changing later-Roman water conditions.

## Verification

After regeneration, `make validate` passed: the start mirror reports 34
M5/M7 buildings. Enabled-mod `make smoke` reached the menu and reported zero
new `error.log` lines against the accepted baseline.

Sources: `UNESCO-FAY`; P12.3.

# M4 reviewed location-name corrections

The full-map name pass deliberately uses generated Tier-2 and Tier-3 ledgers to
cover every installed location key. Those bulk ledgers remain stable inputs so
that their 28,573-label output can be reproduced and audited. This file records
a smaller authoritative correction layer for mistakes found after that pass.

`tools/generate_m4_location_name_corrections.py` reads
`docs/m4/location_name_corrections.csv` and writes one exact-mirror localization
file per supported client language. The generated filename begins with
`antq_zz_`, so it loads after `antq_m4_location_names...`; duplicate root,
language, and dialect keys here intentionally supersede the older bulk label.
No generated full-map file should be edited by hand.

## Confidence

- `secure`: the displayed form and installed field match are directly supported.
- `tier2`: the correction removes a clear anachronism but the replacement is a
  conservative geographic or inherited-name proxy.
- `contested`: the existing label is demonstrably too late, while the surviving
  pre-conquest name evidence permits only a cautious reconstruction.

## Validation

Run:

```text
python tools/generate_m4_location_name_corrections.py --write
python tools/generate_m4_location_name_corrections.py --check
python tools/m11_localization.py --check
python tools/m12_anachronism_audit.py --write
```

The repository-wide `make validate` and `make.cmd validate` paths pin the
correction generator in check mode.

## First chronology batch

The initial batch removes five labels whose current full Roman titles postdate
1 January AD 1: the Bath sanctuary, Chester fortress, Cologne colonia, Lincoln
colonia, and Londinium. Where no secure settlement name survives, the ledger
uses a clearly marked Tier-2 or contested inherited hydronym/toponym proxy
rather than inventing a false city.

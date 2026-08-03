# R5 geography batch proof

- Ledger: 15,628/33,801 rows; all coarse levels and locations 1-10,400.
- Localization: 15,625 distinct researched keys, exactly one owner in each of
  11 clients; zero missing, duplicate, stale, or later-overridden values.
- QA: no vanilla/raw/generic/post-colonial/placeholder/corrupt labels, sibling
  collisions, invalid parents/kinds/sources, or labels over 60 characters.
- Static: `make validate` 170/170.
- Runtime: paired vanilla/mod menu smoke, zero new `error.log` lines; fingerprint
  `030e91e96e5e694afae86aa0d6369583b07efa57cbb742d6c785282dcaea02b4`.

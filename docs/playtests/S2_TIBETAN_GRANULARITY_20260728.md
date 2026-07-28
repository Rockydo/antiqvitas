# Tibetan Plateau Granularity — 2026-07-28

## Accepted scope

- Removed the 199-location `TIB` / Tibetan Societies catch-all.
- Added nine bounded frames: Zhang Zhung (38), Sumpa (33), Changtang Pastoral
  Networks (7), Bangga-Yarlung Horizon (6), Central Tsangpo Valley Network
  (22), Western Tsang Valley Network (18), Qamdo River-Corridor Network (28),
  Drichu Highland Network (29), and Eastern Plateau Corridor Network (18).
- Added eight new regional cultures, three plural plateau-tradition faith
  families, twelve direct doctrines, five government reforms, nine direct
  standards, nine period-safe capital-polygon names, and full agenda/rank/law/
  estate/research/start-state propagation.
- Added direct-art naked barley as a raw good for Yarlung and Tsangpo valley
  cultivation. Corrected Changtang fiber crops and unsupported Drichu gold to
  livestock.
- The global settlement generator gives every replacement frame at least one
  productive opening seed. The complete map now has 3,011 regional building
  placements across 1,609 settlement-ranked locations and 356 polities.

## Deterministic probe

`tools/s2_tibetan_granularity.py --check` passes:

- exactly 199 former TIB locations, owned once;
- no replacement larger than 38;
- no TIB roster, direct, residual, localization, or resolved-ownership entry;
- all cultures, faiths, doctrines, reforms, research unlocks, standards,
  capitals, names, RGO anchors, and settlement seeds present;
- eleven localization clients complete.

## Reduced QA acceptance

- `make validate`: **PASS**, 118 commands.
- Paired vanilla/mod `make smoke`: **PASS**.
- Both launches reached a responsive rendered menu.
- Normalized `error.log` comparison: **zero new lines unique to the mod**.
- No long observer campaign was run, following the user-approved reduced QA
  policy.

## Evidence boundary

The split uses textual names only where defensible and archaeological/economic
labels elsewhere. It does not backdate the Tibetan Empire, imperial Buddhism,
organized later Bon, later provinces, modern ethnic borders, or recovered AD 1
office lists. Sources and limitations are recorded in
`docs/world_1ad/SOURCES.md`, `docs/ASSUMPTIONS.md`, and the generated
`docs/m12/tibetan_granularity.csv`.

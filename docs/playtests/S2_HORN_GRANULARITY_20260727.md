# S2 Horn granularity — 2026-07-27

## Scope

This tranche replaces the single 79-location Barbaria Societies opening
country. It uses six independently governed far-side markets from the
*Periplus of the Erythraean Sea* and three bounded hinterland gameplay frames:
Guban Pastoralists, Haud Pastoralists, and Northern Azania.

The *Periplus* is a mid-first-century witness and is therefore backdated
cautiously to AD 1. Port-site equations and hinterland boundaries retain the
confidence qualifications recorded in `docs/ASSUMPTIONS.md`; no unitary Somali
state or later clan geography is asserted.

## Deterministic checks

- `s2_horn_granularity`: PASS — 9 frames, 79 owned entries, largest frame 30,
  6 independent ports, 3 cultures, 2 reforms, 9 direct standards, and all 11
  localization clients.
- `s2_placeholder_polity_census`: PASS — 25 literal placeholder names remain.
- `world_roster`: PASS — 301 polities and 301 mapped capitals.
- `ownership_map`: PASS — 13,550 owned locations across 301 tags.
- `m8_knowledge`: PASS — all 301 opening profiles can research.
- `make validate`: PASS — all 113 registered checks.

## Rapid runtime check

`gmake smoke` launched a current vanilla control and then ANTIQVITAS through
the automated game driver. Both sessions reached responsive rendered menus.
The normalized comparison reported:

`smoketest: PASS (zero new lines; 0 baseline line types absent)`

Four archived-baseline delta types appeared in the current vanilla control;
none was unique to the mod. No long observer campaign was run under the
reduced QA policy.

## Asset note

The estate generator rewrote ten existing PNG payloads while rebuilding the
full dependency chain. A decoded comparison against `HEAD` confirmed identical
dimensions and identical RGBA pixels for all ten; this is encoding/compression
drift, not an illustration change.

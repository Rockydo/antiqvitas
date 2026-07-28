# S2 Bantu-frontier granularity - 2026-07-28

## Scope

This tranche replaces the 94-location Bantu Societies opening country. It uses
four bounded early-ironworking or ceramic-horizon frames, two southern
hunter-herder networks, and separate Wadai and Bauchi plateau communities.
Ngazidja is deliberately unowned because secure AD 1 settlement evidence is
absent.

The horizon names are gameplay adapters, not assertions of uniform ethnicity,
language, centralized government, or fixed borders. Historical limitations
and the temporary southern-religion fallback are recorded in
`docs/ASSUMPTIONS.md` and `docs/TODO.md`.

## Deterministic checks

- `s2_bantu_frontier_granularity`: PASS - 8 frames, 93 owned entries,
  Ngazidja intentionally empty, 8 cultures, 2 reforms, 8 direct standards,
  and all 11 localization clients.
- `s2_placeholder_polity_census`: PASS - 24 literal placeholder names remain.
- `world_roster`: PASS - 308 polities and 308 mapped capitals.
- `ownership_map`: PASS - 13,549 controlled locations across 308 tags.
- `territory_coverage`: PASS - 13,533 assigned ownable locations and 43
  evidence-led intentional empty locations.
- `m8_knowledge`: PASS - all 308 opening profiles can research.
- `gmake validate`: PASS - all 114 registered checks.

## Rapid runtime check

`gmake smoke` launched a current vanilla control and then ANTIQVITAS through
the automated game driver. Both sessions reached responsive rendered menus.
The normalized comparison reported:

`smoketest: PASS (zero new lines; 0 baseline line types absent)`

Four archived-baseline delta types appeared in the current vanilla control;
none was unique to the mod. No long observer campaign was run under the
reduced QA policy.

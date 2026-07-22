# M3 Political Map Gate

## Result

**PASS — M3-done political-map gate, 22 July 2026.**

The M3 acceptance criterion is the AD 1 political map: every §8 polity is
present and no vanilla 1337 country-start survives. The final gate uses the
exact start-manager mirror rather than a partial map impression, then confirms
that result in a fresh driver-run session.

## Static political-map census

`tools/m3_political_map.py`, now part of `make validate`, independently joins
the reviewed roster, collision-safe engine tag map, generated country
definitions, and generated `10_countries.txt` start manager. Its current
result is:

```text
m3_political_map: PASS (157 roster polities; 157 AD 1 starts;
157 country definitions; 25 exact start managers;
13552 sourced controlled locations)
```

The 25 mod start-manager filenames exactly mirror the installed inventory, so
their same-name overrides replace the vanilla start snapshot. The check rejects
an omitted roster tag, a duplicate/extra AD 1 country, a mismatched capital, a
missing country definition, an unowned capital, or a changed manager inventory.
The existing ownership checks additionally report 13,576 ownable locations,
13,535 assigned locations, and 41 reviewed intentional empties.

## Fresh autonomous visual inspection

The game driver launched the enabled ANTIQVITAS playset directly, selected New
Game, enabled Observer, and entered the paused live map. No time was advanced.

- `docs/screens/20260722_m3_gate/m3_generated_map.png` shows the country
  selection map at `08:00, 1 January, 1`, including the Roman Commonwealth,
  Parthia, Cappadocia, the Aorsi/Roxolani steppe surface, and other AD 1
  polities.
- `docs/screens/20260722_m3_gate/m3_observer_ready.png` confirms the Observer
  choice at the same AD 1 start map.
- `docs/screens/20260722_m3_gate/m3_paused_observer.png` shows the actual
  paused Observer game at `08:00, 1 January, 1`, with the AD 1 political map
  retained after game start.

The map is not claimed to turn broad society-of-peoples frames into exact
ancient frontiers; their source boundaries and contested status remain in the
reviewed M3 ownership ledgers. It does establish the requested playable AD 1
world and eliminates the vanilla 1337 country-start layer.

## Scope boundary

The old M3 month-long observer note recorded then-unowned economy,
government/law, and diplomacy systems. It was a valid integration finding at
the time, but is not M3's stated acceptance predicate. The M6 Han
minor-regency presentation defect remains an M6 mechanical gate; M5 trade-flow
and renderer-bound long-observer work remain their own later-milestone gates.

## Verification

`make validate` passed after adding the focused M3 census. The required final
`make full` gate also passed on 22 July: every generator and static contract
was green, and the enabled-mod smoke test reported zero new normalized
`error.log` lines.

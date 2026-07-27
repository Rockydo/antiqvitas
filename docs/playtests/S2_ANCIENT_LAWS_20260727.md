# S2 Ancient Legal Profiles — 2026-07-27

## Scope

Rapid verification of the replacement law surface requested after the second
manual playtest. No long campaign or observer playback was required.

## Implemented contract

- 13 tag-aware historical legal profiles cover all 292 opening polities.
- Each profile has 14 law groups and three mutually exclusive policies:
  182 groups and 546 options in total.
- Every profile contains 42 distinct effect packages; every option has at
  least three verified effects, estate preferences, a description, sources,
  confidence, and an explicit historical boundary.
- All 182 groups are unlocked once through the ten universally held Age-I
  roots. The profile triggers reduce each polity's visible surface to its own
  14 groups.
- Every authored opening government receives the mediated starting policy in
  all fourteen groups while retaining narrower pre-existing country or
  regional laws.

## Static and mounted results

- `make validate`: PASS, 101/101 commands.
- `s2_ancient_laws`: PASS, 13 profiles / 292 tags / 182 groups / 546 options.
- `m6_power`: PASS, 227 active ancient law groups.
- `m8_knowledge`: PASS, 579 ancient-system unlocks and all 292 opening
  research profiles reachable.
- `m11_localization`: PASS, 64,328 unique English quoted entries and ten exact
  client mirrors.
- `m12_anachronism_audit`: PASS, zero prohibited player-facing terms.
- Paired vanilla/mod `make smoke`: PASS, responsive rendered menus and zero
  mod-unique new `error.log` lines.

## Focused runtime attempt

The mod rendered the ANTIQVITAS total-conversion menu. The automated Observer
transition then remained on the main menu after both bounded start attempts,
so no law-panel screenshot is accepted. The driver capture is retained under
`docs/screens/20260727_105024/`.

Crucially, the attempt left `<EU5_USER_DIR>\logs\error.log` unchanged
at 1,211 bytes. There were no removed-law, invalid-policy, trigger, or
script-system diagnostics. This is recorded as a driver transition limitation
in `docs/BLOCKERS.md`; it does not relax any content baseline.

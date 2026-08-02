# S4 structural audit - 2026-08-02

## Verified

- `make validate`: 158/158 pass.
- Paired vanilla/mod smoke: zero new or mod-unique `error.log` lines.
- Population: 81,706 strata, 13,553 populated locations, exact 230,000.000
  thousand total; all eight pop classes; no installed 1337 input.
- Knowledge/war: 906 advances with no vanilla law or unit unlocks; 117 ancient
  units; five-level coastal capability model; 117 unique direct unit images.
- Agency: 416 events, including 332 two-choice mechanical phases; 40 decisions
  with AI/automation cadence, explicit AI-list registration, and stock debits;
  463 opening AI personalities.
- Privacy: 11,231 tracked files pass the release guard. Local paths use an
  ignored config and public template.

## Runtime repair loop

The first paired smoke found 40 unregistered AI actions, three unreadable fiscal
script values, and seven rejected IO trust fields. Installed contracts were
substituted or removed, validators were strengthened, and the second paired
smoke passed with zero new lines.

## Still open

Fresh in-map proof remains required for the Rome annona import row, contrasting
naval capability panels, representative religion eligibility, four IO bodies,
and long observer trajectories. Published Git history also needs a coordinated
privacy rewrite before public release; `HEAD` itself is clean.

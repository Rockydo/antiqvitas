# R5 situation-action surface — 2026-08-04

- Added two material, AI-usable responses to each of 43 ancient situations:
  relief/negotiation (+18 progress) and coordinated mobilization (+28 progress).
- Every action is anchored to its current's exact polity, selects only that
  active situation, consumes Wealth, has a two-year cooldown, and is in the AI
  registry. The audit rejects a missing response, selector, progress link, or
  AI registration.
- `make validate` passes 171/171. Paired smoke is zero-delta at
  `98d51c936f74b3d2029524a8da9ecd6d6d1b7d2fab57400e2d199b995ea58c71`.
- Live panel capture remains blocked by the recorded main-menu observer-control
  drift; no failed UI attempt is treated as a content failure.

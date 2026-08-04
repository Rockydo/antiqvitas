# R5 Rome direct UI checkpoint — 2026-08-04

- Fresh AD 1 player start: Roman Imperium; Agenda, markets, location, and country
  panels rendered normally.
- `change_date 100` reached 1 January 100 and switched Rome from Principate to
  High Empires. The Roman advance panel exposed 41 profile-filtered advances;
  the unrelated names in the compact research strip are global institutions,
  not selectable advances.
- Directly opened and inspected the Roman *Immensum Bellum* and *Great Illyrian
  Revolt* event surfaces. Each had title, illustration, description, and choice;
  no new script diagnostic or crash occurred.
- This is focused UI/age evidence, not the final uninterrupted real-time century
  run. The existing renderer/accelerated-playback limitation remains open.
- The renderer profile now uses the engine-accepted `upscale = DISABLED` and
  `upscale_quality = off` keys. An attempted `tick_day 12000` still reaches the
  known installed market self-relation assertion and then the FSR crash path;
  that shortcut is excluded from further century tests.

- Fresh selector probes after BCE-date removal and after the installed `age`
  adapter both still substituted a generated Roman regent. The engine-level
  pre-campaign-adult limitation is recorded in `BLOCKERS.md`; the green
  no-BCE generator and its static/smoke coverage are retained.

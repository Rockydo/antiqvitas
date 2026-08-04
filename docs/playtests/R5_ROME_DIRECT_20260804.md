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

- The former pre-campaign-adult limitation is resolved by the generated
  `on_game_start` native-age bootstrap. A fresh selector and live Rome start
  show Augustus (63) with Gaius Caesar as heir; a live Han switch renders the
  Ping/Wang regency context. Validation passes 170/170 and paired smoke is
  zero-delta after that repair.

# M12 tutorial and hint audit

The installed tutorial lesson chains are not automatic and contain no dated
historical lesson text, so the M12 intervention is limited to the installed
`in_game/common/scriptable_hints/scripted_hints.txt` surface.

`tools/m12_disable_historical_hints.py` reads that exact installed filename on
every validation and renders an exact-name mod overlay. It injects
`always = no` into the `priority` trigger of exactly 33 selected definitions:

- 25 dated or named post-antique crisis, situation, and event hints, from the
  coup/Chinese-dynasty and Delhi/Black Death families through the Reformation,
  colonial, Timurid, Sengoku, Nanbokucho, and Brandenburg hints;
- six country-specific hints for Holland, Hungary, Norway, Naples, Castile,
  and the Ottomans; and
- the Holy Roman Empire and Eastern Roman Empire country/organization hints.

Every other byte from the installed file is retained. In particular, generic
economy, food, stability, warfare, estates, slavery, and research guidance is
still available. This is a deliberately narrow historical-surface correction,
not a replacement tutorial system.

The guarded output passes `make validate` and reached the enabled-mod settled
menu for the driver’s 90-second smoke hold with zero new `error.log` lines on
20 July 2026. A future game update that changes a selected definition or its
priority contract fails validation rather than silently changing the overlay.

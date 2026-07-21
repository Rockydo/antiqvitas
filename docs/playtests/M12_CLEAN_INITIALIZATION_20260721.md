# M12 clean AD 1 initialization - 2026-07-21

The last startup diagnostic was one invalid capital dereference in the installed Catalan Sitges flag variant. The installed game uses capital ?= location comparisons for possibly absent capitals; the checked exact-source renderer changes only that predicate.

Full make validate and the rendered enabled-mod smoke passed. The autonomous driver then launched the enabled playset, selected New Game, reached the AD 1 map, enabled Observer, and started the live observer map using the retained 1920x1080, 70-percent profile.

Evidence: docs/screens/m12_capital_probe/generating.png, docs/screens/m12_capital_probe/observer_enabled.png, and docs/screens/m12_capital_probe/observer_start.png.

The immediate post-start log scan returned script_errors=0. This is a pass for AD 1 startup, on-action, CoA, and flag-runtime compatibility. It does not test sustained playback: that gate remains deferred after the two documented FSR renderer crashes.

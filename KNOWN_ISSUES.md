# Known Issues

## Deferred M2 year-one runtime cleanliness

The calendar generator has been proven in the UI, including a real save/reload,
but its generated files are intentionally not enabled until M3 replaces the
vanilla 1337 setup snapshot. That snapshot creates 868 ruler-term validation
errors at an AD 1 start. See `BLOCKERS.md` for reproduction and recovery.

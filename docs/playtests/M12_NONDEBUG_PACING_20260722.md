# M12 non-debug pacing and stability probe — 22 July 2026

## Scope

Measure the longest stable real-simulation interval available after the AD 1
market-manager mitigation, using the normal non-debug renderer profile and the
automated Observer driver.

## Procedure

1. Regenerated the source-led start mirror with all 42 historical market hubs
   retained as urban/harbor anchors and no pre-game `add_market` seed.
2. Passed `make validate` and the enabled-mod `make smoke` with zero new
   normalized error-log lines.
3. Entered a fresh AD 1 Observer session with the automated driver and ran it
   at the configured maximum-tick setting for a requested 600 seconds, taking
   a screenshot every 60 seconds.

## Result

The driver captured a running session from `08:00, 1 January, 1` through
`11:00, 18 March, 1` before its 600-second interval completed. The final
pre-crash image is
[observer_0004.png](../screens/20260722_m12_pacing/observer_0004.png).

That is approximately 76.125 simulated days in 240.3 wall-clock seconds:
0.316792 days/second (3.157 seconds/day). The project calendar calculates
173,737 days from AD 1 to the terminal date, so unchanged normal simulation
would require roughly 6.35 wall-clock days even if it did not crash.

The process then exited; `Europa Universalis V20260722_043956/exception.txt`
records `C0000005` in `ffxFsr2ResourceIsNull`, followed by
`NVSDK_NGX_D3D12_Shutdown1`. This is the same renderer failure family already
recorded for debug observer profiles. The run produced no
`Getting relation with itself` assertion, confirming that the market-manager
mitigation survives the observed 2.5-month interval.

## Conclusion

This is a valid short pacing/stability measurement but not enough time to
judge annual population, inflation, research, or war outcomes. A complete
AD 1–476 Observer run remains blocked on the local renderer, not on a scripted
content error.

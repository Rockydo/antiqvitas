# M12 Observer recovery probe — 22 July 2026

## Scope

This is a normal-renderer recovery-contract probe, not a completed campaign.
It tests the durable route required when the previously recorded FSR/NGX
renderer exit destroys the EU5 window.

## Procedure and result

`gamedriver.py observer-recover --seconds 20 --maximum-speed` was run with the
relocated user directory on G:. It performed the following without launcher or
human input:

1. Fingerprinted the three newest `autosave_*.eu5` files.
2. Launched the configured EU5 executable and waited for the menu-ready check.
3. Used the normal Continue confirmation's documented Enter binding.
4. Waited for the local `MainMenu->Game` state-4 and cached-data completion
   records before operating the country-selection map.
5. On the first bounded map-input attempt, retained screenshots and restarted
   cleanly after Observer did not activate. The second attempt entered live
   paused Observer at `08:00, 1 January, 7`.
6. Ran maximum-speed Observer for 20 seconds. The 10-second capture shows
   `08:00, 29 April, 7`; no game window exit occurred. Three newer autosaves
   were written after the interval.

The live screenshots are `recovery_00_attempt2_live.png` and
`observer_0001.png` under
`docs/screens/20260722_m12_checkpoint_recover_pass/`; the machine-readable
autosave/retry record is `observer_recovery.json` in that directory.

## Verdict

**Pass for checkpointed recovery capability.** `make validate` passed. The
probe does not satisfy the M12 long-run gate: it did not encounter a real
renderer crash, reach any decade boundary, or establish economy/AI balance.

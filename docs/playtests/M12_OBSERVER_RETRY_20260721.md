# M12 observer retry -- 2026-07-21

## Scope

Test the fully source-preserved 7,440-event quarantine in a real AD 1 observer
session, rather than accepting menu smoke as runtime evidence.

## Preconditions

- Commit `5be3b43` passed full static validation.
- Its enabled-mod 90-second smoke reached a rendered menu with zero new
  `error.log` lines.
- The exact-name country-change rule overlay was active.

## Attempt 1

The autonomous driver reached the selector at `08:00, 1 January, 1`, enabled
Observer Mode, and started the live map. The frame
[observer_start.png](../screens/M12_event_runtime/observer_start.png) visibly
shows Observer Mode and the Age of Principate. The first play-control target
caused the EU5 window to disappear before the driver could take its scheduled
follow-up frame.

## Attempt 2

The driver performed a fresh launch and selector load, again reached the live
observer map, and first tried the keyboard pause toggle. That input left the
visible `Game is Paused` state unchanged. It then targeted the play control
using the live window rectangle established by the driver. The preceding map
frame is [observer_start.png](../screens/M12_event_runtime_retry/observer_start.png).
The game again exited before the next capture.

## Evidence and result

The second crash report at
`G:\antiqvitas_user_data\crashes\Europa Universalis V20260720_225407`
records an `Unhandled Exception C0000005` in an `ffxFsr2ResourceIsNull` stack.
Its system log reports 14.6 GB free RAM and 17.3 GB free swap. The error log
also lists nine missing generated institution birth modifiers and existing
vanilla HRE/coat-of-arms fall-through for unset government and IO scopes; it
does not identify an event-quarantine loader error.

**Fail for observer-dependent milestones.** The event overlay remains accepted
at the static and settled-menu boundaries, but the renderer prevents a live
time advance. The detailed recovery boundary is in `BLOCKERS.md`; no unchanged
observer retry is warranted until a supported low-resolution renderer profile
or equivalent material graphics change is verified.

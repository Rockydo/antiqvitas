# M11 Exact-Name Message Registry Overlay

EU5 registers each generic action as `PERFORM_<action>_ACTION` during database
load. The installed build does not additively load sibling message-type files,
so ANTIQVITAS mirrors the exact installed registry filename only.

`tools/m11_message_overlay.py` reads the configured EU5 1.3.1.1 build
(`24187685`) source at `game/main_menu/gui/messagetypes.txt`, verifies SHA-256
`610D35361A27253F93EBF6EC3F74247124C998A859B0E6D2BC8908D8741BBD1F` and its
1,348-definition inventory, then copies those bytes unchanged before appending
the 40 validated M11 registrations. It fails on a game build, hash, newline,
inventory, or key-collision change; it never modifies the game installation.

The one-action `endow_public_games` pilot reached the enabled-mod menu with
zero new error-log lines. The full 40-row expansion then also reached the menu
with zero new lines on a clean retry. Two later full-gate attempts ended in the
renderer's `ErrorOutOfDeviceMemory` assertion without a script or registry
error; a reduced-resolution experiment did not change that renderer failure
and was reverted. The successful menu smoke remains the registry acceptance
result, while the intermittent Vulkan-memory condition is an M12 driver risk.

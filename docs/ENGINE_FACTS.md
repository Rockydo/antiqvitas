# Verified Engine Facts

Build examined: Steam app 3450310, build ID 24187685. The autonomous menu
screenshot reports **Europa Universalis V 1.3.1.1 (Pavia), checksum 7917**.
All paths below are relative to the verified read-only game directory unless
otherwise stated.

## Runtime and paths

- `binaries/eu5.exe` exists and the three content trees are `game/in_game`,
  `game/main_menu`, and `game/loading_screen`.
- `--user_dir=<absolute path>` is accepted. A real launch created logs, account
  data, settings, and caches under `G:\antiqvitas_user_data`.
- `-debug_mode` enables the in-game console. The physical key below Escape
  (scan code `0x29`) opens it on this machine's French keyboard.
- `--ignore-disable-mods-on-crash` and `-leavepops` strings are present in the
  executable and are retained in the harness.
- Steam was already running; `tools/steam_ensure.ps1` verified it as responsive.
- There is no launcher SQLite database in this build. The launcher uses
  `USER_DIR/playsets.json`, whose installed schema was inspected and is managed
  atomically by `tools/enable_mod.py`.
- `helplog` works and writes `USER_DIR/console.txt`. The harvested build-specific
  list is `docs/REF_console_commands.txt`.
- Local `script_docs` is listed but fails to return; see `BLOCKERS.md`.

## Dates

`game/loading_screen/common/defines/00_defines.txt` defines:

```text
NGame = {
	START_DATE = "1337.4.1"
	END_DATE = "1836.12.31"
}
```

The read-only EU5-1444-Start-Date repository at commit checked out during M0
overrides `NGame.START_DATE` in
`loading_screen/common/defines/1444_defines.txt`. Therefore ANTIQVITAS will
override both keys in the same loading-screen database. Acceptance of year 1
and save/UI behavior remain M2 runtime gates; all generated dates already pass
through `tools/dates.py`, preserving the AUC fallback.

## Setup layout

The master plan's provisional setup paths differ from build 1.3.1.1:

- Start-state managers are in `game/main_menu/setup/start` (25 files).
- Templates are in `game/main_menu/setup/templates` (205 files).
- Country definitions are in `game/in_game/setup/countries` (46 files).
- There is also an `game/in_game/setup` tree for definitions loaded after the
  main-menu setup phase.

The 1444 precedent mirrors the same split. All M3 replacement work will use the
local layout, not the provisional path examples in the plan.

## Encoding

The extractor inspected every local file and recorded the result in
`docs/vanilla_symbols/file_inventory.json`.

- All 25 `main_menu/setup/start` files are UTF-8 without BOM.
- All 46 `in_game/setup/countries` files are UTF-8 with BOM.
- 198 of 205 `main_menu/setup/templates` files have BOM. Seven named vanilla
  files omit it; ANTIQVITAS follows the plan's stricter BOM rule.
- All 528 inspected English localization files have BOM.
- Common definition files such as cultures also use BOM.

## Metadata and replacement

Installed Workshop mods use `.metadata/metadata.json` with:
`name`, `id`, `version`, `supported_game_version`, `short_description`, `tags`,
`relationships`, and `game_custom_data`. `picture` is optional in observed
mods; thumbnails may be beside `.metadata` at the mod root.

Both `replace_path` and `replace_paths` strings exist in the executable, and DLC
manifests expose a `replace_path` array. No installed Workshop metadata uses
either key, so mod-metadata replace-path support is not yet accepted. M1 will
test it in isolation; otherwise M3 uses exact-filename mirror overrides.

EU5 enumerates metadata for every directory under `USER_DIR/mod` even when the
playset disables it. This is why M0's true vanilla baseline was captured with
the ANTIQVITAS junction absent.

## Flags

Flags are a layered coat-of-arms system, not country DDS files.
`game/main_menu/common/coat_of_arms` contains palettes, patterns, colored
emblems, and pre-scripted compositions. Country definitions contain color,
culture, and religion but no texture path. Flag-definition lists select CoAs by
tag and trigger. ANTIQVITAS will compose era emblems in this system and add new
emblem textures only where vanilla primitives are insufficient.

## Extracted databases

`tools/extract_vanilla.py` uses a tolerant Clausewitz tokenizer and produced
machine-readable inventories under `docs/vanilla_symbols/`. Selected counts:

- 28,573 locations; 4,309 provinces; 805 areas; 82 regions.
- 2,087 cultures; 528 languages; 293 religions in 29 groups.
- 74 goods; 465 buildings; 323 unit types; 3,179 advances.
- 8 pop types; 8 estates; 5 government types; 196 laws.
- 20 subject types; 36 international organizations; 22 situations; 36 disasters.
- 7,532 event IDs and 234,652 English localization keys.

The full setup, event, situation, disaster, encoding, and DLC inventories are
in `content_inventory.json` and `file_inventory.json`.

## DLC

The installed build contains:

- `D000_shared`
- `D008_fate_of_the_phoenix`
- `D015_ancient_monuments_pack`
- `D017_sacred_sites_pack`

M3 replacement generation must inventory/neutralize setup-visible content from
all four while remaining valid if optional packages are unavailable.

## Vanilla baseline

The clean vanilla menu was reached autonomously at fixed 1280×720. The accepted
baseline contains only repeated store-backend misses for unavailable item IDs
3865300 and 3699010. Those normalized messages are accepted; no other new
message is permitted.

## Deferred runtime probes

- M1 will test metadata `replace_path(s)` in isolation.
- Symbol extraction will become reference-aware as each content surface is
  implemented; current top-level counts intentionally include valid wrapper
  constructs where the engine database permits them.

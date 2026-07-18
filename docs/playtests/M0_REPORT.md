# M0 Autonomous Verification Report

Date: 2026-07-19  
Game: EU5 1.3.1.1 (Pavia), checksum 7917, Steam build 24187685  
Result: **PASS with documented exporter fallback**

## Acceptance results

- Steam discovery/startup: pass. Steam was found from the registry and verified
  responsive without user action.
- Game discovery: pass. `binaries/eu5.exe` and all three game content trees were
  verified at `G:\SteamLibrary\steamapps\common\Europa Universalis V`.
- Storage: pass. Repo, Python environment, ImageMagick, caches, logs, screenshots,
  and relocated user data are on G:. C: had about 4.0 GiB free at discovery.
- Mod visibility mechanism: pass. `--user_dir=G:\antiqvitas_user_data` was proven
  by a real launch; the G:-local mod junction is recreated idempotently.
- Playset scripting: pass. Build-specific `playsets.json` mutations are backed
  up, atomic, idempotent, and checked after writing.
- Vanilla extraction: pass. Symbols, setup/content/DLC inventories, and per-file
  BOM/encoding records were generated from the installed build.
- Start-date precedent: pass. The 1444 mod and vanilla both use
  `loading_screen/common/defines` and `NGame.START_DATE`; vanilla exposes
  `NGame.END_DATE` beside it.
- Console: pass for opening, exact command entry, screenshots, and `helplog`.
  `script_docs` and `dump_data_types` are present but fail to return after
  instrumented runs. The plan-authorized community fallback and the required
  local-script+smoke corroboration rule are recorded in `BLOCKERS.md`.
- Static validation: pass.
- Real-game smoke: pass. Menu-ready heuristic passed and normalized
  `error.log` had zero new line types against the accepted vanilla baseline.

## Visual evidence

The clean vanilla menu at fixed 1280×720 is recorded at
`docs/screens/M0_baseline/vanilla_clean_menu.png`. It visibly shows version
1.3.1.1 (Pavia) and checksum 7917.

## Commands

```text
make validate
  pdxlint: PASS
  popcheck: PASS (no setup pops yet)

make smoke
  gamedriver: menu-ready heuristic passed
  smoketest: PASS (zero new lines)
```

## Judgment

M0's feedback loop is operational without human input. The local documentation
exporter defect reduces reflected-command freshness, but does not weaken the
mandatory current-build smoke gate and is explicitly covered by the plan's
fallback. M1 may proceed.

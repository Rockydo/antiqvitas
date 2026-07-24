# M12 Packaging Notes

This is a development repository, not a published Workshop upload. Do not
publish or overwrite any external item from this environment.

## Release payload

A release copy must retain these paths at the mod root:

- `.metadata/metadata.json` and `thumbnail.png`;
- `in_game/`, `main_menu/`, and `loading_screen/`;
- `CREDITS.md`, `KNOWN_ISSUES.md`, and `README.md`.

Exclude development-only data: `.git/`, `.venv/`, `.cache/`, `.tmp/`,
`.tools/`, `assets_queue/`, `baselines/`, `config/local_paths.json`,
`external/`, local screenshots, crash dumps, and the `G:` user directory.
The release payload contains no audio assets by design.

## Version and compatibility gate

`metadata.json` identifies `antiqvitas`, version `0.1.0`, and EU5 `1.3.11`.
The M12 rapid gate is tagged `M12-done`: static validation, clean menu smoke,
and fresh AD 1 initialization are recorded locally. A full observer run to AD
476 and finale screenshot remain optional evidence. Update the metadata
version only with a subsequently tested release commit; do not claim broader
game-version support.

M11's exact-name `main_menu/gui/messagetypes.txt` overlay is intentionally in
the payload. Its generator pins the installed registry hash; if an EU5 patch
changes that file, regenerate and menu-smoke the overlay before packaging.

## Workshop handoff

Use PDX Workshop Manager only after the local gate above is green. Select the
staged mod root, preserve the metadata ID unless deliberately creating a new
item, upload the reviewed `thumbnail.png`, use the `Total Conversion` and
`Historical` tags, and copy the concise scope plus Known Issues into the item
description. Do not package `config/local_paths.json` or publish local log,
save, screenshot, cache, or source-research material.

# M1 Autonomous Verification Report

Date: 2026-07-19
Game: EU5 1.3.1.1 (Pavia), checksum 7917, Steam build 24187685
Result: **PASS**

## Acceptance results

- Metadata: pass. `.metadata/metadata.json` is valid and declares ANTIQVITAS
  with the engine-accepted compatibility string `1.3.11`.
- Thumbnail: pass. The generated bronze-eagle/Han-banner thumbnail was
  inspected at 512x512 and 745,988 bytes. It is supplied at both required
  metadata and observed root locations, with the linter enforcing those facts.
- Mod enablement: pass. `tools/link_mod.ps1` recreated the G:-local junction
  and `tools/enable_mod.py` activated ANTIQVITAS in the relocated user's
  `playsets.json`, with a read-back check.
- Real-game menu: pass. The driver launched the active playset directly through
  Steam, detected the menu-ready state, and cleanly stopped the game.
- Static validation: pass (`pdxlint`, including image dimensions/size, and
  `popcheck`).
- Smoke: pass. The normalized mod `error.log` had zero new line types against
  the frozen vanilla baseline and zero baseline line types absent.

## Visual evidence

`docs/screens/M1/M1_mod_menu.png` is the autonomously captured, manually
reviewed menu proof. It shows the 1280x720 EU5 menu, version 1.3.1.1 (Pavia),
and checksum 7917 after the mod-active process reached its ready state.

## Commands

```text
make full
  pdxlint: PASS
  popcheck: PASS (no setup pops yet)
  gamedriver: menu-ready heuristic passed
  smoketest: PASS (zero new lines; 0 baseline line types absent)
```

## Judgment

M1 satisfies its acceptance criterion: an empty but valid ANTIQVITAS mod is
visible, enabled without a launcher click, and reaches the real game menu with
no new errors. M2 may proceed.

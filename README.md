# ANTIQVITAS

ANTIQVITAS is a total-conversion mod for *Europa Universalis V* spanning
1 January AD 1 through 4 September AD 476. It replaces the campaign's start
state with a sourced ancient-world political map and adds period-specific
peoples, faiths, economies, governments, armies, knowledge, diplomacy, and
historical currents.

## Current build

The repository targets EU5 `1.3.11` (local build `24187685`). M11 is complete;
M12 remains in progress for observer-based pacing, full-timeline, and finale
verification. The current full static and enabled-mod menu gate is green, but
the long observer run remains blocked by the documented renderer fault. See
[Known Issues](KNOWN_ISSUES.md) before using this development build for a long
campaign.

## Included scope

- AD 1 start state: 157 documented polities, 13,552 controlled locations,
  25 dependencies, and a 230-million population baseline;
- 350 cultures, 37 religions, 42 markets, 43 audited transport segments, five
  ancient custom goods, M6 law/government adapters, and 26 ancient unit types;
- five ancient ages, 250 advances, nine institutions, M9 subject/CB/IO
  contracts, and 416 source-window historical-current events through AD 476;
- 40 source-led player actions, English-first localization mirrored to ten
  other clients, and reviewed 2D art with no audio changes.

## Local development use

This repository contains the complete mod root: retain `.metadata/`,
`in_game/`, `main_menu/`, `loading_screen/`, and `thumbnail.png` together.
Use the EU5 launcher to activate the `antiqvitas` playset, or launch with the
same user-directory relocation configured in `config/local_paths.json`.

On Windows, from the repository root:

```powershell
.\make.cmd validate
.\make.cmd smoke
.\make.cmd full
```

`validate` checks generated output, dates, references, localization mirrors,
and asset contracts. `smoke` starts the enabled mod and rejects every new
normalized `error.log` line. The local configuration and paths are deliberately
machine-specific and are not release metadata.

## Documentation

- [Master plan](docs/ANTIQVITAS_MASTER_PLAN.md) is the design source of truth.
- [Progress](docs/PROGRESS.md), [decisions](docs/DECISIONS.md), and
  [assumptions](docs/ASSUMPTIONS.md) record implementation boundaries.
- [Credits](CREDITS.md), [surface audit](docs/SURFACE_AREA.md), and
  [packaging notes](docs/m12/PACKAGING.md) describe release obligations.
- [Finale verification](docs/m12/M12_FINALE_VERIFICATION.md) distinguishes
  the checked terminal contract from the still-required observer evidence.
- [M12 final-gate status](docs/m12/M12_FINAL_GATE.md) records the current
  full-gate result and the remaining release blocker.

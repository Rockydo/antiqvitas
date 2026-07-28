# Central Indian Granularity — 2026-07-28

## Accepted scope

- Removed `CIN` / Central Indian Societies and reassigned its 167 locations
  exactly once.
- Added Tondai-Kanchi, Atiyaman-Tagadur, Ujjayini, Vedisa, Chedi,
  Narmada-Vindhya, Son-Vindhya, Dakshina Kosala, Bastar, and Maldivian frames.
- Boundedly expanded Chola, Pandya, Chera, and Satavahana.
- Added seven cultures, one plural faith, four direct doctrines, six reforms,
  ten standards, names, agendas, research, laws, settlements, and 11-client
  localization.
- Corrected four Maldivian atolls to marine production and two Gulf of Mannar
  ports to pearls.

## Deterministic probe

`tools/s2_central_indian_granularity.py --check` passes:

- 167 former locations reassigned once; no `CIN` residue;
- ten new frames match exact capitals, counts, cultures, faiths, and reforms;
- four existing expansions match bounded arithmetic;
- standards, names, settlements, research, RGO anchors, four direct doctrine
  icons, and all localization clients resolve.

## QA acceptance

- `make validate`: **PASS**, 119 commands.
- Paired vanilla/mod `make smoke`: **PASS**.
- Both launches reached a responsive rendered menu.
- Normalized `error.log`: **zero new lines unique to the mod**.

## Evidence boundary

Urban and textual names are used only where defensible; evidence-poor uplands
use archaeological/geographic network labels and anonymous openings. No later
Pallava, imperial Tamil, Gupta, or Maldivian state is projected into AD 1.
Sources and limitations are recorded in `docs/world_1ad/SOURCES.md`,
`docs/ASSUMPTIONS.md`, and `docs/m12/central_indian_granularity.csv`.

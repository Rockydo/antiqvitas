# S2 Four-State Political Profiles - 2026-07-27

## Scope

This focused pass replaces the broad royal fallback for Armenia, Nabataea,
Himyar, and Satavahana. Each state now has a generated contract spanning its
opening reform, two research alternatives, council, social-order names,
privileges, programmes, issues, agendas, localization, direct art, and startup
assignment.

## Rapid subsystem checks

- `s2_ancient_politics.py --check`: PASS - 17 councils, 85 programmes, 51
  issues, 51 agendas, and 102 direct political icons.
- `s2_estate_orders.py --check`: PASS - 17 profiles, 126 profile grants, 126
  direct privilege icons, and 102 polity-aware social-order names.
- `m6_power.py --check`: PASS - 57 reform contracts and 172 total ancient
  privileges; every new base or alternative reform selects its matching
  council.
- `m8_knowledge.py --check`: PASS - 671 ancient-system unlocks, all 292 opening
  profiles researchable, and no vanilla unlocks.
- `generate_start_mirror.py --check`: PASS - ARM, NAB, HIM, and SAT receive
  their dedicated base reform and parliament type in the exact 25-manager
  startup mirror.
- `m11_privilege_icons.py --check`: PASS - 172/172 direct privilege icons and
  zero fallbacks.
- `p4_manual_regression.py --check`: PASS - the 17-profile political and
  126-grant breadth is pinned as a regression floor.
- Full `make validate`: PASS - 102/102 commands.

## Visual review

Eight 1536x1024 atlases were reviewed before cropping. Each is an exact 3x2
sheet of centered archaeological object still lifes with safe circular-crop
margins. Armenian objects emphasize highland fortresses, domains, routes, and
diplomacy; Nabataean objects use Petra/Hegra water, caravan, sanctuary, and
customs contexts; Himyarite objects use terrace masonry, incense, Red Sea, and
lineage contexts; Satavahana objects use Deccan routes, weights, beads,
waterworks, titled-house service, and religious gifts. No accepted cell
contains people, readable or pseudo writing, heraldry, medieval equipment, or
modern objects.

## Runtime smoke

The normal paired-control smoke launched vanilla and then ANTIQVITAS. Both
reached a responsive rendered menu; the comparison reported zero mod-unique
`error.log` line types.

The paired `-leavepops` smoke repeated the same vanilla/mod sequence. Both
sessions again reached a responsive rendered menu and the comparison reported
zero mod-unique lines. The four current vanilla DX12 assertion fragments were
present in the control and therefore correctly excluded from the mod delta.

The user's reduced QA policy does not require repetitive clicks through four
structurally generated political panels. Startup assignment, reform/council
routing, localization, icon chains, and research reachability are all derived
from the same checked profile tables, making the focused static probes plus
paired real-game menu loads the proportional acceptance surface.

## Result

PASS. The four-state tranche is complete and green. S2-P4 remains open for
additional major-state subdivisions and dated successor systems.

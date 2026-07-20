# M9 International Organizations and Known Worlds

## International organizations

M9 generates four types from the locally inspected 1.3.1.1 IO interface:

- Han Tributary System, created at AD 1 with Han and the five sourced Western
  Regions tributaries from `docs/world_1ad/subjects.csv`;
- Xiongnu Confederation, created at AD 1 with Xiongnu itself rather than an
  invented constituent-country roster;
- Panhellenic Games, created at AD 1 with Rome as a non-leader technical
  custodian; and
- Christian Church, type-only and dormant for M10's 325 activation.

The engine requires every IO type to have a corresponding `io_opinion_*` bias
and diplomatic-status localization. `tools/m9_diplomacy.py` owns the contracts,
biases, all eleven localization mirrors, and the M3 start-manager instances.
The real-game smoke first exposed both requirements; the corrected layer has
zero new log lines.

The intended later behavior remains deliberately outside M9: Xiongnu
shatter/reform, Christian councils and Pentarchy, and the 393 games sunset are
M10 time-based work. Sources: plan sections 8.3, 8.8, 10, and 16.3; row-level
`CAH-XI` and `CHG` citations in `docs/world_1ad/SOURCES.md`.

## Discovery profiles

Every generated AD 1 country gets an installed `discovered_regions` block.
The script validates all 157 profiles against harvested local region keys and
fails if one contains an Atlantic or Pacific ocean-discovery region. The three
wide profiles are Rome's oikoumene, Han's Western-Regions-to-Daqin horizon,
and the Indian Ocean world; all other polities use bounded regional profiles.

EU5 provides no verified dim/fuzzy discovery tier in this start surface. A
region is therefore a coarse knowledge horizon, not an assertion of direct
state contact, cartographic precision, or cultural familiarity throughout it.
Historical basis: plan section 16.4 and its section 8 regional contexts.

# ANTIQVITAS Surface-Area Audit

Status key: `done` = generated and static/menu-checked; `deferred` = retained
or blocked with an explicit reason; `open` = an M12 release requirement still
needs work. This is an inventory audit, not a claim that every runtime surface
has passed the observer gate.

| Surface | Status | Evidence / disposition |
| --- | --- | --- |
| Metadata, thumbnail, launcher visibility | done | M1 metadata and thumbnail; user-dir relocation/playset tooling is checked. |
| Defines and campaign calendar | done | M2 generated loading-screen defines and `tools/dates.py` own AD 1--476.9.4. |
| Every setup/start manager | done | `generate_start_mirror.py` locks 25 exact filenames and AD 1 manager totals. |
| Setup countries and templates | done | 157 generated country definitions; templates are deliberately not campaign-state seeds. |
| Countries, political colours, CoAs | done | M3/M11 definitions, named colours, 157 AD 1 standards, and 13 dynamic standards. |
| Ages, advances, institutions | done | M8's 5 ages, 250 advances, 9 institutions, disabled vanilla progression, and M11 UI coverage. |
| Cultures, languages, religions, pops | deferred | Loaded/checked M4 base is 69 cultures, 37 faiths, and 230M people; broader culture/name expansion remains evidence-blocked. |
| Goods, RGOs, markets, buildings, roads, development | deferred | Data is generated and checked, but the live RGO override gap remains in `KNOWN_ISSUES.md`. |
| Governments, reforms, laws, estates, characters, dynasties | deferred | M6 profiles load; Han regency runtime coverage remains blocked. |
| Units, levies, mercenaries, forts, navies | deferred | M7 static/menu surfaces are checked; observer war plausibility remains blocked. |
| Subjects, CBs, treaties, IOs, discovery, AI weights | deferred | M9 contracts and the M12 static AI pass are checked; observer war-frequency judgement remains open. |
| Situations, disasters, formables, tag changes, events | deferred | M10/M11 generated currents and 411 events are checked; all-century observer playback is open. |
| Generic actions and action message types | done | 40 source-led player actions; exact registry overlay is pinned and menu-smoked. |
| Scripted effects, triggers, values, on-actions | done | No unsupported custom global hook is retained; current layers use locally checked native contracts. |
| Diseases | deferred | The vanilla disease taxonomy is retained; long-run disease-current behaviour awaits observer evidence. |
| Missions and mission-task definitions | open | Installed generic mission files exist and need an explicit M12 semantic-retention or clean-disable decision before release. |
| Game rules, tutorials, and hints | open | Game-rule/hint surfaces require the final anachronism and usability review. |
| Localization, glossary, credits | done | 17 English files mirror exactly to ten clients; glossary and Pleiades/ORBIS credits are present. |
| Flags, goods/religion/advance/estate/government icons, event/age/loading art | done | M11 audit covers direct-key common screens, 83 event images, 5 age panels, and source/master/DDS chains. |
| Main menu, GUI, fonts | deferred | Vanilla menu and fonts are retained; GUI is touched only for the guarded M11 registry overlay. |
| Map geometry, terrain, 3D models | deferred | Explicit v1 non-goal: vanilla map and nearest-period 3D assets remain. |
| Audio and music | deferred | Explicit v1 non-goal: no custom audio is shipped. |
| Achievements | deferred | Explicit v1 non-goal; no achievement support is claimed. |
| Packaging and Workshop metadata | open | Release notes are present in `docs/m12/PACKAGING.md`; no external upload before M12 observer/finale acceptance. |

The two `open` semantic audits and the observer-dependent rows are tracked in
`docs/TODO.md`, `KNOWN_ISSUES.md`, and `BLOCKERS.md`. No row is silently
treated as a release pass.

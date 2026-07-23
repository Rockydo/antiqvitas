# Technical and Design Decisions

## 2026-07-23 - Ara Pacis and Mausoleum reuse established building contracts

The Ara Pacis uses the installed religious-building contract with small
cultural and unrest effects; the Mausoleum uses the cultural-building contract.
Both are one-level Rome city-point specials rendered by the existing M5 ledger,
start-manager, localization, and 128px direct-art pipeline. No new building
category, production chain, or speculative ancient statistic is introduced.

## 2026-07-23 - Privilege art uses the native portrait contract

The estate interface resolves `GetEstatePrivilegeIcon` directly and its
installed asset directory uses 64x90 portrait textures. The new M11 privilege
ledger therefore keeps each completed key bound to a unique generated source,
an exact 64x90 PNG master, and an ANTIQVITAS-owned BC7 DDS at the native direct
path. It reports incomplete migration explicitly; it neither copies a generic
privilege image nor permits shared source/master assets.

## 2026-07-23 - Rome expansion remains data-rendered and source-bounded

The Theatre of Balbus is added through the existing named-special ledger,
generated building-definition/localization path, direct 128px DDS contract,
and start `building_manager`. It uses the locally verified cultural building
contract and a modest goods-upkeep proxy rather than a custom production chain
or an unverified building type. This keeps additional Roman depth compatible
with the existing market-system blocker and preserves reproducibility.

## 2026-07-23 - Religion art migrates through a checked direct ledger

The existing direct filenames were not enough because most M4 religions still
aliased a small group of installed motifs. M11 now retains those aliases only as
a staged compatibility layer while `direct_religion_icons.csv` binds completed
rows to unique ANTIQVITAS source, 128px master, and DDS paths. The common-icon
validator checks every direct row against the religion definitions and rejects
shared direct source/master assets. The final contract is 37 direct rows and no
aliases; its first batch is intentionally non-reconstructive material context.

## 2026-07-23 - Institution visuals require source and master uniqueness

The M11 direct-key contract is tightened beyond a unique filename: every M8
institution now needs its own generated source and its own 128px master. The
common-icon validator rejects shared institution sources and masters, preventing
a visually shared fallback from returning later. The new Theology and settlement
statecraft motifs remain generic, uninscribed material contexts rather than
claims about a specific council, treaty, people, or event.

## 2026-07-22 - Dense regional production uses reusable families, not fictional monuments

The user's 100-building expansion is implemented as ten reusable AD 1
production families, each with a unique direct UI illustration and a
source-labelled engine contract, rather than a hundred unique building types.
This gives Europe, North Africa, and the Middle East 112 visible economic
placements while keeping the system legible and avoiding invented named sites.

Each type is an `is_special` one-level start building so its locally verified
category, employment, build-time, goods-upkeep, and icon contract are stable.
Its modest upkeep makes existing era goods visible in market demand; it does
not manufacture a new good, synthesize workforce, or assert historical output.
Individual placements are limited to reviewed urban or historic city-point
anchors and are source-bounded regional-hinterland proxies.

This is a technical/content-density choice, not an archaeological claim that
every listed engine polygon contains a surviving named workshop. The named
Rome/Ravenna/Mainz layer remains separate and stricter in
`roman_buildings.csv`.

## 2026-07-22 - Validation scope is targeted, not a full-timeline observer gate

The user has explicitly replaced the AD 1-to-476 observer-run completion
requirement with strict smoke checks, static contracts, and short targeted
driver probes for changed subsystems. The master plan now treats long observer
runs as optional evidence: no milestone may be held open solely for lack of an
extreme playthrough. Fresh-start cleanliness and mod-unique error detection
remain non-negotiable.

The same user direction raises visual scope: every player-facing ANTIQVITAS
advance, privilege, building, good, religion, and institution requires its own
dedicated art contract. Roman civic/commercial buildings and period-correct
location naming are immediate implementation priorities.

## 2026-07-22 - Menu smoke uses a same-machine vanilla control

The archived M0 vanilla baseline predates a reproducible current-machine DX12
`D3D12_FEATURE_D3D12_OPTIONS8` assertion. A 22 July unmodded menu run emits
the same three normalized lines as the enabled ANTIQVITAS run and otherwise
reaches the rendered menu. It is not evidence of a mod regression.

`tools/smoketest.py` consequently launches vanilla immediately before every
enabled-mod smoke and fails on every line unique to the mod, using the union of
the accepted baseline and that same-run vanilla log as its reference. The
archived-baseline delta remains in the JSON report; it is neither accepted into
the ANTIQVITAS baseline nor hidden. This gives each content batch an actual
control under the current GPU/driver state while preserving strict detection of
mod-only diagnostics.

## 2026-07-22 - RGO worker ceilings are not current-labour seeds

The installed location-scoped `change_max_raw_material_workers` effect changes
an RGO's maximum workforce; it does not allocate workers at an AD 1 start.
A disposable Faiyum wheat calibration from six to 30 worker levels left the
fresh Observer market output and capacity state unchanged through 21 January.
The project therefore retains the reviewed source-led level of six and rejects
using a larger ceiling as a synthetic annona or trade-route fix.

The installed Create Trade generic action also requires source-market surplus
and a merchant market with country capacity. Those predicates explain why a
valid route syntax alone does not establish Roma grain imports. M5 remains
blocked pending a locally documented, historically defensible source-surplus
contract; no static transfer or current workforce is fabricated.

## 2026-07-22 - M3 acceptance proves the political map, not later systems

M3's master-plan acceptance is an AD 1 Earth political map containing every
§8 polity with no vanilla 1337 country-start layer. The project now verifies
that directly with a focused static census of the roster, runtime tags,
definitions, exact manager mirror, capitals, and ownership ledger, plus a
fresh paused Observer map.

The earlier month-long M3 observer finding correctly exposed systems that were
then still owned by M5, M6, and M9. It is not a reason to redefine the stated
map criterion as a long AI simulation. The unresolved Han minority-regency
binding remains M6 work, and sustained observer evidence remains M7/M8/M10/M12
work; neither is silently accepted by the M3 tag.

## 2026-07-22 - M9 foundation acceptance is a paused AD 1 web gate

The master plan assigns M9 a concrete founding-state acceptance: diplomacy
screens must be coherent and client/tributary webs must match the reviewed AD
1 ledger. This gate therefore pairs a no-time-advance Observer inspection of
Rome, Western Han, and Parthia with the generated dependency and IO audit; the
live counts are 11, 5, and 9 and exactly total the ledger's 25 edges.

War resolution and sustained AI observation are not silently substituted into
that criterion. They remain M7 and M12 work, while dated foederati behavior is
M10 work. This keeps the accepted M9 result technically bounded and prevents a
renderer-limited long replay from obscuring a successfully validated AD 1
diplomatic foundation.

## 2026-07-22 - Raw-material remaps use the startup effect, not map templates

The installed `location_templates.txt` is parsed for a mod but does not
instantiate its changed raw materials at the AD 1 bookmark. Local effect docs
and a live Roma clay probe establish that location-scoped
`change_raw_material` is the runtime contract. The generated exact-name
`_hardcoded.txt` overlay therefore injects the 328 reviewed corrections after
the source `setup_area_preferences` anchor, with count, duplicate, custom-key,
and annona-seed guards.

The installed goods registry also requires each custom raw good in
`pop_demands.txt`; an exact source-pinned mirror supplies the five keys. A
localized worker seed is necessary for each runtime-added good. A trial
`base_production` value was rejected because it created global market supply,
not output at the historical anchor. This is an engine-loading decision, not a
change to the source ledger.

## 2026-07-22 - Runtime console controls use generated engine tags

ANTIQVITAS's historical design tags are collision-safe source identifiers, not
always the tags loaded by the EU5 runtime. The checked
`docs/world_1ad/tag_map.json` maps Rome `ROM` to `XAA` and Parthia `PAR` to
`XAH`; console `tag` and `declarewar` require the latter. The M7 controlled
war probe verified `tag XAA` from an active player and `declarewar XAH` through
the populated live War Viewer.

Tools and playtests must read that generated map rather than typing a design
tag into engine-facing console commands. This is a technical namespace rule;
it does not rename any historical polity or alter the source ledger.

## 2026-07-21 - AD 1 country starts do not include vanilla government templates

All 157 generated country starts previously included either installed
`east_asia_monarchy` (96) or `asia_advanced_tribe` (61). Those templates
serialize medieval law and estate-default sets before ANTIQVITAS's explicit
government adapters. A live AD 1 observer consequently removed 213 laws and
227 estate privileges as incompatible at game start.

`tools/generate_start_mirror.py` now renders only the independently generated
technology tier, discovery profile, and government block. The 107 source-led
M6 profiles remain byte-for-byte defined by their ledger. The 50 deliberately
unsourced/collective profiles receive the minimal locally verified equivalent
of their former template type: a monarchy with cognatic primogeniture, or an
SoP tribe with tribal-oldest-male succession, each with `ruler = random` and
no imported laws or privileges. The fresh paused observer test has zero
removal diagnostics, so this is the engine-correct contract rather than a
suppression of valid ANTIQVITAS content.

## 2026-07-21 - Named AD 1 incumbents use date-less current terms

The installed start parser accepts `START_DATE = 1.1.1` but rejects an open
`ruler_term` beginning at that exact instant as a future term. Installed
ordinary starts pair their named `ruler` with a `ruler_term`; omitting that
term silently generated a replacement head in live Rome and Parthia probes.
The M6 generator consequently serializes a date-less current term for each of
the 31 source-led non-regency incumbents. It carries no `start_date`, so it
does not turn the campaign boundary into a fabricated accession day.

This follows the local engine contract rather than fabricating a pre-campaign
accession date. Fresh live panels bind Augustus and Phraates V correctly, and
validation plus smoke report zero new errors. The native Han minority-regency
shape remains an explicit exception: two date-less Ping variants still produced
a generated ruler and are deferred in `BLOCKERS.md`.

## 2026-07-21 - Dynamic names use a separate secure curated ledger

`tools/generate_dynamic_names.py` now accepts a second, explicit ledger for
reviewed non-capital names. It rejects an unknown location/culture, a duplicate
location, a missing language contract, an empty source/note, or any confidence
grade other than `secure`. Capital anchors remain coordinate-derived; the
generated report now identifies each row as `capital` or `curated`.

This separation prevents a market, road, or vanilla localization key from
silently becoming a historical name. The owner-profile culture is an engine
lookup adapter, not evidence that the selected city had one spoken language.

## 2026-07-22 - Roman-world names require an exact ancient-point review

The 17-location Italian and Sicilian expansion accepts only entries with a
named Pleiades ancient point, a campaign-valid form, an installed map-key
match, and secure confidence. `PLE:<id>` now records the exact source entry
rather than relying on a generic classical-source label. The coordinate
projection is a rejection check for a bad key match, not a basis for remapping
the game map or fabricating a city boundary.

This retains direct Latin-period display forms even at old Greek settlements
where Pleiades lists multiple historical names. The selected M4 culture remains
only the engine's dynamic-language adapter; it does not settle local language,
demography, sovereignty, or civic status.

## 2026-07-21 - Game-driver activation handles minimized EU5 windows and capture focus

EU5 can be minimized by Windows between a valid menu screenshot and the next
driver input. A minimized Win32 window reports only a title-bar geometry; the
previous title/size filter rejected it before `activate_window()` could restore
it. The discovery routine now retains title-matched minimized windows, and the
click path foregrounds EU5 again immediately before its evidence capture.

This is a driver-integrity repair: it prevents capture of an unrelated desktop
application after a game input. It does not alter game data or make a failed
observer start appear successful.

The final M4 run also found that repeating the cross-thread focus sequence
while EU5 was already foregrounded could make Windows revoke that focus. The
driver now returns immediately in that safe state; successful screenshot and
input evidence confirms the narrower safeguard.

## 2026-07-21 - Germanic corpus uses existing language-group render contracts

The locally harvested M4 language registry has no verified dedicated roots for
the 36 new Germanic, Baltic, and Fennian frames. The generator therefore uses
the existing engine-valid Germanic/German, Baltic/Baltic, and Uralic/Sami
contracts. These choices make valid nested culture records; they are not a
historical decision on individual local languages, ancestry, or identity.

The start-mirror generator also correctly rejects a culture selector that
resolves to no controlled AD 1 locations. The rejected Savolax selector was
replaced by a documented controlled Karelia location; this retains a visible,
reviewable approximation instead of manufacturing a population scope.

## 2026-07-21 - Culture symbol yields to the existing Liburnian unit key

The M7 navy already owns the global localization key `antq_liburnian`. The
first real-game smoke correctly reported the collision when M4 introduced a
same-named culture. The culture is therefore namespaced as
`antq_liburnian_culture`, while its player-facing name remains "Liburnian".
This preserves the M7 unit contract and avoids a second global localization
definition; a fresh validation and smoke prove the repair.

## 2026-07-21 - Balkan-Anatolian language groups are rendering adapters

The locally harvested language registry lacks verified roots for the 50 new
frames. Their Balkan/Anatolian/Hellenic/Celtic group fallbacks are technical
engine adapters only, not conclusions about local speech, language-family
membership, ethnicity, or Romanization. (Sources `STR-BAL`, `STR-ANA`,
`MIT-ANA`, and `CAH-XI`.)

## 2026-07-21 - Gallic and Aquitanian labels reuse verified language adapters

The installed language registry has no verified roots for the 47 named Gallic
and Aquitanian frames. The generator consequently uses its existing
Celtic/Gaelic and Iberian/Latin rendering contracts. These are loadability
adapters only, not a decision on individual languages, language-family
membership, Romanization, or ethnicity. (Sources `STR-GAL`, `PLN-GAL`, and
`OCD-GAL`.)

## 2026-07-21 - Narrower sourced culture selectors refine broad sourced frames

The initial culture ledger rejected every overlap. That made a reviewed
province-scale ethnographic frame impossible to add without deleting the broad
regional source frame that remains necessary for all other locations. The
resolver now applies a deterministic source-specificity order: location >
province > area > region. It rejects equally-specific overlap and does not use
CSV order as evidence. This keeps a broad source as the documented fallback
while permitting a newer, independently sourced narrower frame to refine it.

## 2026-07-21 - Iberian culture-group languages are rendering adapters

The installed language registry has no verified roots for the 38 named Iberian
communities. Their generated records reuse the existing Celtic/Gaelic and
Iberian/Latin technical contracts only so the engine can render valid nested
language records. The adapters do not resolve local speech, language-family
membership, ethnicity, or Romanization. (Sources `STR-IBR`, `PLN-IBR`,
`OCD-HIS`, and `MAI-IBR` where applicable.)

## 2026-07-21 - Observer readiness uses visual/log quiescence without a CPU cap

The fresh M4 observer launch rendered a responsive menu and an AD 1 Observer
screen, but its live renderer sustained about 110 percent aggregate CPU after
the debug log became quiet. A manually supplied `--max-cpu 10` constraint
therefore produced a false driver timeout. The smoke harness's normal
visual/log-based readiness predicate passed on the same build. Future observer
launches use that normal predicate unless a task specifically needs a CPU
measurement; CPU is telemetry, not menu-readiness evidence.

## 2026-07-21 - Hami and Turpan retain the existing Iranian naming adapter

The locally verified M4 contract renders `antq_iranian_group` through the
engine-valid Persian fallback. The Hami and Turpan Oasis records reuse that
adapter rather than inventing unverified local languages. It is a rendering
choice only: it does not identify AD 1 Hami or Turpan as Iranian, settle their
languages or ethnicities, or impose population majorities. (Source `IRAN-CT`.)

## 2026-07-21 - Kashgar retains the existing Iranian naming adapter

The locally verified M4 contract renders `antq_iranian_group` through the
engine-valid Persian fallback. The Kashgar Oasis record reuses that adapter
rather than inventing an unverified local language. It is a rendering choice
only: it does not identify AD 1 Kashgar as Iranian, settle its language or
ethnicity, or impose a population majority. (Source `IRAN-KAS`.)

## 2026-07-21 - Aksu retains the existing Iranian naming adapter

The locally verified M4 contract renders `antq_iranian_group` through the
engine-valid Persian fallback. The Aksu Oasis record reuses that adapter rather
than inventing an unverified local language. It is a rendering choice only: it
does not identify AD 1 Aksu as Iranian, settle its language or ethnicity, or
impose a population majority. (Source `IRAN-AKS`.)

## 2026-07-21 - Yarkand retains the existing Iranian naming adapter

The locally verified M4 contract renders `antq_iranian_group` through the
engine-valid Persian fallback. The Yarkand Oasis record reuses that adapter
rather than inventing an unverified local language. It is a rendering choice
only: it does not identify AD 1 Yarkand as Iranian or Saka, settle its language
or ethnicity, or impose a population majority. (Source `IRAN-YAR`.)

## 2026-07-21 - Loulan retains the existing Iranian naming adapter

The locally verified M4 contract renders `antq_iranian_group` through the
engine-valid Persian fallback. The Loulan city-oasis record reuses that adapter
rather than inventing an unverified local language. It is a rendering choice
only: it does not identify AD 1 Loulan as Iranian, settle its language or
ethnicity, or impose a population majority. (Source `CAM-LOU`.)

## 2026-07-21 - Kucha retains the existing Iranian naming adapter

The locally verified M4 contract renders `antq_iranian_group` through the
engine-valid Persian fallback. The Kucha Oasis record reuses that existing
adapter rather than inventing an unverified Kucha language. This is a rendering
choice only: it does not claim an AD 1 Iranian or Kuchean language, ethnicity,
or population majority. (Source `IRAN-KUC`.)

## 2026-07-21 - Kulay retains the existing Uralic naming adapter

The verified M4 language contract has no Kulay root, while the established
`antq_uralic_group` renders through the engine-valid `sami_language` fallback.
The Kulay archaeological proxy reuses that contract rather than inventing an
unverified language definition. It is a rendering choice only: it does not
identify Kulay material culture as Uralic or Sami, settle its linguistic
affiliation, or project a later Siberian identity into AD 1. (Source
`TOM-KUL`.)

## 2026-07-21 - Samad retains the verified Semitic naming adapter

The M4 language contract renders `antq_semitic_group` through the existing
`antq_semitic_dialect`, whose root has the locally verified
`aramaic_language` fallback. Samad reuses that engine adapter rather than
inventing an unverified Samad language. Its `arabic_language` validation seed
and the rendered dialect are technical compatibility choices only; neither
identifies the Samad archaeological context as an Arab or Aramaic tribe,
language community, state, or later Omani identity. (Sources `IRAQ-SAM`;
`OUP-GUL`.)

## 2026-07-21 - Permic retains the existing Uralic naming adapter

The verified M4 language contract has no separate Permic root, while the
established `antq_uralic_group` renders through the engine-valid
`sami_language` fallback. The new Permic proxy therefore uses that existing
adapter without inventing a second dialect or a locally unverified language
root. It is a rendering contract only: it does not identify early Permic as
Sami, settle the reconstructed affiliation, or project later Komi/Udmurt
languages into the start date.

## 2026-07-21 - Khotan retains the existing Iranian naming adapter

The locally verified M4 contract already supplies `antq_iranian_group` through
the engine-valid Persian fallback. The Khotan Oasis record uses that existing
adapter so the generated culture remains loadable, while the primary historical
source specifically warns that Han-era evidence does not determine whether
Khotan's inhabitants were Iranian. This is therefore a rendering/naming
contract only: it does not claim an AD 1 Khotanese-Saka language, ethnicity,
or Iranian population majority.

## 2026-07-21 - Chadic Basin retains the existing Sub-Saharan language adapter

The verified M4 language contract provides one generated dialect per culture
group, and the established `antq_subsaharan_group` uses the engine-valid
`mande_language` fallback. The new Chadic Basin culture therefore joins that
existing group rather than inventing an unverified Chadic engine language or
duplicating a second language record for the group. Its documentation and
definition explicitly state that this is a naming/rendering contract, not a
claim that Chadic was Mande or a resolution of local Chadic languages.

## 2026-07-21 - Sargat retains the existing Uralic language adapter

The Sargat archaeological culture has no locally verified language key, and
the Uralic-group contract already renders through the engine-valid
`sami_language` fallback. The new Sargat entry therefore uses that existing
adapter without introducing an invented language root or a second dialect for
the same culture group. This is a rendering/naming contract only: the source
does not identify Sargat as Sami, uniformly Ugric, or linguistically settled.

## 2026-07-21 - Moche uses a future-only dynamic tag anchored to VIR

`MOC` must not appear in the AD 1 roster or tag map because Moche is a later
historical current. The second-century generator therefore reserves `MOC` as a
locally checked `define_unique_country_tag`, emits its color, CoA, and
localization in the same generated future-formation layer, and validates that
the AD 1 `VIR` proxy owns its only seed location before rendering. M11's
pre-formation phase notices anchor on `VIR`, which exists at campaign start;
the primary M10 event alone creates `MOC`. This follows the installed
dynamic-country contract without a phantom start-country definition.

## 2026-07-21 - Venedi regional frames retain the proto-Slavic fallback dialect

The installed language inventory has no verified proto-Slavic root. The two
regional Venedi records use the existing `west_slavic_language` fallback so
EU5 can render valid nested language records. This is an engine contract, not
a claim that AD 1 northeastern or Dnieper populations spoke a later West Slavic
standard or that their affiliations are resolved.

## 2026-07-21 - Rhaetic uses the existing technical Latin fallback

The verified build has no Rhaetic language root. The bounded Rhaetic culture
therefore uses the same engine-valid Latin fallback already used for other
under-documented residual European cultures. It is an implementation contract
only and does not claim that Rhaetic was Latin or erase Alpine linguistic
uncertainty.

## 2026-07-21 - Southwest China keeps an explicit engine-language fallback

The installed language inventory lacks a verified Dian or Yelang language root.
Those two source-led culture records therefore use the existing highland group
and its engine-valid fallback dialect, `mongolian_language`, solely so EU5 can
render a valid nested language record. The attached historical labels remain
contested regional proxies; this technical fallback does not assert a
Mongolic language, a uniform southwest population, or a resolved affiliation.

## 2026-07-21 - Preserve the Micronesian map gap with a disjoint province selector

The harvested `micronesia_region` resolves to the controlled Yap/Ulithi surface
but not the separately controlled Mariana location in `piranga_province`.
The M4 ledger therefore uses the region plus that disjoint installed province,
rather than falsely treating the map hierarchy as a historical boundary or
silently omitting the verified M3 Micronesian surface. The resolver expands
both selectors to concrete locations and rejects any overlap.

## 2026-07-21 - Culture-ledger regions use the harvested hierarchy with the same strict coverage contract

Some source-qualified AD 1 frames, including the Bantu-frontier ledger, are
installed geographic regions rather than a fabricated collection of smaller
selectors. The local harvested hierarchy already resolves regions to concrete
locations. The M4 resolver therefore accepts an explicit `region` selector in
addition to area, province, and location, validates it against the local
symbol inventory, and applies its existing non-empty and overlap checks after
expansion. This is a bounded topology capability; every regional cultural
assignment still requires a source, confidence, and rationale in the ledger.

## 2026-07-21 - Normalize only direct self-members in the harvested location hierarchy

The installed hierarchy occasionally represents a parent location both as a
container and as one of its own children (for example, `kilkenny` contains
`cullahill` and `kilkenny`). Treating that shape as a general recursive cycle
wrongly rejects an otherwise valid geography selector. The M4 resolver now
accepts only a direct self-member as that location's leaf while retaining its
strict rejection of every indirect cycle. This is a local topology
normalization, not an expansion of selector scope or a historical judgement.

## 2026-07-21 - Guard the dormant GLH horde localization against absent government scope

The fresh northern-atlas observer replay identified the installed `GLH` custom
localization's strict `government_type = government_type:steppe_horde`
comparison as another inactive-legacy-tag scope error. Adjacent installed
scripts use the optional `?=` comparison for this precise case. The checked
renderer preserves the local source file and changes only that comparison, so
the horde label remains available for a real scope and evaluates false without
an error when the legacy country has no government. This is an engine
compatibility guard, not a change to any AD 1 polity.

## 2026-07-21 - Culture remaps use source-labelled geography selectors, never vanilla culture keys

The installed template-culture field is a later-period geographic helper, not
evidence for an AD 1 population identity. M4 therefore resolves an explicit
area, province, or location selector through the harvested hierarchy and
requires an ANTIQVITAS culture, source, confidence, rationale, non-empty
coverage, and no selector overlap. The generated population mirror applies a
narrow location override first, then this audited ledger, then only the
existing regional profile fallback. This makes the 1,406-location first batch
reproducible and prevents a broad regional source judgement from silently
overwriting a documented frontier exception.

## 2026-07-21 - Legacy parliament scope checks are guarded as local exact-source overlays

The complete observer save-load exposed eight installed `government_type`
comparisons on absent legacy country scopes in two parliament-issue files.
The engine's locally evidenced `?=` form yields false for such a scope while
preserving the ordinary result for active countries. The renderer copies both
local source files, changes only those eight identified comparisons, and
verifies their per-file line inventory before writing. This is an initialization
compatibility decision, not a change to the historical availability of any
parliament issue.

## 2026-07-21 - Universal start law categories belong at technology tier one

The installed tribal start templates assign `education_masses_law` and
`tribal_legal_basis_law` before the AD 1 knowledge tree is evaluated. Placing
their category bridges on later advances emitted missing-advance diagnostics
for tier-one societies. M8 now places both on the universally granted
depth-zero `antq_imperial_cult` node, without restoring vanilla units or
levies. This is an engine-category bridge only; the historical government
meaning remains in M6's namespaced reforms and laws.

## 2026-07-21 - Preserve native government categories through ancient advances

The AD 1 government adapters intentionally retain a small set of installed
law and policy categories, but M8 disables the vanilla advances that normally
unlock them. A fresh paused observer run proved that the engine was stripping
otherwise valid start-state laws. The M8 generator now carries the fifteen
locally evidenced category bridges on historically named ancient advances,
including the installed `aristocratic_court_policy` gate while retaining no
vanilla unit or levy unlock. The marriage category is unlocked rather than
pretending that polygyny itself is a technology. This is a mechanics bridge,
not a claim that the vanilla labels describe ancient institutions; M6's
source-led adapters remain the player-facing historical layer.

## 2026-07-21 - Keep historical faith families while using native mechanics groups

The local religion-group registry and the installed `polygyny` rule show that
EU5's hardcoded pagan contracts recognise native folk groups. ANTIQVITAS keeps
its namespaced historical families in source data and localization, but maps
each religion's engine-facing group to the closest installed family. This lets
the game's pagan/reform/marriage mechanics recognise AD 1 faiths without
renaming them. The remaining Buddhist, Dharmic, Iranian, and Manichaean start
policies are covered by a checksum-guarded exact overlay of the installed
`01_common.txt`; it extends policy availability only and fails validation if
the local source file changes. A fresh paused observer start has zero invalid
policy removals.

## 2026-07-21 - Make the dormant Sitges flag test optional

The sole remaining observer-initialization script error came from the
Catalan Sitges flag variant comparing an absent capital on an inactive legacy
tag. The installed game uses capital ?= location comparisons throughout its
own scripts. A checked exact-source overlay changes only this one comparison,
so the variant remains available when a real country has Sitges as capital
and evaluates false rather than emitting an error otherwise. Full validation,
smoke, and a fresh AD 1 observer initialization are green; the latter records
zero script-system errors.

## 2026-07-21 - Make legacy CoA predicates false rather than fabricate state

Vanilla CoA template registries evaluate generic monarchy, republic,
theocracy, and HRE special-status predicates for inactive legacy tags. Their
government and IO scopes are absent in the AD 1 start, causing script errors
without implicating any ANTIQVITAS standard. The installed engine already uses
government_type ?= comparisons and HRE existence guards in adjacent scripts.
The M12 renderer therefore preserves the installed CoA trigger file while
changing exactly four comparisons and inserting exactly three HRE guards. This
makes the predicates false on absent state and leaves real ANTIQVITAS
governments and standards eligible. The generated overlay passed static and
menu smoke gates, then removed every targeted signature in a fresh observer
initialization.

## 2026-07-21 - Guard hardcoded startup compatibility by exact local contracts

The installed on-game-start handler presumes that Catholic and Shinto
international-organization instances exist and runs country-specific setup for
China, Majapahit, Japan, Byzantium, Verona, the Teutonic Order, and Bulgaria.
Those instances and empty legacy country tags are deliberately absent from the
AD 1 conversion, producing runtime scope errors even though ANTIQVITAS's own
Han and other profiles were valid. The M12 renderer preserves the installed
file, changes only five of its absent-IO references to the locally evidenced
safe-scope form, and wraps exactly eight dated country blocks in a dynamic
post-end-date condition rendered from tools/dates.py. Its own check rejects
source inventory drift, and pdxlint's date exemption is limited to this
re-rendered exact-source overlay. A fresh observer initialization reduced all
former targeted signatures to zero without modifying the game installation.

## 2026-07-21 - Pin the UI-verified 70-percent render scale in the game driver

The installed Graphics settings UI reports Upscale Method Disabled and Upscale
Quality Off, so setting an imagined FSR-off enum would not be a real recovery
change. Its Render Scale control supplied the verified numeric contract:
100, 90, 80, then 70 percent, persisted as Graphics.render_scale = 0.700000.
The autonomous driver now writes that exact 0.7 value while retaining the
supported 1920x1080 windowed profile and the existing very-low options. Full
validation and a 90-second enabled-mod smoke are green. The fresh observer
playback reached 1 June but reproduced the same FSR crash as the full-scale
profile; retain this profile for smoke stability, but pause further profile
changes until a material engine or driver recovery is evidenced.

## 2026-07-21 - Generate each custom institution's required birth modifier

The installed institution manager asks the static-modifier registry for the
exact key formed by an institution ID plus _birth. The local vanilla
institutions file confirms that each such modifier is a location-category
record. M8 now generates all nine matching records in the correct main-menu
path and checks their key coverage against the institution manifest. Their
small, source-theme-aligned local values remain below the corresponding vanilla
birth-modifier scale. The associated names and descriptions are included in the English
source and exact client-language mirrors. Static validation and a 90-second
enabled-mod menu smoke are green. A fresh AD 1 observer initialization verified
that neither the missing-modifier nor missing-localization diagnostic remains.

## 2026-07-21 - Use the installed 1920x1080 renderer mode for autonomous driving

The configured 960x540 window string is not a valid enum value in the installed
EU5 build: the debug log rejected it and the engine retained the 2560x1440
desktop mode before the two FSR crashes. The installed loading-screen scripts
explicitly contain the `1920x1080` mode. The driver therefore now writes that
lower, supported windowed resolution through its single width/height constants
while retaining the already locally accepted very-low graphics values. A
90-second enabled-mod smoke loaded a rendered menu with the persisted 1920x1080
setting and zero new error-log lines. This is a bounded recovery change; only a
fresh observer play-control probe can establish whether it cures the renderer
fault.

## 2026-07-21 - Quarantine vanilla events by preserving their loader contract

EU5's generic systems validate referenced events, their scope types, and parts
of their variable/effect graph at load time. Empty files and generic stubs lose
that information. The checked M12 renderer instead mirrors all 347 installed
event files (7,440 definitions), preserves direct historical schedulers, and
adds `current_date > 476.9.4` inside every direct event trigger. The date
condition is unreachable in the AD 1--476 campaign but is not a compile-time
false constant, so EU5 retains each scheduler/reference graph and emits neither
orphan nor unused-variable diagnostics. Files without a trigger receive the
same guarded trigger. Period-external dates are normalized through `tools/dates.py`.
The full overlay passed static validation and a settled enabled-mod smoke with
zero new lines; event contents remain compatibility data only.

## 2026-07-20 - Do not stub the coupled vanilla event runtime by filename overlay

The installed loader validates vanilla event calls from generic actions,
buildings, parliaments, scripted effects, and other registries even when their
direct on-actions are neutralized. Empty event files leave missing references;
uniform hidden stubs become orphaned or have the wrong scope; preserving their
variable/effect network would reintroduce the dated subsystem. M12 therefore
does not ship a speculative partial quarantine. The exact source-verified
attempts are documented in `BLOCKERS.md`, and the clean pre-experiment baseline
is retained until a locally proven whole-graph replacement surface exists.

## 2026-07-20 - Disable only dated and dynastic vanilla hints

M12 uses an exact-name overlay of the installed scriptable-hint file to add an
impossible `priority` trigger to 33 post-antique definitions. The selected
inventory is limited to named historical crises/situations, later named states,
and HRE/Eastern-Roman country cues. The renderer copies every other source byte,
so generic economic, food, stability, warfare, estates, slavery, and research
guidance stays available. Its source inventory and priority contract are checked
on every validation, and the enabled overlay has a clean settled-menu smoke.

## 2026-07-20 - Restrict the automated anachronism sweep to authored player text

The M12 anachronism guard reads the 17 English localization files rather than
all mod bytes. Exact-name vanilla overlays and technical identifiers must retain
some later-game names for database compatibility, but they are not campaign
claims shown to a player. The audit blocks narrowly unambiguous post-476 terms
and inflections (colonialism, Renaissance/Reformation, firearms, railways, and
named early-modern polities) while leaving contextual vocabulary such as
`empire`, `church`, and `feudal` to source review. The exact client-language
mirror check makes this English-first result apply across the supported UI.

## 2026-07-20 - Treat host pagefile headroom as a runtime prerequisite

The latest failed launcher experiment's crash metadata recorded 9 MB of free
pagefile, 4.85 GB system RAM available, and only 2.5 GB used from the RTX
3080's 10 GB dedicated pool. The mod therefore treats the reported Vulkan
out-of-device-memory exception as a host virtual-memory condition until a run
with material pagefile headroom proves otherwise. The unproven early physical
window resize is not retained. Changing the system pagefile or terminating
unrelated host processes is outside the mod's safe project scope; the evidence
is logged and independent work continues instead.

## 2026-07-20 - Preserve crash evidence across an early game-process exit

The autonomous driver treats a process disappearing during its CPU-sampling
window as a normal failed readiness result, not a driver exception. It also
performs stale-reporter cleanup when the recorded game PID is already gone.
Cleanup remains path-pinned to the configured EU5 installation's
`crash_reporter/binaries/CrashReporter.exe`; broad process-name cleanup would
be unsafe and could close unrelated applications. This is diagnostic tooling
only and does not change game content or relax the observer retry boundary.

## 2026-07-20 - The driver cleans only detached crash reporters from this EU5 install

Past failed game launches left detached `CrashReporter.exe` dialogs above later
healthy EU5 windows, confusing screenshot-driven UI automation. The driver now
matches the reporter's resolved executable path against this installation's
`binaries/crash_reporter/binaries/CrashReporter.exe` and closes only those
processes before launch and after a controlled stop. It never matches by name
alone or touches a reporter outside the configured game directory. The
cleanup-enabled, 90-second menu smoke is green.

## 2026-07-20 - Observer access uses a one-default exact-name game-rule overlay

The installed `country_change` rule defaults to prohibited, which is why the
previously visible Observer confirmation could not complete despite receiving
input. The M12 overlay mirrors the full installed rules file and changes only
that default to `country_change_allowed`, with source re-rendering and drift
checks on every validation. Its enabled-mod menu smoke is clean. This enables
the autonomous test hand without changing historical currents, AI choices,
country data, or normal rule definitions.

## 2026-07-20 - The game driver writes the installed very-low graphics contract

The previous fixed-window driver wrote a numeric frame-cap and lowercase
anti-aliasing value. The game rejected both, logged the failure, and fell back
from the intended profile. The driver now uses the installed string enum for a
30-FPS cap and the exact very-low values for AA, map objects, portrait sampling,
textures, filtering, shadows, effects, terrain-adjacent render features, and
unit CoAs. It drives a 960x540 window and holds a rendered menu for 90 seconds,
so resource loading cannot be mistaken for a completed smoke. A clean
enabled-mod post-splash smoke confirms all supplied values are accepted; the
engine still notes its optional `multi_sampling` key is absent, so the driver
does not guess an unsupported value. This is a renderer-stability repair, not a
content or balance change.

## 2026-07-20 - M6 measures complete roster coverage without fictionalizing unknown courts

Section 19's 250--400-character target is enforced as a source-led roster
floor, not as a mandate to create a named person for every Tier-1/2 tag. The
existing 107 profile ledger separates 32 governments with a named active head
from 75 documented anonymous or collective starts. `m6_power.py` now validates
that split and emits the reviewable roster report. This preserves an engine
valid random-ruler contract where local source routes establish the polity but
not an AD 1 officeholder; later M10 currents may introduce a named figure only
when dated evidence warrants it.

## 2026-07-20 - M11 moves dynamic CoAs into their owning M10 generators

Five M10 generators emitted thirteen temporary solid-color CoAs for future
formations and successor identities. M11 changes those source generators,
rather than overlaying their output, so a normal regeneration preserves the
reviewed standard. A dedicated validator confirms each tag, its colored-emblem
asset, and its three-color contract against the installed game catalogue.

## 2026-07-20 - M11 reaches event density by phase-reviewing existing sourced currents

Section 18 asks for at least 400 events but separately budgets roughly 80
shared event paintings. M10 already has 83 source-led currents and reviewed
art links. M11 therefore gives every non-terminal current four no-effect,
dated review events derived through `dates.py`, rather than inventing hundreds
of unsupported incidents or images. This produces 411 events while leaving
the campaign sandboxed. The final 4 September 476 event is deliberately not
expanded past the campaign end.

The installed engine rejects dynamic historical events addressed to a future
country at load time. M11 routes only the optional phase notification through
an existing AD 1 anchor for HNS, ERO, and VND; the original M10 formation and
current logic continues to own the historical polity transition.

## 2026-07-20 - M11 keeps the five M8 icon identifiers and supplies exact DDS overrides

The M8 tree already groups its 250 advances into five 50-item visual surfaces.
Keeping those identifiers avoids a data-only rewrite while replacing all five
rendered surfaces. The installed game supplies four of the names as vanilla
files, but it has no `crown_power_advance_discovery.dds`; the mod now provides
that exact name rather than relying on a non-existent fallback. The dedicated
validator makes the five-to-250 mapping, source/master chain, and texture
contract explicit.

## 2026-07-20 - M11 replaces the five exact age-illustration filenames

The installed advance view obtains its banner through
`AdvancesLateralView.GetAgeIllustration`, while the installed asset inventory
contains one 1080x440 illustration for each of the five playable vanilla age
keys. M11 therefore keeps the compatible keys and overrides only those exact
filenames with reviewed BC7 panels. The post-end sixth age is intentionally
untouched. `tools/m11_age_art.py` makes the retained source/master/DDS chain a
validation invariant, and the event contact-sheet filter excludes age masters
so two visual review surfaces do not drift together.

Sources weighed: local advance-view UI, asset inventory, and master plan
sections 15 and 20.

## 2026-07-20 - M11 credits use the verified metadata description surface

The local metadata schema exposes `short_description`, not a separate long
description or credits field. M11 keeps that schema unchanged, adds a concise
Pleiades/ORBIS pointer to `short_description`, and makes `CREDITS.md` the
complete attribution record. Pleiades' official download page confirms its
downloadable data is CC BY 3.0; ORBIS is credited as a route-sanity source
without claiming a license or reproducing its map data.

Sources weighed: local metadata schema in `ENGINE_FACTS.md`; Pleiades data
download page; master plan sections 20-21.

## 2026-07-20 - M11 retires M2's no-op advance scaffolds

M2's five age records remain the campaign-calendar surface. Its five
`potential = { always = no }` advance records were deliberately temporary
compatibility scaffolds; M8 has since supplied the complete 250-advance
ancient tree. M11 therefore removes the old definitions, source-generator
branch, and mirrored localization rather than leaving unreachable entries in
the research UI or a second nominal owner for the age surface.

Sources weighed: local M8 generated advance tree, `tools/dates.py`, and master
plan sections 4, 8, and 22.

## 2026-07-20 - M11 core CoAs use a data-validated engine-emblem contract

`docs/m11/core_coas.csv` owns the bounded Rome/Han/Parthia override set.
`tools/generate_country_definitions.py` validates each source tag and the
installed `ce_*.dds` colored-emblem texture, then emits the locally observed
solid-pattern, named-colour, colored-emblem, and instance syntax. This replaces
only three conspicuous M3 placeholders and leaves all other flags visibly
pending rather than silently converting generic design into asserted history.

Sources weighed: local installed CoA definitions and textures; plan sections
8.1-8.3 and 20.

## 2026-07-20 - M5 Via Popilia stops before unavailable Adria and Altino

The available source documents Popilia's Rimini-Ravenna-Adria-Altino
trajectory, but the installed map has neither Adria nor Altino. The road ledger
therefore ends after two labelled, contested regional links at the available
Rovigo proxy; it does not use Venice as an anachronistic terminus or manufacture
unavailable intermediate map keys.

Sources weighed: local `tools/generate_start_mirror.py`; plan sections 8.1 and
12.2; ORBIS; the Italian Ministry of Culture record listed in `MIC-POP`.

## 2026-07-20 - M5 Via Aemilia preserves its missing-anchor uncertainty

The source establishes a Rimini-Piacenza corridor and its central
Bologna-Modena-Reggio Emilia axis, while the installed map lacks Reggio Emilia
and minor stations. The renderer consequently writes four endpoint links, with
the two long links marked contested in the source ledger. This preserves an
engine-valid regional connection without inventing a detailed route.

Sources weighed: local `tools/generate_start_mirror.py`; plan sections 8.1 and
12.2; ORBIS; the Italian Ministry of Culture records listed in `MIC-AEM`.

## 2026-07-20 - M5 Via Flaminia uses one explicit high-level engine link

The local road renderer only accepts installed, AD 1-controlled endpoints, but
the historic eastern branch runs through unavailable Terni and intermediate
anchors. It therefore emits one labelled, contested `narni = spoleto` link,
rather than fabricating a detailed trace or silently omitting the documented
connection. The generated value uses the locally verified bare endpoint
contract and leaves the independent RGO/trade-flow blocker open.

Sources weighed: local `tools/generate_start_mirror.py`; plan sections 8.1 and
12.2; ORBIS; Italian Ministry of Culture, ["Archeologia Via
Flaminia"](https://sabapumbria.cultura.gov.it/archeologia-e-territorio/archeologia-via-flaminia/).

## 2026-07-20 - M11 final-century art requires full generated-current coverage

`tools/m10_final_century.py` now rejects both orphaned image-map keys and any
final-century timeline current lacking a reviewed event-image link. All thirteen
AD 400-476 currents have an inspected retained master and 1080x440 BC7 DDS, so
the one-to-one check makes this complete surface regeneration-safe rather than a
manual audit result that could silently regress.

Sources weighed: local `tools/m10_final_century.py`, `docs/timeline.csv`, and
the installed country-event image contract.

## 2026-07-20 - M11 fourth-century art requires full generated-current coverage

`tools/m10_fourth_century.py` now rejects both orphaned image-map keys and any
fourth-century timeline current lacking a reviewed event-image link. All fourteen
AD 300-399 currents have an inspected retained master and 1080x440 BC7 DDS, so
the one-to-one check makes this complete surface regeneration-safe rather than a
manual audit result that could silently regress.

Sources weighed: local `tools/m10_fourth_century.py`, `docs/timeline.csv`, and
the installed country-event image contract.

## 2026-07-20 - M11 fourth-century art uses a generator-owned image map

`tools/m10_fourth_century.py` now validates reviewed map keys and the existence
of each DDS before it renders image fields. Its first entry is Armenia's AD 301
current; later fourth-century artwork will use the same regenerable contract.

Sources weighed: local fourth-century renderer and the installed country-event
image contract.

## 2026-07-20 - M11 third-century art requires full generated-current coverage

`tools/m10_third_century.py` now rejects both orphaned image-map keys and any
third-century timeline current lacking a reviewed event-image link. All ten AD
200-299 currents have an inspected retained master and 1080x440 BC7 DDS, so the
one-to-one check makes that complete surface regeneration-safe rather than a
manual audit result that could silently regress.

Sources weighed: local `tools/m10_third_century.py`, `docs/timeline.csv`, and
the installed country-event image contract.

## 2026-07-20 - M11 second-century art uses the generator-owned image map

`tools/m10_second_century.py` now owns `EVENT_IMAGES`, matching the checked
first-century generator contract. It rejects unknown timeline keys and missing
mod-relative DDS textures before rendering, and it emits the event `image`
field from that map. This keeps later M10 art references regenerable rather
than hand-editing generated events and prevents orphaned or silently dropped
game-facing textures.

Sources weighed: local `tools/m10_history.py`,
`tools/m10_second_century.py`, and the installed country-event image contract.

## 2026-07-20 - M11 art review derives from retained masters

The M11 review surface is generated from every
`assets_queue/generated/antq_*_1080x440.png` master rather than manually
maintained. `make art-review` renders both the browsable HTML sheet and a
compact PNG, so each added event image enters the visual audit automatically.
The review assets remain documentation only; game-facing DDS textures continue
to be individually dimension-checked and wired through `EVENT_IMAGES`.

## 2026-07-20 - M5 does not invent a bathhouse building contract

The locally extracted base-game building symbol table has no bathhouse, thermae,
spa, or equivalent public-bath building key. The existing `aqueduct_system` at
Rome remains the verified water-infrastructure representation; M5 does not add
an unsupported script symbol or relabel an unrelated building as a literal bath
complex. The Baths of Agrippa were already supplied by the Aqua Virgo before
AD 1, but that historical fact does not establish a safe engine contract.

Sources weighed: local `docs/vanilla_symbols/building.json`; ANTIQVITAS master
plan section 12.3; Digital Augustan Rome's Thermae Agrippae record.

## 2026-07-20 - M11 replaces native pepper art without duplicating the good

The installed game already defines `pepper` and exposes exact matching
128x128 and 1080x440 DXT5 surfaces named `icon_goods_pepper.dds`. M11 replaces
those same mod-relative filenames with inspected generated DDS files rather
than adding an unneeded `antq_pepper` economic symbol. This preserves M5's
existing good and RGO mapping while making its visible art reviewable.

## 2026-07-20 - M5 uses the verified marketplace contract for Forum Romanum

The installed building catalogue has no forum- or agora-specific contract. The
source records the Forum Romanum as both marketplace and political/legal civic
centre, so M5 uses the engine-valid generic `marketplace` at the already
validated Rome city node. This avoids inventing a building key or attaching a
misleading later monument; source and assumption records bound the generic
building's interpretation.

## 2026-07-20 - M11 attaches *Immensum Bellum* through the checked event-image contract

The installed `earthquake_events.txt` uses an `image` key directly on a
country-event definition, and its checked texture is 1080×440 BC7. The first
M10 event illustration therefore uses that same mod-relative event-art path,
owned by `EVENT_IMAGES` in `tools/m10_history.py`; the generator validates
that every mapped texture exists before it renders the event. This avoids an
unregistered art asset and makes regeneration safe.

ImageMagick can inspect the installed BC7 DDS but its local encoder falls back
to DXT output. `tools/dds.py` therefore dispatches explicitly requested BC7
textures to the locally installed work-drive DirectXTex `texconv.exe`, retaining
the source PNG's opaque alpha and generating the full mip chain. The tool is
ignored under `.tools/`, so no binary build dependency is committed.

## 2026-07-20 - M11 replaces the checked vanilla loading-screen filename

The local asset manifest identifies the vanilla loading screen as
`loading_screen/gfx/loadingscreens/startscreen.dds`, a 1920×1080 DDS texture.
M11 uses that exact mod-relative filename rather than inventing an unregistered
asset path. The generated master and resized derivative remain under
`assets_queue/`, while the reviewed DDS is the only game-facing copy.

## 2026-07-20 - M5 maps Ferrum Noricum to Friesach's generic iron good

The RGO renderer can write only installed, controlled location keys. `friesach`
is the reviewed nearby Carinthian candidate for Hüttenberg; M5 changes only its
raw-material key to the locally verified vanilla `iron` symbol. It does not add
a new good, special mine building, market node, or a claim that static RGO data
currently drives runtime trade.

## 2026-07-20 - M5 represents Oc Eo through Angkor Borei without pre-creating Funan

The plan includes Oc Eo as a Southeast Asian growth hub, while the installed
map contains `angkor_borei` rather than an exact Oc Eo key. The source records
a canal connection between Angkor Borei and the Oc Eo region, so M5 adds that
checked location to the market and town ledgers as a clearly contested
near-region proxy. It does not change ownership, create a Funan tag, rename an
installed location, or add unsupported harbour infrastructure.

## 2026-07-20 - M5 represents Ephesus through Ayasuluk without renaming the map key

The plan specifically lists Ephesus among its market hubs. The installed map
has no `ephesus` key but does have the nearby Ayasuluk location under Roman AD
1 control. M5 adds that checked location to both market and urban-node ledgers,
then reuses the smoke-proven protected-harbor contract; it does not introduce a
new geography key or imply a precise Roman shoreline.

## 2026-07-20 - M5 anchors Dacian gold at Baia de Arieș

The RGO renderer can override only installed controlled locations. A local
coordinate projection makes `baia_de_aries` the nearest reviewed candidate to
Roșia Montană, and it is already controlled by the Dacian start tag. M5 changes
only its raw-material key to the installed `goods_gold`; the site is not given
a market, building, event, or a claim to be the later Roman mine itself.

## 2026-07-20 - M5 maps Carthage harbor through the reviewed Tunis anchor

The building renderer accepts a protected-harbor row only at a checked M5 urban
node under its AD 1 owner. Carthago already has the reviewed `tunis` city-node
proxy; adding the locally verified harbor contract there preserves that
constraint and avoids inventing a new map key or a special Punic/Roman harbor
type. Its source ledger and contested metadata make the spatial approximation
visible.

## 2026-07-20 - M5 maps Prima Porta through Rome rather than inventing a location key

The installed map lacks a Prima Porta key. The verified `noble_villa` building
is therefore seeded at Rome, the existing city-scale regional anchor, with
source and proxy limits retained in the special-building ledger. This is a
technical scale choice, not a decision to treat villa properties as urban or to
model the generic building name as an exact Roman social category.

## 2026-07-20 - M5 permits the verified generic monastery for Buddhist institutions

The plan expressly allows monasteries in Buddhist eastern contexts at the
campaign start. M5 therefore uses the installed generic `monastery` at the
source-qualified Anuradhapura node, with a ledger note preventing its display
or mechanics from being read as a Christian or later monastic structure. No
new building type or unsupported religion-specific contract was invented.

## 2026-07-20 - Historic buildings may use a checked non-market site ledger

The original M5 renderer restricted specialist buildings to the forty market
nodes. The plan-required Jerusalem Temple demonstrates that a historically
central site need not be a trade hub. `historic_building_sites.csv` is therefore
validated for installed location, AD 1 owner, unique key/location, source, and
confidence before it can authorize a non-market M5 building.

The AD 70 event uses the installed location-scope `has_building_with_at_least_one_level`
and `destroy_building = "building(building_type:temple|owner)"` contracts. The
guard makes the dated event safe if gameplay has already removed the proxy.

## 2026-07-20 - M5 distinguishes a roadstead from a harbor building

The source's explicit no-harbor statement rules out reusing the
`protected_harbor` contract at Muza. M5 instead seeds the verified
`market_warehouse` building at the already validated market-town location.
This keeps the game-visible trade effect while preserving the historical
distinction in the ledger rather than silently homogenizing every port.

## 2026-07-20 - M5 splits the western Roman corridor into reviewed map links

The road generator accepts only installed, AD 1-controlled endpoint pairs and
emits the vanilla bare `origin = destination` contract. The western extension
therefore uses seven short reviewable links rather than a single Rome-to-Iberia
edge. Exact Domitia legs, broad Via Augusta legs, and unavoidable connector
proxies keep their separate source and confidence metadata in the CSV.

## 2026-07-20 - M5 reuses one verified harbor contract across ancient ports

The installed `protected_harbor` building already loads cleanly at Alexandria.
M5 uses the same country/tag/location/level manager shape for six additional
source-led market anchors rather than inventing a separate antiquity harbor
type or placing later-era special buildings. The start renderer validates that
each target is an existing controlled M5 urban node and rejects a duplicate
building/location pair.

## 2026-07-20 - Third-century history extends the M6 adapters only where a current changes them

The smoke harness now configures UTF-8 replacement output before reporting a
log diff. This is diagnostic-only: it prevents a Windows cp1252 console from
hiding a real engine error containing replacement characters; the baseline and
comparison logic are unchanged.

The AD 200-299 renderer adds two generated government-reform definitions and
one additional option within the existing Roman citizenship law. Its dated
events use the locally harvested `remove_reform`/`add_reform` and
`remove_policy`/`add_policy` contracts: the Sassanid Revolution exchanges the
Arsacid great-house reform, Diocletian exchanges the Principate reform, and
the Constitutio Antoniniana exchanges the legal policy. These are narrow
transition surfaces, not a broad retroactive rewrite of the AD 1 M6 profiles.

The renderer is intentionally separate from the prior two M10 renderers,
owns only the AD 200-299 ledger slice, has a unique event-ID range, checks
its cosmetic identities against the AD 1 runtime tag map, and emits the
folder-specific BOM/CoA encoding pattern. `ALM`, `SAS`, and `FRK` were also
checked absent as installed setup-country tags; they are cosmetic identities,
not dynamically created states. M11 owns their final visual art.

## 2026-07-20 - Second-century currents use a separate deterministic renderer

`tools/m10_second_century.py` owns the non-overlapping AD 97-199 ledger slice,
all of its events, current managers, temporary Champa visual assets, and
eleven mirrored localization files. Like the first-century renderer, it reads
each game date from `docs/timeline.csv` through `AntqDate`, resolves its
recipient through the generated tag map, and treats situations/disasters as
locally proven manager contracts rather than copied vanilla pulses.

The AD 192 formation uses the locally harvested
`create_country_from_location`/`define_unique_country_tag` surface to make
`CPC`, which was checked absent from the installed setup, common, event, and
main-menu scripts as well as the AD 1 tag map. Its placement is guarded by the
current Han ownership block for the four reviewed Rinan locations. The color
and solid CoA are intentional M10 temporary assets; M11 owns their final art.

## 2026-07-20 - Population exceptions are checked separately from ownership

M3 political ownership is not a safe proxy for every local population's
culture, religion, social form, or macro-population allocation. The start
renderer now accepts a small source-qualified population-location ledger and
the population checker applies the same expected culture/religion and region
contract. This first protects the Rinan/Linyi Han frontier from both an
accidental Southeast-Asian SoP ownership assignment and an opposite accidental
Han-population conversion. The ledger is deliberately narrow: every exception
must name its local location, culture, religion, pop type, allocation region,
source, confidence, and reason.

## 2026-07-20 - Northern Xiongnu is a unique dynamic country, not a static tag

The installed event corpus proves the required contract: a location-scoped
`create_country_from_location` can define a stable three-letter runtime tag,
set its name/adjective/color/flag, and then receive locations through
`change_location_owner`. M10 uses the unoccupied `XNO` runtime tag for Northern
Xiongnu. The generated event creates it at the reviewed northern seed,
inherits the continuing Xiongnu culture/religion, and applies the locally
verified steppe-horde, reform, and heir-selection effects before moving the
remaining reviewed slice. `XSO` remains a cosmetic identity for the Southern
continuity.

The release seed is explicit data rather than an implicit geographic query. Its
generator validates every location against both the locally indexed map and
the current AD 1 Xiongnu ownership block, so a future M3 map change fails
validation until this dated historical approximation is reviewed again. `XNO`
is absent from the installed setup/common/event/main-menu scripts and from the
AD 1 tag map. The color and solid CoA are M10 temporary assets; M11 owns their
historical visual replacement.

## 2026-07-20 - M10 transformations use cosmetic tags until a new polity is needed

The installed `change_tag_cosmetic` effect is a safe in-place adapter: it sets
the country name, adjective, map color, and flag without replacing the country
identity. M10 uses `KSH` for the Yuezhi-to-Kushan formation and raises that
country to empire rank. It uses `XSO` for the surviving Southern Xiongnu and
destroys the M9 Xiongnu Confederation IO on the split outcome. Both cosmetic
keys receive generator-owned temporary map colors and solid CoAs; M11 owns
their sourced final visual treatment.

The engine rejects a cosmetic name containing a rank word because the UI adds
the rank itself. The base localization is consequently `Kushan`, not `Kushan
Empire`. A true Northern-Xiongnu polity is deliberately not fabricated by this
adapter; it awaits a separately validated dynamic-country release surface.

## 2026-07-20 - M10 uses the installed dynamic-history event manager

The local 1.3.1.1 event corpus exposes `dynamic_historical_event` with repeated
`tag`, `from`, `to`, and `monthly_chance` fields. M10 uses that contract for
single-date and formation/tag-switch notifications, while multi-year currents
use the locally established situation and disaster managers. This is narrower
and more engine-native than overriding `country_yearly.txt`; no vanilla
on-action file is copied into the mod.

The first real load also proved two required support contracts: the loader
rejects a set-but-never-read variable and dynamic events need an `.entry`
localization key. The generator omits premature state variables and emits both
long and short entry labels. Its initial formation and tag-switch events are
explicit launch surfaces, not a claim that their in-place/new-tag
transformations are already implemented.

## 2026-07-20 - M10 preserves one calendar ledger for campaign and history

The existing `docs/timeline.csv` was the M2 campaign-calendar input. M10
extends it in place rather than creating a parallel history calendar: each
row has a validated date/key/type/region/summary/rails surface plus an optional
end date. `tools/dates.py` now rejects duplicate keys, unsupported content
types or rail strengths, reversed windows, and out-of-order records before any
renderer can consume them. This retains the plan's single date authority and
prevents future history scripts from carrying independent date literals.

The first date of a plan-specified year or window is a technical activation
boundary, not a claim about an undocumented calendar day. Date-specific claims
will only be narrowed when their source record supports that precision.

## 2026-07-20 - M9 IO instances are deliberately narrow and generated

The installed IO parser requires a per-type `io_opinion_<type>` bias and three
diplomatic-status localization keys, even for a dormant type. M9 generates
those required support surfaces with the IO contracts so the local build cannot
silently drift out of sync. The initialized Han instance contains only the
Han court and the five sourced Western Regions tributaries; the Xiongnu
instance contains Xiongnu itself because no separate AD 1 constituent-member
ledger exists; the games use Rome as a non-leader technical custodian. The
Christian Church is a type-only 325 scaffold.

This avoids inventing a Panhellenic city roster, Xiongnu constituent hierarchy,
or an AD 1 pan-Christian institution merely to populate a UI list. M10 owns
dated membership, shatter/reform, councils, votes, and the games sunset.

## 2026-07-20 - M9 discovery profiles use regions as a deliberately coarse horizon

EU5's installed start interface accepts `discovered_regions`, `areas`, and
`provinces` but exposes no source-safe dimness tier. The generator uses only
locally harvested region keys, gives Rome/Han/Indian Ocean tags the explicitly
specified broad horizons, and gives every other polity an ownership-world
regional profile. It rejects every Atlantic and Pacific ocean discovery region
as a permanent M9 invariant. A discovered region therefore means an
era-appropriate map horizon, never equal survey quality or direct diplomacy
with all countries inside it.

## 2026-07-20 - M9 war contracts distinguish historical availability from AI policy

The local 1.3.1.1 CB, wargoal, and peace-treaty files establish the generated
field vocabulary. Client-king and tributary CBs refer only to their matching
custom treaties; every custom treaty has a distinct key because this build
reports duplicate localization keys even when CB and treaty labels coincide.
The installed engine also requires a registered antagonism bias whenever a
peace term sets `base_antagonism`, so the ancient terms intentionally use its
verified zero-antagonism default instead of inventing global bias entries.

The unification CB definitions are intentionally invisible and AI-disabled
until M10's dated, source-led situations grant them. All current custom CBs
are AI-disabled as well: their historical granting and weighting belongs to
specific situations rather than an unsourced blanket war policy at AD 1.

## 2026-07-20 - M9 subjects are generated adapters over the reviewed ledger

The local 1.3.1.1 `vassal` and `tributary` definitions establish the field
shapes used by the five M9 subject contracts. `tools/m9_diplomacy.py` owns
those UTF-8-BOM scripts, their eleven localization mirrors, and the 382
foederati date through `AntqDate`; `generate_start_mirror.py` imports its
design-tag adapter table rather than duplicating a relationship mapping.

This separates historically reviewed membership from technical behavior:
`docs/world_1ad/subjects.csv` remains the sole source for each AD 1 edge,
while M9 contracts model the distinct Roman, Arsacid, and Han forms without
claiming a uniform legal text. The implementation is additive and does not
modify the installed game files.

## 2026-07-19 - Wang Clan Regency reuses the verified nobles-estate contract

The installed estate interface has no safe country-specific estate attachment,
whereas the existing `nobles_estate` contract supports the small power,
satisfaction, and cabinet modifiers needed for a bounded court-network adapter.
The Wang privilege is assigned only to Western Han's AD 1 profile, so it does
not create a global Han estate or a new engine system. Its historical limits
are recorded separately in `ASSUMPTIONS.md` and the source ledger.

## 2026-07-19 - M6 enforces Tier-1/2 government coverage

`tools/m6_power.py` now reads the reviewed AD 1 polity roster and fails if a
Tier-1 or Tier-2 tag has no M6 government profile. This turns the 107-of-107
coverage result into a maintained build invariant, while deliberately not
equating a generated anonymous ruler with completion of the separate named
character, dynasty, or regnal-history requirements.

## 2026-07-19 - M6 distinguishes advanced chiefdoms and settled town clusters

Plan P8.5 explicitly differentiates emerging Aksum from Djenné-Djenno's
settled town cluster. M6 adds an `Advanced Chiefdom` reform on the installed
`tribe` type and a `Settled Town Cluster` reform on the installed `republic`
type, each with a deliberately small labelled estate/law adapter. Both use a
random ruler rather than manufacturing an individual or constitutional detail.
They are bounded representations of political scale and settlement form, not
claims that Aksum or Djenné-Djenno used later European-style institutions.

## 2026-07-19 - M6 uses a bounded Regional Kingship adapter

The installed `monarchy` surface is the narrowest valid contract for an
attested regional court whose current AD 1 ruler is not defensibly named. M6
therefore adds `antq_regional_kingship`, a small crown-power/cabinet-efficiency
reform paired with an explicitly generic court privilege and administrative
law. It is deliberately lower-claim than the specific Han, Parthian, Roman,
Kushite, or frontier adapters. The random-ruler sentinel supplies an engine
character while the ledger keeps the historical omission visible.

## 2026-07-19 - Northern Indian courts use separate bounded monarchy reforms

The installed monarchy and estate/law modifier contracts are sufficient to
separate the Indo-Scythian regional-satrapal court from the late Indo-Greek
city-court setting without introducing unverified government types. M6 adds
two labelled reforms, paired privileges, and administrative laws. Their notes
make clear that `nobles_estate` and `burghers_estate` are UI proxies, not
claims of a shared feudal or municipal constitution.

## 2026-07-19 - M6 supports source-qualified collective and anonymous profiles

Local start data establishes `ruler = random` for `republic`, `tribe`, and
`monarchy` profiles; its 1337 examples use `tribal_oldest_male` for the tribal
form. The M6 generator permits that sentinel only for those locally observed
types and does not require a campaign ruler term for it. This preserves the
audit requirement for every named ruler while allowing either an attested
collective polity or a source-qualified polity with no identifiable AD 1
incumbent to retain a historically bounded government profile.

## 2026-07-19 - Roman civic-cult practice uses the installed religious-law category

The installed religious laws and government reforms prove the `religious` law
category and `tolerance_heathen` modifier are live engine contracts. M6 extends
its ledger validator to that verified category and uses a Rome-specific law
with a single small tolerance value. The label and data explicitly reject a
modern-freedom reading; the later persecution/toleration ladder requires dated
M10 events and is not claimed complete here.

## 2026-07-19 - Roman legal status reuses the installed slavery-law contract

The local `slavery_laws` contract establishes `slavery_blocked` and the two
slave-goods trade flags as live country modifiers. M6 adds a namespaced Roman
law that explicitly sets their permitted baseline instead of relying on an
implicit vanilla default. It deliberately adds no numerical economic bonus and
does not attempt an unverified population reclassification; M4/M10 own those
separate historical systems.

## 2026-07-19 - Anuradhapura uses bounded monastic and irrigation adapters

The local registry verifies `clergy_estate`, crown-estate power, cabinet
efficiency, and food-consumption modifiers, but supplies no ancient Lankan
institutional category. M6 therefore uses a narrowly labelled monarchy reform,
a monastic-patronage privilege, and a canal-endowments law. These make a
source-attested court pattern visible while stating in the generated data that
they do not reconstruct Buddhist fiscal jurisdiction, a water-law code, or a
complete Anuradhapura constitution.

## 2026-07-19 - Legion political power uses the privilege/disaster fallback

The local `common/estates/00_default.txt` is a global estate-type registry.
Its seven installed definitions have no country-potential or setup attachment
field, and a local search found no `add_estate`/`remove_estate` effect that
could instantiate a Rome-only estate. Estate UI, privileges, events, and
parliament resources also enumerate fixed installed estate identities. A custom
Legion estate would consequently be a system-wide unverified contract, not the
plan's country-specific political actor. M6 retains the locally tested
Praetorian Donatives privilege on its explicit noble-estate adapter; M10 owns
legionary donative, acclamation, and crisis-disaster interactions.

## 2026-07-19 - Han Mandate maps to the installed legitimacy surface

The local Chinese bureaucracy definitions and government-reform files use
`monthly_legitimacy` as a live monarchy power modifier. M6 therefore adds the
same conservative `0.05` contract to Han Imperial Bureaucracy and makes the
mapping explicit in localization. It does not use `monthly_celestial_authority`:
that is tied to unadopted later-game bureaucracy systems whose runtime behavior
is not yet established for the AD 1 Han profile. M10 owns the dynamic collapse
and restoration mechanics.

## 2026-07-19 - M6 coinage laws reuse the installed socioeconomic contract

The local `common/laws/01_common.txt` defines `coin_laws` in the
`socioeconomic` category and supplies live gold, silver, and copper minting
modifiers. M6 exposes only that proven surface: a gold-and-silver Rome law and
a copper Han law, both restricted to monarchy profiles. The values are the
installed coin-law contracts, not a numerical reconstruction of ancient fiscal
systems. This gives the two imperial cores visibly distinct AD 1 monetary
standards while reserving crisis debasement and Wang Mang's later reforms for
dated M10 content.

## 2026-07-19 - Second Temple priesthood uses the installed clergy estate

The installed `common/estates/00_default.txt` and
`common/estate_privileges/clergy_estate.txt` verify `clergy_estate`,
`global_clergy_estate_power`, and `clergy_estate_target_satisfaction` as live
contracts. M6 therefore represents the Second Temple priesthood with a
namespaced clergy-estate privilege and a Judean administrative law, rather than
adding an unproven country-specific estate. The generated profile and its
enabled-mod smoke are green. This preserves a visible political actor while
labelling the estate bucket as a narrow technical adapter, not a Christian or
medieval social classification.

## 2026-07-19 - Brittonic druidic authority uses the installed clergy estate

The installed clergy-estate privilege contract is already live for the Second
Temple adapter. M6 reuses that verified surface for a separate, source-labelled
Brittonic druidic-authority privilege rather than creating an unproven estate.
Its small mechanical effect is paired with the existing kin-based tribal elder
council, so it represents a distinct religious actor without treating it as a
single British constitution. The profile scope and historical qualification are
recorded in `docs/m6/BRITTONIC_DRUIDIC_AD1.md`.

## 2026-07-19 - Near Eastern courts use explicit regional adapters

EU5 provides no historical sub-kingdom or border-court government type. M6
therefore adds `antq_parthian_subkingdom` and `antq_buffer_kingdom` as unique
reforms over the locally verified monarchy type, with separately labelled
privilege/law adapters. Media Atropatene uses the former; Osroene and Armenia
use the latter. These are strictly pre-M9 political adapters: they do not
assert a finished Parthian satrapy, Roman client, or neutral-buffer subject
contract, which requires the planned diplomacy work.

## 2026-07-19 — Regnal histories are ledgered; current terms start at the campaign boundary

The installed engine accepts a signed pre-AD-1 `ruler_term` while parsing the
menu, but the prior live AD 1 probe showed that historic term dates are
validated against the campaign window at game instantiation. M6 consequently
retains source-led back-history in `docs/m6/regnal_histories.csv`, while
`tools/m6_power.py` renders exactly one current ruler term per implemented
government at campaign-valid `1.1.1`. It validates every emitted term through
`AntqDate`, forbids pre-campaign dates, and does not invent accession days.
Later succession situations will consume the ledger instead of treating a
technical start date as a historical accession claim.

## 2026-07-19 — Biography dates are a narrow signed-date domain

Campaign time remains exclusively `AntqDate` (`1.1.1` through `476.9.4`).
Character `birth_date` and `death_date` are separately parsed through
`BiographyDate`, which permits only years -1000 through 476 and rejects year
zero. This is necessary for the plan's AD 1 Augustus roster, while preventing
an accidental pre-AD-1 campaign script from passing validation. `pdxlint`
recognizes the exception only on those two named fields.

## 2026-07-19 — M6 reskins installed government types through reforms

Build 24187685 exposes only five government types. The initial Principate, Han
Imperial Bureaucracy, and Parthian King of Kings are therefore `monarchy`
profiles with unique, locally verified government-reform modifiers. The
adapter is explicit in generated data and localization; it is not a historical
claim that the three states shared one institution. Custom estate identities
and the remaining world-government coverage remain subsequent M6 work.

## 2026-07-19 — M6 privileges and laws use narrow estate adapters

The engine's installed estate and law contracts are used without adding an
unverified estate type. `nobles_estate` and `burghers_estate` are therefore
explicit, source-noted technical adapters for senators, urban plebs, palace
personnel, and Parthian great houses. Five privileges, four laws, and direct
societal-value fields are generated only after their CSV keys, local symbols,
and start-manager syntax validate. This avoids treating a technical UI bucket
as a historical social classification, while giving the three core profiles
distinct playable constraints.

## 2026-07-19 — M6 uses the installed tribe and steppe-horde government types

The installed `government_types/00_default.txt` permits
`tribal_oldest_male` for both `tribe` and `steppe_horde`; the latter exposes
horde-unity behavior. M6 therefore uses `steppe_horde` for Wuzhuliu's Xiongnu
confederation and `tribe` for the Marcomannic and Catuvellaunian kingdoms,
with source-labelled reforms, laws, and privileges. This is a tested engine
choice, not a claim that the named polities were mechanically identical.

## 2026-07-19 — Herodian tetrarchs retain client-monarchy mechanics in AD 1

Archelaus, Antipas, and Philip are distinct AD 1 client rulers. The engine has
no native ethnarch/tetrarch government type, so their three start profiles use
the already smoke-tested client-monarchy adapter while their separate tags and
source notes preserve the historical division. A Judean priestly/theocratic
flavor layer remains separate rather than being asserted through an unverified
government type.

## 2026-07-19 — Roman client courts reuse one qualified political adapter

The current engine exposes a small fixed government-type set, whereas the AD 1
Roman client ring includes ethnarchies, tetrarchies, kingdoms, and a contested
Bosporan queenship. Each verified client court therefore uses the locally
tested client-monarchy reform, law, and privilege while retaining its own
source-labelled ruler, dynasty record, and uncertainty note. This keeps the
shared imperial-patronage relationship playable without erasing historical
differences or inventing constitutional categories.

## 2026-07-19 — Western Han uses the Jingzhao/Xi'an Chang'an anchor

The installed key `changan` is north of the historical city. The local
`jingzhao` (Xi'an) key is the 4.4-pixel coordinate match for Chang'an, so it
replaces the prior erroneous Luoyang capital. `capital_mapper.py` records that
specific alias to keep generated candidate reports honest.

## 2026-07-19 — Via Appia starts at the first installed inland proxy

The installed location map has no Capua key. The road generator therefore uses
one source-labelled Rome–Benevento high-level leg, then resumes the attested
Benevento–Taranto–Brindisi sequence. This is marked contested in the ledger;
it neither fabricates a Capua location nor presents the abstract engine edge as
a geometrically exact Roman-road reconstruction. The Taxila–Mathura link uses
the same explicit high-level convention for the named Uttarapatha corridor.

## 2026-07-19 — Taxila reuses the reviewed Attock geographic proxy

The installed map has no `taxila` key. The world roster already resolves the
Indo-Scythian capital and territorial anchor through nearby `attock`, with a
recorded coordinate candidate and contested confidence. The M5 market and city
node intentionally reuse that one audited proxy rather than introduce an
unverified map substitution or omit the plan-listed city.

## 2026-07-19 — Civic infrastructure uses conservative installed proxies

The installed building vocabulary has no literal Circus Maximus, Roman bath, or
ancient reservoir key. The M5 ledger therefore maps the Circus Maximus to the
verified `hippodrome` slot, Alexandria's period harbor to `protected_harbor`,
and the Dujiangyan/Abhayawewa water systems to `irrigation_systems`. Each row
states that it is a technical proxy, rather than quietly claiming a one-to-one
architectural identity. All are level one, source-labelled, and restricted by
the existing AD 1 owner and urban-location checks.

## 2026-07-19 — Dedicated ancient goods use the full generated engine contract

Papyrus, silphium, naphtha/bitumen, jade, and camels are separate raw goods,
not cosmetic renames of paper, medicaments, tar, gems, or livestock. The local
goods parser synthesizes eight modifier types for every good, so the generator
renders the exact installed type contracts, their required UI name and
description keys, and a neutral existing vanilla modifier-icon fallback. This
keeps the new definitions additive, visible, and free of missing-symbol UI
errors while preserving later balancing freedom.

The installed game also requires BOM-encoded raw-goods scripts and streams
both the 128x128 good icon and 1080x440 illustration. `tools/dds.py` now
builds a complete DXT5 mip chain for every asset. It assembles individually
ImageMagick-compressed levels for non-power-of-two illustrations because the
upstream writer only auto-generates mips for power-of-two textures. The output
headers and byte sizes match the inspected vanilla silk samples exactly.

## 2026-07-19 — Specialist buildings use the verified start manager

The locally installed `07_cities_and_buildings.txt` proves that a start file
may provide `building_manager = { building = { tag = <engine tag> level = 1
location = <location> } }`. M5 now renders that exact contract from a compact,
source-labelled CSV rather than editing a large copied vanilla building file.
The generator resolves the owner from the AD 1 ownership ledger and requires
the location to have an AD 1 town/city profile, so ownership changes cannot
silently leave an invalid building tag behind. The live new-game probe accepted
the event-only Pharos and all other entries without a building-manager error.

This pass uses only locally verified era-compatible building keys and level 1.
It deliberately does not repurpose a later mill/manufactory or override a
vanilla production method merely to claim a historical good; custom goods and
their art remain a separate M5 implementation task.

## 2026-07-19 — Development is a transparent engine scale, not a census

The installed development manager adds values from selectors such as `road`,
`town`, and `city`. M5 uses only those four selectors and leaves the global
base at zero, preventing later-period regional bonuses from becoming silent AD
1 history. M4 population totals and M5 city/town classifications remain the
historical sources; the four development values are intentionally modest,
validated technical parameters.

## 2026-07-19 — M5 roads use the installed base-road start syntax

The installed `09_roads.txt` records a road as a bare `origin = destination`
pair, without a road-type field. The initial ancient network uses that exact
locally verified contract and does not invent an unverified paved-road syntax.
Its scope is a small historical corridor ledger, not a copied 1337 network;
road type progression and broader density remain later M5/M8 work.

## 2026-07-19 — Runtime probes distinguish economic from later-system failures

The first observer run is recorded as an M5 foundation probe, not a milestone
pass. It verifies that the new markets, RGO override, town setups, and their AI
tick surface do not emit runtime errors through 11 January AD 1. Vanilla
coat-of-arms triggers still fail on absent governments and international
organizations; those errors are explicitly attributed to M6/M9 and remain
outside the M5 economic acceptance claim.

## 2026-07-19 — Menu readiness requires visible rendering

Driver readiness cannot be inferred from a quiet debug log or a surviving
process: an M5 probe produced a black, hung window under those conditions. The
driver now requires the Windows hung-app check to pass and samples the game
client pixels, requiring at least five percent non-black coverage. This makes
the stored screenshots evidence of a usable menu state rather than a process
liveness artifact.

## 2026-07-19 — Source anchors override regional RGO rules

`docs/goods_remap.csv` establishes broad ancient production limits, while
`docs/m5/rgo_anchors.csv` records a small set of source-labelled places whose
goods are specifically named by the design bible. The generator resolves an
anchor before a regional rule. This lets an attested silk, incense, pepper, or
mine site correct the installed map without granting the same good to a broad
region; the report records which mechanism changed each location.

## 2026-07-19 — M5 urban profiles are intentionally small and generated

The 36 source-labelled market hubs each receive exactly one generated town or
city record, rather than inheriting a later-period regional town setup. The two
M5 profiles use only locally verified building keys: market towns get temple,
marketplace, and entrepot; market cities add a granary and mason. They are
engine-building proxies, not a claim that a medieval production ladder existed
in AD 1. The generator writes the required `common/town_setups` definition in
UTF-8 BOM because the live parser rejected its no-BOM form.

## 2026-07-19 — Raw-material corrections use an exact map-template override

The installed start managers do not provide a raw-material initialization
surface; raw materials are defined in the complete `map_data/location_templates`
file. M5 therefore generates an exact-name copy of that installed file,
preserving every unmodified template and changing only source-labelled
`docs/goods_remap.csv` raw-good rules
on locations controlled in the AD 1 ownership ledger. The generated override is
version-pinned to the local game base and must be regenerated after a game-map
patch. This is preferable to an incomplete partial map file whose replacement
semantics could discard unrelated location data.

## 2026-07-19 — Markets are generated from explicit ancient hub records

The M5 market manager is generated from `docs/m5/markets.csv`, not inferred
from country capitals or a later-period vanilla market list. The generator
rejects duplicate hubs, unknown locations, missing citations, and invalid
confidence labels. This preserves an auditable distinction between a historical
trade hub and the installed location key used to represent it.

## 2026-07-19 — Installed culture templates are a geographic index only

The M4 audit records the 680 installed template cultures present in controlled
AD 1 locations alongside the profile that the current historical roster would
assign there. It is deliberately an inventory, not an automatic translation:
a modern or later-period template key may cross multiple ancient cultural
zones. Any many-to-one or one-to-many remap must therefore enter a separate,
source-labelled table before it changes a pop.

## 2026-07-19 — Conservative dynamic-name v1

The first dynamic-name layer is limited to secure, coordinate-reviewed capital
anchors and uses the period historical-capital label already recorded in the
roster. It emits both `location.<M4 language>` and `location.<M4 dialect>`
keys because cultures use the engine-required dialect form while installed
location-name files demonstrate root-language keys. This is a verified-safe
compatibility layer; it deliberately does not rename broad geographical
proxies, for which a plausible label would be a historical assertion.

## 2026-07-19 — Population allocation is target-led and geographically weighted

The M4 population generator makes section 12.4's documented macro totals its
authoritative input. It uses the installed vanilla pop file only to distribute
each regional target among existing location geometry, with a small non-zero
floor so every controlled land location receives a base population. The source
tables, not the later-period vanilla snapshot, remain the historical claim.
This gives the game a complete working start state while making each regional
allocation inspectable and replaceable as local research improves.

## 2026-07-19 — Resumable smoke completion

`smoketest.py --resume` performs the normal readiness, termination, and
error-log diff stages against a game launched by the same driver. It exists for
automation hosts that interrupt a single long cold-start command; normal
`make smoke` remains the default path. The driver also treats a stale saved
process ID as already stopped, rather than failing a later autonomous run.

## 2026-07-19 — M4 profiles are data, not presentation fallbacks

M3's `Profile` records remain the source of map colors and placeholder flag
colors only. M4 introduces separate, source-labelled regional and tag profile
tables; the generator combines the two at render time. This prevents a visual
fallback from becoming an unreviewed historical assertion. It rejects a missing
roster region, an unknown tag override, or an M4 symbol that has not been
generated, rather than falling back to a vanilla culture or faith.

## 2026-07-19 — Bounded menu-ready smoke heuristic

The game-driver smoke check now requires a visible game window, 30 seconds
from launch, and 15 seconds without debug-log growth. The previous 45+20
second floor could not complete within the available 60-second automation
command slice even after the game had reached the menu. The new threshold was
proven against a full normal `make smoke`; it remains a menu-load check, not a
substitute for milestone observer verification.

## 2026-07-19 — Roster before setup generation

M3 starts from a CSV roster with explicit source, confidence, historical
capital, and verified-map-capital fields. A capital is `TBD` rather than guessed
until it is matched to the current game's extracted location keys. The build
validator rejects tag collisions and any asserted-but-invalid map key; this
keeps scholarly uncertainty visible while allowing the world-mapping pipeline
to proceed region by region.

## 2026-07-19 — Collision-free engine tags

The installed country database already defines 67 of the roster's natural
three-letter codes. `docs/world_1ad/tag_map.json` preserves a natural code as
the design identifier where possible and assigns a deterministic `X..` engine
tag only for a collision. This avoids unverified duplicate-key precedence while
keeping historical sources and later event writing readable through the map.

## 2026-07-19 — Country-key namespace and temporary definition profiles

Country tags are also localization keys. The M3 allocator therefore excludes
both three-character vanilla localization keys and engine-hash collisions, not
only country-definition tags. Build 24187685 proved `XAD` collides by hash with
`name_li3.mandarin_language`, so it is explicitly reserved and every generated
tag is smoke-tested before acceptance. The initial 133 country definitions use
only verified current culture/religion keys to keep M3 parsable; they are
explicitly temporary database defaults, not a claim about AD 1 map-mode
culture or faith. M4 replaces them with the sourced ancient trees.

The country database independently rejects duplicate display names and adds
rank titles itself. The roster remains historically precise, while its M3 UI
labels use `Roman Commonwealth` and `Parthia` rather than duplicate/compound
`Empire` forms. This is a technical display adaptation, not a historical
renaming.

## 2026-07-19 — Exact M3 start-manager mirror

The installed build has 25 `main_menu/setup/start` manager files. Their
empty, correctly named manager roots load with zero new errors, whereas leaving
any filename unmirrored would retain its additive 1337 state. The generated M3
mirror tracks that installed inventory during `make validate`, uses the
installed no-BOM convention, and is the safe base that later M3 generators
extend with country, ownership, pop, character, market, and other AD 1 state.

## 2026-07-19 — Verified-capital political slice

The first active AD 1 country manager assigns ownership only where a roster
capital directly matches a local EU5 location key: 57 entries at this point.
Each owns/controls its capital under a current-engine generic template and a
random ruler, both explicitly temporary until M6 supplies sourced state forms
and characters. This creates a real, smoke-clean map surface without inventing
territory from fuzzy city-name matches; all remaining ownership stays absent
until its source mapping exists.

## 2026-07-19 — Pleiades-to-raster capital method

The official Pleiades CSV snapshot is cached off-repo on G: and its candidate
records are committed with permanent Pleiades paths. EU5 location centroids are
extracted from the installed RGB raster. The candidate projector fits a
two-dimensional affine model to globally distributed known sites, then applies
nearby anchor residual correction. It is a discovery and review aid only:
every promoted local key remains an explicit sourced `polities.csv` edit, and
the 2D model is never treated as evidence on its own.

## 2026-07-19 — Hierarchy-resolved ownership, not implicit borders

M3 territory rows name installed EU5 geography keys with a historical source,
confidence, and scope note. `ownership_map.py` recursively expands them from
the harvested map hierarchy, filters broad rows to locations owned in the
installed vanilla setup, rejects inter-tag overlap, and emits a checked engine
location list. Exact site rows may use a currently unowned archaeological
location only after real-game smoke. This keeps the large Roman, Parthian, and
Han surfaces reproducible while refusing to infer unfinished frontier,
subordinate, and SoP boundaries.

The first run exposed three same-name traps in the current map: `edessa` is
Macedonian Edessa, `susa` is Italian Susa, and `khwar` is in the Rey area.
Osroene now uses Urfa and Elymais Shush after Pleiades coordinate review;
Khwarazm is intentionally reset to `TBD`. Name equality alone is therefore no
longer considered a capital verification method.

## 2026-07-19 — M3 subject-contract adapter

The first 20 sourced AD 1 dependencies are generated into the exact
`12_diplomacy.txt` start-manager mirror. They use the installed `vassal` and
`tributary` types because those keys and `dependency` syntax are locally
verified and smoke-clean. This is deliberately an M3 political-map adapter:
M9 replaces it with the plan's own client-kingdom, satrapy, tributary, and
foederati contracts rather than treating medieval UI labels as historical
descriptions.

## 2026-07-19 — Cross-check imperial-core and frontier assignments

The ownership resolver rejects a location before it can belong to two active
AD 1 tags. Its first frontier expansion found the initially selected Xianbei
and Wuhuan anchors inside the broad Han geography frame; they were moved to
nearby non-Han local keys before generation. This is an intentional guardrail:
a visual capital proxy must not silently create a contradictory sovereignty
claim at an imperial frontier.

## 2026-07-19 — Complete capital anchors are not a completed political map

M3 now requires every roster tag to have one unique, engine-valid local-map
capital anchor. The generated capital-control seed makes all 133 polities
visible and lets the ownership resolver reject overlap before the game starts.
That invariant is deliberately narrower than historical territorial completion:
area ownership and SoP coverage remain separately sourced M3 work, and M4 will
replace the temporary generic-country handling of societies of peoples with
their population-based representation.

## 2026-07-19 — Foreground-only game screenshots

The autonomous driver moves the EU5 window to a fixed game rectangle and refuses
to capture unless that process owns the foreground window. It uses the Windows
foreground attachment sequence before taking the image. This prevents a game
test artifact from including another application when focus changes during
launcher handoff; the clean menu checkpoint is retained as M3 driver evidence.

## 2026-07-19 — Append-only collision tag allocation

The tag-map generator first reserves all valid engine tags from the last
committed map, then allocates only genuinely new collisions. This preserves
existing internal tags when historical roster rows are inserted and avoids
needless save/setup churn. It still rejects a previously allocated tag if the
current game build now reserves it through a vanilla or localization namespace.

## 2026-07-19 — Coarse area rows require explicit uncertainty

For the Indian Ocean territorial pass, a whole installed geography area is used
only when it has a direct regional association in the plan's AD 1 synthesis.
Every such frame is marked `contested` in `ownership_areas.csv`: the installed
area geometry is a reviewable M3 adapter, not evidence that a modern/local map
edge is an ancient administrative border. Exact capitals, source labels, and
the resolver's no-overlap invariant remain stricter than these provisional
regional extents.

## 2026-07-19 — Five campaign ages with a compatibility sentinel

The campaign has five real ages: Principate, High Empires, Crisis, Dominate,
and Migrations. The installed engine validates references to all six vanilla
age keys while loading unrelated vanilla databases. Once the M3 mirror is
ready, the generated M2 file will therefore retain `age_6_revolutions` as an
unreachable year-477 compatibility sentinel; it is not a campaign age and does
not make any date after 4 September 476 playable.

## 2026-07-19 — M2 deferment until setup replacement

The year-one calendar itself works, including a real save/reload. Enabling it
against the retained vanilla snapshot yields 868 ruler-term validation errors.
Because M3 already requires exact replacement of every setup manager and AD 1
ruler histories, the generated M2 layer is deferred rather than normalizing or
accepting those errors. This preserves the zero-new-error invariant.

## 2026-07-19 — M2 reactivated on the clean M3 mirror

Once all 25 start-manager files were exact-name mirrored, the M2 generator was
reactivated. A fresh smoke has zero new errors, and a driver-created AD 1
observer save reloads at `08:00, 1 January, 1` with the Age of Principate
header. M2 is therefore complete and tagged; the intentionally blank map in
its final report is the separate, visible M3 ownership backlog.

## 2026-07-19 — Metadata compatibility and thumbnail placement

The in-game version label is `1.3.1.1`, but the metadata comparator rejects
that form and accepts `1.3.11`. ANTIQVITAS therefore pins
`supported_game_version` to `1.3.11`, with the successful M1 menu smoke as
runtime evidence. The manifest declares `picture = "thumbnail.png"`; the same
512x512, sub-1-MB PNG is deliberately present both at the mod root (the
observed Workshop convention) and inside `.metadata` (the plan's required
placement). The linter enforces both copies while the engine convention remains
underdocumented.

## 2026-07-19 — Repository location

The repository root is `G:\antiqvitas`, on the same drive as the verified EU5
installation. This follows §2 and keeps generated content away from the nearly
full C: drive.

## 2026-07-19 — Build command compatibility

The host has no GNU Make. A repo-local `make.cmd` exposes the required
`make validate`, `make smoke`, and `make full` interface while the portable
`Makefile` documents equivalent targets.

## 2026-07-19 — User-directory relocation

The local executable contains the `user_dir` option and an actual launch proved
that `--user_dir=G:\antiqvitas_user_data` relocates logs and account state.
ANTIQVITAS uses that option plus
`G:\antiqvitas_user_data\mod\antiqvitas` as a junction to the repo. This leaves
only Steam itself on C: and prevents the project's logs, saves, screenshots, and
mod content from consuming the system drive.

## 2026-07-19 — Launcher format adaptation

Build 24187685 uses `USER_DIR\playsets.json`; no `launcher-v2.sqlite` is present.
`tools/enable_mod.py` therefore performs backed-up, atomic JSON mutations with a
read-back integrity check. It recognizes SQLite only to inspect and refuse an
unknown schema safely.

## 2026-07-19 — Baseline isolation

EU5 reads metadata from every directory below `USER_DIR\mod` even when its
playset entry is disabled. The vanilla M0 baseline was therefore captured with
the ANTIQVITAS junction temporarily absent. The link tool recreates it
idempotently once valid M1 metadata exists.

## 2026-07-19 — Current-script verification with documented fallback

The installed `script_docs` exporter did not return after two instrumented
attempts (see `BLOCKERS.md`). The project uses the community dump from
GlossMod/EU5-Modding-Mcp commit
`90790df9478a61035a2099c115b21ba7f04c3763` only as an index. Because that dump
is dated 2025-11-07, current-build behavior is accepted only when a key is also
present in local 1.3.1.1 scripts and a real-game smoke test is green.

## 2026-07-19 - Exhaustive ownership needs a residual ledger

Named historical area and direct-location rows are resolved first. A separate,
ordered `ownership_residual_areas.csv` then assigns only locations still
unclaimed by those rows, and `intentional_empty_areas.csv` is the sole allowed
exception. `territory_coverage.py` fails the build unless every locally
ownable location is either assigned or in that explicit exception list. This
keeps an exhaustive M3 political surface reproducible without allowing a broad
SoP fallback to overwrite a reviewed state/client claim.

The 41 exceptions are the plan-required empty Iceland, Madagascar, and
post-period eastern-Polynesian locations. The residual frames are technical
geometry adapters for named societies of peoples; M4 replaces their temporary
country-shaped representation with population-based societies.

## 2026-07-19 - M4 definitions are additive and runtime-proven

M4 begins with additive files rather than broad directory replacement, so
untouched vanilla references remain parsable while the ancient database grows.
The initial real smoke established four build-specific contracts: cultures need
at least one valid graphical tag, culture/religion colors must be unique named
colors, a culture `language` field expects a nested dialect rather than a
language root, and every religion needs a nonempty definition modifier.

The generator therefore supplies verified graphical fallback tags, deterministic
unique named colors, complete shared-namespace localization, and a minimal
valid religion modifier. It deliberately leaves language binding until M4 can
generate historically sourced dialect/name pools, rather than attaching a
modern or unrelated name list just to make a parser pass.

## 2026-07-19 - Language families are a fixed engine registry

The engine rejects invented language-family keys. M4 therefore maps each new
language root to the closest installed technical family while its own culture
group and source record remain the historical authority. This adapter is not a
claim that, for example, the UI's nearest available family resolves every
ancient language classification. The generated dialect itself, its source
name-pool, and the culture grouping remain namespaced ANTIQVITAS data.

The engine also treats a bare name-pool token as a localization key. The
generator converts every source token to a unique `antq_name_*` key and mirrors
its display text into every supported localization file; raw name strings are
therefore forbidden in generated language scripts.

## 2026-07-19 - Han minority regency follows native shape but is not accepted

The installed start file consistently represents a minority without a
simultaneous `ruler`: it places the nominal monarch in `heir`, then supplies a
regency, active regent, and dates. The M6 generator now emits that exact order
and passes dates through `AntqDate`. A fresh AD 1 inspector still creates Han
Zhang rather than resolving Emperor Ping and Wang Mang, with no new log line.
This native-shape adapter is consequently retained as the least speculative
script form, not treated as proof of runtime correctness. `BLOCKERS.md`
records both attempts and keeps the M6 milestone unaccepted.

## 2026-07-19 - Unknown biography dates remain blank despite the age-zero UI

The Parthian inspector confirms that this EU5 build displays a character with
no `birth_date` as age 0. Several current AD 1 figures, including Phraates V,
have no defensible birth day or year in the project source set. The data keeps
those fields blank rather than inserting a plausible-looking value just to
change the UI. This is a source-integrity choice; the later prosopography pass
may only replace it with an evidence-qualified date or a locally verified
display contract.

## 2026-07-19 - Han court dynasties use natal-clan identity

The engine's dynasty field is a character-family label, not the dynasty of the
state the character serves. Grand Empress Dowager Wang and Wang Mang therefore
use a Wang-clan label rather than the Han imperial House of Liu. The label makes
the documented consort-kin distinction visible while neither inventing parent
links nor attempting a complete Wang genealogy. Wang Shun uses the same narrow
label as a court figure only; no government field depends on it.

## 2026-07-19 - A hosted court character keeps the host's start context

The M6 character tag identifies the campaign-start court context that makes a
character visible to the engine, not an assertion of their ethnicity or natal
dynasty. Vonones therefore uses the Roman start context while retaining his
Parthian culture, Arsacid religion, and Arsacid dynasty. This narrow mapping
records his documented residence in Rome without pre-scripting the later
Parthian or Armenian reigns that belong to M10.

## 2026-07-19 - Thin court identities do not invent kinship

When a directly attested court figure needs an engine dynasty but the source
route does not establish a usable genealogy, M6 assigns a person-specific
court-identity label anchored at the current court. Shared surnames may share a
label only when the note says that it is not a kinship assertion. This keeps
the character database structurally valid without folding unrelated officials
into a fabricated royal house.

## 2026-07-19 - Reuse validated estate buckets for Roman civic orders

The current EU5 estate registry is global and has no safe Rome-only attachment
surface. M6 therefore represents the equestrian order through a distinct
`nobles_estate` privilege and public priestly colleges through a distinct
`clergy_estate` privilege, using only locally harvested power, satisfaction,
and cabinet-efficiency modifiers. This makes the plan's estate adapters visible
without adding a speculative worldwide estate type or treating either Roman
group as literally medieval nobility or Christian clergy.

## 2026-07-19 - Zhongshan family context uses a documented local proxy

EU5 character dynasties require an installed location anchor even when a
source identifies only a historical region. For Emperor Ping's maternal Wei
family, M6 uses `anxi_dingzhou`: the project source route connects Han Lunu,
the Zhongshan centre, to the Dingzhou area. The character tag remains HAN and
the records have no implied Chang'an residence. This is an engine anchor for a
bounded family context, not an ownership, border, capital, or exact-residence
assertion.

## 2026-07-19 - M7 gates vanilla military unlocks by exact-name source-derived overrides

The installed build distributes unit and levy unlocks through 48 advance files,
not only the generic army and ship files. M7 therefore generates a UTF-8-BOM
exact-name override for every local file containing `unlock_unit` or
`unlock_levy`, retaining all non-unit statements verbatim while stripping those
two statements. `tools/m7_war.py --check` regenerates against the pinned local
install and fails stale if its source changes. This is the narrowest verified
way to prevent gunpowder and oceanic unit progression before M8 replaces the
complete advance tree; it does not modify the game installation.

## 2026-07-19 - M7 force seeds use locally accepted unit-manager shapes

The local unit reference establishes `army`, `navy`, and `sub_units` as the
unit-manager vocabulary, while the generated start manager retains one
country/location per named force. The source ledgers permit only M7 units that
are available to their own bounded country tag. The starting strengths are
technical test seeds rather than historical orders of battle; the runtime
observer probe remains the acceptance test for their behavior.

## 2026-07-19 - M8 replaces advances and institutions by installed filename manifest

The local build distributes advances and institutions over many additive files.
M8 therefore generates UTF-8-BOM exact-name replacements for every installed
definition file, then puts the complete namespaced ancient tree and institution
set in its own files. Vanilla advance keys remain as permanently unavailable
definitions (with unit/levy unlocks stripped), while vanilla institutions
remain defined with `can_spawn = { always = no }`; this preserves hardcoded
event and trigger references without leaving their gameplay content reachable.
The generator re-reads the pinned local manifest and fails on a stale or
unexpected file; it never changes the game install. M7 detects the M8 tree and
yields ownership of its temporary 48-file unlock-filter layer.

The installed `victory_card` and `unique` age fields are the verified objective
and ability mechanisms. M8 uses those fields rather than inventing unsupported
syntax. It reuses five locally verified vanilla advance icon keys only as an
interim UI adapter; the plan's generated per-advance icon batch remains M11
visual work.

Smoke testing further established that the engine validates an advance's
`requires` only within the same age. M8 therefore uses five complete ten-step
strands inside each age rather than cross-age prerequisites; the age transition
is the historical gate between their thematic continuations.

## 2026-07-20 - M10 fourth-century renderer uses generated transition ledgers

`tools/m10_fourth_century.py` owns all fourteen AD 300-399 currents and emits
dates only through `AntqDate`. Its Hunnic and Roman-partition adapters produce
reviewable CSV ledgers alongside game content. `HNS` and `ERO` are checked
dynamic identifiers rather than reused vanilla/runtime tags; `WRE` is a
checked cosmetic identity. The 395 event derives its actual activation date
from the shared `age_migrations` timeline row, while retaining the plan's 394
Frigidus-to-396 current window. This makes the source-qualified territorial
approximation explicit and preserves the event's no-hardcoded-date invariant.

## 2026-07-20 - Final M10 current layer resolves dynamic successor recipients

`tools/m10_final_century.py` owns the thirteen AD 400-476 ledger rows. It
uses the established situation `content_trigger` contract (not the
disaster-only country scope) and names `HNS`, `ERO`, and post-429 `VND` as
runtime recipients only after their prior historical-current creators run.
Visigoth and Vandal releases use collision-checked dynamic tags and explicit
local lists. The campaign finale derives its 476 activation window and exact
end from `tools/dates.py`; no standalone scripted calendar literal is used.

## 2026-07-20 - M11 actions require a registered message type, not only localization

The installed generic-action contract accepts player-only `owncountry` actions
with tag scopes, gold gates, cooldowns, and ordinary country effects. It also
registers a `PERFORM_<action>_ACTION` message at database load. Mirroring the
message-localization keys alone is insufficient, and the current build does
not load a separate additive `main_menu/gui` message-type file. Future M11
action work must begin with a one-action pilot based on an exact-name copy of
the locally installed `messagetypes.txt`; retain every vanilla type and record
the source hash before expanding the overlay. This is a compatibility decision,
not an assertion about any historical institution.

## 2026-07-20 - CoA standards replace the one generated placeholder file

The CoA generator now writes `antq_00_coa_standards.txt` and the superseded
placeholder file is removed. This avoids duplicate country keys and never
relies on alphabetical file order. Direct CoA reviews win over the regional
theme catalog; both must resolve to local colored-emblem textures. This is a
technical rendering decision, with the historical non-reconstruction boundary
recorded in `ASSUMPTIONS.md`.

## 2026-07-20 - Direct-key UI icons supersede default fallbacks

The installed GUI resolves religion and institution art with `GetReligionIcon`
and `GetInstitutionIcon`; the installed asset trees establish direct
definition-key filenames, not a field in the script definitions. M4's 37
religions and M8's nine institutions had no key-matched textures and fell back
to `_default.dds`. M11 now provides every direct-key file. Religion assets are
exact local aliases so their format, alpha, and filename behavior remain
engine-native; M8's institution assets are generated and BC7-encoded to the
same 128x128 sRGBA contract. `tools/m11_common_icons.py` is the ownership and
patch-drift guard. This is a renderer decision, not a claim that a shared motif
defines a faith's historical identity.

## 2026-07-20 - Complete advance icon coverage at the reviewed shared tier

M8's five fifty-entry age groups use the master plan's permitted shared-icon
fallback tier. The M11 generated group textures now cover all 250 entries and
the validator locks each group to exactly fifty bindings. This completes the
advance icon surface without manufacturing a separate artifact-like visual
claim for every abstract advance key; unique art remains warranted only when a
screen exposes a direct, historically meaningful subject.

## 2026-07-20 - Enforce English-first localization rather than partial translation

The plan makes English the only authored localization and requires other
clients to see that text. M11 therefore treats every non-English file as an
exact source mirror with only its required header changed, and validates all
fifteen source-file names, UTF-8 BOMs, entries, and values across the ten
supported folders. This is clearer and safer than accumulating incomplete or
machine-translated strings, and prevents raw-key regressions without extending
the project's translation scope.

## 2026-07-20 - Active ancient CBs use bounded installed-contract AI scores

The local casus-belli contract uses an additive `ai_will_do` block, with the
vanilla attack-threat CB setting its base score to 10. M9's uniform
`value = -1` sentinel was appropriate only for the three deliberately hidden
future-unification CBs; on the seven visible CBs it prevented AI selection
entirely. M12 therefore uses bounded 4--16 scores near that local baseline,
leaving each CB's historical visibility and eligibility restrictions as the
primary safeguard against universal aggression. The dormant Chinese, Sasanid,
and Gupta definitions retain their hidden and disabled state. This is a
technical AI-contract correction; the observer run remains the authority for
runtime frequency tuning.

## 2026-07-20 - M11 messages use a pinned exact-name overlay

The installed message registry does not load additive sibling files, but the
generic-action database requires a registered `PERFORM_<action>_ACTION` type.
After a one-action exact-name pilot was menu-smoke-clean, M11 copies the
configured build's exact `messagetypes.txt` bytes and appends the 40 validated
action entries. The renderer pins the local build, SHA-256, file-ending
contract, and 1,348-entry inventory, so a game update fails validation rather
than silently replacing changed vanilla GUI data. This is a technical
compatibility overlay; its decision content remains bounded by the existing
source ledger and player-only action contract.

## 2026-07-20 - M12 documentation distinguishes static proof from runtime proof

The ship documentation records generated-contract validation and enabled-menu
smokes as static/load evidence, not as proof of long-run AI, economy, disease,
or finale behaviour. The AD 476 event is therefore documented as a checked
terminal contract while its screenshot acceptance remains open. The surface
inventory similarly marks retained vanilla generic missions and rule/hint
surfaces as open until they are consciously retained or disabled through a
local-contract test. This prevents release-facing documents from converting a
technical load result into a historical or gameplay claim.

## 2026-07-20 - Disable vanilla generic missions by exact-name visibility gates

The installed generic mission packs explicitly depend on vanilla Discovery,
colonial, Renaissance, Reformation, banking, paper-guild, and institution
surfaces. Rather than selectively reinterpret their rewards or leave hidden
anachronisms reachable, M12 mirrors all eleven exact source filenames and adds
`always = no` only to each top-level visibility trigger. The definitions and
keys remain loaded for references, while `tools/m12_disable_missions.py`
regenerates against the installed inventory and fails patch drift. Future
ancient missions must be independently source-led rather than reviving a
vanilla generic pack.

## 2026-07-22 - A direct parent link is not a start-loader workaround

The installed character format accepts `mother`, and the source ledger directly
identifies Wei Ji as Emperor Ping's mother. A clean, parent-before-child
fixture nevertheless left both named heirs and Wang Mang invalid during start
load. The relationship fields and generated output were therefore reverted.
Keep the bounded historical records, but do not add engine family links merely
to satisfy the Han minority-regency loader until a local fixture identifies the
actual contract.

## 2026-07-22 - Defer AD 1 market-manager seeds, retain the historic hub ledger

The installed `market_manager` contract parses and initializes in the AD 1
setup, but it asserts `Getting relation with itself` at the first monthly pulse.
An empty-manager Observer control reached 14 February AD 1 without that
assertion; a Massawa-only fixture reproduced it on 1 February; and the full
build still reproduced it after Massawa alone was deferred. This is therefore a
runtime compatibility decision, not evidence against Adulis or any other
historical exchange centre.

`docs/m5/markets.csv` retains all 42 source-led hubs. Their 42 town/city,
building, harbor, RGO, road, and localization records remain generated. The
start mirror deliberately emits no `add_market` records, allowing the
installed game's automatic market initializer to construct runtime markets
without the invalid pre-game relation state. Any future attempt to restore an
explicit seed must first demonstrate a zero-assertion monthly Observer run.

## 2026-07-22 - Use the game-exposed DX12 renderer for the long Observer retry

The installed Graphics screen exposes exactly `Vulkan` and `DX12`; the project
had only exercised Vulkan profiles. The selected native `DX12` setting persisted
to the relocated user directory and its startup log confirmed
`gfx_dx12_master_context` on the local NVIDIA GeForce RTX 3080. This was a
material renderer change, not an unsupported launch switch or a game-install
edit.

DX12 reached a clean AD 1 Observer map, 18:00 on 13 January, and a live 14:00
3 March checkpoint before exiting at 07:05:19 through the same
`ffxFsr2ResourceIsNull` / `NVSDK_NGX_D3D12_Shutdown1` C0000005 family as
Vulkan. Retain the native renderer selection evidence, but do not repeat either
backend unchanged; the result is recorded in
`docs/playtests/M12_DX12_RENDERER_20260722.md`.

## 2026-07-22 - Recover Observer play through the normal autosave menu route

The installed console reference documents save/load commands, but the normal
non-debug renderer exposes no usable console surface and no save-file parser
is a safe substitute for an engine load. The locally exercised UI route is
therefore authoritative: Continue -> Continue as Observer -> Observe -> Start
Observing the game. `gamedriver.py` waits for the local `MainMenu->Game`
state-4 and cached-data-completion log records before it clicks the map, records
the three newest autosaves before and after every cycle, and requires the live
Observer pause banner before it starts simulation.

This decision deliberately accepts a bounded UI retry after a failed map-input
attempt. The final 22 July probe established that a renderer restart can return
to the latest checkpoint autonomously, so the FSR/NGX exit is no longer by
itself grounds to abandon the long campaign. It is not evidence that a
multi-century chronology is clean; the campaign must still demonstrate actual
renderer-exit recovery and decade capture coverage.

## 2026-07-22 - Rome uses named special buildings, not global medieval labels

The installed game has valid reusable civic, trade, cultural, religious, and
infrastructure mechanics but its generic labels would make an AD 1 Rome read
as a later settlement. M5 therefore introduces sixteen one-level,
`is_special = yes` ANTIQVITAS building types. Each uses only category,
population, employment, build-time, modifier, good, and maintenance contracts
read from the installed `common/building_types` files; they are not normal
construction replacements or a new 3D-model system.

`tools/m5_roman_buildings.py` makes the historical ledger authoritative and
requires one generated localization and one 128px DDS file per building. The
first actual smoke found that the installed `common/building_types` folder
requires UTF-8 BOM and that unique production-method keys need localization;
the generator locks both requirements in. This is a presentation and mechanics
decision, not a claim of a precisely mapped monument for every function.

## 2026-07-22 - Navalia Romae is a conservative naval-supply special

Digital Augustan Rome securely places the Navalia in the Republican Tiberine
arsenal tradition, but its precise Augustan arrangement remains debated. M5
therefore adds one city-scale, named naval-supply special rather than a fleet
roster, harbour reconstruction, dockyard chain, or shipbuilding output model.
The local installed `naval_category` and `dock_employment` contracts support
the limited sailors/repair effect and the historically legible tar, naval
supplies, tools, lumber, and cloth maintenance basket.

The existing M7 frontier stockades remain deliberately generic. In particular,
Castra Praetoria is excluded: the reviewed local historical source dates its
construction under Tiberius in AD 21-23, after the start. This prefers an
honest bounded proxy to an attractive but anachronistic named building.

## 2026-07-22 - Classis Ravennatis uses Ravenna as a bounded Classe proxy

The Italian Ministry of Culture's Classe record and Ravenna Turismo's
archaeological-port record independently support Augustus' Ravenna military
harbour in 27 BC. The installed map has Ravenna but not a separate Classe
location, so M5 renders a named `Classis Ravennatis` special at Ravenna and
records the near-site relation in both ledgers.

Its naval/dock contract is intentionally smaller than a fleet reconstruction:
limited local sailors and repair speed, with tar, naval supplies, tools, lumber,
and cloth maintenance. The model does not encode the source's ship count,
specific vessels, coastal jurisdiction, harbour geometry, or a naval order of
battle. A direct dedicated DDS ensures that this military-supply layer is not a
generic dock icon.

## 2026-07-22 - Castrum Mogontiacum receives a low Augustan camp contract

Mainz's city history identifies the Drusus-era legionary camp at the Main
confluence and its 13/12 BC foundation. The new special is therefore a named
frontier exception to the generic M7 stockade layer, not evidence for naming
every fort. The installed `defense_category`, `stockade_employment`,
`small_fort_building`, and one-level raw `fort_level` contracts were inspected
locally and generated only for this defense building.

The definition deliberately copies the stockade's non-propagating low-fort
behavior, then uses substantially smaller garrison/unrest effects. This models
a timber-and-earth camp without importing later stone fortification, an AD 1
unit roster, a fixed legion count, or a complete German frontier map.

## 2026-07-23 - Augusta Raurica camp uses a bounded Basel near-site proxy

The official Augusta Raurica record supplies an unusually narrow second
frontier exception: its post-15-BC Augustan refoundation includes a wood-built
military camp at Kaiseraugst. The installed map has no Augst or Kaiseraugst
location, but `basel` is an AD 1 Roman-controlled location. The named-building
ledger therefore permits that one reviewed near-site, using exactly the same
low non-propagating stockade contract already proven for Mogontiacum.

The special's display name is deliberately functional rather than an asserted
recovered Roman fort title. It adds no legion identifier, garrison total, stone
fortress, limes line, or camp plan. `basel` itself is not dynamically renamed:
the city-point proxy is sufficient for a bounded building seed but is not a
license to replace the distinct historical place name with Augusta Raurica.

## 2026-07-22 - M8 uses a checked per-advance art migration

The former five age-group advance illustrations remain available only as a
transitional fallback. The user-facing final requirement is one dedicated
illustration per advance, but generating all 250 before a single engine check
would conceal broken binding and DDS assumptions. M8 therefore reads a
completed-row ledger and swaps only that advance's icon identifier; its M11
validator requires the real known advance/age, source PNG, 256px master, BC7
DDS, one tree use, and adjusted group count. This is a technical migration
decision, not a claim that an icon's broad visual motif reconstructs a
historical object or practice.

## 2026-07-22 - Campus Martius is modeled as three bounded civic functions

The Pantheum, Saepta, and Diribitorium are each secure pre-AD 1 monuments, but
the installed map supplies only one Rome location and the engine has no
period-specific election or cult-system primitive. M5 therefore uses three
one-level specials with the existing religious/government building contracts:
modest unrest/literacy context for the Pantheum, modest control/tradition for
the Saepta, and modest control for the Diribitorium. Their upkeeps create
small demand for actual materials and services rather than setting economic
output, vote totals, a cult calendar, or administrative staffing.

## 2026-07-22 - Dynamic names require an exact archaeological-city match

The Italian expansion retains only Pleiades points whose reviewed projection
lands directly on the named installed location. Eleven Cisalpine/central and
Sardinian city forms met that bar. Near but non-identical candidates are not
silently promoted: Ferrara is not relabeled Spina, and Palermo is not relabeled
from an unmatched Panormus record. The M4 culture-language adapter remains an
engine localization route, not a claim that every resident used the displayed
Latin form in daily speech.

## 2026-07-22 - Direct icon review rejects anachronistic visual hardware

The direct-art pipeline is an accuracy gate, not merely a texture-existence
check. Two Provincial Census drafts passed their file-format constraints but
showed notebook-like metal binder loops, so neither entered the repository or
the M8 tree. Public Granaries, a separate non-reconstructive subject, was
accepted instead. A failed individual art subject must not stall independent
icons or reduce the validator's source/master/DDS requirements.

## 2026-07-22 - Palatine temple and library retain distinct engine contracts

The direct sources establish a temple and a bilingual library as related
Palatine Augustan structures, but not as a single undifferentiated palace
building. M5 therefore renders a religious Temple of Apollo with modest cult
inputs separately from a cultural Palatine Library with modest tradition and
control inputs. The local generic `books` good represents scroll collections;
it is not relabelled or treated as evidence for a codex collection. This keeps
both game-facing roles legible without inventing an unsupported palace,
library-room, rite, staff, or inventory system.

## 2026-07-22 - Curia Iulia and Porticus Octaviae are separate civic spaces

The Curia Iulia and Porticus Octaviae sources describe materially different
AD 1 civic environments, so they receive separate one-level specials rather
than one generic "Roman civic complex." Curia's government contract carries
modest control and records inputs; the portico's cultural contract carries
only modest tradition and public-order context. The debated Chalcidicum,
Porticus sponsor, internal room layout, individual temples, and any precise
Senate procedure remain outside both effects. This preserves player-facing
distinction without claiming an engine model of Roman constitutional practice.

## 2026-07-22 - Emporium demand represents handling, not a Roman trade ledger

The installed trade-building contract can represent local merchant capacity
and a building's upkeep demand, but it cannot prove a precise ancient cargo
flow or solve M5's separate market-transfer blocker. Porticus Aemilia therefore
adds modest demand for historically relevant staple, container, and handling
goods without producing, moving, or quantifying them. Aqua Alsietina likewise
uses only small infrastructure modifiers. Both names/configurations remain
explicitly contested where the sources require it, and neither substitutes for
a tested market relation or a full urban water-distribution simulation.

## 2026-07-22 - Augustan public spaces are not automated spectacles or clocks

The existing cultural-building contract can convey public-space context, but
cannot model a naval performance or calendar system faithfully. Naumachia and
Horologium therefore receive distinct, modest one-level cultural specials: the
former has maintenance for water-display infrastructure and the latter uses
copper solely as the engine proxy for bronze. Neither creates a battle, an
observer spectacle, a timekeeping effect, exact dimensions, or a reconstructed
Campus Martius plan.

## 2026-07-23 - M5 reusable families use native guild recipes

Seven families use exact installed guild recipes; all ten use scalable guild
contracts. This reaches 70% productive-family coverage without price guesses.

## 2026-07-23 - M5 second pass uses market-node expansion, not unique buildings

The 100 additional M5 placements reuse the ten reviewed direct-art families at
twenty existing historical city anchors. The start mirror requires every M5
building to be a market node or named historic site, so matching deferred
market and urban-node ledgers were added. No route edges, new building types,
or special-site claims were introduced. This keeps the economy scalable and
auditable while meeting the intended Roman-world density.

## 2026-07-23 - M5 building audit uses all placed M5/M7 entries

The user-facing production and scalability rules are enforced against every
regional seed, named M5 special, and M7 fort placement, not merely against
building definitions. Fifty additional productive, scalable Near Eastern
placements establish a conservative 64.2% productive and 80.1% scalable
whole-system result. `m5_building_audit.py` now makes these limits a permanent
`make validate` gate.

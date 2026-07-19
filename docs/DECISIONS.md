# Technical and Design Decisions

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

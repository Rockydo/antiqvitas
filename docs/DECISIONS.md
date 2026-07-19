# Technical and Design Decisions

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

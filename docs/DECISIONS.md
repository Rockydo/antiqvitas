# Technical and Design Decisions

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

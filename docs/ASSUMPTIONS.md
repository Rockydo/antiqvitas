# Historical Assumptions

## 2026-07-19 — Civic and hydraulic infrastructure proxies

Rome's Circus Maximus, Alexandria's Roman-period maritime role, the
Dujiangyan system serving the Chengdu plain, and Anuradhapura's early
reservoirs all predate the AD 1 start. They are represented as engine capacity
anchors, not as claims that the abstract building slots reproduce their exact
form or full footprint. Sources weighed: Italian cultural-heritage material on
the Circus Maximus (https://digitallibrary.cultura.gov.it/notizie/al-massimo-dello-splendore/);
Cambridge, “Alexandria and the sea in Hellenistic and Roman times”
(https://www.cambridge.org/core/books/abs/sea-in-history-the-ancient-world/alexandria-and-the-sea-in-hellenistic-and-roman-times/63CE49E6514F84622EB8A8FF848156B4);
UNESCO on Dujiangyan (https://whc.unesco.org/en/list/1001/) and Anuradhapura
reservoirs (https://whc.unesco.org/document/163318). [contested]

## 2026-07-19 — Five dedicated ancient trade goods

Alexandria is used as an Egyptian papyrus production-and-export proxy; Barca
stands for the Cyrenaican silphium district; Hit is a Mesopotamian natural
bitumen/naphtha proxy; Khotan is a Tarim jade anchor; and Medina is a deliberately
narrow Arabian dromedary-trade proxy. These are map-key approximations, not
claims that the named town alone produced the full regional output. The later
loss of silphium is reserved for M10 rather than being projected backward from
its imperial-era scarcity. Sources weighed: P12.1; Cambridge, “Silphium in
Ancient Art” (https://www.cambridge.org/core/journals/libyan-studies/article/abs/silphium-in-ancient-art/22D6AD4632F135C6630050CDD7D5426B);
University of Chicago OIP 147 (https://isac.uchicago.edu/sites/default/files/uploads/shared/docs/Publications/OIP/oip147.pdf);
University of Washington Silk Road sources on Khotan jade
(https://depts.washington.edu/silkroad/texts/hhshu/notes4.html) and caravan
animals (https://depts.washington.edu/silkroad/culture/animals/animals.html).
[contested]

## 2026-07-19 — Specialist production and civic-building anchors

The design bible explicitly identifies glassware at Sidon, Alexandria, and
Cologne; Han lacquerware export; terra sigillata; the Roman aqueduct/mint
layer; and the Alexandrian Pharos/library complex. These are represented with
the installed period-neutral `glass_guild`, `lacquerware_guild`,
`pottery_guild`, aqueduct, mint, library, and event-only Pharos slots. Sidon,
Cologne, and Chengdu are deliberately added as source-labelled market-town or
market-city anchors rather than inferred from the later vanilla urban map.

`pottery` is an engine proxy for the plan's fine-ceramic/terra-sigillata
production; it does not assert that every pottery output was terra sigillata.
Papyrus, silphium, jade as a distinct good, camels, and naphtha/bitumen are not
mislabelled as paper, gems, livestock, or wood tar here. They need dedicated
good definitions, localization, UI art, and in some cases date gating. Sources
weighed: P12.1; P12.3; P8.1–P8.3; P8.7; CAH-XI; BHR. [contested]

## 2026-07-19 — Development profile is not historical output data

EU5's scalar development cannot be equated with ancient population, wealth, or
urbanization without a separate calibrated study. The M5 profile therefore
uses only a zero base and relative road/town/city increments to make the
source-labelled settlement and transport layers legible to the engine. It does
not claim that one point equals a measurable ancient quantity; any later
location-specific calibration must cite an explicit historical dataset. Sources
weighed: P12.2; P12.4; ORB. [contested]

## 2026-07-19 — First-pass ancient road corridors

The 25 M5 road rows are high-level engine links between reviewed location
anchors, not surveyed reconstructions of every ancient mile. Roman legs are
sanity-checked against ORBIS's principal-route model; Persian, Han, Central
Asian, and Indian legs follow the named design-bible corridors and cited
regional syntheses. Some long or proxy legs remain contested until a
route-by-route itinerary/coordinate pass can split them into finer map links.
Sources weighed: ORB; P8.1–P8.8; BHR; CHG; CAH-XI; *Periplus*. [contested]

## 2026-07-19 — Named resource anchor proxies

Huelva represents the Rio Tinto district, Truro Cornwall tin, Sidon the Tyrian
purple-dye coast, Al Mukha Muza, and Massawa Adulis/Horn incense. These are
deliberately location-key proxies rather than claims of exact mine or workshop
coordinates. Khotan retains the installed `gems` good as an engine proxy for
jade; Paphos already carried the correct copper good and is retained as a
checked anchor. Sources weighed: P12.1; P8.1–P8.7; Pleiades; *Periplus*;
CAH-XI. [contested]

## 2026-07-19 — First-pass urban market ranks

The M5 city/town classifications identify an engine settlement tier for the
plan-listed market hubs; they are not population censuses or claims that every
proxy location had the exact later map footprint. Rome, Alexandria, Antioch,
the Han capitals, and other securely attested metropolitan centres use `city`;
Byzantium and the explicit growth-arc or proxy anchors use the more conservative
`town`. All geographic proxies retain their existing contested label in
`docs/m5/urban_nodes.csv`. Sources weighed: P8.1–P8.10; P12.2; P12.3; CAH-XI;
Pleiades; *Periplus*. [contested]

## 2026-07-19 — First-pass raw-material localization

The first RGO pass implements the explicit section 12.1 prohibitions and
production limits: coffee is absent, saltpeter is removed from the
pre-gunpowder layer, silk is retained only in China, incense only in the Arabia
and Africa proxy regions, pepper only in India, war elephants only in India and
Southeast Asia, tea only in broad China, sugar only in India and Southeast Asia,
and tobacco/cocoa/maize/potato remain in the Americas. `medicaments`,
`fiber_crops`, `fruit`, `millet`, `legumes`, `livestock`, and `salt` are
engine-valid technical replacements, not claims that each altered location
produced that specific ancient commodity. China is a deliberately coarse
temporary proxy for the plan's Sichuan-only tea qualification; the later
source-led RGO pass must narrow it. Sources weighed: P12.1; P8.3; P8.4; P8.5;
P8.6; P8.9; P8.10. [contested]

## 2026-07-19 — Market geographic proxies

Several plan-specified AD 1 hubs have no exact installed location key. Baghdad
stands for Seleucia-Ctesiphon, Tunis for Carthago, Taman for Panticapaeum, Homs
for Palmyra, Shendi for Meroe, Massawa for Adulis, Al Mukha for Muza, Khambat
for Barygaza, and regional map keys for several Southeast Asian and American
hubs. Each is labelled `contested` in `docs/m5/markets.csv`; it is a gameplay
market anchor, not a claim that the ancient city occupied the map key exactly.
Sources weighed: P8.1–P8.10; P12.2; Pleiades; *Periplus*; CAH-XI. [contested]

## 2026-07-19 — No automatic re-dating of installed culture keys

The installed location-template culture field is retained only as a geographic
index pending source review. Labels such as Turkish, Muscovite, or Greek cannot
be projected back to AD 1 without a region-specific historical decision; where
one label occurs across several M4 profiles, the audit records that ambiguity
rather than selecting one. Pleiades supports ancient toponyms and coordinates,
not a worldwide ethnic map. [contested]

## 2026-07-19 — Missing installed culture-template proxies

Antilebanon Mountains, Monterey Coast, and Dalai Nur Lake are controlled map
anchors with no installed location-template culture. Their source-labelled
exceptions retain the reviewed Batanean, Pacific-coastal, and Xianbei profiles
respectively for now. This is a technical map limitation, not evidence that a
mountain, coast, or lake had a homogeneous culture. Sources weighed: P8.1;
P8.8; P8.10; OCD; CAH-XI; Pleiades. [contested]

## 2026-07-19 — Dynamic capital names are a limited first pass

M4's first 61 dynamic names reproduce only the `historical_capital` labels of
secure capital-coordinate rows. Pleiades/CHGIS/Samguk Sagi coordinate review
establishes that the installed location is an acceptable anchor, not that every
surrounding location has an attested AD 1 name. Contested anchors and all SoP
geographic seeds retain their existing display name until a source-specific
toponym review can distinguish an attested name from a plausible invention.
Sources weighed: P8.1–P8.10; Pleiades; CHGIS; SAM. [contested]

## 2026-07-19 — AD 1 population distribution scaffold

`docs/m4/population_targets.csv` implements every numeric range in plan §12.4,
including the AD 2 Han census of 57,671 thousand. Its 34 regional allocations
sum exactly to the plan's 230,000-thousand world target. Where the plan gives
only a macro range, the regional split is a transparent working allocation,
not a claimed census: especially the 29.5 million residual Mediterranean,
West Asian, and Oceanian bucket and the distribution inside broad SoP frames.
The installed later-period pop density provides location weighting only; it is
not used as historical evidence. Sources weighed: P8.1–P8.10; P12.4; BHR;
CAH-XI. [contested]

## 2026-07-19 — M4 state-profile overrides

The 45 `docs/m4/tag_profiles.csv` overrides use the roster's relevant P8
section together with the culture and religion catalogues' P10/P11/CAH-XI/OCD
citations. They identify unusually well-attested state or court profiles such
as Roman Latin civic religion, Second Temple Jewish Herodian clients, Arsacid
Iranian courts, Tamilakam kingdoms, South Arabian kingdoms, and named American
societies. They do not assert that every inhabitant shared the listed profile.
All remaining countries inherit their explicitly labelled regional scaffold;
those broad defaults remain contested until location-level M4 population
allocation is researched and generated. [contested]

## 2026-07-19 - Residual societies-of-peoples coverage

The final M3 coverage ledger assigns otherwise-unclaimed inhabited land only to
an explicitly named residual people/society family (for example Caucasian,
Brittonic, Germanic, Siberian, Tibetan, Bedouin, Central/Gangetic Indian,
Southeast Asian, Berber, Mesoamerican, Andean, Melanesian, and Micronesian
societies). These are broad political/cultural frames, not claims of a unitary
state or exact border in AD 1, and are all treated as `contested` until M4 can
model their peoples at the population layer. Iceland, Madagascar, and eastern
Polynesia remain unpopulated as required by P8.9/P8.10. Sources weighed:
P8.1-P8.10; CAH-XI; regional archaeology syntheses. [contested]

## 2026-07-19 - M4 regional culture and faith frames

The first M4 catalog uses broad regional cultures and religious communities as
a transparent foundation, not a final ethnographic atlas. Secure rows cover
the best-attested Roman, Han, Parthian, Armenian, Judean, Tamil, Buddhist, and
major American traditions; mobile, frontier, and many regional folk frames
remain `contested`. The later location-level remap and population pass must
split them before M4 can be called complete. Sources weighed: P10-P11;
CAH-XI; BHR; OCD. [contested]

## 2026-07-19 — American SoP regional coverage

Plains/Coastal and Pacific Coast SoPs are separate from Hopewell, Basketmaker,
and Dorset because the plan names those landscapes separately. Omaha and
Monterey Coast are geographic anchors, not AD 1 capitals. The remaining area
rows are broad cultural-political frames for named Mesoamerican and Andean
entities, all marked `contested`. Pacific Coast has no vanilla-ownable surface
in the installed start data, so it intentionally retains only its reviewed
anchor. Sources weighed: P8.10; CAH-XI. †

## 2026-07-19 — African SoP regional coverage

West African iron-age societies, Bantu-expansion societies, and Barbaria/Horn
societies are separate SoP families because the design bible explicitly treats
them as non-state political landscapes. Kumasi, Mombasa, and Mogadishu are map
anchors, not asserted AD 1 capitals. Their area frames, and the expanded
Mauretanian/Garamantian/Blemmyan/Aksumite rows, remain `contested` until the M4
population and culture layers can distinguish settlement clusters from states.
Sources weighed: P8.5; CAH-XI; *Periplus of the Erythraean Sea*. †

## 2026-07-19 — Han-world regional extent proxies

The Han-world pass assigns only frames tied directly to the plan's AD 1 roster:
the Roman/Parthian client edges, Korean polities and Samhan clusters, Buyeo and
Wuhuan, and the Xiongnu/Xianbei/Dingling pastoral zones. Tarim oasis-state,
Levantine, Mesopotamian, and Transoxianan areas that contain multiple active
capital anchors are intentionally not collapsed to one tag. All added broad
rows remain `contested`. Sources weighed: P8.1–P8.3; P8.8; CAH-XI; CHGIS;
*Samguk Sagi*. †

## 2026-07-19 — AD 1 roster entries requiring later review

These entries are deliberately retained as `contested` in
`docs/world_1ad/polities.csv`. They are not yet game setup; M3 mapping must not
turn them into silent certainties.

- **Bosporan succession (BOS):** Dynamis is used as the AD 1 dynastic anchor,
  following the master plan's explicit caution. Sources weighed: P8.1; OCD,
  "Dynamis" and "Bosporus, Cimmerian". †
- **Samhan and future southern Korean tags (MAH/JIN/BYE):** traditional
  political labels are used as small SoP clusters, not centralized kingdoms.
  Sources weighed: P8.3; *Samguk Sagi* conventional chronology; archaeology
  must control the M3 location extent. †
- **Satavahana and Indo-Scythian configuration (SAT/ISK):** AD 1 is treated as
  a fragmented/interregnum phase rather than a falsely crisp imperial border.
  Sources weighed: P8.4; CAH-XI South Asia syntheses. †
- **Djenne-Djenno (DJN):** represented as a settled SoP cluster, not a state,
  reflecting uncertainty over the political form. Sources weighed: P8.5;
  CAH-XI African archaeology syntheses. †
- **Early Malay/Javanese organization (MAL/JAV):** represented only as SoP
  clusters before historically documented state formations. Sources weighed:
  P8.9; CAH-XI Southeast Asia syntheses. †
- **Cuicuilco timing (CUI):** the entity is present for the planned Xitle
  disaster window, with the exact eruption chronology left event-configurable.
  Sources weighed: P8.10; CAH-XI Mesoamerican archaeology syntheses. †

## 2026-07-19 — Capital geometry proxies

Where an AD 1 capital has no identically named EU5 location, M3 uses a nearby
local-map key only after its Pleiades coordinate projects onto the matching
geographic site. These are geometry proxies, not historical renamings: M4's
dynamic naming layer renders the ancient name. Current examples are
Tiberias→Safed, Petra→Shoubak, Tyana→Bor, Samosata→Samsat, Emesa→Homs,
Seuthopolis→Boruy/Stara Zagora, Ctesiphon→Baghdad, Persepolis→Istakhr,
Arbela→Erbil, Artaxata→Khor Virap, Phasis→Poti, Kabalaka→Qabala,
Uraiyur→Srirangam, Meroe→Shendi, Garama→Ubari, Zafar→Dhafar, Taxila→Attock,
Talmis→Kalabsha, Batavodurum→Nijmegen, Venta Icenorum→Norwich,
Isurium→Ripon, Calleva→Basingstoke, and Caerwent→Monmouth. Sources
weighed: P8.1–P8.6; Pleiades; local EU5 raster coordinate index. The nearby
location is explicit in `polities.csv` and may be revised when a closer map key
or an ancient naming overlay is available.

## 2026-07-19 — Area-frame ownership pass

The first territorial pass uses whole current-EU5 area/region hierarchy keys
only where they sit unambiguously inside a named AD 1 macro-region in P8.1,
P8.2, or P8.3 (for example, Italia, the Hispaniae, core Gaul, the Han
commandery frame, and the Iranian Arsacid core). This is a geometry adapter,
not a claim that modern area edges reproduce every Roman provincial frontier.
Client areas, frontier Germania, Parthian sub-kings, and all SoP extents are
left narrower or unassigned until their own sourced rows exist. Sources
weighed: P8.1–P8.3; CAH-XI; Book of Han geography tradition. †

## 2026-07-19 — Confederacy and frontier anchor proxies

Several M3 polity rows describe a people or a broad region rather than an
attested single capital. Their map keys are therefore explicitly geographic
anchors: Naju/Gyeongju/Uian for the three Samhan clusters, Nara for the Wa
polities, Inverness and Armagh for the Caledonian/Ulaid clusters, Heves and the
Lower Don/Caucasus keys for Sarmatian groups, and Otrar/Gulja/Dalai Nur/Yizhou
for the Central-Asian and eastern-steppe groups. They are not claims that the
modern-label settlement was a period capital; M4 dynamic names and later M3
territory rows will replace the display/geographic scaffolding. Sources
weighed: P8.3, P8.7, P8.8; CAH-XI; CHGIS; *Samguk Sagi*. †

Bosporus uses Taman and Characene Al-Muhammerah as constrained capital-region
proxies; both remain contested because Panticapaeum/Charax Spasinu mapping is
not a one-to-one local-key match. Ganzak→Malekan and Corduene→Eruh are
Pleiades-coordinate matches; the remaining classical site proxies are listed
in `capital_coordinates.csv`. Sources weighed: P8.1–P8.2; OCD; Pleiades. †

## 2026-07-19 — Final M3 capital-anchor coverage

The completed M3 anchor registry must not be read as an atlas of formal ancient
capitals. For broad regional peoples and societies of peoples, the local key is
an explicitly labelled geographic seed pending a sourced territorial and pop
pass. Examples include Caesarea Philippi→Antilebanon Mountains for Batanea,
Longcheng→Qingzhou Mongol for the Xiongnu, Pratishthana→Daulatabad, Qaryat
al-Faw→Aqiq, Kath for Khwarazm, Mataram for Java, Azcapotzalco for Cuicuilco,
Chan Chan for the Moche, and regional anchors for the Americas and Oceania.
They are transparent map proxies rather than claims about exact period names,
polities, or borders. M4 dynamic names and the unfinished M3 territory rows are
the required corrective layers. Sources weighed: P8.4–P8.10; CAH-XI; Pleiades;
CHGIS. †

## 2026-07-19 — Indian Ocean regional extent proxies

The current Indian and Southeast Asian ownership rows use labelled regional
frames instead of invented province lines: the Indo-Scythian north-west,
Satavahana Deccan interregnum, Kalinga, Chera coast, Anuradhapura, Han Jiaozhi,
and the Pyu, Mon, proto-Khmer, Malay, Javanese, Philippine, and Bornean SoP
clusters. The area boundaries are inherited from the installed map and are not
claims of period sovereignty at every location. They remain `contested` until
the M4 pop/culture pass and later local historical research can refine them.
Sources weighed: P8.3–P8.4; P8.9; CAH-XI; *Periplus of the Erythraean Sea*. †

## 2026-07-19 — Barbaricum and northern-frontier extent proxies

The expanded northern-European rows are region-level political frames, not
archaeological settlement boundaries. They use the plan's named Caledonian,
Hibernian, Germanic, Scandinavian, Venedi, Dacian/Getic/Sarmatian, Armenian,
and Caucasian groups where the installed local geography has an unmistakable
matching macro-region. The real political mosaic was finer and mobile; all
these rows stay `contested` pending the M4 population/culture map and later
local research. Sources weighed: P8.1–P8.2; P8.7; CAH-XI. †

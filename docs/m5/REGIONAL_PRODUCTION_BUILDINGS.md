# Regional antique production buildings

This M5 layer adds one hundred and forty-two reusable, directly illustrated antique production
families and **1,684 AD 1 start placements**: 590 in Europe, 382 in North Africa,
468 in the Middle East, 122 in South Asia, and 122 in East Asia. The
ledger is deliberately a family system rather than fictional unique monuments.
Each family has a direct PNG source, a
reviewed BC7 128px DDS icon, localized name/description, a locally verified
EU5 building contract, conservative goods upkeep, and a source boundary.

`regional_building_seeds.csv` is the placement ledger. Every entry is
explicitly `contested` at the individual-location level: a city-point building
stands for its market and productive hinterland, never an assertion that a
particular excavated workshop was inside the EU5 polygon. The validator checks
that all placements are controlled on AD 1, stay within the requested
geographic macros, use every family, contain no duplicate family/location
pair, and total at least 100.

## Families and economic inputs

| Family | Placements | Goods represented by upkeep |
| --- | ---: | --- |
| Olive press | 22 | olives, pottery, tools, lumber |
| Wine press | 43 | wine, pottery, tools, lumber |
| Fish saltery | 16 | fish, salt, pottery, lumber, tools |
| Pottery kiln | 45 | clay, lumber, tools |
| Fullonica | 40 | wool, cloth, dyes, tools |
| Glassworks | 22 | glass, clay, lumber, tools |
| Dye workshop | 6 | dyes, cloth, fish, tools |
| Metalwork shop | 33 | iron, copper, coal, tools |
| Stone yard | 14 | stone, masonry, marble, lumber, tools |
| Antique shipyard | 23 | lumber, naval supplies, tar, cloth, tools |
| Silk loom | 2 | fiber crops |
| Scriptorium | 22 | dyes, paper, lumber |
| Jewelers' quarter | 22 | gold |
| Weapon smithy | 17 | lumber, coal, tools |
| Cotton weavery | 2 | cotton |
| Linen weavery | 22 | fiber crops |
| Alum dyehouse | 2 | alum, lumber |
| Joinery | 2 | lumber, dyes, tools |
| Bronze foundry | 2 | copper, tin |
| Ivory carver | 7 | ivory |
| Leatherworks | 7 | livestock, sand, tar, tools |
| Amphora depot | 17 | pottery, lumber, tools |
| Grain mill | 14 | wheat, tools |
| Ropewalk | 14 | fiber crops, lumber, tools |
| Brickworks | 14 | clay, lumber, tools |
| Lamp workshop | 14 | clay, olives, lumber |
| Tile yard | 14 | clay, lumber, tools |
| Papyrus workshop | 14 | paper, dyes, lumber |
| Incense workshop | 14 | incense, lumber, tools |
| Basketry | 14 | lumber, fiber crops, tools |
| Linen bleachery | 14 | fiber crops, cloth, tools |
| Copper smithy | 14 | copper, tin, tools |
| Spice grinder | 14 | incense, dyes, tools |
| Reed boat yard | 14 | fiber crops, lumber, tar, tools |
| Oil bottling workshop | 14 | olives, pottery, lumber |
| Garum workshop | 14 | fish, salt, pottery |
| Lime kiln | 14 | stone, lumber, tools |
| Marble yard | 14 | marble, stone, tools |
| Wool carding shed | 14 | wool, tools |
| Mordant dyehouse | 14 | alum, dyes, lumber |
| Scale armoury | 14 | copper, iron, tools |
| Wheelwright | 14 | lumber, iron, tools |
| Granary | 14 | wheat, lumber |
| Glass bead workshop | 14 | glass, dyes, tools |
| Loom-weight weavery | 14 | fiber crops, clay, tools |
| River barge yard | 14 | lumber, tar, fiber crops, tools |
| Saddlery | 10 | leather, tools, gold |
| Parchment workshop | 10 | leather, dyes, tools |
| Mosaic workshop | 10 | stone, marble, glass, tools |
| Stucco yard | 10 | stone, clay, lumber, tools |
| Lead foundry | 10 | lead, coal, tools |
| Lapidary | 10 | gems, gold, tools |
| Perfumery | 10 | incense, olives, pottery |
| Wax workshop | 10 | beeswax, pottery, fiber crops |
| Sailmaker | 10 | fiber crops, cloth, tools |
| Brewhouse | 10 | wheat, fruit, pottery |
| Quernworks | 10 | stone, iron, tools |
| Textile dye finisher | 10 | cloth, dyes, alum, tools |
| Monetal workshop | 10 | gold, silver, copper, tools |
| Hide curing yard | 10 | livestock, sand, tar, tools |
| Apothecary | 10 | incense, dyes, pottery, tools |
| Bread oven | 10 | wheat, stone, pottery, tools |
| Amphora warehouse | 10 | pottery, lumber, tools |
| Tegula kiln | 10 | clay, lumber, tools |
| Hypocaust furnace yard | 10 | coal, lumber, clay, stone, tools |
| Writing-supplies stationer | 10 | paper, dyes, lumber, tools |
| Weightmaker | 10 | copper, lead, tools |
| Chariotwright | 10 | lumber, iron, leather, tools |
| River ferry quay | 10 | lumber, fiber crops, tar, tools |
| Raised grain store | 10 | wheat, lumber, tools |
| Saltworks | 10 | salt, stone, lumber, tools |
| Purple dyehouse | 10 | dyes, cloth, fish, tools |
| Iron bloomery | 10 | iron, coal, tools |
| Tin smelter | 10 | tin, copper, coal, tools |
| Charcoal hearth | 10 | lumber, tools |
| Glass bead furnace | 10 | glass, dyes, sand, tools |
| Cordwainer | 10 | leather, tools, dyes |
| Netmaker | 10 | fiber crops, tar, lead, tools |
| Pack-saddle workshop | 10 | leather, wool, lumber, tools |
| Stone carver | 10 | stone, marble, tools |
| Cooperage | 10 | lumber, iron, tools |
| Spice warehouse | 10 | pepper, incense, pottery, tools |
| Honey house | 10 | beeswax, fruit, pottery, tools |
| Olive soapworks | 10 | olives, lumber, pottery, tools |
| Flax retting yard | 10 | fiber crops, lumber, tools |
| Bone carver | 10 | livestock, tools, dyes |
| Hornworker | 10 | livestock, tools, dyes |
| Amber carver | 10 | amber, gold, tools |
| Coral workshop | 10 | gold, tools, pottery |
| Sponge drying yard | 10 | fish, fiber crops, lumber, tools |
| Reed matmaker | 10 | fiber crops, lumber, tools |
| Lacquer workshop | 10 | lumber, dyes, tools |
| Instrument maker | 10 | lumber, leather, tools |
| Figurine kiln | 10 | clay, lumber, tools |
| Public cistern | 10 | stone, lumber, tools |
| Fountain house | 10 | stone, clay, tools |
| Macellum stalls | 10 | fish, fruit, pottery, tools |
| Mensores office | 10 | copper, lead, tools |
| Way station | 10 | lumber, livestock, fiber crops, tools |
| Caravanserai | 10 | lumber, fiber crops, pottery, tools |
| Wharf crane | 10 | lumber, naval supplies, fiber crops, tools |
| Lamp-oil depot | 10 | olives, pottery, lumber, tools |
| Bath fuel depot | 10 | coal, lumber, clay, tools |
| Pack-animal yard | 10 | livestock, leather, wool, lumber |
| Grain weighhouse | 10 | wheat, pottery, lumber, tools |
| Customs gate | 10 | lumber, pottery, copper, tools |
| Ironmongery | 10 | iron, coal, tools |
| Bronze vessel shop | 10 | copper, tin, coal, tools |
| Oil-lamp kiln | 10 | clay, olives, lumber, tools |
| Fineware kiln | 10 | clay, lumber, tools |
| Scroll workshop | 10 | paper, dyes, lumber, tools |
| Silverwork shop | 10 | silver, gold, tools |
| Arrow fletchery | 10 | lumber, iron, tools |
| Harness maker | 10 | leather, livestock, tools |
| Wickerwork shed | 10 | fiber crops, lumber, tools |
| Loom house | 10 | fiber crops, cloth, tools |
| Cauldron smithy | 10 | copper, tin, coal, tools |
| Barge chandlery | 10 | lumber, fiber crops, tar, tools |
| Combmaker | 10 | ivory, tools |
| Bell foundry | 10 | copper, tin, coal, tools |
| Oarwright | 10 | lumber, fiber crops, tar, cloth, tools |
| Spindlework | 10 | fiber crops |
| Torchmaker | 10 | lumber, dyes, tools |
| Sieve maker | 10 | lumber, dyes, tools |
| Mortar and pestle workshop | 10 | iron |
| Seal cutter | 10 | gold |
| Kiln furniture workshop | 10 | clay, lumber, tools |
| Reed-pen maker | 10 | dyes, paper, lumber |
| Sail-needle shop | 10 | lumber, fiber crops, tar, cloth |
| Pulley workshop | 10 | lumber, fiber crops, tar, cloth |
| Locksmith | 12 | copper, tin |
| Nailery | 12 | iron |
| Chainmaker | 12 | iron |
| Wire drawer | 12 | copper, tin |
| Shieldmaker | 12 | lumber, coal, tools |
| Scabbard maker | 12 | livestock, sand, tar, tools |
| Fishing-tackle workshop | 12 | lumber, fiber crops, tar, cloth |
| Feltworks | 12 | wool |
| Carpet loom | 12 | wool |
| Cork workshop | 12 | lumber, dyes, tools |
| Brushmaker | 12 | lumber, dyes, tools |
| Tesserae kiln | 12 | lumber, sand, tools |

These numbers are gameplay demand weights, not reconstructed ancient output,
workforce, prices, or cargo quantities. Existing antique RGO and goods work
remains the source of regional raw-material distribution; this layer creates
visible, modest urban demand for the era-appropriate goods.

## Historical boundary

The family references establish documented ancient production categories:
Roman olive-oil factories and maritime trade; the Roman fish-salting works at
Baelo Claudia; early imperial Arretine and Roman-period Memphis ceramic
workshops; Pompeii's fulling/textile economy; the Roman glass industry's
eastern-Mediterranean lineage; Tyre's purple-dye association; and ordinary
ancient stone, metal, and ship-repair craft contexts. They do not license an
individual named workshop, artisan, output total, mine, quarry concession,
fleet roster, or architectural reconstruction at each city-point seed.

The only named direct anchors remain in `roman_buildings.csv`. This separates
source-secure named sites from the broad regional economic texture requested
for the AD 1 world.

The second expansion deliberately adds 20 reviewed, pre-existing city anchors
as deferred M5 market nodes and no speculative trade-route edges: Corduba,
Tarraco, Emerita Augusta, Olisipo, Caesaraugusta, Narbo Martius, Nemausus,
Burdigala, Arelate, Mediolanum, Bononia, Mutina, Ravenna, Tarentum,
Brundisium, Hippo Regius, Hippo Diarrhytus, Caesarea Mauretaniae, Tacape, and
Hadrumetum. Their `city`/`town` profiles are engine adapters for a regional
urban market, not population totals, municipal-rank reconstructions, or proof
of a named production site.

The third placement pass adds five already reviewed manufacture classes to each
of those twenty Roman and North-African market anchors. It creates no additional
named site, route, market node, or building family: the broad city-point
economic representation remains explicitly contested.

A production-and-scale audit now counts every 1,790 M5/M7 start placement rather
than only these regional rows. It locks the actual layout at 76.9% productive
and 94.1% scalable; see [BUILDING_AUDIT.md](BUILDING_AUDIT.md).

## Art review

The source illustrations, including the eleven twelve-family expansions, were
reviewed for clear process
silhouettes, antique material culture, absence of text/insignia/modern
technology, and distinctness at 128px. They are committed under
`assets_queue/generated_sources/`; the engine uses their BC7 DDS derivatives
under `main_menu/gfx/interface/icons/buildings/`. The reviewed set is shown in
[the original regional-building contact sheet](REGIONAL_BUILDING_ICON_CONTACT_SHEET.png)
and [the manufactures contact sheet](REGIONAL_MANUFACTURES_ICON_CONTACT_SHEET.png).
The second-pass source sheet is committed as
`assets_queue/generated_sources/antq_reg_second_pass_sheet_source.png`; its
BC7 derivatives remain the engine-facing assets.
The third-pass sheet is
`assets_queue/generated_sources/antq_reg_third_pass_sheet_source.png`.
The fourth-pass sheet is
`assets_queue/generated_sources/antq_reg_fourth_pass_sheet_source.png`.
The fifth-pass sheet is
`assets_queue/generated_sources/antq_reg_fifth_pass_sheet_source.png`.
The sixth-pass sheet is
`assets_queue/generated_sources/antq_reg_sixth_pass_sheet_source.png`.
The seventh-pass sheet is
`assets_queue/generated_sources/antq_reg_seventh_pass_sheet_source.png`.
The eighth-pass sheet is
`assets_queue/generated_sources/antq_reg_eighth_pass_sheet_source.png`.
The ninth-pass sheet is
`assets_queue/generated_sources/antq_reg_ninth_pass_sheet_source.png`.
The tenth-pass sheet is
`assets_queue/generated_sources/antq_reg_tenth_pass_sheet_source.png`.
The eleventh-pass sheet is
`assets_queue/generated_sources/antq_reg_eleventh_pass_sheet_source.png`.

# Regional antique production buildings

This M5 layer adds twenty-two reusable, directly illustrated antique production
families and **388 AD 1 start placements**: 218 in Europe, 70 in North Africa,
and 96 in the Middle East, plus two in South Asia and two in East Asia. The
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

A production-and-scale audit now counts every 455 M5/M7 start placement rather
than only these regional rows. It locks the actual layout at 70.1% productive
and 85.3% scalable; see [BUILDING_AUDIT.md](BUILDING_AUDIT.md).

## Art review

The original ten source illustrations and the twelve-manufacture expansion were reviewed for clear process
silhouettes, antique material culture, absence of text/insignia/modern
technology, and distinctness at 128px. They are committed under
`assets_queue/generated_sources/`; the engine uses their BC7 DDS derivatives
under `main_menu/gfx/interface/icons/buildings/`. The reviewed set is shown in
[the original regional-building contact sheet](REGIONAL_BUILDING_ICON_CONTACT_SHEET.png)
and [the manufactures contact sheet](REGIONAL_MANUFACTURES_ICON_CONTACT_SHEET.png).

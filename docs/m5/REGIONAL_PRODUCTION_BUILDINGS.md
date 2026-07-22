# Regional antique production buildings

This M5 layer adds ten reusable, directly illustrated antique production
families and **112 AD 1 start placements**: 55 in Europe, 15 in North Africa,
and 42 in the Middle East. The ledger is deliberately a family system rather
than 112 fictional unique monuments. Each family has a direct PNG source, a
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
| Olive press | 11 | olives, pottery, tools, lumber |
| Wine press | 16 | wine, pottery, tools, lumber |
| Fish saltery | 11 | fish, salt, pottery, lumber, tools |
| Pottery kiln | 16 | clay, lumber, tools |
| Fullonica | 16 | wool, cloth, dyes, tools |
| Glassworks | 9 | glass, clay, lumber, tools |
| Dye workshop | 4 | dyes, cloth, fish, tools |
| Metalwork shop | 11 | iron, copper, coal, tools |
| Stone yard | 8 | stone, masonry, marble, lumber, tools |
| Antique shipyard | 10 | lumber, naval supplies, tar, cloth, tools |

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

## Art review

The ten original source illustrations were reviewed for clear process
silhouettes, antique material culture, absence of text/insignia/modern
technology, and distinctness at 128px. They are committed under
`assets_queue/generated_sources/`; the engine uses their BC7 DDS derivatives
under `main_menu/gfx/interface/icons/buildings/`. The reviewed set is shown in
[the regional-building contact sheet](REGIONAL_BUILDING_ICON_CONTACT_SHEET.png).

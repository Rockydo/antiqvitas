# [PRO] Master-Plan Culture Completion

This pass implements every culture category that section 10 of the master plan
named but the previous 350-culture catalogue either omitted or collapsed into a
broader proxy. The source rows are `pro_master_plan_cultures.csv`; the map rows
are `pro_master_plan_remap.csv`.

The pass adds **23 definitions**. Twenty-two receive controlled AD 1 pop
placements. Na-Dene is deliberately definition-only because every
source-appropriate northwestern cell lies outside the installed controlled AD 1
footprint; assigning it to Puebloan, Inuit, or Pacific-coast anchors would be a
false historical claim. It remains available for scripted settlement and later
atlas expansion. The pass also makes Colchis and Osroene use the new Colchian
and Syriac profiles, and changes the Finland regional profile from generic
Uralic to Finnic.

| Master-plan promise | Earlier treatment | Implemented treatment |
|---|---|---|
| Colchian | Folded into Kartvelian | Separate eastern-Black-Sea Colchian frame; inland Georgia remains Kartvelian |
| Syriac | Folded into Aramaic | Separate Edessa–Nisibis Syriac-Aramaic frame |
| Nilotic | Folded into Nubian/Cushitic or generic African profiles | Separate, deliberately narrow Upper Blue Nile interface anchor |
| Khoisan | Missing | Separate Shashe–Limpopo frontier anchors; no false Cape/Kalahari placement in uncontrolled cells |
| Qiang | Folded into Tibeto-Burman or Shu-Han | Separate Amdo and upper-Min frontier frame; Chengdu basin remains Shu-Han |
| Zhangzhung | Folded into Tibeto-Burman | Separate Ngari–Changtang frame |
| Tai | Missing | Separate northern mainland highland frame |
| Cham | Folded into Sa Huynh | Broader Proto-Cham frame with a narrower Sa Huynh archaeological core retained |
| Yilou | Folded into Tungusic | Separate Amur–Ussuri frame with one upper-Amur residual Tungusic anchor |
| Finnic | Folded into Uralic | Separate Finland–Karelia frame |
| Ugric | Folded into Uralic | Separate western-Siberian frame, below narrower archaeological selectors |
| Samoyedic | Folded into Uralic | Separate controlled Vorkuta frame; uncontrolled lower-Ob cells are not fabricated |
| Totonac | Missing | Separate Gulf-slope frame |
| Na-Dene | Missing | Separate definition retained without a false AD 1 placement because the appropriate northwest is uncontrolled |
| Iroquoian | Missing | Separate eastern-Great-Lakes frame |
| Mixe-Zoquean | Approximated by Epi-Olmec | Broader linguistic-regional frame with a narrower Epi-Olmec core retained |
| Purépecha precursor | Folded into West Mexican | Separate Michoacan precursor frame |
| Oasisamerica | Missing | Separate controlled Basketmaker/Puebloan southwest and Zacatecas exchange-zone frame |
| Hopewellian | Folded into Plains-Woodland | Separate Illinois interaction frame within the controlled atlas |
| Adena Woodland | Folded into Plains-Woodland | Separate Ohio-valley residual anchor at the AD 1 transition |
| Aymara | Folded into generic Andean/Tiwanaku | Separate Qullaw altiplano frame |
| Puquina | Folded into generic Andean/Tiwanaku | Separate puna frame |
| Quechua zone | Folded into generic Andean/Nazca | Separate central-Andean frame; no Inca polity is projected into AD 1 |

## Boundary discipline

These are game-scale implementation frames, not claims of homogeneous
populations or exact ancient borders. Every row is marked `contested` where the
source does not justify an exact polygon. Archaeological labels such as
Hopewellian, Adena, Sa Huynh, and Epi-Olmec are explicitly kept separate from
ethnolinguistic claims.

The language column is an engine adapter. Notes identify every case where the
adapter must not be read as a historical language assignment.

## Generation contract

`tools/generate_pro_culture_expansion.py` merges the completion ledgers into the
canonical catalogue and remap, then regenerates:

- culture definitions;
- named colors;
- all supported localization mirrors;
- the culture symbol index;
- AD 1 pop culture assignments;
- affected country and regional culture profiles;
- generated country definitions;
- catalogue counts and documentation.

The generator rejects unknown selectors, equal-specificity overlaps, duplicate
keys, invalid confidence values, and any mapped PRO culture without an AD 1
population presence. The single definition-only exception is explicit in code
and documentation; it cannot silently expand.

# M4 reviewed location-name corrections

The full-map name pass deliberately uses generated Tier-2 and Tier-3 ledgers to
cover every installed location key. Those bulk ledgers remain stable inputs so
that their 28,573-label output can be reproduced and audited. This file records
a smaller authoritative correction layer for mistakes found after that pass.

`tools/generate_m4_location_name_corrections.py` reads
`docs/m4/location_name_corrections.csv` and writes one exact-mirror localization
file per supported client language. The generated filename begins with
`antq_zz_`, so it loads after `antq_m4_location_names...`; duplicate root,
language, and dialect keys here intentionally supersede the older bulk label.
No generated full-map file should be edited by hand.

## Confidence

- `secure`: the displayed form and installed field match are directly supported.
- `tier2`: the correction removes a clear anachronism but the replacement is a
  conservative geographic or inherited-name proxy.
- `contested`: the existing label is demonstrably too late, while the surviving
  pre-conquest name evidence permits only a cautious reconstruction.

The `culture` column accepts one M4 culture key or a `|`-separated set. Multiple
adapters are appropriate only where the same reviewed place-name must resolve
through more than one historically relevant language layer; they do not imply
a uniform population or erase local multilingualism. Duplicate language groups
are collapsed deterministically by the generator.

## Validation

Run:

```text
python tools/generate_m4_location_name_corrections.py --write
python tools/generate_m4_location_name_corrections.py --check
python tools/m11_localization.py --check
python tools/m12_anachronism_audit.py --write
```

The repository-wide `make validate` and `make.cmd validate` paths pin the
correction generator in check mode.

## First chronology batch

The initial batch removes five labels whose current full Roman titles postdate
1 January AD 1: the Bath sanctuary, Chester fortress, Cologne colonia, Lincoln
colonia, and Londinium. Where no secure settlement name survives, the ledger
uses a clearly marked Tier-2 or contested inherited hydronym/toponym proxy
rather than inventing a false city.

## British foundation-chronology batch

The second batch removes four Roman urban labels that did not yet exist on
1 January AD 1: Durnovaria, Isca Dumnoniorum, Glevum, and Eboracum. `Isca`
retains only an inherited British river-name. Dorchester, Gloucester, and York
use plainly documented tribal-area proxies because replacing a late city with
an invented pre-conquest city would merely exchange one error for another.

Canterbury's `Durovernum`, Carlisle's `Luguvalium`, Chichester's `Noviomagus`,
and Leicester's `Ratae` are deliberately not changed in this batch: each may
preserve an indigenous toponym or an Iron Age settlement horizon despite later
Roman urban development.

## Syrian multilingual-city batch

The third data batch removes a Persian-only dynamic-name path from Antioch,
Laodikeia, Beroia, and Damascus. Near-contemporary civic coinage and the Roman
city record support Greek public forms, while the wider Levant remained
linguistically plural. Each row therefore emits both Semitic and Hellenic
adapters. This is a localization-lookup correction, not a claim that every
inhabitant used one language or that older Semitic place-name traditions
disappeared.

## Generated British-capital batch

The fourth data batch corrects three names injected by the AD 1 polity roster,
not by the bulk map ledger. `Venta Icenorum`, `Isurium Brigantum`, and `Venta
Silurum` were Roman administrative settlements founded decades after the
campaign start. Their installed fields at Norwich, Ripon, and Monmouth are also
only approximate map proxies for the archaeological sites. The replacement
labels therefore name the Iceni, Brigantes, and Silures explicitly instead of
pretending that later civitas capitals already existed.

## Southern-Levant adapter batch

The fifth data batch removes three geographically impossible Iranian lookup
paths at Philadelphia, Bostra, and Ptolemais and restores the missing Hellenic
path at Heliopolis. The names themselves are period forms; the defect was the
linguistic adapter. Amman and Acre receive paired local-Semitic and Hellenic
paths, Bosra receives a Nabataean path, and Baalbek retains both its Phoenician
cultic context and its Hellenistic public name. These adapters describe usable
name traditions, not uniform ethnic populations.

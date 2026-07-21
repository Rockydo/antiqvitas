# Cultures and Languages

This is the M4 culture-tree foundation. It follows Part II section 10 of the
master plan: regional culture definitions use locally verified EU5 language
keys, while the source tables retain the historical grouping, source, and
confidence judgment separately from engine syntax.

The generated catalogue currently contains 165 culture definitions across the
plan's principal Italic, Hellenic, Celtic, Germanic, Iranian, Caucasian,
Semitic, Nile, African, Indian, Sinitic, Southeast Asian, steppe, Uralic,
Balkan, and American/Oceanic families. It remains a foundation rather than the
finished 350-500 culture target. Its first twenty-four source-led location batches
use 313 selectors to resolve 11,714 controlled locations through
`docs/culture_remap.csv`; later batches must not silently turn a regional frame
into a claim of a homogeneous population.

`culture_remap.csv` accepts only installed area, province, location, or region selectors
and resolves them to exact controlled locations through the harvested geography
hierarchy. Every selector carries a source, confidence, and rationale; the
generator rejects unknown symbols, nested-selector overlap, empty selectors,
and unreviewed vanilla culture-key translations. A narrow location override
still takes precedence where it protects a documented mixed frontier.

The catalogue records language families verified in the installed build and
renders engine-valid nested dialects from sourced name pools; EU5 does not
accept a language root directly in a culture record. Technical family fallbacks
are implementation contracts only and never substitute for the historical
family/source fields in the ledger.

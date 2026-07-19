# Cultures and Languages

This is the M4 culture-tree foundation. It follows Part II section 10 of the
master plan: regional culture definitions use locally verified EU5 language
keys, while the source tables retain the historical grouping, source, and
confidence judgment separately from engine syntax.

The first generated set covers the plan's principal Italic, Hellenic, Celtic,
Germanic, Iranian, Caucasian, Semitic, Nile, African, Indian, Sinitic,
Southeast Asian, steppe, Uralic, Balkan, and American/Oceanic families. It is a
foundation rather than the finished 350-500 culture target. The next M4 passes
split these large frames with a location-level `culture_remap.csv`; they must
not silently turn a regional frame into a claim of a homogeneous population.

The catalogue records language families verified in the installed build. The
first generated culture definitions deliberately do not attach them yet: the
runtime smoke established that EU5 culture records require a nested dialect key,
not a language root. The next M4 language/namelist pass will generate those
engine-valid dialects from sourced name pools. This prevents a modern language
fallback from silently becoming a historical claim.

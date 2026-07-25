# M8 Knowledge Design

`tools/m8_knowledge.py` renders 250 advances across the engine's six age slots:
five statecraft, warfare, exchange, learning, and society DAGs per age. The
first four ages contain ten-node trees with two shared roots, two regional
branches, one convergence route, and alternative terminal choices; the final
two contain five-node forked trees. Requirements remain inside one age because
that is the installed engine contract. Validation proves 50 roots, 50 branch
points, 20 convergence nodes, 80 terminal choices, acyclicity, direct art,
complete descriptions/effects, and no post-antique token.

Eleven regional paths cover Roman/Italic, Hellenic, Celtic, Germanic,
Iranian/steppe, Indic, Han/East Asian, Near Eastern, African, American, and
Oceanian practice. Culture groups grant the native path; historically plausible
institutions provide explicit adoption routes. Regional names are visible in
the tree while the reviewed 250-icon corpus and stable script keys remain
unchanged.

The DAG directly packages all 154 regional workshops, 44 ancient units, 19
government reforms, 24 privileges, ten casus belli, five subject types, and the
required start laws/policies. Workshop tiers represent capacity to reproduce a
practice at scale, not invented dates. `tools/advance_event_packages.py` adds
age/track preparedness bonuses to all 84 M10 historical currents without
gating their occurrence. Institutions also act as cross-cultural prerequisites.

The installed age contract exposes one `victory_card` per age, so those five
cards are the engine-visible objectives. The locally verified `unique` block
in the age definition carries one small era ability per age. No unverified
custom objective or ability field is emitted.

## Institutions

| Institution | Origin / release | Engine representation |
| --- | --- | --- |
| Hellenism | active, Athens | active at start |
| Roman Law and Engineering | active, Rome | active at start |
| Han Bureaucratic Statecraft | active, Jingzhao/Chang'an | active at start |
| Buddhist Monasticism | active, Anuradhapura | active at start |
| Cataphract Warfare | Iran proxy, AD 96 | Merv fixed spawn |
| Papermaking | Luoyang, AD 105 | Luoyang fixed spawn |
| Christian Monasticism | Egypt, AD 270 | Alexandria fixed spawn |
| Theological Orthodoxy | Nicaea, AD 325 | Iznik fixed spawn |
| Foederati Statecraft | Thrace, AD 382 | Edirne fixed spawn |

The two monastic entries are a mechanical representation of the plan's
dual-origin Monasticism instruction, rather than a claim that either tradition
was the other's origin. All release dates are rendered after `AntqDate`
validation, never handwritten in generated script.

## Starting technology levels

The checked M3 roster is partitioned mechanically as follows: Rome, Han, and
Parthia are level 4; Tier-1/2 countries and subjects are level 3; Tier-3
countries are level 2; and all societies-of-pops are level 1. This implements
the plan's imperial-core > literate-periphery > tribal-world ordering without
turning it into a claim of universal cultural rank. The integer scale is a
gameplay tuning surface, not a civilizational hierarchy.

## Evidence route

Plan §15 fixes the age themes, institution names, and dated origins. `CAH-XI`
supports the Roman and late-antique frameworks; `BHR` supports the Han
administrative context; the plan's general research route includes scholarship
on Roman, Persian/steppe, Indian, and Chinese worlds. M8 uses these only for
the broad, source-labelled design surface. It does not infer that an innovation
originated at one exact building, nor does it make contested stirrup adoption
reachable before the end date.

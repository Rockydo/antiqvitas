# M8 Knowledge Design

`tools/m8_knowledge.py` is the sole renderer for this milestone. It creates
five research strands (statecraft, warfare, exchange, learning, and society)
within each of the five campaign ages: exactly 50 advances per age and 250 in
total. EU5 permits advance requirements only within their own age, so each age
has five complete ten-step strands and the age transition is the historical
gate between thematic continuations. Every non-root node requires its immediate
predecessor; the renderer checks that there are 25 terminal nodes, no dangling
or cross-age requirements, and no post-antique military or colonial unlock
token.

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

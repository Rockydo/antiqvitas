# M11 event-density pass

The M10 chronology contains 83 sourced, shared-art historical currents. M11
adds four non-mechanical review events within each current's documented window,
for 328 additional events and **411 total** section-18 events.

| Surface | Count | Treatment |
|---|---:|---|
| Primary M10 currents | 83 | Original dated situation/disaster/event/formable surfaces and their reviewed paintings |
| M11 phase events | 328 | Four dated, no-effect review events for each non-terminal current; inherit the parent painting |
| Total | 411 | Meets the master-plan target of at least 400 events |

The terminal Odoacer finale on 4 September 476 receives no derived phases: it
has no usable campaign time after its source date, and its primary finale event
remains the historically appropriate terminal surface.

## Historical and art discipline

Phase entries do not invent separate incidents, participants, outcomes, or
artwork. Each restates the parent timeline current in project-authored wording,
within its existing sourced interval, and explicitly preserves a divergent
campaign outcome. The parent current's reviewed event illustration is reused,
matching the plan's expectation of roughly 80 shared paintings rather than
hundreds of false visual reconstructions.

## Technical contract

`tools/m11_flavor_events.py` reads the five M10 generator inventories and
`docs/timeline.csv`; `tools/dates.py` derives four 62-day trigger windows at
20%, 40%, 60%, and 80% of each source interval. It verifies the source/master
art link, all localizations, exactly 83 source currents, 328 derived events,
and the aggregate >=400 count.

The installed engine rejects `dynamic_historical_event` entries whose target
country does not exist in AD 1. The optional notification for future Huns is
therefore anchored to the existing Xiongnu (`HNS` -> `XIO`); future eastern-Roman
and Vandal entries use the existing Roman anchor (`ERO`/`VND` -> `XAA`). The
original M10 future-formation and current logic remains responsible for those
polities themselves.

Local basis: installed event parser behavior observed in the enabled-mod smoke
test, installed no-effect country-event options, M10 generators, and master
plan sections 9, 18, and 20.

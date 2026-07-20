# M11 decision ledger

`docs/m11/decisions.csv` holds 40 source-labelled candidate player actions:
Rome (8), Han (8), Persia/steppe (6), India/SEA (5), religion (5),
Barbaricum (4), and other world regions (4). Each is a bounded player-facing
abstraction tied to reviewed AD 1 design tags, a modest gold cost, a 3-8 year
cooldown, and one locally documented country effect. The rows do not claim a
named decree, ceremony, office-holder, annual calendar, or uniform institution.

`tools/m11_decisions.py` validates the ledger against the AD 1 roster and tag
map, and can render the locally verified `owncountry` generic-action contract.
The game-facing output is intentionally not retained at present: the installed
build requires a registered `PERFORM_<action>_ACTION` GUI message type for each
generic action, and additive message-type files did not load. See the dated
entry in `BLOCKERS.md`. The ledger remains ready for a controlled exact-name
message-registry overlay after the blocker recovery is attempted.

Sources: ANTIQVITAS master plan sections 8.1-8.10 and 18; `CAH-XI`, `ORB`, and
`PER` as indexed in `docs/world_1ad/SOURCES.md`; local EU5 generic-action,
message-type, effect, and trigger contracts.

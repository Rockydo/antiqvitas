# R37 rejected at AD 15: rival-replacement relation race

R37 was a fresh, non-debug production campaign at 1920x1080 or higher on
fingerprint `e1067007f903b492605a56de9fc601b902a636196c3ed9d319f002bfba0094be`.
The same EU5 process ran continuously from 1 January AD 1 through 20 February
AD 15 while the council, laws, state offices, administrative programmes,
event choices, succession, construction, markets, and reports were actively
exercised.

The Roman succession path passed its persisted post-handoff gate.  On
1 January AD 15, Tiberius (`6990`) ruled without a regent and the protected
succession reserve (`9721`) was heir.  The global save contained 449 real
polities, zero bankruptcies, zero civil wars, 59 active construction projects,
and complete three-role mercenary cells.  Script errors remained zero.

The run is nevertheless rejected because `ai.log` recorded one invalid
hardcoded `replace_rival` command on 8 May AD 14.  The R35 repair had removed
the command's mutable stability price, but this exposed the remaining engine
race: a planned rival replacement also becomes invalid if war or either rival
relation changes before asynchronous execution.  The log supplies neither an
actor nor a script callsite, so the defect cannot be repaired at an individual
country command site or excused as a proven native baseline family.

The follow-up repair uses EU5's AI-only `rival_criteria` surface to block the
unsafe hardcoded replacement planner for every AD 1 engine tag and every
ancient country created later in the campaign.  Player rival controls,
scripted `add_rival` and `remove_rival` effects, historical rivalry queries,
and ANTIQVITAS rivalry situations remain available.  The generator owns the
complete tag inventory so newly mapped opening countries cannot silently
escape the guard.

R37 cannot contribute elapsed years to the final AD 100 gate.  Evidence is
retained in:

- `docs/screens/R37_FINAL_PRODUCTION_ROME_AD1_100/`
- `docs/playtests/R37_M6_AD15.json`
- `docs/playtests/R37_STABILITY_AD15.json`
- `in_game/common/rival_criteria/zz_antq_ai_rival_replacement_guard.txt`

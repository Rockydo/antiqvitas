# M12 Mission-Surface Audit

The installed game has eleven active generic mission packs. Their conditions
and rewards are not era-neutral: the audit found Discovery, colonial-charter,
Renaissance, Reformation, banking, paper-guild, and vanilla-institution gates.
Leaving them active would make those unreachable or anachronistic mechanics
part of the AD 1--476 campaign.

`tools/m12_disable_missions.py` reads the configured installed mission folder
on every run and creates exact-name overlays for all eleven pack files. Each
original definition remains present, but its top-level `visible` trigger gains
`always = no`. The checker rejects an unexpected source inventory, a missing
visibility gate, or a stale output, so a game patch cannot silently alter the
disable layer. `____Info.txt` is informational only and is not overridden.

The static gate and an enabled-mod menu smoke pass are green. This is a narrow
technical compatibility decision, not a claim that generic mission concepts
are absent from antiquity; any future ancient mission system must be source-led
and replace this unavailable layer deliberately.


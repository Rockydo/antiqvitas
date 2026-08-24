# R27 rejected production campaign — AD 12 mercenary AI race

R27 was a fresh, non-debug Rome campaign at native 1920x1080 using paired-smoked
fingerprint `96d01847fedbaf0ff539e5eac800c1c8527abd8e8d0c228016fe331c61154513`.
It ran continuously from 1 January AD 1 through the AD 12 autosave. The AD 2
checkpoint passed. The AD 12 checkpoint is rejected and cannot satisfy the
final production gate.

`docs/playtests/R27_AD10_CHECKPOINT.json` records zero script errors but two
actionable `hire_mercenary_from_leader` command failures. Both occurred at
04:57:18. The save contains two successful contracts for borrower 122, with
distinct leaders 5195 and 5196 and distinct home cells; both pool records are
correctly marked `state=hired`, and the manager contains no duplicate leader
reference. This isolates a same-tick global-captain contention race.

The campaign was stopped after diagnosis. The next candidate must begin from
AD 1 after full validation and paired smoke of the bounded mercenary-AI
preference repair.

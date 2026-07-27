# S2 opening economy and research probe — 27 July 2026

## Scope

This is a short deterministic subsystem probe under the reduced QA policy. It
tests the exact manual-playtest symptoms without attempting a multi-year
observer run.

## Clean AD 1 opening

A fresh player game was started on 1 January AD 1 and switched to Rome through
the local game driver. The Economy panel showed:

- treasury: 10.96K;
- monthly income: +523.51;
- monthly expenses: -478.15;
- monthly balance: +45.36;
- no bankruptcy banner.

The Advances panel showed 21 of 29 opening advances already owned, six
researchable Roman/Italic cards, and +1.17 monthly research. Imperial Archives
opened its confirmation dialog and entered the queue successfully.

Evidence:

- `docs/screens/20260727_062355/final_clean_state.png`
- `docs/screens/20260727_054438/advances_day1_clean.png`
- `docs/screens/20260727_054539/queue_confirmed.png`

## Genuine-bankruptcy control

The driver then issued the installed `bankrupt XAA` console command in the same
player session. The Economy panel immediately displayed the normal red
bankruptcy banner and event. The Advances panel retained the queued advance but
monthly research fell from +1.17 to -0.03.

This control proves that the low-year adapter removes only the false engine
startup state. A real bankruptcy still receives the five-year timed state, UI
presentation, and complete native-equivalent penalty package.

Evidence:

- `docs/screens/20260727_062431/final_genuine_state.png`
- `docs/screens/20260727_054634/genuine_bankruptcy_research.png`

## Result

Pass. Rome is solvent and research-capable on day one, and genuine bankruptcy
remains functional. Static all-roster reachability remains covered by
`docs/m8/start_research_reachability.csv`.

# M12 Balance and AI Audit

This is the static half of the M12 balance pass. It records what the generated
data actually does and separates that evidence from measurements which require
the autonomous observer run.

## Research pacing

`tools/m8_knowledge.py` renders five ages, each with five independent ten-step
strands (250 advances). Per-entry research cost is generated as
`2 + age_index * 2 + depth * 0.5`, so each age spans a 4.5-point band and the
five age totals are 212.5, 312.5, 412.5, 512.5, and 612.5. The complete tree
therefore totals 2,062.5 nominal research-cost points. Every rendered advance
has a local `ai_weight` from 100 at strand roots down to 55 at leaves; there is
no negative or zero research preference in the tree.

This establishes monotonic structural pacing across the planned 1--476 age
windows. It cannot establish how rapidly a particular country completes it:
that depends on live income, literacy, institutions, and AI behaviour, which
must be sampled by the M12 observer session before declaring the pacing pass
complete.

## Population and inflation

`tools/popcheck.py` already locks the AD 1 baseline to the plan's 230 million
world target within its regional tolerances. There is no active
`global_population_growth` modifier in the generated ANTIQVITAS advance tree;
the vanilla advance copies which mention that field are disabled by M8. The
long-run growth result is consequently an engine/runtime measurement, not a
number this audit invents.

The active M6 coinage adapters are intentionally distinct:

- Rome's Augustan bimetallic law enables gold and silver minting, with a 0.03
  minting-inflation threshold and 0.10 income factor.
- Han's Wuzhu law enables copper minting, applies 0.10 copper inflation,
  offsets gold and silver inflation by 1.0, has a -0.025 threshold, and uses a
  0.20 income factor.

No generic M12 inflation modifier is added here. A third-century result must
be tested in a run before changing the historical-current or law surfaces.

## Casus-belli AI priorities

The installed `common/casus_belli/attack_threat.txt` establishes the additive
`ai_will_do = { add = { desc = "BASE" value = ... } }` form and uses 10 as its
normal threat baseline. M9 had accidentally assigned the AI-disable sentinel
`value = -1` to all ten custom CBs. That made all seven visible ancient CBs
unselectable by AI regardless of their historical eligibility rules.

M12 restores deliberately bounded baseline scores: punitive expedition 10,
client king 8, tribute 7, frontier rectification 16, loot raid 14, succession
intervention 6, and holy suppression 4. The three source-led future
unification CBs remain both invisible and AI-disabled. Eligibility conditions,
not a high arbitrary score, still constrain every active CB; a runtime
observer remains required to judge war frequency and outcomes.

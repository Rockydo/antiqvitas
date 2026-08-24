# R37 AD 11 peaceful Germania policy runtime proof

- Campaign: fresh no-debug Rome start, continuously advanced from 1.1.1.
- Exact checkpoint save: `autosave_25d724e6-8293-49bf-86c6-2000b0352075.eu5`, dated 11.1.1.
- AD 9 state: Rome remained at peace throughout the sourced Teutoburg window. The gated Teutoburg preparation and battle events did not fire.
- AD 10 fallback: *The Germania Frontier Policy* fired after the battle window. The observer selected its first historical option, the defensible Rhine command; the visible treasury, stability, and prestige deltas matched that option.
- Save persistence: the melted AD 11 save contains `antq_teutoburg_policy_resolved`. It contains none of `antq_teutoburg_battle_resolved`, `antq_teutoburg_varus`, `antq_teutoburg_chain_active`, or `antq_teutoburg_opponent`, proving that no phantom battle was recorded and the temporary Varus/chain scopes were cleaned up.
- Ruler gate: `docs/playtests/R37_M6_AD11.json` passes with Augustus (6861), Tiberius (6990), Livia (6910), and no regency.
- World gate: `docs/playtests/R37_STABILITY_AD11.json` passes: 462 real polities, no negative stability, no bankruptcy, no civil wars, complete mercenary cells, zero script errors, and zero actionable AI-command errors.
- Live evidence session: `docs/screens/R37_FINAL_PRODUCTION_ROME_AD1_100/`, especially `observer_0047.png` (AD 9 peaceful closing event), `r37_ad9_paused_after_illyrian.png` (peace at the battle-window opening), and `observer_0057.png` (post-policy AD 11).

This proves the player-Rome peace branch in the engine. It does not substitute for the separately required eligible-war and invalid-scope engine scenarios.

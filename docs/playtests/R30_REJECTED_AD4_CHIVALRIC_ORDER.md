# R30 rejected at AD 4: chivalric-order leakage

- Build: exact post-R29 accepted tree; fresh non-debug Rome campaign at
  1920×1080.
- Campaign: started at AD 1, reached 4.1.1 without a crash or new script-log
  line; the strict first-checkpoint economy/stability audit passed.
- Material defect: Marcus Servilius Servilian's live character menu exposed an
  enabled `Invite to Order of Chivalry` action.  This is an active early-modern
  mechanic, not merely stale wording, so the production run was rejected and
  EU5 was stopped immediately.
- Root cause: the mounted chivalric-order registry contains fifteen definitions;
  six German society definitions have no `potential` gate.  Consequently Rome
  could satisfy `has_chivalric_order = yes`, making the companion mounted
  character interaction reachable.
- Corrective contract: exact-mirror the complete mounted chivalric-order and
  character-interaction filename unions.  False-gate every order and every
  reviewed post-antique/specialized interaction, explicitly retain the portable
  ancient interaction set, and pin both unions in the installed-content census.
  Present the retained marriage system consistently as dynastic marriage.
- Evidence retained: `docs/screens/R30_FINAL_PRODUCTION_ROME_AD1_100/` and
  `docs/playtests/R30_FIRST_CHECKPOINT.json`.

R30 is not ship evidence.  The final AD 1–100 gate must restart from AD 1 on a
new fully validated build.

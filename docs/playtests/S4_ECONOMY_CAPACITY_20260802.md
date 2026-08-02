# S4 economy and opening capacity

## Result

PASS.

- Removed Principate `monthly_gold_income = 500`; seeded one 50%-capacity province
  food reserve. Fresh Rome: 6.34K gold and +20.31/month on 2 February.
- Parthia has no food purchase on 2 February. By 29 April, AI-adjusted Han and
  Satavahana run +73.72 and +5.34/month.
- Fresh engine `overpopulation`: 464 locations / 6,506,587 people before repair;
  zero after calibrated adapters at bookmark and after the February pulse.
- Four-minute maximum-speed observer was stable at native render scale. Only
  accepted HRE and engine assertion noise grew in `error.log`.

Evidence: `docs/screens/S4_FOOD_FIX_20260802/`,
`docs/screens/S4_FOOD_FIX_LONG_20260802/`,
`docs/screens/S4_CAPACITY_DAY1_20260802/`,
`docs/screens/S4_CAPACITY_MONTHLY_FINAL_20260802/`.

Static gate: `make validate` 164/164. Paired smoke: zero new lines at
`a687df49daa5aa30ad920d2a3915792d0dcb00413367375001e3c0602e6b760c`.

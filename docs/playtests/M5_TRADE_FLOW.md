# M5 trade-flow probe — 2026-07-19

## Scope

Test the M5 economic surface in a real AD 1 observer game using the installed
build's log-backed market exports. This is a milestone probe, not a pass.

## Procedure and evidence

1. Ran `make validate` and an enabled-playset `make smoke`: both green, with
   zero new normalized `error.log` lines.
2. Started a new game, entered Observer Mode, and let the live clock reach
   late May AD 1. `docs/screens/M5_trade_flow/roma_market_map.png` records the
   instantiated Roma market, stockpile, local balances, and Roman merchant
   capacity; `docs/screens/M5_trade_flow/cologne_market_trades.png` shows the
   market-trades interface.
3. Typed the locally documented `export_goods_by_market`,
   `export_market_capacity`, and `analyse_market` console commands with the
   game driver. The resulting `USER_DIR/docs` TSVs are the authoritative
   readback. They show 40 active named markets; pepper had 11.63 imports at
   Attock while Kodungallur and Khambat retained production surpluses. The
   Attock analysis listed Khambat, Kodungallur, and Anuradhapura as available
   pepper sources.
4. The same export found the required east-to-west/north and Rome-annona
   patterns incomplete: silk and incense had zero imports in this early run,
   and Roma produced 25.92 wheat with no import.
5. To test the generated RGO layer directly, changed Roma's source-led
   location-template RGO from wheat to clay and started a fresh observer
   session. `export_goods_by_market wheat` still reported Roma producing
   23.46 wheat and no import. A second fresh test added the exact
   `replace_path` array shape seen in local DLC manifests for the specific
   location-template path; it still yielded the same outcome and was removed.

## Result

**Fail/deferred for the M5 milestone gate.** The market/road layer itself
loads, ticks, and carries at least one real long-distance pepper transfer, but
the generated map-template raw-material changes are not runtime-effective in
the installed build. Consequently the complete grain-to-Roma, silk-westward,
incense-north, and pepper-to-Egypt acceptance pattern cannot be substantiated.
The green static and smoke result is preserved; recovery is tracked in
`BLOCKERS.md` and `KNOWN_ISSUES.md`.

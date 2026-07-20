# M12 game-rule audit

The installed `country_change` rule defaults to
`country_change_prohibited`. That prevents the autonomous game driver from
entering Observer after a valid selector load; it is not an input or
confirmation-dialog failure.

`tools/m12_game_rules.py` mirrors the exact installed
`main_menu/common/game_rules/00_game_rules.txt` file and changes only that one
default to `country_change_allowed`. It preserves every rule definition and
option, re-reads the installed source each validation, and rejects any patch
drift. The change is an observer/playtest accessibility setting; it does not
alter a country, historical current, economy, or AI rule.

The separate tutorial audit found all four installed tutorials use
`start_automatically = no` and no dated historical lesson text. The remaining
hint audit is retained as a separate M12 task because dated vanilla hints must
be disabled only after this exact-name overlay itself receives a clean menu
smoke.

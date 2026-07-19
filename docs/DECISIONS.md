# Technical and Design Decisions

## 2026-07-19 — Roster before setup generation

M3 starts from a CSV roster with explicit source, confidence, historical
capital, and verified-map-capital fields. A capital is `TBD` rather than guessed
until it is matched to the current game's extracted location keys. The build
validator rejects tag collisions and any asserted-but-invalid map key; this
keeps scholarly uncertainty visible while allowing the world-mapping pipeline
to proceed region by region.

## 2026-07-19 — Collision-free engine tags

The installed country database already defines 67 of the roster's natural
three-letter codes. `docs/world_1ad/tag_map.json` preserves a natural code as
the design identifier where possible and assigns a deterministic `X..` engine
tag only for a collision. This avoids unverified duplicate-key precedence while
keeping historical sources and later event writing readable through the map.

## 2026-07-19 — Country-key namespace and temporary definition profiles

Country tags are also localization keys. The M3 allocator therefore excludes
both three-character vanilla localization keys and engine-hash collisions, not
only country-definition tags. Build 24187685 proved `XAD` collides by hash with
`name_li3.mandarin_language`, so it is explicitly reserved and every generated
tag is smoke-tested before acceptance. The initial 133 country definitions use
only verified current culture/religion keys to keep M3 parsable; they are
explicitly temporary database defaults, not a claim about AD 1 map-mode
culture or faith. M4 replaces them with the sourced ancient trees.

The country database independently rejects duplicate display names and adds
rank titles itself. The roster remains historically precise, while its M3 UI
labels use `Roman Commonwealth` and `Parthia` rather than duplicate/compound
`Empire` forms. This is a technical display adaptation, not a historical
renaming.

## 2026-07-19 — Exact M3 start-manager mirror

The installed build has 25 `main_menu/setup/start` manager files. Their
empty, correctly named manager roots load with zero new errors, whereas leaving
any filename unmirrored would retain its additive 1337 state. The generated M3
mirror tracks that installed inventory during `make validate`, uses the
installed no-BOM convention, and is the safe base that later M3 generators
extend with country, ownership, pop, character, market, and other AD 1 state.

## 2026-07-19 — Verified-capital political slice

The first active AD 1 country manager assigns ownership only where a roster
capital directly matches a local EU5 location key: 50 entries at this point.
Each owns/controls its capital under a current-engine generic template and a
random ruler, both explicitly temporary until M6 supplies sourced state forms
and characters. This creates a real, smoke-clean map surface without inventing
territory from fuzzy city-name matches; all remaining ownership stays absent
until its source mapping exists.

## 2026-07-19 — Five campaign ages with a compatibility sentinel

The campaign has five real ages: Principate, High Empires, Crisis, Dominate,
and Migrations. The installed engine validates references to all six vanilla
age keys while loading unrelated vanilla databases. Once the M3 mirror is
ready, the generated M2 file will therefore retain `age_6_revolutions` as an
unreachable year-477 compatibility sentinel; it is not a campaign age and does
not make any date after 4 September 476 playable.

## 2026-07-19 — M2 deferment until setup replacement

The year-one calendar itself works, including a real save/reload. Enabling it
against the retained vanilla snapshot yields 868 ruler-term validation errors.
Because M3 already requires exact replacement of every setup manager and AD 1
ruler histories, the generated M2 layer is deferred rather than normalizing or
accepting those errors. This preserves the zero-new-error invariant.

## 2026-07-19 — M2 reactivated on the clean M3 mirror

Once all 25 start-manager files were exact-name mirrored, the M2 generator was
reactivated. A fresh smoke has zero new errors, and a driver-created AD 1
observer save reloads at `08:00, 1 January, 1` with the Age of Principate
header. M2 is therefore complete and tagged; the intentionally blank map in
its final report is the separate, visible M3 ownership backlog.

## 2026-07-19 — Metadata compatibility and thumbnail placement

The in-game version label is `1.3.1.1`, but the metadata comparator rejects
that form and accepts `1.3.11`. ANTIQVITAS therefore pins
`supported_game_version` to `1.3.11`, with the successful M1 menu smoke as
runtime evidence. The manifest declares `picture = "thumbnail.png"`; the same
512x512, sub-1-MB PNG is deliberately present both at the mod root (the
observed Workshop convention) and inside `.metadata` (the plan's required
placement). The linter enforces both copies while the engine convention remains
underdocumented.

## 2026-07-19 — Repository location

The repository root is `G:\antiqvitas`, on the same drive as the verified EU5
installation. This follows §2 and keeps generated content away from the nearly
full C: drive.

## 2026-07-19 — Build command compatibility

The host has no GNU Make. A repo-local `make.cmd` exposes the required
`make validate`, `make smoke`, and `make full` interface while the portable
`Makefile` documents equivalent targets.

## 2026-07-19 — User-directory relocation

The local executable contains the `user_dir` option and an actual launch proved
that `--user_dir=G:\antiqvitas_user_data` relocates logs and account state.
ANTIQVITAS uses that option plus
`G:\antiqvitas_user_data\mod\antiqvitas` as a junction to the repo. This leaves
only Steam itself on C: and prevents the project's logs, saves, screenshots, and
mod content from consuming the system drive.

## 2026-07-19 — Launcher format adaptation

Build 24187685 uses `USER_DIR\playsets.json`; no `launcher-v2.sqlite` is present.
`tools/enable_mod.py` therefore performs backed-up, atomic JSON mutations with a
read-back integrity check. It recognizes SQLite only to inspect and refuse an
unknown schema safely.

## 2026-07-19 — Baseline isolation

EU5 reads metadata from every directory below `USER_DIR\mod` even when its
playset entry is disabled. The vanilla M0 baseline was therefore captured with
the ANTIQVITAS junction temporarily absent. The link tool recreates it
idempotently once valid M1 metadata exists.

## 2026-07-19 — Current-script verification with documented fallback

The installed `script_docs` exporter did not return after two instrumented
attempts (see `BLOCKERS.md`). The project uses the community dump from
GlossMod/EU5-Modding-Mcp commit
`90790df9478a61035a2099c115b21ba7f04c3763` only as an index. Because that dump
is dated 2025-11-07, current-build behavior is accepted only when a key is also
present in local 1.3.1.1 scripts and a real-game smoke test is green.

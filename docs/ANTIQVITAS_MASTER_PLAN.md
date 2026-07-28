# ANTIQVITAS — Master Plan
## A total-conversion mod for Europa Universalis V: the world from 1 AD to the Fall of Rome (4 September 476)

**Audience:** the Codex agent executing this project under `/goal`. This document is the single source of truth. Read it fully before your first action. When this document and your general knowledge disagree about how EU5 works, **the local game files win, then this document, then your knowledge.**

**Spirit of the project:** rebuild the entire playable content of EU5 — start date, countries, populations, cultures, religions, economy, technology, warfare, diplomacy, and 475 years of scripted history — at the same density and quality as the vanilla 1337–1837 game, while reusing vanilla's Earth map geometry and engine systems wherever they still fit antiquity. Historical accuracy is the prime directive; where sources are genuinely unclear, make a defensible scholarly assumption and log it. Human mod teams make such calls constantly; so will you.

---

# PART I — OPERATIONS

## 1. Mission, pillars, non-goals

**Mission.** Ship a playable, stable, historically rigorous total conversion: single start date **1 January, AD 1**; end date **4 September, AD 476**. Any country playable, sandbox after start, with strong (not railroaded) historical currents: the Pax Romana, the Han restoration and collapse, the Sassanid revolution, the Crisis of the Third Century, Christianization, the Gupta golden age, the Völkerwanderung, and the fall of the West.

**Pillars, in priority order:**
1. **It loads and runs clean.** Zero new errors in `error.log` relative to the accepted baseline, at every commit.
2. **Historical accuracy.** Borders, rulers, populations, religions, goods, and events defensible against mainstream scholarship (sources in Appendix C). Assumptions logged, never silent.
3. **Vanilla-density content.** Not a thin reskin. Quantified targets in §22.
4. **Reuse before rebuild.** Vanilla map geometry, engine mechanics, 3D assets, UI, and sounds are kept unless antiquity demands otherwise.
5. **Fun.** Mechanics should produce the era's drama: legions making emperors, steppe confederations rising and shattering, plagues, church councils, barbarian foederati inside a crumbling empire.

**Non-goals (v1.0):** no new music or sound (vanilla audio stays); no new 3D unit/building models (reuse nearest vanilla assets); no map geometry changes (heightmap, location shapes, rivers, terrain untouched); no multiplayer balancing; no achievements; English localization only (other languages auto-filled with English text); no dates before AD 1 or after 476.

## 2. Environment and prerequisites

You run on the user's machine via Codex CLI with EU5 installed. Establish and record these in `config/local_paths.json` during M0 (ask nothing; discover programmatically, and only fall back to a `BLOCKERS.md` note if truly undiscoverable):

- **Host machine:** Windows, EU5 installed via **Steam in a secondary library on the D: or G: drive** (the user doesn't recall which — discover it). **The C: drive is nearly full: create nothing of size on C:.** The repo, all caches, venvs, generated art, and baselines live on the game's drive.
- `GAME_DIR`: discover it — parse every Steam library from `libraryfolders.vdf` (under the Steam install, typically `C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf`; each listed library has `<lib>\steamapps\common\Europa Universalis V`). Confirm by the presence of `game/` (with `in_game`, `main_menu`, `loading_screen`) and `binaries/eu5.exe`. Check D: and G: first, then all listed libraries.
- `WORK_DRIVE` / `REPO_DIR`: the drive containing `GAME_DIR` (fall back to whichever non-C: drive has the most free space). Repo at `<WORK_DRIVE>:\antiqvitas\` — **the git repo root is the mod folder** (plus `tools/`, `docs/`, `config/`, `baselines/`, `assets_queue/` as repo-only directories; that's fine since the game only reads `in_game/`, `main_menu/`, `loading_screen/`, `.metadata/`). Point pip/npm/ImageMagick temp and any model-asset caches here too (set `PIP_CACHE_DIR`, `TMP`/`TEMP` for your subprocesses).
- `USER_DIR`: `%USERPROFILE%\Documents\Paradox Interactive\Europa Universalis V` — contains `mod/`, `logs/`, `docs/`, `pdx_settings.json`. Resolve the real Documents path via `[Environment]::GetFolderPath('MyDocuments')` (it may be OneDrive-redirected). **Warnings (wiki-documented):** non-ASCII characters anywhere in the path break mod loading — if detected, log to BLOCKERS.md and try the user-dir relocation below.
- `MOD_DIR` (how the game sees the repo without touching C: for content): in M0, test in this order and record the winner in `config/local_paths.json`: **(a)** a launch option that relocates the whole user directory onto WORK_DRIVE (Paradox titles have historically supported flags like `--user_dir`; check `eu5.exe` supported args / wiki / `helplog`) — best outcome, since logs and saves leave C: too; **(b)** a **directory junction**: `cmd /c mklink /J "USER_DIR\mod\antiqvitas" "REPO_DIR"` — junctions need no admin rights and cost ~0 bytes on C:; **(c)** direct `-mod=`-style CLI mod loading if the engine supports it. Whichever wins, the repo stays on WORK_DRIVE and C: gains at most a zero-size link plus the game's own logs/saves.
- Tooling: Python 3.10+ (with **pyautogui + Pillow** for the game driver, §5), Git, **ImageMagick** (`magick`) for PNG→DDS conversion and DDS inspection, `sqlite3` (Python stdlib is fine). Install locally if missing (winget/choco), installing to WORK_DRIVE where the installer allows. If an image-generation tool is available in your harness, use it per §20; if not, write prompts to `assets_queue/IMAGE_REQUESTS.md` and continue with placeholder art.

**There are no human-in-the-loop steps. None.** The user will not run console commands, click launchers, or playtest. Everything below that older mod workflows treat as manual, you automate:
1. **Steam must be running** for the game to launch (Steam DRM). Detect the `steam.exe` process; if absent, start it (path from the registry key `HKCU\Software\Valve\Steam\SteamExe` or the default install) and wait for it to settle before launching `eu5.exe` directly with flags.
2. **Playset/mod enablement is scripted, not clicked.** The Paradox launcher stores playsets in a SQLite DB in `USER_DIR` (`launcher-v2.sqlite` — verify name/schema in M0; community tools like Irony Mod Manager and paradox-launcher scripts document it). `tools/enable_mod.py` backs up the DB, then inserts/activates a playset containing `antiqvitas`. If option (c) above (CLI mod loading) works, prefer it and skip the DB entirely.
3. **Console commands are typed by the game driver** (`tools/gamedriver.py`, §5): it launches `eu5.exe -debug_mode`, waits for the menu, opens the console and types `script_docs`, `dump_data_types`, `helplog` — harvesting the authoritative effect/trigger/scope docs into `USER_DIR/docs` and `USER_DIR/logs` with zero human keystrokes. Fallback if the driver can't reach the console yet: the community mirrors `script_docs` output on GitHub — fetch the dump matching the installed game version and log the substitution in ASSUMPTIONS.md.

## 3. Verified engine facts (as of July 2026) and what you must re-verify

These were verified against the EU5 wiki and community sources. Treat as reliable but **re-confirm each against local files in M0**, because patches change details.

**Mod structure (verified):**
- Mod lives at `USER_DIR/mod/<name>/`, mirroring the game's `game/` folder. Top-level folders are exactly `in_game/`, `main_menu/`, `loading_screen/` — e.g. `in_game/common/...`, `in_game/events/...`, `in_game/setup/...`. Wrong nesting fails **silently**.
- `.metadata/metadata.json` is required (name, id, version, supported game version, etc.) plus `.metadata/thumbnail.png` (512×512, <1 MB). Check vanilla/other mods for the full schema, including whether a `replace_paths`-style key exists; if it does, use it to blank out vanilla setup/content directories cleanly. If not, use same-filename overrides (a modded file with a vanilla filename replaces the vanilla file completely).
- Among conflicting files, last-alphabetical filename wins over launcher order — never rely on that; use exact-name overrides.

**Setup system (verified — this is the heart of the conversion):**
- `in_game/setup/start/` holds the "savefile-like" start state via managers: `institution_manager`, `religion_manager`, `market_manager`, `dynasty_manager`, `character_db`, `locations` (with `define_pop`, `rank`, `town_setup`, per-location institutions, `timed_modifiers`), `road_network`, `countries` (ownership verbs `own_control_core / own_control_integrated / own_control_conquered / own_core / control` etc.; `capital`, `country_rank`, `type = pop` for pop-based societies, `add_pops_from_locations`, `discovered_provinces/areas/regions`, `starting_technology_level`, `accepted_cultures`, `currency_data`, `government { ruler / heir / consort / type / reforms / laws / societal-value sliders / parliament / privilege / ruler_term ... }`, `include = <template>`), `diplomacy_manager` (opinions, rivals, guarantees, `dependency` for subjects), `war_manager` (wars, civil wars, truces), `international_organization_manager`, `exploration_manager`, `disease_outbreak_manager`, `colony_manager`, `development`, `work_of_art_manager`.
- `in_game/setup/countries/` holds **country_definitions** (colors, unit colors, `culture_definition`, `religion_definition`, regnal name lists, `is_historic`, difficulty). Every tag used in setup must be defined here.
- `in_game/setup/templates/` holds reusable country templates (`include` by filename).
- **Encoding matrix (critical, wiki-documented):** files in `setup/start` = UTF-8 **without** BOM; files in `setup/countries` and `setup/templates` = UTF-8 **with** BOM; localization `.yml` = UTF-8 **with** BOM, filenames ending `_l_english.yml`. Most other script `.txt` follow vanilla (verify per-folder by sniffing vanilla files' BOMs in M0 and encoding the rule table into the linter).
- **Setup managers are additive.** To *remove* vanilla 1337 entries you must override the entire vanilla file (same filename, replacement content) — inventory every vanilla `setup/` file and mirror-replace all of them. Pop definitions: `size = 1` means 1,000 people. `define_pop` numbers get adjusted at game start by caps/buildings/levies; the `-leavepops` launch flag disables those adjustments for verifying raw setup numbers.
- Load-order constraints: dynasties before characters that use them; parents/spouses before children referencing them.
- Character DB fields (verified): names via loc keys, culture, religion, adm/dip/mil, birth/death dates, traits by category (ruler/general/admiral/cabinet/health/child/religious_figure/artist), tag, estate, dynasty, father/mother/spouse, fertility.

**Precedents proving feasibility (verified to exist — study their techniques):**
- **EU5-1444-Start-Date** (GitHub, `EU5-1444-Team/EU5-1444-Start-Date`): changes the start date to 1444.11.11. Clone it read-only in M0 and extract *exactly* which define(s)/files move the start date. This settles the project's single biggest technical unknown.
- **Modern Universalis** (modernuniversalis.com): a year-2000 total conversion that keeps vanilla terrain/locations and rebuilds countries, pops, goods, and tech — the same architecture as ours.
- License note: study techniques and file locations freely; do **not** copy their content/assets unless their license explicitly permits, and never copy content from any third-party mod into ours. Copying *vanilla* files into the mod as override bases is standard practice and fine.

**Debug & test surface (verified):**
- Launch flags: `-debug_mode` (console, dev tools, and a **file watcher that hot-reloads changed mod files** — on_actions excluded), `-console` (separate console window), `-leavepops`, `-map_editor`, `--ignore-disable-mods-on-crash` (forces the same playset after a loading crash — essential for our loop, since a crash otherwise silently disables mods on next launch).
- Logs: `USER_DIR/logs/error.log` (script errors/warnings, dumped at load and runtime), plus `game.log` and others in the same folder.
- Console commands: `script_docs`, `dump_data_types`, `helplog` (full command list for the installed build), `error`, `gamelog`, `reload`, observer tools (fog removal; Ctrl+click a country to switch control) — use `helplog` output in M0 to write `docs/REF_console_commands.md`.
- **There is no headless/autotest mode.** The automated loop is therefore: static validation (fast, every edit) → real game launch to menu/map with log diffing (slow, per task-batch) → **driver-run in-game verification at milestones** (the pyautogui game driver of §4/§5 navigates menus, runs console commands, starts observer games, and screenshots the results for you to inspect — no human involved at any tier).
- Editor/validation ecosystem: CWTools (VS Code, EU5 rules exist; check whether its CLI can consume the EU5 ruleset for headless linting — if yes, wire into Tier 1), IntelliJ Paradox Language Support, EU5-ModHelper (has a JS Paradox parser worth reading), Arcanum (map/data editor), PDX Workshop Manager (publishing), Jomini.js/Rakaly parsers. `script_docs` output is also mirrored by the community on GitHub.

**Things to verify in M0 (write findings to `docs/ENGINE_FACTS.md` before touching content):**
1. Exact mechanism for start/end date (defines key names; confirm against the 1444 mod and `loading_screen/common/defines/`). Confirm the engine accepts year 1 and 3-digit years in dates, saves, and UI. **Contingency C-1:** if very low years misbehave anywhere, shift the whole calendar to **AUC** (Ab Urbe Condita: AD 1 = 754 AUC, end = 1229 AUC) — thematically Roman, mechanically safe, purely a data/localization change if all dates are generated from a single constants table (so: generate all dates through `tools/dates.py` from day one).
2. metadata.json full schema; existence of replace-path support.
3. Whether vanilla flags are DDS textures, a layered coat-of-arms system, or both (read the wiki `Flag_modding` page + `in_game/gfx` + country_definitions). Adapt §20 accordingly.
4. Pop types list (expect nobles/clergy/burghers/peasants/tribesmen/slaves or similar), estate keys, government type keys, law/policy keys, societal value slider keys, location rank ladder, country rank ladder, subject type list, IO types, unit types, goods list, building list, advance/age/institution structure, disease types, character trait keys — extract all from vanilla into machine-readable symbol tables under `docs/vanilla_symbols/*.json` (a script does this; see §4).
5. Which content is DLC-gated (the game has post-release DLC by now, e.g. a Byzantine-focused pack): the mod targets **base game**; detect DLC folders and ensure our overrides also neutralize DLC-added 1337 content when present (graceful if absent).
6. The full list of vanilla `setup/start` files (for mirror-replacement) and vanilla `events/`, `common/situations/`, `common/disasters/` files (to disable and supersede).

## 4. Phase 0 tooling you must build (repo `tools/`)

Build these before content work. They are the feedback loop the user asked for.

- `tools/find_game.py` — parses Steam's `libraryfolders.vdf` across all drives, locates GAME_DIR (D:/G: first), picks WORK_DRIVE, resolves the real Documents/USER_DIR path, verifies path ASCII-ness and free space, and writes `config/local_paths.json`. Companions: `tools/link_mod.ps1` (junction or user-dir relocation per §2) and `tools/steam_ensure.ps1` (start Steam if not running, wait until responsive).
- `tools/enable_mod.py` — backs up then edits the launcher's playset SQLite DB to register and activate `antiqvitas` (schema discovered in M0; idempotent; restores the backup on any integrity failure). Skipped entirely if direct CLI mod loading works.
- `tools/gamedriver.py` — the **autonomous in-game hand**: pyautogui + screenshots. Capabilities, built up incrementally: (a) launch `eu5.exe` with flags and detect menu-ready via log sentinel + pixel check; (b) open the console (`` ` ``) and type arbitrary commands (`script_docs`, `helplog`, `error`, `reload`, fog/observer commands), reading results back from `USER_DIR/logs` rather than the screen wherever possible; (c) navigate to and start a new game / observer session by screenshot-guided clicking — you inspect each screenshot and issue the next click, then replay recorded click sequences once they're stable; (d) set game speed, let time run, screenshot on a cadence, watch error.log and date progression; (e) clean shutdown/kill. **Robustness rules:** force a fixed windowed resolution via `pdx_settings.json` before driving; save every screenshot to `docs/screens/<session>/`; verify state after every input (screenshot diff or log line) and retry ×2; on repeated UI failure, degrade gracefully to launch+log-diff verification and record the coverage gap in KNOWN_ISSUES.md — never wait for a human.
- `tools/extract_vanilla.py` — walks `GAME_DIR/game`, parses all Paradox-script files (write a tolerant Clausewitz tokenizer: `key = value`, nested `{}`, quoted strings, `#` comments, `rgb {}`/`hsv {}`), and emits `docs/vanilla_symbols/` JSON: every location key, province/area/region hierarchy, culture, religion, good, building, unit, advance, government, law, estate, subject type, IO, pop type, trait, event id, loc key. Also record per-folder file inventories and per-file BOM/encoding. Re-run after any game patch.
- `tools/pdxlint.py` — Tier-0 validator over the mod: encoding matrix compliance; brace/quote balance; duplicate keys where illegal; every referenced symbol (tag, culture, religion, location, good, trait, law, …) resolves against vanilla+mod symbol tables; setup ordering constraints (dynasty→character, parent→child); date format and range (`1.1.1`–`476.9.4`); localization coverage (every new key has an English line; report orphans); every referenced icon/texture path exists with plausible DDS dimensions; metadata.json schema.
- `tools/popcheck.py` — sums `define_pop` by location→province→region→our historical macro-regions and diffs against the population targets table (§12.4), flagging deviations >15%. Also validates culture/religion shares per region against §10–§11 rules.
- `tools/smoketest.py` — launches `eu5.exe -debug_mode --ignore-disable-mods-on-crash` (plus `-leavepops` variant when testing pops), waits for load (detect via log growth quiescence or a sentinel line; cap ~8 min), terminates the process, then diffs `error.log` against `baselines/vanilla_error.log` (captured in M0 *before* the mod exists) and against `baselines/last_accepted_error.log`. Output: NEW errors (fail), fixed errors, unchanged. Update `last_accepted` only on explicit green.
- `tools/dds.py` — wraps ImageMagick: PNG→DDS with per-usage compression/mipmap settings mirrored from vanilla (`magick identify` vanilla samples to learn each asset class's format/size), and a checker used by pdxlint.
- `tools/dates.py` — single source for all scripted dates (loads `docs/timeline.csv`), so Contingency C-1 (AUC shift) is one flag.
- `tools/gen_loc_stubs.py` — auto-creates English loc entries for new keys with TODO markers, and clones `l_english` content into the other language files so non-English clients see English rather than raw keys.
- `Makefile` (or `validate.ps1`/`justfile` per OS): `make validate` = pdxlint + popcheck (+ CWTools CLI if wired); `make smoke` = smoketest; `make full` = both.

## 5. The validation loop (non-negotiable protocol)

- **Every task:** edit → `make validate` → fix until green.
- **Every task-batch that touches game-visible content** (setup, common, events, gfx, loc): `make smoke` → zero NEW error.log lines vs baseline → only then commit. Batch related edits; a full launch takes minutes, so don't smoke per-file — but never commit game-visible changes unsmoked.
- **Never commit red.** If blocked after 2 honest attempts, revert to green, write `BLOCKERS.md` (what, why, what you tried, proposed paths), pick the next task.
- **Milestone gates:** each milestone in §22 ends with `make full` green **plus** a driver-run in-game verification you design for that milestone (which map modes to open, which console commands to run, what the screenshots must show). Write the findings — with the screenshots — to `docs/playtests/M<N>_REPORT.md`, judging pass/fail yourself against the milestone's acceptance criteria. If the driver can't yet perform a step, note the exact gap in the report and in KNOWN_ISSUES.md, keep the milestone's log-diff bar mandatory, and move on: **the project never blocks on a human.**
- **Pop-truth runs:** when validating population setup, smoke once with `-leavepops` and once without; record both.
- **After any game patch** (detect version change in launcher metadata/game files): re-run `extract_vanilla.py`, re-capture the vanilla baseline log, re-validate.

## 6. Working agreements

- **Autonomy is total:** the user is a spectator. Never wait for them — not for a launcher click, a console command, a playtest, or an approval. Anything a human modder would do by hand, you do via tooling (§4) or route around. Make the call, log it. `docs/DECISIONS.md` (technical/design choices, dated, with reasoning) and `docs/ASSUMPTIONS.md` (historical judgment calls, with the sources weighed — mark contested items †). `docs/PROGRESS.md` gets a dated entry per session: done, validated, next.
- **Git:** small conventional commits (`setup: seed Gallia pops`, `events: crisis of the third century pt2`). Tag milestone completions (`M3-done`). Never commit `baselines/` game logs with user paths scrubbed? — keep them, but scrub the Windows username from committed logs.
- **Style guide for script:** tabs like vanilla; one concern per file; file prefix `zzz_antq_` only where alphabetical override order matters, otherwise `antq_`; every new key namespaced `antq_` except tags and location-bound keys; comments cite dates/sources for historical claims (`# Rhandeia compromise, AD 63`).
- **Vanilla data is read-only.** Never edit `GAME_DIR`. Copy-then-modify into the mod.
- **Research protocol:** you may browse for historical facts. Source hierarchy: (1) the datasets in Appendix C (Pleiades, Book of Han census, etc.), (2) academic references (Cambridge Ancient History, Oxford Classical Dictionary, Barrington Atlas naming), (3) Wikipedia for gazetteer/date lookups (fine for uncontroversial facts), (4) never fan wikis for history (fine for EU5 mechanics). Do not copy prose; you're extracting facts into script.
- **Sensitive content:** slavery, religious persecution, and plague are simulated factually with the same sober register vanilla EU5 uses for its own dark history — mechanics, not endorsement; no gratuitous text or imagery. Religious-founding events (e.g., the Crucifixion c. AD 30–33 spawning Christianity, Mani's revelation, the Buddhist councils) are written respectfully and factually, as Paradox's own titles do.
- **When the doc is wrong:** if a verified engine fact contradicts Part II's design, adapt the design, log it in DECISIONS.md, and keep the historical intent.

---

# PART II — DESIGN BIBLE

## 7. Architecture decisions (locked unless the engine forces otherwise)

1. **Reuse the vanilla Earth map wholesale** — heightmap, ~27k locations, rivers, terrain, climate, harbors, impassables. Geography barely changed in 1300 years. All conversion happens in *data*: ownership, pops, names, goods, roads.
2. **Renaming without remapping:** keep vanilla location *keys*; change display names via localization overrides and EU5's culture-based dynamic naming (vanilla already renames locations by owner culture — extend those tables: Londinium/Lugdunum/Byzantion/Chang'an…). Use the **Pleiades gazetteer** (Appendix C) to auto-match ancient toponyms to locations by coordinates for the Greco-Roman world; Book of Han commandery lists for China; curated lists elsewhere. Locations with no attested ancient name keep a plausible culture-appropriate form (log method in ASSUMPTIONS.md).
3. **Societies of Pops (SoPs) are the era's backbone** for non-state peoples: most of Germania, the steppe beyond the confederations, pre-state Britain's fringes, Arabia's interior, most of sub-Saharan Africa, the Americas outside Mesoamerican/Andean states, Siberia, Japan at start, Australia. Settled-tag vs SoP decisions per region in §8. SoP→settled formation events model state genesis (Aksum, Yamato, Frankish/Alemannic confederations…).
4. **Single start, strong currents:** one bookmark (AD 1). History unfolds through situations/disasters/events with real dates but player/AI-divertible outcomes. A game rule **"Historical Currents: Strong / Mild / Off"** scales their weight if game rules are moddable (verify; else default Strong).
5. **Empire-scale is modeled honestly:** Rome and Han are *huge single tags* with internal-pressure mechanics (control, estates, legitimacy, civil-war disasters) rather than pre-split. Their client rings are subjects.
6. **New-world isolation preserved:** no contact mechanics needed — era tech simply cannot cross oceans; set per-civilization discovered-regions to authentic known worlds (§16.4) and gate ocean-capable navigation out of the advance trees entirely.
7. **Dates:** all scripted dates flow from `docs/timeline.csv` through `tools/dates.py` (Contingency C-1 ready).
8. **Tag namespace:** 3-letter tags, table in `docs/tags.csv`; reserve blocks: R** Rome-related, H** Sinitic, dynamic-formation tags listed in §17.4.

## 8. The world at 1 January, AD 1 — region by region

Full machine-readable roster lives in `docs/world_1ad/*.csv` (you create it in M3 from this section + research). Below: the design-complete summary. **Tier 1** regions get exhaustive treatment (every polity, characters, flavor); **Tier 2** solid (all polities, key characters, main events); **Tier 3** accurate setup + light scripting. († = contested scholarship, log it.)

### 8.1 Rome (Tier 1) — tag ROM
Augustus (Imperator Caesar Augustus, b. 63 BC), Julio-Claudian dynasty; heir **Gaius Caesar** (Tiberius is adopted only in AD 4 — do not pre-script it). Government: **Principate** (§13). Capital Roma. ~45M pops. Owns (as integrated/conquered per date of annexation): Italia, the Hispaniae, the four Gauls, Illyricum, Macedonia, Achaea, Asia, Bithynia-Pontus, Galatia, Syria, Aegyptus, Africa Proconsularis, Cyrenaica-Creta, Sicilia, Sardinia-Corsica, Raetia, Noricum, Moesia (forming), and a **low-control conquered zone in Germania to the Weser/Elbe** (the *immensum bellum* is literally ongoing AD 1–5 — start with a live pacification situation; Teutoburg in AD 9 flips it). Client-kingdom subjects (subject type `antq_client_kingdom`): Judea's Herodian tetrarchies (Archelaus in Judea/Samaria, Antipas in Galilee-Perea, Philip in the north), Nabataea (Aretas IV), Cappadocia (Archelaus), Commagene, Emesa, minor Cilician kings, Thrace (Odrysian), Bosporan Kingdom (Dynamis†), Mauretania (Juba II), Armenia **contested with Parthia** (throne disputed at AD 1; the Gaius Caesar eastern settlement of AD 1–4 is your opening Rome-Parthia situation).
Flavor systems: Praetorian Guard, annona (Egyptian/African grain to Roma — market + building mechanics), Senate estate, legions as an army-estate, roads network seeded from ORBIS/itineraries, limes buildable.

### 8.2 Parthia & the Iranian world (Tier 1) — tag PAR
Arsacid Phraates V ruling with queen-mother Musa† (scandal events available). Feudal King-of-Kings government: sub-king subjects Characene, Elymais, Persis (Frataraka heirs — **future Sassanid cradle**), Media Atropatene, Adiabene, Osroene, Gordyene; Hatra rises ~1st c.; Indo-Parthian Gondophares breaks off ~AD 19 (scripted). Caucasus: Armenia (great-power football), Iberia (Pharasmanes I accedes ~AD 1), Colchis/Lazica, Caucasian Albania. Steppe-facing: Sakastan, Margiana.

### 8.3 China & the Han world (Tier 1) — tag HAN
Western Han, Emperor Ping (age 9), **Wang Mang regent** — the usurpation of AD 9, Yellow River avulsion floods (~AD 11), Red Eyebrows, and the Guangwu restoration (25) are the opening mega-arc. Government: Imperial Bureaucracy with **Mandate of Heaven** legitimacy (§13). Population anchored to the **census of AD 2: 57,671,400** — commandery-level data exists; use it (Appendix C). Protectorate of the Western Regions: Tarim city-states (Loulan, Khotan, Kucha, Kashgar, Turfan…) as tributaries. Vietnam: Jiaozhi under Han (Trung sisters revolt 40–43). Dian & Nanyue already annexed. **Xiongnu** (XIO): unified under Wuzhuliu Chanyu, at heqin peace with Han; north–south split scripted 48. Korea: Han's Lelang commandery; Goguryeo (King Yuri), Buyeo; Samhan confederacies (Mahan/Jinhan/Byeonhan) as SoP-clusters with Baekje/Silla formation arcs (traditional founding dates kept as tiny chiefdom tags†). Japan: Wa — Yayoi SoPs; Himiko/Yamatai embassy 238 flavor; Yamato formable ~250–300.

### 8.4 India & the Indian Ocean (Tier 2) — 
Satavahana (Deccan; weak interregnum phase at AD 1†), Indo-Scythian (Saka) realms: Gandhara–Taxila under "Azes"† and the Northern Satraps toward Mathura (Rajuvula); **Strato II's Indo-Greek rump** in the eastern Punjab (annexed ~AD 10 — last Hellenistic state, lovely flavor); the **Yuezhi confederation in Bactria** (YUE) with the Kushan unification formable (Kujula Kadphises, ~AD 30–50) → Kanishka's peak (~127, Buddhist council, Silk Road apex) → 3rd-c. decline under Sassanid Kushanshahs → **Gupta** formable from Magadha ~320 (Samudragupta's digvijaya as a conquest situation; Chandragupta II peak; Hephthalite invasions from ~455 vs Skandagupta). Ganasangha **republics** (Yaudheya, Arjunayana, Kuninda) with republic government. Kalinga/Mahameghavahana. Tamilakam: Chera, Chola, Pandya (Sangam era) + Roman pepper trade via Muziris; Anuradhapura in Lanka. Monsoon (Hippalus) Indian-Ocean trade is live at start: Red Sea ports ↔ Barygaza/Muziris.

### 8.5 Africa (Tier 2)
Roman North Africa + client Mauretania (annexed 40–44, Aedemon revolt scripted; Tacfarinas war 17–24). **Kush/Meroë** (Natakamani & Amanitore co-rule — the great builders), post-25 BC treaty with Rome. Blemmyes/Beja SoPs. **Aksum**: emerging polity — start as advanced chiefdom, imperialize ~100 (Zoskales per the Periplus), Ezana's conversion ~330s and conquest of Meroë ~350. Garamantes (Fezzan state, trans-Saharan trade). Sahara/Sahel: Gaetulian and Berber SoPs; Djenné-Djenno on the Niger as a rare settled town-cluster†; W. African iron-age SoPs (Nok fading). **Bantu expansion** modeled as a slow scripted SoP culture-frontier moving east/south across the whole 475 years (periodic pulse events — elegant and accurate). Horn/coast: Barbaria SoPs, early Swahili-coast precursors late-period†.

### 8.6 Arabia (Tier 2)
Nabataea (Roman client, annexed 106 → Arabia Petraea). Yemen four-way: Saba, Himyar (rising; unifies by ~275; **shifts to monotheism ~380s** — Rahmanism/Judaizing kings†), Qataban, Hadramawt. Kindah in the interior; Lakhmids (al-Hira, pro-Persian) and Ghassanids (pro-Roman) emerge 3rd–4th c. as the classic buffer-client pair (late-game subject flavor). Interior bedouin SoPs; Arabian polytheism religion with Kaaba flavor.

### 8.7 Barbaricum Europe (Tier 1 for Germania/Britain, Tier 2 east)
Germania: **Marcomanni under Maroboduus** (a real organized kingdom in Bohemia — settled tag), Cherusci (with young **Arminius** currently in Roman auxiliary service — he is the Teutoburg situation's protagonist), Chatti, Frisii, Batavi (client), Langobardi, Semnones, Hermunduri, Quadi, **Gutones on the Vistula** (proto-Goths — scripted migration to the Pontic steppe ~160–230 → Tervingi/Greuthungi), Vandili, Rugii, Burgundiones, Angles/Saxons/Jutes (raiders late; *adventus Saxonum* ~449†), Suiones and Scandinavian SoPs, Aestii (Balts), **Venedi (proto-Slavs — deliberately quiet all game; their hour is post-476)**, Finnic SoPs. Confederation formables: Alemanni (~213), Franks (~250s), Saxons, Picts (~297 merge of Caledonii).
Britain: pre-conquest kingdoms — Catuvellauni (Tasciovanus; Cunobelinus ~AD 9), Trinovantes, Iceni (Boudica 60–61), Brigantes (Cartimandua arc), Atrebates (Verica, the 43 pretext), Silures, Ordovices, Dumnonii, Cantiaci; Caledonian SoPs; Hibernia as túath SoP-clusters (Ulaid etc.; Palladius/Patrick 431/432). Claudian invasion 43 = flagship situation; Agricola, walls (122/142), third-century raids, Constantine III & the 407–410 abandonment.
Danube/east: fragmented Dacian kingdoms (post-Burebista) with a Decebalus reunification situation ~85 → Trajan's wars 101–106 → Roman Dacia → Aurelian evacuation ~271–275; Getae, Bastarnae; Sarmatians (Iazyges — scripted migration to the Tisza plain ~20–50, Roxolani, Aorsi, Siraces) and Alans; Scythian remnants in Crimea; Bosporan Kingdom as the grain-and-fur north-Pontic hinge.

### 8.8 Central Asia & steppe (Tier 2)
Kangju, Wusun, Dayuan (Fergana), Sogdian city-states (Marakanda…), Khwarazm. Xiongnu as the start-date steppe IO/confederation; Xianbei and Wuhuan rise as Xiongnu fractures (48 split, 89–91 Han-Xianbei hammer, 2nd-c. Tanshihuai confederation pulse†); Dingling/Tiele; **Huns spawn as an invader confederation on the Volga ~370** (the endgame catalyst; Attila arc 434–453; Nedao shatter 454); Rouran rise in the east 4th–5th c.; **Hephthalites** hit both Persia and India from ~440s.

### 8.9 Southeast Asia & Oceania (Tier 3)
Pyu city-states, Mon precursors, proto-Khmer; **Funan** founds 1st c. (Kaundinya legend event; Oc Eo as the Rome-China entrepôt — Roman goods attested); **Champa** founds 192 (Linyi revolt from Han Rinan — scripted); early Malay/Javanese polities†; Philippine and Bornean SoPs. Oceania: **western Polynesia only** (Tonga/Samoa/Fiji settled); eastern Polynesia, Hawai'i, Rapa Nui, Aotearoa **empty** (settlement is post-period per modern chronology — audit vanilla and strip). Madagascar empty (arrival debated ~350–550†; optional late flavor event, no pops by default). Australia: Aboriginal SoPs, no state mechanics.

### 8.10 The Americas (Tier 3, accuracy still mandatory)
Mesoamerica: **Teotihuacan** (rising; Sun Pyramid built ~100–200 — great-work event; apex 350–450; the **378 "entrada"** into the Maya lowlands under Siyaj K'ak' is a scripted intervention), Cuicuilco (destroyed by the Xitle eruption — volcano disaster, window 200–315†), Preclassic→Classic Maya (El Mirador collapse ~150; Tikal & rivals' dynasties consolidate; long-count dated flavor), Monte Albán (Zapotec), Epi-Olmec remnant, West Mexican shaft-tomb SoPs. Andes: **Moche** (forms ~100), Nazca, Lima, Recuay, early **Tiwanaku**; Chibcha-area chiefdom SoPs. North America: Hopewell interaction sphere (SoP network with an exchange-flavor mechanic), Basketmaker II Southwest, Dorset Arctic, coastal/plains SoPs. Amazonia/Caribbean: Arawak/Tupi/Carib SoPs. **Empty-lands audit:** Iceland, Azores, Madeira, Cape Verde, Bermuda, NZ, E. Polynesia must have zero pops (Canaries stay inhabited — Guanches).

## 9. The timeline, AD 1–476 — the scripted-history spine

Encode as `docs/timeline.csv` (`date,key,type[situation|disaster|event|tagswitch|formation],region,summary,rails_strength`). The table below is the authoritative seed — every row becomes content. (~ = window, not fixed date.)

| Date | What | Type |
|---|---|---|
| 1–4 | Gaius Caesar's eastern settlement; Armenia contested (Rome/Parthia) | situation |
| 1–5 | *Immensum bellum* — Germania pacification | situation |
| 6–9 | Great Illyrian Revolt (Bellum Batonianum) | situation |
| 9 | **Teutoburg Forest** — Arminius; Rome loses Germania Magna | situation climax |
| 9–23 | **Wang Mang's Xin dynasty**; Yellow R. floods ~11; Red Eyebrows; 25 Eastern Han restoration | mega-situation |
| 14 | Augustus dies; first succession test of the Principate | event chain |
| 17–24 | Tacfarinas' war (Numidia) | situation |
| 21 | Florus & Sacrovir Gallic revolt | event |
| ~30–50 | Kushan unification of the Yuezhi (Kujula) | formation |
| 30–33 | The Crucifixion; Christianity founded in Judea | religion spawn |
| 40–43 | Trung sisters' revolt (Jiaozhi) | situation |
| 40–44 | Mauretania annexed; Aedemon revolt | situation |
| 43 | **Claudian invasion of Britain** | mega-situation |
| 48 | Xiongnu split north/south | tagswitch |
| 58–63 | Roman–Parthian war over Armenia; Rhandeia; 66 Tiridates crowned by Nero (Arsacid Armenia under Roman blessing — condominium peace) | situation |
| 60–61 | Boudica | situation |
| 64 | Great Fire of Rome | event |
| 65–68 | Buddhism reaches the Han court (White Horse Temple) | institution/religion spread |
| 66–73 | **Great Jewish Revolt**; 70 Temple destroyed (Judaism → Rabbinic transformation chain); 73 Masada | mega-situation |
| 68–69 | **Year of the Four Emperors** | disaster |
| 69–70 | Batavian revolt (Civilis) | situation |
| 79 | Vesuvius: Pompeii & Herculaneum | disaster event |
| 83 | Mons Graupius (Agricola in Caledonia) | event |
| 85–92 | Domitian's Dacian & Suebic wars; Decebalus unifies Dacia | situation |
| 89–91 | Han–Xianbei destroy the Northern Xiongnu | situation |
| 97 | Gan Ying sent toward Rome (reaches the Gulf) | flavor event |
| 101–106 | **Trajan's Dacian Wars** → provincia Dacia; 106 Nabataea annexed | mega-situation |
| 105 | Cai Lun standardizes papermaking | institution birth |
| 113–117 | Trajan's Parthian war (brief Mesopotamia); 115–117 Kitos War diaspora revolts | situation |
| 122 / 142 | Hadrian's Wall / Antonine Wall | building events |
| ~127 | Kanishka: Kushan apogee, 4th Buddhist council | situation |
| 132–135 | Bar Kokhba revolt | situation |
| 142 | Way of the Celestial Masters founded (organized Daoism; Hanzhong theocracy 191–215) | religion event |
| 161–166 | Verus' Parthian war; Ctesiphon sacked | situation |
| **165–180** | **Antonine Plague** (empire-wide + echoes in Han records 171–185) | pandemic disaster |
| 166 | "Daqin embassy" reaches the Han court by sea | flavor event |
| **166–180** | **Marcomannic Wars** (pressure wave from Gothic migration behind) | mega-situation |
| ~160–230 | Gothic migration Vistula → Pontic steppe (Wielbark→Chernyakhov) | scripted migration |
| 184 | **Yellow Turban Rebellion** → warlord era; 189 Dong Zhuo | mega-situation |
| 192 | Champa (Linyi) founds | formation |
| 193 | Year of the Five Emperors → Severans; 197–198 Ctesiphon sacked, Mesopotamia province | situation |
| 208–211 | Severus in Caledonia; 212 **Constitutio Antoniniana** (citizenship for all free provincials — pop legal-status conversion event) | events |
| ~213 / ~250s | Alemanni / Franks confederate | formations |
| 220 → 265/280 | Han abdication → **Three Kingdoms** (Wei/Shu/Wu) → Jin unification 280 | mega-arc |
| **224** | **Ardashir I: the Sassanid revolution** (Persis overthrows Parthia; Zoroastrian state church reform) | tagswitch mega-situation |
| **235–284** | **CRISIS OF THE THIRD CENTURY** — barracks emperors, debasement/inflation, plague of Cyprian 249–262, Abritus 251 (Decius killed by Goths), Heruli sack Athens 267, Naissus 269, **Gallic Empire 260–274** and **Palmyra under Zenobia 267–273** as playable breakaways, Valerian captured at Edessa 260, Aurelian's reconquest + Walls of Rome + Sol Invictus 274, Dacia evacuated ~271–275, Diocletian ends it 284 | flagship disaster |
| ~240s–274 | Mani preaches; Manichaeism spreads (persecuted by both empires) | religion spawn |
| 284–305 | **Diocletian: the Dominate** — Tetrarchy 293, Price Edict 301 (fails), Great Persecution 303 | reform mega-situation |
| 291–306 | War of the Eight Princes (Jin) → 304–316 north falls (Yongjia sack of Luoyang 311) → 317 Eastern Jin; **Sixteen Kingdoms** engine in the north (model the majors: Han-Zhao, Later Zhao, Former Yan, Former Qin, Later Yan/Qin, N. Wei) | mega-arc |
| 301/314† | Armenia first Christian state (Tiridates III); Georgia (Mirian III) ~326/334; Aksum (Ezana) ~330s | conversion events |
| 306–324 | Constantine's civil wars; 312 Milvian Bridge; **313 Edict of Milan**; 324 sole rule; 330 Constantinople dedicated | mega-situation |
| **325** | **Council of Nicaea** — council mechanic debut; Arian controversy; Ulfilas converts the Goths to Arianism ~341+ | religion system |
| 337–363 | Shapur II's Roman wars; 363 Julian's Persian expedition fails (Julian's pagan revival 361–363 as its own situation) | situations |
| ~350 | Aksum conquers Meroë | situation |
| ~370 | **The Huns arrive on the Volga**; Alans broken | invader spawn |
| **376–382** | **Gothic refugee crisis** → **Adrianople 378** (Valens dies) → 382 foedus (unlocks foederati subject type) | mega-situation |
| 380 | Edict of Thessalonica: Nicene state religion | event |
| 383 | Battle of Fei River — Former Qin shatters; N. Wei rises 386, unifies north 439 | situation |
| 391–413 | Gwanggaeto the Great (Goguryeo); Lelang fell 313; Buddhism to Goguryeo 372 / Baekje 384 | Tier-2 arc |
| ~393 | Theodosius ends the Olympic games (Panhellenic IO sunset) | flavor |
| 394–395 | Frigidus; Theodosius dies → **permanent East–West division (WRE/ERE)** | tagswitch |
| 399–412 | Faxian's pilgrimage; Gupta apogee under Chandragupta II | flavor/situation |
| 405–406 | Radagaisus; **31 Dec 406: the Crossing of the Rhine** (Vandals, Alans, Suebi) | mega-situation |
| 407–410 | Constantine III; Honorius' rescript — Britain abandoned | situation |
| **410** | **Alaric sacks Rome** (24 Aug) | event |
| 418 | Visigoths settled in Aquitaine as foederati | treaty event |
| 429–439 | **Geiseric: Vandal conquest of Africa**; 439 Carthage — WRE fiscal death spiral (annona lost) | mega-situation |
| 434–453 | **Attila**: tribute extortion on both empires; 447 Balkans; **451 Catalaunian Plains**; 452 Italy & Pope Leo; 453 death → **454 Nedao** collapse | mega-situation |
| 440s–460s | Hephthalites maul Persia (Peroz's disasters just post-date) and Gupta (Skandagupta holds, empire strained) | situations |
| 449† | *Adventus Saxonum* | situation |
| 451 | Council of Chalcedon (Miaphysite split); **Avarayr** — Armenian revolt vs Yazdegerd II (same year!) | events |
| 455 | Vandal sack of Rome | event |
| 468 | Cape Bon: joint E–W armada destroyed by Geiseric; ERE near-bankrupt | disaster event |
| **476** | **4 Sept: Odoacer deposes Romulus Augustulus** — end-of-timeline finale screen (§17.5) | finale |

Also seed the natural-disaster calendar (115 Antioch quake, 365 Crete quake/Alexandria tsunami, 447 Constantinople walls quake with Huns at the gates) and the **silphium extinction** (Cyrenaica good disappears, "last stalk to Nero" window 54–68).

## 10. Cultures & languages

**Method:** don't hand-place 27k locations. (a) Extract vanilla's location→culture map as a geographic template; (b) write `docs/culture_remap.csv` translating each vanilla culture in-place where lineage is continuous (Tamil→Tamil, Basque→Aquitanian) and overwriting where history diverged (Anatolia: Turkish→Greek/Phrygian/Cappadocian/Isaurian; Hungary: Magyar→Sarmatian/Pannonian-Celtic; Russia: East Slavic→Balt/Finnic/Sarmatian; Maghreb: Arabic→Berber/Punic; etc.); (c) hand-fix frontier zones. Target **350–500 cultures** in era-appropriate groups; give each group namelists (mine Pleiades/prosopography for Greco-Roman, Book of Han for Chinese, attested onomastics elsewhere; generate plausible names only where attestation fails, log it).

Groups (non-exhaustive; full tree in `docs/cultures.md` you author): Italic (Latin, residual Etruscan/Oscan-Umbrian†, Venetic), Hellenic (Greek koine zones, Macedonian), Celtic (Gallic, Belgic, Brittonic, Caledonian, Gaelic, Celtiberian, Galatian), Germanic (12–15 tribal cultures incl. Gothic, Vandalic, Suebian, Frankish-precursor Istvaeonic set), Iranian (Persian, Parthian, Median, Sogdian, Bactrian, Chorasmian, Saka, Sarmatian, Alan), Anatolian residue (Phrygian, Cappadocian, Isaurian, Lycian-Carian†), Caucasian (Armenian, Iberian-Kartvelian, Albanian, Colchian), Semitic (Aramaic/Syriac, Phoenician-Punic, Judean, Samaritan, Nabataean Arab, Arab, Sabaean, Himyarite, Ge'ez), Egyptian (Coptic-Egyptian), Cushitic/Nilotic (Meroitic, Blemmyan, Beja, Nubian), Berber set, Sub-Saharan sets (Mande-area, Chadic, Bantu wave-cultures, Khoisan), Indo-Aryan (regional Prakrit cultures), Dravidian (Tamil, proto-Telugu/Kannada), Sinitic (Han + regional), Tibeto-Burman (Qiang, Pyu, Zhangzhung), Tai, Austroasiatic (Mon, proto-Khmer, Vietic), Austronesian (Cham, Malay, Javanese, Philippine, W-Polynesian), Korean (Buyeo-Goguryeoic, Samhan), Japonic (Wa), Xiongnu†, proto-Mongolic (Xianbei/Wuhuan), Tungusic (Yilou), Uralic (Finnic, Ugric, Samoyedic), Balt, proto-Slavic (Venedi), Thracian, Dacian, Illyrian, Pannonian, Iberian (non-IE), Aquitanian, Lusitanian†, Ligurian, Rhaetic, Nuragic residue†, Americas sets (Maya, Zapotec, Teotihuacano†, Mixe-Zoquean, Totonac, Purépecha-precursor, Oasisamerica, Hopewellian/Adena Woodland, Moche, Nazca, Aymara/Puquina zone, Quechua zone, Chibchan, Arawak, Tupi, Carib, Na-Dene, Algonquian, Iroquoian, Siouan, Inuit-Dorset), Oceania/Australia sets.

**Languages/dialects (EU5 has a language layer distinct from culture — verify keys in M0):** Latin (west admin), **Koine Greek** (east admin/liturgical), Aramaic (Near-East lingua franca), Parthian/Middle Persian, Sanskrit & Prakrits, Classical Chinese, Ge'ez, Meroitic, Punic, Celtic/Germanic vernacular families, etc. Court-language mechanics: Latin west / Greek east is delicious and free.

## 11. Religions

Full tree in `common/religions` rework; design targets ~**30–40 religions** + denominational schools. Mechanics: reuse each vanilla religion-mechanic *slot* (whatever vanilla gives Catholicism/Islam/etc. — councils, curia-like bodies, schools, blessings) and reskin to era equivalents; verify moddability of each mechanic in M0.

- **Greco-Roman polytheism** ("Religio Romana" west / "Hellenic" east or one faith with rites†): Imperial Cult mechanic (legitimacy from deified emperors), *interpretatio* (cheap syncretic conversion between pagan pools), **mystery-cult aspects** (Isis, Mithras, Cybele, Sol Invictus — adoptable for modifiers; Aurelian's Sol event 274).
- **Christianity**: spawns AD 30–33 in Judea; spreads pop-by-pop via missionary dynamics, *accelerated by persecution* (martyrdom mechanic — historically resonant); denominations unlock by council: Early Church → (325 Nicaea) Nicene vs **Arian** (Ulfilas takes Arianism to the Goths → the Arian-Germanic-kings-over-Nicene-subjects tension that defines the 5th c.) → Donatist (Africa, 311), Novatianist, Marcionite/Gnostic currents (fading by 300s), Montanist → (431 Ephesus) **Church of the East** eastward into Persia → (451 Chalcedon) **Miaphysite** (Egypt/Syria/Armenia/Aksum). State adoption chain: Constantine 312–337, Julian's reversal 361–363, Theodosius 380/393. Church as International Organization from 325 (§16.3).
- **Judaism**: Second Temple (with Temple building in Jerusalem) → AD 70 destruction transforms it (Rabbinic Judaism event chain); diaspora pops seeded realistically (Alexandria, Rome, Babylonia, Cyrenaica, Anatolia).
- **Zoroastrianism**: Arsacid syncretic form → 224 Sassanid orthodoxy reform (fire temples, Kartir's persecutions of minorities, Zurvanite school†); state-church mechanics mirror-imaging Christianity's.
- **Manichaeism**: spawns 240s at Ctesiphon; universal missionary religion hunted by both empires; spreads along the Silk Road (reaches Rome, Egypt, Central Asia within-period).
- **Buddhism**: schools (Sthavira/Theravada, Mahasamghika→Mahayana; Sarvastivada at Kanishka's council); spread rails: Lanka (already), Central Asia/Tarim (active), **China from 65–68**, SE Asia 2nd–4th c., **Korea 372/384**; Japan is post-period (do not script).
- **Hinduism** (Brahmanism → Puranic temple-Hinduism transition under the Guptas — a reform event), **Jainism** (Digambara/Svetambara split ~1st c.), **Chinese state cult** (Confucian rites + folk religion, with Confucian/Daoist/Buddhist *schools* steering law), **organized Daoism** from 142 (Celestial Masters; the Hanzhong theocracy 191–215 is a playable theocratic mini-state), proto-**Shinto** kami worship, Korean Muism, **Tengri** (steppe), **Bon/Zhangzhung**, **Egyptian** (Kemetic, alive and Serapis-bridged to Hellenism), **Kushite Amun**, **Aksumite** paganism → Christianity, **South Arabian** (Almaqah etc. → 4th-c. Rahmanist monotheism shift†), **Arabian polytheism** (Hubal/al-Lat; Kaaba flavor), **Canaanite-Punic** residue (Tanit), **Celtic** (druidic; Roman suppression events — Mona 60), **Germanic**, **Balt-Slavic**, **Finno-Ugric**, **Berber**, Nilotic/Cushitic traditions, W-African traditions, Bantu traditions, **Mesoamerican** (Teotihuacan Storm-God/Feathered-Serpent, Maya, Zapotec), **Andean** (Moche, Nazca, highland), North-American animisms, Siberian shamanism, Austronesian/Polynesian, Australian Dreaming.

## 12. Economy

### 12.1 Trade goods
Keep every timeless vanilla raw good in place (grain, fish, livestock, wine, salt, iron, copper, lead, gold, silver, gems, horses, wool, flax, lumber, stone/marble, furs, amber, honey/wax, dyes, olives, dates, cotton, pearls, ivory, slaves — vanilla already models the slave trade; follow its sober register). **Add/emphasize:** silk (Chinese near-monopoly; sericulture stays east all game — it reaches Byzantium only in 552, safely post-period), **incense** (frankincense/myrrh — Arabia Felix & Horn; the era's oil money), **papyrus** (Egypt monopoly), **purple dye** (Tyre murex — or a dyes-tier special), **jade** (Khotan→China), **pepper** (Malabar — the Rome-India drain of denarii), lacquerware (Han export), fine ceramics (terra sigillata), glassware (Sidon/Alexandria/Cologne), naphtha/bitumen (Mesopotamia), alum, war elephants (India/succeeding powers)†, camels, **silphium** (Cyrenaica only, with the extinction disaster). **Remove/localize:** coffee (none), tea (Sichuan-only minor herb†), sugar (rare, India/SE Asia only), tobacco/cocoa/maize/potato stay in the Americas untraded, all gunpowder-era and early-modern manufactures replaced by era manufactures above. Rewrite every location's RGO via `docs/goods_remap.csv` (vanilla RGO as prior, corrected by ancient sources — mines: Rio Tinto silver, Cyprus copper, Cornwall tin, Noricum iron, Dacian/Nubian gold, Laurion fading†).
### 12.2 Markets
Seed `market_manager` (~40): Roma, Alexandria, Antiochia, Seleucia-Ctesiphon, Carthago, Gades, Massilia, Lugdunum, Aquileia, Corinthus, Ephesus, Byzantium (small→scripted growth), Panticapaeum, Petra, Palmyra (growth arc), Meroë, Adulis, Muza, Barygaza, Muziris, Pataliputra, Taxila, Anuradhapura, Marakanda, Kashgar, Chang'an, Luoyang, Panyu (Guangzhou), Oc Eo (growth), Teotihuacan, Tikal-zone, Chan Chan-precursor†… Silk Road & monsoon routes emerge from geography + roads + harbors rather than hardcoding.
### 12.3 Buildings
Reskin vanilla ladder + era set: aqueduct, baths, amphitheater/circus (bread-and-circuses: plebs happiness/control), forum/agora, granary (annona), lighthouse (Pharos), library (Alexandria), academy, temple→church/fire-temple/stupa/pagoda by religion, monastery (unlocks ~270 west / exists Buddhist east), villa/latifundium (noble+slave agriculture), irrigation (Nile basins, qanats, Chinese canals), mint (ties into debasement), roads/limes/legionary fortress (castra) as the fort line, harbor tiers. Wonders/great-works if the engine slot exists: Colosseum (80), Pantheon (126), Trajan's Column, Aurelian Walls, Theodosian Walls (413), Sun Pyramid, Great Stupa.
### 12.4 Population targets (thousands; tolerance ±15%; sources App. C)
World ~**230,000**. Roman Empire **45,000–50,000** (Italy ~7–8k, Egypt ~4.5–5k, Gaul ~5–6k, Iberia ~4–5k, Anatolia ~6–7k, Syria-Levant ~3.5–4.5k, Africa Proc.+Cyrenaica ~3–4k, Greece-Balkans ~4–5k, Britain pre-conquest ~1.5–2k outside). Han **57,671** (census AD 2 — allocate by commandery data). Parthia ~**8,000–10,000**. India ~**35,000–45,000**. SE Asia ~3,000–5,000. Korea ~1,000–2,000; Japan ~600–1,000. Central Asia+steppe ~4,000–6,000. Sub-Saharan Africa ~10,000–15,000. Americas ~10,000–15,000 (Mesoamerica-heavy). Non-Roman Europe ~8,000–12,000 (Germania ~3,000). `tools/popcheck.py` enforces these.

## 13. Government, estates, laws, societal values
Government types (reskin vanilla types + reforms): **Principate** (Rome-unique: republic-facade monarchy; Auctoritas-flavored legitimacy; Praetorian succession events; donative mechanic; reform path → **Dominate** unlocked 284-era with Tetrarchy co-rulership flavor), Hellenistic monarchy, client monarchy, city republic, **Parthian feudal King-of-Kings** (powerful noble-house estate: Suren/Karin), **Sassanid centralized monarchy** (+Zoroastrian clergy power), **Han imperial bureaucracy** with **Mandate of Heaven** (legitimacy that collapses in dynastic-cycle disasters: eunuchs/consort-clans/warlords), steppe confederation (elective chanyu/khagan; loot-and-tribute economy; shatter-on-succession risk), tribal chiefdom/kingdom ladder (for SoP graduates), Indian ganasangha republic, theocracy (Celestial Masters; Judean priestly flavor), Greek polis under empire (autonomous-city charter privilege).
Estates: reskin to **Senatorial aristocracy / Equites / Priesthoods / Plebs / Tribes / (if the engine allows a country-specific estate) the Legions** — the army as a political actor is *the* third-century mechanic; if a true estate is impossible, implement via privileges+disaster interactions. Privileges: annona, senatorial land exemption, praetorian donatives, Han eunuch bureau, Parthian great-house autonomy, druidic councils, etc. Laws: citizenship ladder (peregrini→Latin rights→citizens; Constitutio Antoniniana 212 flips it empire-wide), slavery/manumission policies, religious toleration↔persecution ladder (drives Christianity/Manichaeism spread), succession laws, military recruitment (levy↔professional), coinage standard (debasement lever: short-term cash, long-term inflation — the third-century trap, self-inflicted). Societal values: map vanilla sliders to era meanings (centralization, tradition↔innovation, land↔trade, serfdom analog = colonate late-empire drift†).

## 14. Military
No gunpowder anywhere; prune all such advances/units. Unit roster by culture-group (reuse nearest vanilla 3D models; 2D icons regenerated): **Legionaries** (professional heavy foot; Rome's regulars), Auxilia (Rome's levy-analog with citizenship-on-discharge flavor), Hellenistic thureophoroi/remnant phalanx†, Germanic/Celtic warbands, **Han crossbow infantry** (the crossbow edge), Indian longbowmen + **war elephants**, Nubian archers, **cataphracts** (Parthia/Sarmatia/Sassanids; Rome adopts late via advance), **steppe horse archers**, Numidian light horse, camelry (Arabia/Palmyra), **British chariots** (obsolescent, flavorful), late-era comitatenses/limitanei split via Dominate advances. Navy: liburnian / trireme / quinquereme / merchant roundship / monsoon dhow / Austronesian outrigger; no ocean-crossing classes. Mercenaries: era companies (Balearic slingers, Cretan archers, Germanic bodyguards, Saka horse). Forts = limes/castra chains (Rhine-Danube, Hadrian's, Gorgan-precursor†, Han beacon lines). Levies vs regulars is vanilla-native and maps perfectly: Rome/Han/Parthia field regulars, tribes field levies.

## 15. Ages, advances, institutions
Five ages (like vanilla's cadence): **I. Age of the Principate (1–96)** · **II. Age of the High Empires (96–192)** · **III. Age of Crisis (192–284)** · **IV. Age of the Dominate (284–395)** · **V. Age of Migrations (395–476)**. Each: objectives, age abilities, and ~50 advances (≈250 total) themed to era (I: professional standing armies, imperial cult, monsoon navigation, paper precursors; II: jurists' law, cataphract adoption, silk-road caravanserais; III: crisis coinage, mobile field armies, wall-building; IV: state church, codification, foederati settlement, heavy lancer refinement; V: hospitality-of-barbarians, kingdom-building on Roman soil, stirrup†-adjacent horse furniture — keep the stirrup out or very late, it's contested). Institutions (spawn+spread): Hellenism (active, east Med), Roman Law & Engineering (active, Italy), Han Bureaucratic Statecraft (active, China), Papermaking (105, Luoyang), Monasticism (dual-origin: Buddhist India active / Christian Egypt ~270), Cataphract Warfare (Iran, 1st–2nd c.), Theological Orthodoxy (325, Nicaea), Foederati Statecraft (382, Thrace). Starting `starting_technology_level` tiers: imperial cores > literate periphery > tribal world (exact integers tuned in M8).

## 16. Diplomacy, subjects, international organizations
16.1 Casus belli / wargoals: punitive expedition, imposition of client king, tribute demand, frontier rectification, loot raid (steppe/tribal), succession intervention, holy suppression (late, religious), unification wars (Chinese warlords; Sassanid revolt; Gupta digvijaya).
16.2 Subject types: `antq_client_kingdom` (Rome), `antq_tributary` (Han system; steppe extortion variant), `antq_satrapy` (Parthian sub-kings), `antq_foederati` (unlocks 382; settles barbarian tags *inside* imperial borders with land-for-service — the fall-of-the-west engine), autonomous city charter.
16.3 IOs: **Han Tributary System** (start), **Xiongnu Confederation** (start; shatter/reform logic), **The Christian Church** (forms 325; councils as IO votes deciding orthodoxy; Pentarchy special seats post-381; schism outputs = denominations), **Panhellenic Games** (start; prestige events every 4 years; sunset 393 — small, pure delight), optional **Silk Road compact** only if IO mechanics beat market mechanics for it (decide in M9).
16.4 Known worlds: per-tag `discovered_*` sets — Rome knows Ptolemy's oikoumene (Ireland fuzzy, Thule rumor, E. Africa to Rhapta, India well, China as "Serica" dimly); Han knows the Western Regions to Persia/"Daqin" dimly; India knows both directions; Americas know only themselves; nobody crosses the Atlantic/Pacific, ever, by tech design.

## 17. Situations, disasters, dynamic tags
17.1 Situations (~35 majors): every mega-row of §9.
17.2 Disasters (~12): Year of Four/Five Emperors template (imperial civil war), **Crisis of the Third Century** (flagship: triggers off low legitimacy+plague+frontier pressure; stages; Gallic/Palmyrene secessions; Aurelian/Diocletian exits), Mandate-of-Heaven dynastic collapse (Han/Jin variants), steppe shatter, Hunnic domination & Nedao, WRE fiscal collapse (Africa-loss triggered), pandemic package (Antonine/Cyprian with disease_outbreak_manager + resistance geography).
17.3 Formables: Sassanid Persia, Kushan Empire, Gupta Empire, the Three Kingdoms set, Jin, Northern Wei, Aksumite Empire, Himyar-unified Yemen, Alemanni/Franks/Saxons/Picts, Visigoths/Ostrogoths (post-Hun split), Vandal Africa, Hunnic Empire, Yamato, Baekje/Silla consolidations, Champa, Funan, unified Dacia.
17.4 Tag-switch protocol: prefer in-place transformation (rename+reform+dynasty change) over tag replacement where the engine allows; reserve true new tags for genuine new polities (WRE/ERE split 395 is the big scripted one — decide E vs W as "which tag inherits vs which spawns" in M10 after engine testing).
17.5 The 476 finale: end-of-game screen scores the run (did the West fall? who holds Rome/Ctesiphon/Luoyang/Pataliputra; church unity; steppe legacy) with a historical-vs-your-history epilogue generator. Alt-history is allowed — rails bend.

## 18. Events & decisions (flavor targets)
≥400 events total: ~120 Rome-arc, ~60 China-arc, ~40 Persia/steppe, ~40 India/SE Asia, ~30 religion-generic (councils, martyrs, conversions), ~30 barbaricum, ~20 Americas/Africa/Oceania, ~60 generic-era (earthquakes, portents — comets of 44BC-style†, chariot factions, philosophy schools, Sangam poetry, Han lodestone diviners). ~40 decisions (adopt mystery cult, codify laws, debase coinage, endow games, invite foederati, move capital — Constantinople!, abandon Dacia). Every event: era-appropriate art (§20), sourced flavor text in our own words.

## 19. Characters
Start rosters for every Tier-1/2 tag (ruler, consort, heir, 2–4 court/generals) — Augustus/Livia/Gaius Caesar/Tiberius, Ping-di/Wang Mang/Grand Empress Dowager Wang, Phraates V/Musa, Maroboduus, Arminius (as a character in Roman service!), Juba II/Cleopatra Selene, Aretas IV, Natakamani/Amanitore, Wuzhuliu, Yuri of Goguryeo, Cunobelinus… (~250–400 characters). Dynasties in `dynasty_manager` with real onomastics; `ruler_term` back-history for regnal numbers (Augustus's list is short; Han's is long). Era-defining later figures (Ardashir, Constantine, Attila, Samudragupta, Zenobia, Aurelian, Ulfilas, Mani) spawn via their situations, not the character_db, so alt-history stays coherent.

## 20. Asset pipeline (all visuals generated or reused; zero audio work)
- **Inventory first:** `tools/asset_manifest.py` lists every vanilla-referenced asset class our content touches, with exact dimensions/format learned via `magick identify` on vanilla samples. Never guess sizes.
- **Flags:** per M0 finding (texture vs layered CoA). Either way, design language: no anachronistic heraldry — emblem-on-field standards (Roman aquila/SPQR wreath → labarum after Constantine's arc via flag-switch if supported; Sasanian derafsh motifs; Han banner glyphs; tribal totems; muted textile palette). Texture route: image-gen/SVG → PNG → DDS. CoA route: compose from vanilla emblems + a small set of new emblem textures.
- **Image generation:** for event illustrations (~80 shared paintings), 5 age splashes, 8–10 loading screens, situation/disaster art, goods/religion/institution/advance icons. Global style prompt: *"muted painterly historical illustration in the style of Roman fresco and Han dynasty mural art, soft natural light, no text, no borders, no modern objects"* + subject; per-class negative prompts; upscale/crop to exact vanilla dimensions; convert with `tools/dds.py`; visually spot-check by rendering a contact-sheet HTML and reviewing it yourself (screenshot it into the milestone report; it's also a nice artifact for the user to browse later).
- **Icons at scale:** advances need ~250 — batch-generate on a shared template (parchment tile + subject glyph) for coherence; recolor per age.
- **3D:** none. Map unit/building models to nearest vanilla assets (earliest-period sets read acceptably as late antiquity for v1; note in KNOWN_ISSUES.md).
- **Licensing:** generated images and vanilla-asset reuse inside an EU5 mod are fine; credit data sources (Pleiades CC-BY etc.) in `.metadata` description and a CREDITS.md.

## 21. Localization
English only, `antq_` keys, UTF-8-BOM, `_l_english.yml`; `tools/gen_loc_stubs.py` mirrors English into other language files. Naming voice: Latin/Greek forms for the classical world (Mediolanum, not Milan), pinyin-free Han-era readings where conventional (Chang'an, Luoyang), attested endonyms elsewhere; concept glossary (`docs/glossary.md`) keeps terminology consistent (legate, chanyu, satrap, foedus…).

---

# PART III — EXECUTION

## 22. Milestones (seed `docs/TODO.md` from this; each ends green on `make full` + a driver-run verification report, §5)

**M0 — Discovery & tooling.** Run `find_game.py` (locate GAME_DIR on D:/G: via `libraryfolders.vdf`, pick WORK_DRIVE, write `config/local_paths.json`); create the repo on WORK_DRIVE and wire visibility per §2 (user-dir relocation / junction / CLI mods — test in that order); `steam_ensure` + capture `baselines/vanilla_error.log` (launch unmodded); build all §4 tools including the game driver's console tier; drive `script_docs`/`dump_data_types`/`helplog` (GitHub-mirror fallback); script playset enablement (`enable_mod.py`) if needed; run `extract_vanilla.py`; clone & analyze the 1444-start-date repo → write `docs/ENGINE_FACTS.md` answering every §3 verification item (start-date mechanism above all); inventory vanilla `setup/`, events, situations, disasters, DLC. *Accept:* tools run end-to-end with zero human action; ENGINE_FACTS complete; smoke harness proves it can start Steam if needed, launch vanilla, and diff logs; script_docs harvested.

**M1 — Skeleton loads.** `.metadata` + thumbnail; empty-but-valid mod made visible and enabled entirely by tooling (§2 mechanism + `enable_mod.py` if applicable); smoke green with mod active. *Accept:* game reaches menu with mod loaded, zero new errors.

**M2 — Time itself.** Start date 1.1.1, end 476.9.4 (or C-1 AUC fallback); ages skeleton (5 ages, placeholder advances); calendar sanity (UI shows year 1+; saves reload). Vanilla 1337 world data may still load underneath at this stage — that's fine and expected. *Accept:* new game starts on 1 Jan, AD 1.

**M3 — The political map.** `docs/tags.csv` + `docs/world_1ad/` rosters from §8; country_definitions (colors per historiographic convention: Rome purple-red, Parthia/Sassanids deep red†, Han imperial red-gold…); full vanilla-setup mirror-replacement; ownership/subjects/SoPs painted worldwide; capitals; placeholder flags. *Accept:* political map mode is AD 1 Earth; every §8 polity present; no vanilla 1337 country survives.

**M4 — Peoples & faiths.** Culture remap + new cultures/languages/namelists; religion tree; pops seeded worldwide to §12.4 targets (`popcheck` green; `-leavepops` verification run); dynamic location naming layer v1 (Pleiades pipeline). *Accept:* culture/religion/population map modes read as a scholarly atlas of AD 1.

**M5 — Economy.** Goods roster + RGO remap; markets; buildings + town_setups; road_network seeded (Roman roads from ORBIS/itineraries; Persian royal road legacy; Chinese trunk roads); development pass. *Accept:* trade flows sensible (grain→Roma, silk westward, incense north, pepper→Egypt).

**M6 — Power.** Governments/reforms/estates/privileges/laws/societal values per §13; character_db + dynasties per §19; regnal histories. *Accept:* Tier-1 tags read mechanically distinct — driver starts a session as each of Rome/Han/Parthia, screenshots the government/estate/law screens, and you judge them against §13 in the M6 report.

**M7 — War.** Units, levy/regular assignments, mercs, forts/limes, navies; prune gunpowder+oceanics. *Accept:* AI test wars resolve plausibly in a driver-run observer session (fog off, high speed, periodic screenshots you review).

**M8 — Knowledge.** Full 5-age advance trees (~250), institutions, starting tech tiers, age objectives/abilities. *Accept:* no dead-end or anachronistic advance reachable; AI researches sanely.

**M9 — Nations among nations.** CBs/wargoals/peace treaties; subject types incl. foederati (gated 382); IOs (Han tributaries, Xiongnu, Panhellenic Games; Church scaffold, dormant until 325); known-world discovery sets. *Accept:* diplomacy screens coherent; tributary/client webs match §8.

**M10 — History in motion.** All §9 situations/disasters/tag-switches/formables, in chronological batches (1–100, 100–200, 200–300, 300–400, 400–476), each batch smoked + driver-observed to its era (observer autoplay, fog off, screenshot cadence + log watch). *Accept:* an AI-only observer game produces recognizably plausible centuries (not deterministic — plausible).

**M11 — Flavor & face.** Events/decisions to §18 targets; final flags; icon batches; event art; loading screens; age splashes; loc polish; concept glossary; credits. *Accept:* no placeholder art on any common screen; text register consistent.

**M12 — Ship.** Balance/pacing pass (advance costs over 475 yrs; pop growth; inflation), AI weights sanity, full-timeline driver-run observer game to 476 (screenshots each decade-ish, error.log watched throughout, findings in the M12 report), KNOWN_ISSUES.md, README, thumbnail final, PDX Workshop Manager packaging notes. *Accept:* `make full` green; the autonomous observer run reaches 476 without crash; finale fires on screenshot evidence.

## Appendix A — Complete surface-area checklist (nothing forgotten)
Tick each in `docs/SURFACE_AREA.md` as touched-or-consciously-skipped: metadata/thumbnail · defines (all three top folders' defines dirs) · setup/start every manager · setup/countries · setup/templates · common: advances, ages, buildings, casus_belli, characters(traits), countries, cultures, defines?, diseases, estates, goods, governments/reforms, institutions, international_organizations, laws, town_setups, subject_types, situations, disasters, units, wargoals, peace_treaties, religions, pops, scripted_effects/triggers/values, on_actions, static_modifiers, customizable_localization · events (all vanilla files disabled + ours) · missions?(vanilla uses? verify; if present, era content or clean disable) · gfx: flags, goods/religion/advance/estate/gov icons, event pictures, loading screens, age art, IO icons, map-political colors · localization full coverage · main_menu (menu text/art touchups optional) · loading_screen defines (WATER_LEVEL etc. untouched) · music/sound = untouched by design · achievements = untouched/disabled · tutorials/hints (audit for 1337 references; soften or disable) · game rules (Historical Currents) · AI weights on everything scripted · fonts untouched · anachronism sweep (search all loc/text for post-476 concepts).

## Appendix B — AGENTS.md drop-in (create at repo root in M0)
```
# AGENTS.md — ANTIQVITAS
Source of truth: docs/ANTIQVITAS_MASTER_PLAN.md (read fully once per session start).
Loop: pick top unblocked task in docs/TODO.md → implement → `make validate` green →
(if game-visible) `make smoke` green vs baselines → commit → update TODO/PROGRESS,
and DECISIONS/ASSUMPTIONS if you judged anything. Never commit red. Never edit GAME_DIR.
Blocked twice → BLOCKERS.md → next task. Historical claims need a source or a † in
ASSUMPTIONS.md. All dates via tools/dates.py. Encoding matrix is law (§3).
No human-in-the-loop steps exist: automate launcher, console, and playtests via tools/gamedriver.py; if something resists automation twice, log it in BLOCKERS.md with evidence and continue.
```

## Appendix C — Sources & data pipelines
- **Pleiades** (pleiades.stoa.org, CC-BY, machine-readable dumps): ancient Greco-Roman placenames + coordinates → auto-match to vanilla location centroids for the naming layer. Credit required.
- **ORBIS** (Stanford geospatial network model of the Roman world): route/network sanity for roads and market weighting (read methodology; don't scrape wholesale).
- **Book of Han geography treatise** (census AD 2 by commandery): China pops. **Bielenstein** for interpretation.
- **Frier (Cambridge Ancient History XI)** Roman demography; **McEvedy & Jones** world/regional series (adjust upward per modern critique†); **Scheidel** on Rome-Han comparison.
- **Barrington Atlas** conventions for Latin/Greek toponym forms; **CHGIS** (Harvard, Han-era layers; check license — likely CC-BY-NC, acceptable for a free mod with attribution, else fall back to Book of Han lists).
- **Talbert, OCD, CAH volumes, Periplus of the Erythraean Sea** (trade), **Notitia Dignitatum** (late-Roman army/admin), Sangam corpus scholarship (Tamilakam), Samguk Sagi traditional dates (flag †).
- EU5 wiki (mechanics), community script_docs mirror on GitHub, EU5 Mod Co-op Discord (read-only reference), Imperator: Rome's design (Paradox's own antiquity game — legitimate *design* reference for tone/naming; copy nothing).

## Appendix D — Risk register
- **R1 Start date resists modding** → mitigated by 1444-mod precedent; C-1 AUC calendar as final fallback.
- **R2 Additive setup can't fully purge vanilla** → mirror-replace every vanilla setup file (M0 inventory makes this mechanical); verify no 1337 tag survives via a driver-run console spot-check recorded in the M3 report.
- **R3 Hardcoded 1337 content (DLC, situations referencing vanilla tags) errors out** → disable-by-override sweep in M3; error.log diff catches stragglers.
- **R4 Engine hardcodes (migration/battle logic, map modes are documented as unmoddable)** → design within them; never fight hardcode, reflavor around it.
- **R5 Icon volume (~250 advances) overwhelms art budget** → templated batch generation; shared-icon fallback tiers.
- **R6 Pop-scale performance** (AD 1 ≈ 230M vs vanilla's larger total — we're lighter; low risk) → monitor tick speed in observer runs.
- **R7 Long-run AI does ahistorical nonsense** → acceptable in sandbox spirit; steer with rails_strength weights, not hard locks; document egregious cases in KNOWN_ISSUES.
- **R8 Game patches break the mod mid-project** → version-pin in metadata; re-run extract/baseline on patch detect (§5).
- **R9 Year-1 edge cases in date math** (e.g., events firing "before start") → all dates through tools/dates.py + a pdxlint rule: no date < 1.1.1.
- **R10 UI-automation brittleness** (the game driver is the least deterministic tool) → fixed windowed resolution, screenshot-verified inputs with retries, log-based readback over pixel-reading wherever possible, recorded click sequences re-validated per game patch; graceful degradation to launch+log-diff with the gap logged — never a human fallback.
- **R11 Launcher DB schema unknown/changes** → back up `launcher-v2.sqlite` before every write, verify with an integrity read-back, restore on failure; prefer CLI mod loading or user-dir relocation if either works, making the DB irrelevant.
- **R12 Environment friction** (Steam not running / auto-updates mid-run; Documents redirected into OneDrive making the junction sync-noisy) → `steam_ensure` starts Steam and waits; detect game-version change and re-baseline (R8); if OneDrive manages Documents, prefer the user-dir relocation option so mod content never enters a synced folder, and log whichever path was taken in DECISIONS.md.
- **R13 C:-drive pressure** → all repo data, caches, screenshots, and generated art on WORK_DRIVE by construction; the only C: growth is the game's own logs/saves (or none, if user-dir relocation works). Add a `find_game.py` free-space check that warns in PROGRESS.md if C: falls below 5 GB.

*Finis. Roma aeterna est — now go build her, and the whole world she never knew she shared.*

# AGENTS.md — ANTIQVITAS
Source of truth: docs/ANTIQVITAS_MASTER_PLAN.md (read fully once per session start).
Loop: pick top unblocked task in docs/TODO.md → implement → `make validate` green →
(if game-visible) `make smoke` green vs baselines → commit → update TODO/PROGRESS,
and DECISIONS/ASSUMPTIONS if you judged anything. Never commit red. Never edit GAME_DIR.
Blocked twice → BLOCKERS.md → next task. Historical claims need a source or a † in
ASSUMPTIONS.md. All dates via tools/dates.py. Encoding matrix is law (§3).
No human-in-the-loop steps exist: automate launcher, console, and playtests via tools/gamedriver.py; if something resists automation twice, log it in BLOCKERS.md with evidence and continue.

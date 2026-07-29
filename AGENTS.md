# AGENTS.md — ANTIQVITAS
Source of truth: docs/ANTIQVITAS_MASTER_PLAN.md (read fully once per session start).
Loop: pick top unblocked task in docs/TODO.md → implement → `make validate` green →
(if game-visible) `make smoke` green vs baselines → commit → update TODO/PROGRESS,
and DECISIONS/ASSUMPTIONS if you judged anything. Never commit red. Never edit GAME_DIR.
Blocked twice → BLOCKERS.md → next task. Historical claims need a source or a † in
ASSUMPTIONS.md. All dates via tools/dates.py. Encoding matrix is law (§3).
No human-in-the-loop steps exist: automate launcher, console, and playtests via tools/gamedriver.py; if something resists automation twice, log it in BLOCKERS.md with evidence and continue.
Real EU5 sessions share the machine lease at `G:\eu5_runtime\slot` with ENDÓRË.
Exit 75 means DEFERRED, not red: do not wait, poll, count it as a blocker, claim the gate,
or commit game-visible content. Record the pending gate (the tools do this), continue the
next compatible static TODO task, and retry at the next natural checkpoint. `make validate`
never needs the lease. Before a game-visible commit, `tools/eu5_slot.py assert-smoked`
must prove the last green smoke covers the current game-visible tree fingerprint.

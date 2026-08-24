# Native crash debugging for EU5 mods

Use this workflow when EU5 exits with a native access violation and the script
logs do not identify a clear fatal error. The goal is to move from "the game
crashes" to one precise engine subsystem, one bad precondition, and the
smallest safe data-side workaround.

## 1. Preserve one trustworthy reproduction

Start from a fresh campaign unless the bug is explicitly save-specific. Record
the game version, active mod set, mod-tree fingerprint, user directory, country,
date, speed, and the last player action. Keep the complete crash directory,
especially `minidump.dmp`, and copy the logs before launching again.

Change only one variable per control run. Resolution, renderer, audio, drivers,
and caches are useful controls only when the evidence points at those systems;
they should not displace investigation of a repeatable simulation-date crash.

## 2. Classify the fault from the dump

Open the minidump in WinDbg and begin with:

```text
!analyze -v
.ecxr
k
lm m eu5
ub @rip
u @rip
```

Record the exception code, faulting instruction, engine module offset, thread
name, access type, bad address, and registers used by the instruction. A worker
thread running country or building updates is simulation evidence; a render
thread or graphics-driver module is graphics evidence. The last log line is
only temporal context and is not automatically the cause.

Retail builds often lack useful symbols. Module-relative addresses, nearby
instructions, RTTI/type-name strings, function-call structure, and repeated
object layouts are still enough to identify a subsystem.

## 3. Trace the invalid value backwards

Do not stop at "null-pointer dereference." Disassemble the caller and determine:

- which call returned or selected the invalid object;
- which object IDs, locations, countries, or managers were involved;
- which condition should have prevented the call;
- whether the missing object is invalid mod data or an optional engine feature
  the conversion does not use.

Inspect register-backed objects and pointer fields in the dump, then correlate
their numeric IDs with the fresh save and generated setup files. This is usually
more reliable than guessing from warnings in `error.log`.

## 4. Map the engine subsystem back to moddable data

Search the installed vanilla data for the subsystem name, related scripted
properties, and relevant defines. Then inspect mature total-conversion mods for
how they initialize or intentionally disable the same feature. Treat other mods
as leads, not proof: verify every borrowed pattern against the installed game
version and the dump evidence.

Prefer one of these remedies, in order:

1. Populate the missing manager/object when the feature is required.
2. Guard or remove the malformed definition that creates the invalid state.
3. Disable only the unused evaluator or candidate path through a documented
   define when the total conversion intentionally has no content for it.

Never patch the executable or broadly disable AI when a narrow data-side switch
exists. For example, if the fault is inside an optional proximity-building
candidate evaluator and the conversion defines no such building chain, setting
only that evaluator's update chance to zero preserves ordinary building,
construction, road, city, and market AI.

## 5. Prove the fix against the original failure

Validation should include all of the following:

- parser/linter and repository validation;
- a genuinely fresh campaign with the production mod set;
- the same country, speed, actions, and date window as the reproduction;
- a run substantially beyond the old boundary, preferably a full game year;
- confirmation that no new crash directory appeared and the process remained
  responsive;
- a quick check that adjacent systems still operate.

If the crash remains probabilistic, repeat the run or attach WinDbg live and set
a conditional breakpoint immediately after the suspected lookup. Break only
when the relevant country/object matches and the returned pointer is null; this
captures the state before the access violation destroys context.

## 6. Leave an evidence trail

Document the dump path, exception and module offset, thread/subsystem,
offending data IDs, root precondition, exact workaround, validation commands,
runtime dates reached, screenshots, and newest crash-directory timestamp.
Separate facts from inference and explicitly retire earlier hypotheses that the
debugger disproved. Future agents should be able to resume from the smallest
remaining uncertainty instead of repeating renderer, cache, or generic log
experiments.

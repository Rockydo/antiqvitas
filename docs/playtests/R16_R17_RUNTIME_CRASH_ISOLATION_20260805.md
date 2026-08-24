# R16-R34 runtime crash isolation — 2026-08-05

## Reproduction and negative controls

Fresh, non-debug Roman Imperium campaigns repeatedly ended in native
`C0000005` access violations after the live simulation began, usually between
the 1 February *Immensum Bellum* acknowledgement and late April. The failure
survived all of the following focused controls:

- 1280x720, 1920x1080, and other display settings;
- Vulkan shader-cache rebuild and a DX12 control;
- audio suppression and missing-notification-sound repair;
- removal and restoration of the Annona monthly deliveries;
- execution guards and temporary AI-dispatch removal for bilateral actions;
- temporary controls around the scripted `create_market` generic action;
- upgrade to the official NVIDIA 610.47 WHQL driver.

Those results remain useful exclusions, but the earlier renderer and automatic
market-initializer conclusions were wrong. They were based on misleading retail
stack labels and temporal log proximity rather than the exact faulting engine
code.

## WinDbg root-cause isolation

The decisive dump is:

`G:\antiqvitas_user_data\crashes\Europa Universalis V20260805_184015\minidump.dmp`

The exception context resolves to:

- access violation: read from `0x140` through a null base register;
- instruction: `eu5.exe+0x5127989`, `mov r8,[r10+140h]`, with `r10 = 0`;
- thread: `Task_P_N 2`, a parallel simulation worker, not the renderer;
- enclosing routine: `CBuildingAi::HandleProximityBuildings`;
- failing unit: its edge-cost/candidate-evaluation lambda;
- country context: ID 159, XAR / Western Han;
- observed candidate locations: Panyu (10786), Xuzhou (8668), and the Nanhai
  edge (10783).

Backward disassembly showed that the lambda received a null market-like object
after a lookup over country/location membership. The crash therefore occurs in
the optional building-AI proximity-candidate path, not in graphics rendering or
the generic automatic-market action.

The installed data exposes the exact narrow control:
`NAI.AI_PROXIMITY_CANDIDATE_UPDATE_CHANCE`. Its vanilla comment describes the
periodic search for good local-governor locations. ANTIQVITAS quarantines every
installed building type carrying `local_proximity_source` and has no active
local-governor chain, so this evaluator has no valid authored work to perform.

## R34 fix

`loading_screen/common/defines/antq_ai_stability.txt` sets only:

```text
NAI = {
    AI_PROXIMITY_CANDIDATE_UPDATE_CHANCE = 0
}
```

This disables the unused crashing candidate evaluator while preserving normal
building, construction, road, city, and market AI.

## Acceptance result

A fresh Roman Imperium campaign was launched without debug mode at 1920x1080,
the opening Agenda was closed, the 1 February current was acknowledged, and the
game ran at speed 5 from 1 January, year 1 through 1 January, year 2.

Evidence:

- April boundary: `docs/screens/R34_PROXIMITY_AI_FIX_20260805/progress_04.png.png`
  shows 11 April, year 1;
- extended run: `docs/screens/R34_PROXIMITY_AI_FIX_20260805/progress_05.png.png`
  shows 24 August, year 1;
- full year: `docs/screens/R34_PROXIMITY_AI_FIX_20260805/one_year.png.png` shows
  1 January, year 2;
- the process remained responsive throughout;
- no crash directory newer than `Europa Universalis V20260805_184015` appeared;
- `.\make.cmd validate` passed all 172 checks after the fix.

R34 therefore closes the reproduced April crash with a debugger-backed,
minimal engine-define workaround. The general investigation method is recorded
in `docs/CRASH_DEBUGGING_GUIDE.md`.

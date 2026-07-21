# AD 1 startup-default regression - 2026-07-21

## Failure baseline

The first accepted paused AD 1 observer run left its live initialization log in
`G:\antiqvitas_user_data\logs\error.1.log`. It contains 440 removal lines:

- 213 `Removing invalid law` diagnostics;
- 227 `Removing invalid estate privilege` diagnostics.

The messages name installed defaults including `royal_court_customs_law`,
`medieval_levy_law`, `noble_fortification_licenses`, and
`clergy_literacy_rights`. Local installed-file inspection established that all
157 generated countries included one of two 1337 templates: 96 imported
`east_asia_monarchy`, while 61 imported `asia_advanced_tribe`. Both templates
serialize their own government laws and privileges before the generated
ANTIQVITAS government block.

## Repair

`tools/generate_start_mirror.py` no longer emits either template include. The
direct `starting_technology_level` and `discovered_regions` contracts already
replace the other relevant template fields. The 107 source-led M6 government
profiles continue to render their exact reform, privilege, law, character, and
societal-value records. The remaining 50 deliberately unsourced profiles now
receive a minimal installed-shape fallback: monarchy/cognatic primogeniture or
SoP tribe/tribal-oldest-male, each with `ruler = random` and no imported
defaults.

## Verification

- `make validate`: passed all static checks, including the exact 25-file start
  mirror and its 157 countries.
- Enabled-mod `make smoke`: passed with zero new normalized `error.log` lines.
- The autonomous driver reached the AD 1 country selector, chose Observe, and
  paused in Observer Mode at `08:00, 1 January, 1`. Evidence:
  `docs/screens/20260721_template_removal/template_removal_ready.png` and
  `docs/screens/20260721_template_removal/template_removal_observing.png`.
- The live `error.log` contains zero `Removing invalid law`, zero `Removing
  invalid estate privilege`, and zero boundary `ruler_term`/heir/regent
  diagnostics.

**Accepted.** The fresh-start government-default regression is resolved. This
does not claim the remaining M6 country-inspector coverage, M8 AI-research
coverage, or the renderer-blocked long-observer gate.

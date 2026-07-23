# M4 central-European exact-name probe - 2026-07-23

## Scope

This rapid dynamic-name subsystem probe covers six Pleiades-backed direct city
points: Vesontio, Emona, Poetovio, Scarbantia, Savaria, and Vindobona. Their
recorded settlement ranges include AD 1, and each point falls from 0.02 km to
0.61 km from its installed Roman-controlled city key. Near-site candidates were
excluded rather than represented as exact locations.

## Static gate

`gmake validate` passed. The generated dynamic-name layer reports 61
coordinate-verified capitals plus 111 curated direct names across eleven
mirrored localization clients. The localization-derived M12 anachronism audit
was regenerated and reports zero prohibited terms.

## Menu smoke

The paired `gmake smoke` check reached the menu in both the vanilla control and
the enabled ANTIQVITAS playset. Its normalized log comparison reported:

`smoketest: PASS (zero new lines; 0 baseline line types absent)`

No observer game was run because this batch changes generated map labels only;
static rendering checks and a paired menu/log smoke are the bounded acceptance
gate for that subsystem.

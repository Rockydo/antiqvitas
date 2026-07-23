# M4 exact Gallic-name probe - 2026-07-23

## Scope

This rapid dynamic-name probe adds fourteen direct Pleiades-backed city labels
across Roman Gaul. Every settlement point is active at AD 1 and falls within
0.62 km of its installed key. The already-covered Metz point was not duplicated;
near-site candidates remained out of scope.

## Static gate

`gmake validate` passed. The dynamic-name generator reports 61
coordinate-verified capital anchors plus 125 curated direct city labels across
all eleven localization clients. The regenerated M12 audit reports zero
prohibited player-facing terms.

## Menu smoke

The paired vanilla/enabled `gmake smoke` run reached both menus. Its normalized
comparison reported: `smoketest: PASS (zero new lines; 0 baseline line types
absent)`.

No observer game was used: this is generated display-name localization only, so
the static renderer checks and paired menu/log comparison are the applicable
rapid acceptance gate.

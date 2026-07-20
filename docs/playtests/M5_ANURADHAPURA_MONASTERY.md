# M5 Anuradhapura monastic anchor

Run date: 2026-07-20
Game: EU5 1.3.1.1, build 24187685
Mode: enabled ANTIQVITAS playset and debug-mode autonomous driver

## Result

Added an engine-valid `monastery` at the existing Anuradhapura city and market
node. UNESCO documents Anuradhapura's Buddhist monastic complexes as evolving
from the third century BCE, placing their broad institutional presence safely
before the AD 1 campaign boundary.

`make validate` passed. A fresh enabled-mod `make smoke` reached the rendered
menu and reported zero new `error.log` lines against the accepted baseline.

## Scope

The generic building represents a broad Buddhist monastic-institution surface.
It does not call the complex Christian, identify a particular AD 1 structure,
reconstruct landholdings or monastic rule, or assert that its later surviving
monuments had their present form at the campaign start.

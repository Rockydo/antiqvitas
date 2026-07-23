# Tier-3 location-name coverage

`tools/generate_m4_tier3_names.py` makes every installed map key explicit in
mod localization. It emits 28,573 root fallbacks and 12,446 culture-bound,
populated-field adapters after higher-confidence names are excluded. Retained
labels are not historical assertions; each is `tier3` and is replaced whenever
a Tier-1 direct or Tier-2 Pleiades adapter becomes available.

The current Tier-2 precedence chain contains 82 bounded (at most 1.50 px),
216 wide (1.50--3.25 px), and 521 remote (3.25--6.00 px) precise AD 1 Pleiades
settlement adapters. The remote layer is source-labelled `T2R` and explicitly
records its lower-confidence map-proxy boundary rather than asserting exact
local identity.

The 427 map-only keys without an installed English label receive a mechanical
key-derived label, separately marked `ENGINE:location-key;T3`. This prevents
raw keys while making the absence of historical evidence auditable.

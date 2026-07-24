# Tier-3 location-name coverage

`tools/generate_m4_tier3_names.py` makes every installed map key explicit in
mod localization. It emits 28,573 synthetic root fallbacks and 11,199
culture-bound populated-field adapters after higher-confidence names are
excluded. Tier-3 labels use a deterministic, group-shaped display morphology;
they are not historical assertions and are replaced whenever a Tier-1 direct
or Tier-2 Pleiades adapter becomes available.

The current Tier-2 precedence chain contains 82 bounded (at most 1.50 px),
216 wide (1.50--3.25 px), 521 remote (3.25--6.00 px), and 878 far (6.00--12.00
px) precise AD 1 Pleiades settlement adapters. The remote layer is source-labelled `T2R` and explicitly
records its lower-confidence map-proxy boundary rather than asserting exact
local identity.

The map-only keys without an installed English label receive the same neutral
synthetic treatment. This prevents raw keys and unqualified modern labels
while making the absence of historical evidence auditable through `T3M`.

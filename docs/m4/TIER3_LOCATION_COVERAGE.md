# Tier-3 location-name coverage

`tools/generate_m4_tier3_names.py` makes every installed map key explicit in
mod localization. It emits 28,573 root fallbacks and 12,967 culture-bound,
populated-field adapters after higher-confidence names are excluded. Retained
labels are not historical assertions; each is `tier3` and is replaced whenever
a Tier-1 direct or Tier-2 Pleiades adapter becomes available.

The 427 map-only keys without an installed English label receive a mechanical
key-derived label, separately marked `ENGINE:location-key;T3`. This prevents
raw keys while making the absence of historical evidence auditable.

# R5 Rome current acknowledgement and market-notice control - 2026-08-04

A fresh non-debug player Rome session at native 1280x720 reached the live map.
On 1 February, the `Immensum Bellum` historical-current card rendered with its
art, localized title, description, and acknowledgement control. Selecting that
control dismissed the card; the session subsequently advanced from 5 February
to 1 March during a 180-second maximum-speed observer interval without a
renderer exit.

The build changes only `OTHER_PERFORMS_create_market_ACTION` from `popup=yes`
to `popup=no` in the generated message-type overlay. Player-created market
messages and every other installed message definition retain their normal
contract. This prevents AI market notices from becoming a modal obstruction
while preserving the seeded AD 1 market network.

The run still appended one `Getting relation with itself` assertion at the
monthly market pulse. It is therefore evidence that currents are actionable and
the immediate AI-popup pacing problem is removed, not a clearance of the Rome
century gate. Evidence is under `docs/screens/R5_RENDER_720_SILENT/`.

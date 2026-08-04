# Ancient situation panel verification — 2026-08-04

## Scope

Verify that a newly authored situation opens a readable, interactive lateral
panel rather than the previous blank body.

## Controlled route

1. Started the enabled ANTIQVITAS build as player Rome without debug mode.
2. Used the fixed New Game → Rome → Play route, dismissed the opening agenda,
   and advanced at the driver’s bounded maximum speed through the first monthly
   situation pulse.
3. Opened the top-bar **Aestian Amber Shore** situation alert using its native
   `ShowSituation` action.

## Result

The panel is rendered and readable. It shows the Aestian Amber Shore title,
illustration, start date, localized description, expandable end requirements,
resolution-progress control, and the situation data map. The alert tooltip
also rendered the same description and its active end conditions before the
panel was opened.

Evidence screenshots:

- `docs/screens/R5_SITUATION_COMMON_PANEL_20260804/observer_0001.png` — active
  situation notification.
- `docs/screens/20260804_121317/R5_SITUATION_COMMON_PANEL_20260804/alert_hover_3.png`
  — native alert tooltip and end requirements.
- `docs/screens/20260804_121345/R5_SITUATION_COMMON_PANEL_20260804/aestian_panel_full.png`
  — populated lateral panel and data map.

The central empty rectangle visible behind the lateral panel is the independent
New Market Underway event overlay, not the situation panel.

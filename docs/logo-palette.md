# Logo palette alignment

25 November 2026. The existing logo now supplies the dashboard's brand colors.
The layout, typography, motion, data definitions, and native controls retain the
24 November refinement.

## Palette

These RGB colors were sampled directly from `assets/retailpulse-logo.png`:

| Logo color | RGB hex | UI role |
| --- | --- | --- |
| Deep navy | #060A23 | Primary KPI background |
| Navy ink | #070C27 | Main text and headings |
| Electric blue | #2759FB | Navigation, native actions, focus, sales charts |
| Cyan | #3DAAFD | Revenue help icon against navy |
| Violet | #404EFD | Selected segmented controls |

The logo contains gradients and slightly translucent pixels. These are sampled
RGB values rather than a claim that the image has a single flat palette. White
surfaces and lighter blue, violet, and cyan tints provide readable data regions.
Existing positive/negative semantic colors retain their meaning.

CSS brand primitives and semantic roles live in `assets/styles.css`; native
Streamlit theme and Plotly use the same blue, navy, and neutral palette. The
current canonical palette is recorded in
[the interface system](../design-system/retailpulse/MASTER.md).

## Verification

All 84 tests passed after the color changes, and `git diff --check` passed.
Chrome checks passed on all six pages and at 1440px, 768px, and 375px, with no
page overflow, clipped KPI values, console errors, or page exceptions. Revenue,
orders, AOV, and units match the real-workbook baseline. Aggregation, keyboard
reset, visible blue focus, and reduced motion were exercised. Browser evidence
and desktop/phone screenshots are linked below. Analytical
modules and the logo remain byte-identical to the earlier session-start hashes.

- [Desktop](evidence/logo-palette/desktop.png)
- [Phone](evidence/logo-palette/phone.png)
- [Browser and contrast checks](evidence/logo-palette/checks.json)

The installed Brand color-management guidance and Impeccable colorize guidance
informed the palette mapping. The anti-slop checks remain in the owner's selected
implementation mode. Brand direction: cool, precise retail reporting with navy
hierarchy, blue active context, and restrained violet/cyan supporting details.
ENERGY 2 / RHYTHM 2 / MOTION 1.

## Delivery checks

- **Hard gate PASS:** all six pages render, existing recovery tests pass, and
  desktop/phone checks show readable, unclipped values with visible focus.
- **Purpose gate PASS:** sampled logo colors have explicit roles in navigation,
  analytical hierarchy, selected controls, and accessible help. No new assets.
- **Liveliness PASS:** the existing revenue focal point and motion remain, with
  a consistent logo palette connecting the interface.
- **Craft PASS:** 84 tests pass; browser errors are absent; measured text contrast
  is at least 5.37:1 for selected navigation and KPI labels, and control boundaries
  measure 3.50:1. See the recorded checks above.

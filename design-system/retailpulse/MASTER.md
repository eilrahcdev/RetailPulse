# RetailPulse interface system

## Purpose and direction

Help a retail analyst assess selected-period sales, compare the preceding period,
then trace changes to invoice items, countries, and individual transactions.
Revenue is the primary decision surface; orders, AOV, and units give context.

Compact, aligned enterprise reporting with the owner's logo palette, confirmed
25 November 2026: deep navy, electric blue, cyan, violet, and white. Cool white
surfaces and blue-family summary tints connect the UI to the logo. The rounded
panels and motion retain the owner's 24 November video reference. That reference
refines the existing dashboard;
its finance screens, payment cards, example values, and navigation are not content
for RetailPulse. Existing analytical hierarchy and native controls remain.

Reading this as: a retail analytics workspace for an analyst, in a cool, restrained
reporting style, dial ENERGY 2 / RHYTHM 2 / MOTION 1. Visitor mode: Operate.
Revenue is the focal point, the full-width trend follows, and compact supporting
breakdowns retain the existing scanning order.

The installed Brand, Impeccable, Animate, and anti-slop skills inform this refinement.
The Impeccable context launcher could not run because its engine was unavailable;
the existing application and this system provided the project context directly.

## Verified research and scope

Local UI UX Pro Max searches:

- `retail analytics enterprise dashboard --design-system`: Minimalism & Swiss
  Style fits enterprise dashboards. Its Enterprise Gateway marketing pattern is
  irrelevant; a narrower retry returned the same pattern, which is not adopted.
- `Swiss enterprise tabular --domain typography`: Minimal Swiss recommends one
  sans-serif family and weight variation for dashboards. Use locally available
  Arial/Helvetica rather than introducing a network font dependency.
- `trend time-series line --domain chart`: Trend Over Time recommends line charts,
  distinguishable line styles, nearby legends, and a data-table alternative.
- `chip collection reflow --domain ux`: preserve filter labels through wrapping
  rather than clipping a fixed-height row.

The catalog has no Streamlit stack entry. Platform-independent recommendations
are adapted to native Streamlit controls and Plotly. Marketing sections, a second
accent, Fira Code headings, GSAP, and framework changes are not adopted.

## Semantic tokens

Phase 1 analytical extensions retain this system. Data Quality Center uses the
native metrics and bordered table regions. Source scope is explicit;
inapplicable shared controls remain visible and disabled. Credit breakdowns use
native tabs inside the established sales page. Small current-period trend
markers enable Plotly point selection; comparison styling remains distinct.
Every selectable chart has a native record selector and context-restoring Back
action. UI UX Pro Max searches for error clarity/recovery and navigation state
preservation informed these interactions; the catalog has no Streamlit stack.

| Role | Value | Reason |
| --- | --- | --- |
| Canvas | #F5F7FD | Cool white tinted toward the logo's blue |
| Surface | #FFFFFF | Clear data and control surfaces |
| Primary text | #070C27 | Navy sampled from the logo at (640, 180) |
| Secondary text | #56617B | Readable blue-gray supporting context |
| Primary accent / focus | #2759FB | Logo blue sampled at (350, 850); navigation, focus, current sales |
| Accent surface | #E9EFFF | Light blue hover and order grouping |
| Revenue surface | #060A23 | Logo navy sampled at (640, 250); primary sales measure |
| Supporting KPI surfaces | #E9EFFF / #EFEDFF / #E7F5FF | Light blue, violet, cyan tints of the logo bars |
| Selected segmented controls | #404EFD | Logo violet sampled at (625, 840) |
| Revenue help icon | #3DAAFD | Logo cyan sampled at (625, 550), visible against navy |
| Static border | #DCE2F0 | Separate analytical regions |
| Control border | #80899F | Discoverable input boundaries |
| Comparison / secondary marks | #717B94 | Prior period and secondary ranked bars |
| Chart grid | #E8ECF5 | Support values without competing with data |

Samples use original image RGB channels; the logo has slightly translucent pixels.
Lighter UI tints and darker hover states are derived colors, not claimed samples.
Exact bright cyan stays on navy; readable text and focus use the darker blue.

Semantic positive/negative delta colors remain native, with arrows and signed
values. They do not introduce another branding accent.

## Typography and spacing

- One family: Arial, Helvetica, sans-serif; no external font request.
- Page title: 30px / 38px (26px / 34px on phones), weight 600.
- Section title: 16px / 24px, weight 600.
- KPI revenue: 30-32px; other values: 24-28px; tabular figures throughout.
- Body/control copy: 14-16px. Context/chart labels: 12-13px, never below 12px.
- Spacing unit: 8px; group gaps/padding use 8, 16, 24, or 32px.
- Radius: 14px panels, 8px controls, 6px segmented choices. Panels remain flat;
  color groups the existing sales measures rather than implying interactivity.
- Interactive controls retain visible labels, native semantics, focus indicators,
  and at least 44px height for principal touch controls.

## Five implementation priorities

1. Hierarchy: revenue-weighted native KPI cards, followed by a full-width trend.
2. Density: preserve compact reporting and fine rules, with reference-inspired
   grouping and rounding rather than adding new dashboard sections.
3. Orientation: compact persistent navigation, a short contextual header, and
   stable shared filter controls whose full values remain available.
4. Charts: one logo-blue accent, gray dashed comparison, readable legends and axes,
   rank labels with exact hover values, and optional native data tables.
5. Records: dates/invoices and monetary measures in a useful column order,
   explicit numeric formatting, compact rows, working search and pagination.

## Component and responsive rules

- Sidebar direction follows the supplied video's compact brand row, grouped
  icon navigation, selected-row treatment, and bottom workspace details. Keep
  the logo palette and native sidebar resizing, collapse, and mobile drawer.
- The existing `navigation` radio remains the single stateful control. Visual
  groups are Workspace (Overview), Analytics (sales, products, geography), and
  Data (explorer, quality). Decorative SVG masks match those six existing pages;
  their order follows `PAGES`. Native accessible names and arrow keys remain.
- Expanded branding pairs the original image with the existing name/subtitle.
  Native `st.logo` continues to supply the collapsed header logo and favicon.
  The dataset disclosure retains the upload, duplicate policy, and source link.
- Source details sit at the bottom when space permits and remain in the normal
  sidebar scroll flow on short screens. Navigation targets are at least 44px;
  group headings and supporting sidebar copy use 12px or larger text.
- Native radio navigation, date range, multiselects, metrics, segmented controls,
  expanders, dataframes, uploader, and downloads retain their working state keys.
- Main revenue plot spans the content width. Product and country breakdowns share
  the next row when space permits. Period findings use a quiet textual section.
- Four KPI indicators use tinted surfaces, with the wider revenue column first.
  Reflow to two columns on tablet/phone and one only when values cannot fit.
- Controls wrap by content width; date range stays readable. Selected product
  labels wrap rather than disappear. Do not hide filters through CSS.
- Product/country detail tables and explorer records remain native sortable
  dataframes. Wide tables may scroll inside their own boundary; the page must not.
- Routine control feedback uses 140ms color transitions. Pointer press feedback
  uses a 1px translation over 100ms, gated to fine pointers with hover support.
- Page headers are keyed by existing page names. A new header settles by 4px
  from 75% opacity over 180ms using cubic-bezier(0.23, 1, 0.32, 1). Purpose:
  acknowledge a destination change without delaying or moving analytical data.
  `@starting-style` keeps the normal state visible in browsers without support.
  Stable header keys avoid replaying the entrance on routine filter updates.
- Reduced-motion mode uses immediate state changes and removes spatial motion.
  Charts and KPI numbers do not animate, count up, or loop.
- Prepared CSV downloads use Streamlit's native `on_click="ignore"`, so exporting
  the displayed selection does not rerun the dashboard or replay its states.
- Preserve loading, missing-file, invalid-upload, and no-match recovery states.

## Preservation boundary

Do not change the data processing, metrics, duplicate policy, comparison dates,
raw workbook, notebooks, Python environment, or dependencies for this visual pass.
No deployment, commit, or push is part of this work.

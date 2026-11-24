# RetailPulse interface system

## Purpose and direction

Help a retail analyst assess selected-period sales, compare the preceding period,
then trace changes to invoice items, countries, and individual transactions.
Revenue is the primary decision surface; orders, AOV, and units give context.

Swiss-inspired enterprise reporting: compact, aligned, neutral, and legible.
The owner's Linear/Stripe references inform restraint and hierarchy, not copying.
Anti-slop dials: ENERGY 1 / RHYTHM 2 / MOTION 1. UI UX Pro Max research dials:
variance 2/10, motion 1/10, density 8/10.

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
existing metric strip and bordered table regions. Source scope is explicit;
inapplicable shared controls remain visible and disabled. Credit breakdowns use
native tabs inside the established sales page. Small current-period trend
markers enable Plotly point selection; comparison styling remains distinct.
Every selectable chart has a native record selector and context-restoring Back
action. UI UX Pro Max searches for error clarity/recovery and navigation state
preservation informed these interactions; the catalog has no Streamlit stack.

| Role | Value | Reason |
| --- | --- | --- |
| Canvas | #F5F6F8 | Quiet neutral frame for the report |
| Surface | #FFFFFF | Clear data and control surfaces |
| Primary text | #202630 | High-contrast reading and figures |
| Secondary text | #596373 | Readable supporting context |
| Primary accent / focus | #2457C5 | Selected state and current sales series |
| Accent surface | #EAF0FC | Selected navigation only |
| Static border | #DDE1E7 | Separate groups without decorative cards |
| Control border | #7D899A | Discoverable input boundaries |
| Comparison / secondary marks | #6B7483 | Prior period and secondary ranked bars |
| Chart grid | #E8EBEF | Support values without competing with data |

Semantic positive/negative delta colors remain native, with arrows and signed
values. They do not introduce another branding accent.

## Typography and spacing

- One family: Arial, Helvetica, sans-serif; no external font request.
- Page title: 26px / 32px, weight 600. Section title: 16px / 24px, weight 600.
- KPI revenue: 30-32px; other values: 24-28px; tabular figures throughout.
- Body/control copy: 14-16px. Context/chart labels: 12-13px, never below 12px.
- Spacing unit: 8px; group gaps/padding use 8, 16, 24, or 32px.
- Radius: 4px controls and sections; no shadows, glass, or decorative fills.
- Interactive controls retain visible labels, native semantics, focus indicators,
  and at least 44px height for principal touch controls.

## Five implementation priorities

1. Hierarchy: revenue-weighted KPI strip followed by a full-width revenue trend.
2. Density: remove tall independent metric cards, redundant framing, and excess
   header space; use fine rules and a consistent spacing rhythm.
3. Orientation: compact persistent navigation, a short contextual header, and
   stable shared filter controls whose full values remain available.
4. Charts: one blue accent, gray dashed comparison, readable legends and axes,
   rank labels with exact hover values, and optional native data tables.
5. Records: dates/invoices and monetary measures in a useful column order,
   explicit numeric formatting, compact rows, working search and pagination.

## Component and responsive rules

- Native radio navigation, date range, multiselects, metrics, segmented controls,
  expanders, dataframes, uploader, and downloads retain their working state keys.
- Main revenue plot spans the content width. Product and country breakdowns share
  the next row when space permits. Period findings use a quiet textual section.
- Four KPI indicators use a shared surface, with the wider revenue column first.
  Reflow to two columns on tablet/phone and one only when values cannot fit.
- Controls wrap by content width; date range stays readable. Selected product
  labels wrap rather than disappear. Do not hide filters through CSS.
- Product/country detail tables and explorer records remain native sortable
  dataframes. Wide tables may scroll inside their own boundary; the page must not.
- Respect reduced motion; no new entrance animation or animated chart transitions.
- Preserve loading, missing-file, invalid-upload, and no-match recovery states.

## Preservation boundary

Do not change the data processing, metrics, duplicate policy, comparison dates,
raw workbook, notebooks, Python environment, or dependencies for this visual pass.
No deployment, commit, or push is part of this work.

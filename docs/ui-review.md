# RetailPulse UI/UX review

This is the 23 November review. See the [24 November video refinement](video-ui-refresh.md)
and [25 November logo palette alignment](logo-palette.md) for subsequent changes.
The [sidebar refinement](sidebar-refinement.md) records the latest navigation work.

Date: 2026-11-23. Scope: presentation and usability within the existing Streamlit
application. Design authority: the user's Swiss/enterprise brief and local
UI UX Pro Max skill. Canonical rules: `design-system/retailpulse/MASTER.md`.

## Five improvements

| Priority | Previous presentation | Implemented change |
| --- | --- | --- |
| Revenue hierarchy | Four equal rounded cards; trend shares the first row | Revenue-weighted metric strip; full-width trend before product/country detail |
| Information density | Tall metric cards, large corner radii, small shadows | Fine rules, 4px radii, no shadows, 8px spacing increments, aligned tabular figures |
| Orientation and controls | Large colored brand, promotional subtitle, card-framed filters | Neutral wordmark, short analytical context, visible compact filters, persistent native navigation |
| Chart readability | Two accent hues, tinted area fill, small legends | One blue accent, gray dashed comparison, 12px labels, exact hover values, visible rank labels, optional data tables |
| Transaction review | Monetary values appear late in a generic column sequence | Date/invoice first; quantity, unit price, and line value together; readable headers; compact 32px rows |

Long product selections and transaction-type collections wrap within expanding
controls. Full descriptions remain available in chart-data tables and hover
details when a plot label is shortened. Single-point monthly comparisons use
visible markers for both series rather than an invisible one-point line.

## Research and implementation choices

The local skill's Minimalism & Swiss Style, Minimal Swiss typography, Trend Over
Time chart, and Chip Collection Reflow recommendations fit this application.
The generated Enterprise Gateway marketing layout failed the relevance check;
a narrower retry returned the same pattern, so it was not persisted or used.
The curated master records the selected guidance and its limits.

There is no Streamlit stack in the skill's catalog. Implementation uses native
Streamlit configuration, metrics, columns, inputs, expanders, tables, and
downloads; native APIs were checked against the installed version and official
documentation. No React, extra UI package, remote font, GSAP, or application
JavaScript was introduced.

The one accent is #2457C5. Gray comparison marks and neutral surfaces retain the
revenue trend's hierarchy. Native signed/arrow deltas preserve semantic feedback.
Arial/Helvetica keeps a single sans-serif family available on the target machine.

## Measured visual comparison

At a 1440 × 1080 viewport, with the same November 2011 selection:

| Measurement | Before | After |
| --- | ---: | ---: |
| KPI region height | 151px | 126px |
| Revenue panel width | 663px | 1,076px |
| Revenue panel top | 559px | 519px |
| Page-level horizontal overflow | None | None |

The page heading clears Streamlit's own toolbar. All four KPI values match the
starting screenshot exactly: £1,509,496.33, 2,769, £545.14, and 754,507.
Product codes use an explicit categorical axis, preserving distinct ranked bars
even when the stock code looks numeric. All seven displayed countries retain
their labels.

Palette contrast was calculated using WCAG relative luminance:

| Pair | Ratio |
| --- | ---: |
| #202630 on white | 15.20:1 |
| #596373 on #F5F6F8 | 5.62:1 |
| #2457C5 on white | 6.47:1 |
| #6B7483 on white | 4.72:1 |
| #7D899A control boundary on white | 3.55:1 |
| #2457C5 on #EAF0FC selection | 5.66:1 |

## Functionality and preservation

- The existing 45 pytest tests pass; dependency consistency and Python compilation
  checks pass.
- Browser checks exercised all five pages, ranking, shared country/product filters,
  reset followed by another interaction, duplicate policy, date changes, and an
  unavailable comparison.
- Daily/weekly/monthly trends reconcile to the same selected revenue. The new
  chart-data expanders open and close using native controls.
- Product, country, and filtered transaction CSV downloads work. Explorer search,
  page-size changes, page 2, empty search, and recovery were exercised.
- Invalid uploads show recovery guidance. A workbook containing 30 genuine UCI
  rows was used to check valid uploads; removal restored the complete local file.
- Responsive checks covered 375px, 768px, 1024px, 1440px, and 844 × 390 landscape.
  Reduced-motion and 200% CSS zoom were checked. Narrow layouts preserve full
  KPI values, title clearance, and no page-level horizontal overflow.
- Mobile sidebar navigation and keyboard search work. No browser console errors
  or page exceptions occurred in the completed interaction sequence.
- Starting hashes confirm `src/data_processing.py`, `src/metrics.py`,
  `src/utils.py`, requirements, project metadata, both notebooks, and the raw
  workbook are byte-identical. No environment recreation, commit, push, or
  deployment was performed.

Screenshots of upper/lower Overview, Data Explorer, phone/tablet/landscape, and
zoom were actually captured and visually inspected. Temporary browser tooling,
screenshots, exports, baseline source copies, and measurements remain under the
ignored `.venv/qa/ui-refresh/` directory.

## Delivery review

- **Hard gate PASS:** source-backed figures; preserved interactions; working
  loading/error/empty recovery; responsive pages with visible focus treatment.
- **Purpose gate PASS:** blue identifies selection/current sales, gray identifies
  comparison, rules group related data, and each chart has an analytical question.
  No gradient, blur, glow, decorative animation, or cosmetic chart added.
- **Liveliness PASS:** ENERGY 1 / RHYTHM 2 / MOTION 1, with a clear revenue focal
  point, restrained identity, and varied layouts according to data density.
- **Craftsmanship PASS:** verified rendered alignment and labels, explicit
  categorical ranks, data-table alternatives, real downloads, and regression
  coverage. The measured results and limitations are recorded here.

## Limits

This is a light-theme review, not a new dark-theme implementation. Phone and
landscape checks use browser emulation rather than physical devices. CSS zoom is
not an OS magnifier test. Wide transaction tables retain native internal
horizontal scrolling. Plotly hover points are supplemented with native tables;
full screen-reader certification and keyboard traversal of every chart point
were not performed. This work does not verify any hosted deployment.

# RetailPulse validation and design notes

For the current six-page analytical extension, use
[Phase 1 verification](phase1-verification.md). The original checks below are
retained as historical implementation evidence.

The original analytical validation below remains applicable. The 2026-11-23
presentation refresh supersedes the original palette and layout notes; see
[UI/UX review](ui-review.md) and `design-system/retailpulse/MASTER.md` for the
current design system and rendered verification.

## Analytical verification

The focused pytest suite exercises source-preserving classification, exact-row
duplicate flags, missing values, invalid and non-finite numeric inputs, unique
invoices, revenue, AOV, credits, comparison coverage, leap-day boundaries,
country/product/date filters, literal searches, CSV exports, and Streamlit pages.
Test fixtures are artificial and remain inside the test suite.

An independent calculation on the official workbook reconciled the dashboard
against direct Pandas arithmetic on the source records. Product and country
revenue aggregates also reconcile with the positive-sales KPI.

| Full workbook check | Observed value |
| --- | ---: |
| Source rows | 541,909 |
| Exact repeats beyond first | 5,268 |
| Missing customer IDs | 135,080 |
| Missing descriptions | 1,454 |
| Valid positive-sales lines | 530,104 |
| Usable credit lines | 9,288 |
| Excluded / review lines | 2,517 |
| Positive-sales revenue, repeats retained | £10,666,684.54 |
| Unique valid sales invoices | 19,960 |
| Positive-sales units | 5,588,376 |
| Recorded credit value | £896,812.49 |

For the default 1-30 November 2011 selection, observed revenue is £1,509,496.33,
orders are 2,769, AOV is £545.14, and units are 754,507. The equal-duration
comparison is 2-31 October 2011. These are historical dataset results, not live
business figures. Monetary totals are displayed to two decimal places; source
prices and intermediate calculations retain their precision.

The unchanged raw workbook has SHA-256:

```text
43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d
```

## Design decisions

Direction: the supplied business-report screenshot and explicit light palette.
ENERGY 1 / RHYTHM 2 / MOTION 1. No new imagery, identity assets, or animations.

- Indigo identifies the primary revenue series and selected navigation; teal
  distinguishes country performance and the prior-period series.
- White chart surfaces separate the analytical views from the off-white canvas.
  A very small shadow is limited to the peer KPI cards for quick scanning.
- Segoe UI/system sans-serif keeps dense Windows business data readable without
  another font dependency or external font request.
- Equal KPI cards reflect four peer measures. A larger trend panel gets more
  space because its dates need a readable horizontal axis; product details and
  explanatory insights follow below rather than competing above the fold.
- Fourteen-pixel card corners and smaller input/navigation corners distinguish
  content surfaces from controls. The selected sidebar label has a real state.
- Material symbols identify revenue, invoices, order value, units, export,
  external source, and reset actions. No decorative status indicators are used.
- Streamlit owns navigation, input semantics, upload behavior, table interaction,
  and mobile sidebar controls. CSS is limited to keyed regions and documented
  component test IDs; no application JavaScript is injected.
- Missing-workbook guidance, named loading messages, schema errors, no-match
  states, and unavailable comparisons make incomplete states explicit.
- The dataset supplies no product-category or cost fields, so the reference's
  category donut and gross-margin card are replaced with supported analysis.

## Contrast checks

Ratios calculated with the WCAG relative-luminance formula, without rounding
before threshold comparisons:

| Foreground / background | Ratio | Use |
| --- | ---: | --- |
| #17243B / #FFFFFF | 15.53:1 | Main text |
| #64748B / #F7F9FC | 4.51:1 | Muted text on canvas |
| #64748B / #FFFFFF | 4.76:1 | Muted text on cards |
| #4F46E5 / #FFFFFF | 6.29:1 | Primary accent and focus |
| #4338CA / #EEEDFF | 6.85:1 | Selected navigation text |
| #0D9488 / #FFFFFF | 3.74:1 | Primary teal chart marks |
| #8B83DC / #FFFFFF | 3.29:1 | Secondary product chart marks |
| #4B9F93 / #FFFFFF | 3.14:1 | Secondary country chart marks |
| #8190A5 / #FFFFFF | 3.25:1 | Input boundaries |

Teal is used for chart marks rather than small text. Chart tooltips and axes use
the text palette. Native controls retain their keyboard behavior, with explicit
focus outlines and selected navigation focus treatment. The app ships a light
theme, not a custom light/dark toggle.

## Browser and interaction verification

Rendered application inspected in installed Chrome, running locally against the
real UCI workbook. The completed checks were:

| Control or view | Observed behavior |
| --- | --- |
| All five sidebar destinations | Correct page title and page content rendered |
| KPI cards | Actual November totals, full revenue value visible, equal card heights |
| Revenue aggregation | Daily, weekly, monthly choices produced 30, 5, and 1 selected-period buckets |
| Product ranking | Revenue and unit rankings changed the top-ten bar chart |
| Product/country downloads | Real CSV downloads; both revenue totals reconcile with £1,509,496.33 |
| Explorer search | Case-insensitive literal search for 85123A returned 275 matching rows across searchable columns |
| Explorer pagination | Changed rows per page to 25 and moved to page 2 |
| Explorer download | All 275 matching records exported rather than only the displayed page |
| Empty explorer search | Clear no-match guidance, then recovered after clearing the query |
| Global country filter | France changed KPI revenue to £31,758.71 and country chart to France |
| Combined country/product filter | France plus AMAZONFEE showed an empty state |
| Reset filters | Returned to original totals; cleared selections remained cleared on later interactions |
| Duplicate policy | Enabling exclusion changed real totals; disabling restored them |
| Date segments | Changed to December 2010; comparison unavailable and no percentage deltas |
| Invalid upload | Missing-column error; removing the upload restored the local file |
| Valid upload | A test workbook containing 30 unchanged, genuine UCI rows rendered with its own coverage and filters |
| Upload removal | Returned to the complete local workbook and default period |
| Methodology disclosure | Opened source quality counts and metric definitions |
| Official source link | Correct UCI dataset destination |
| Narrow layouts | 1024, 768, and 390 px: no page overflow or truncated KPI values |
| Mobile sidebar / keyboard | Opened navigation, changed to Explorer, closed sidebar, searched using the keyboard |
| 200% CSS zoom | No page-level horizontal overflow; screenshot inspected |
| Browser runtime | No page exceptions or console errors in the completed checks |

The browser check caught a reset issue that AppTest alone did not reproduce:
deleting session-state keys temporarily reset the metrics while stale browser
selections returned later. Reset now explicitly assigns empty selections and the
default date tuple. The browser sequence was repeated successfully after this
fix. Date keyboard edits commit after focus leaves the date control.

The final test run passed **45 tests**. `pip check` found no broken requirements,
and `compileall` completed successfully. Missing/empty/unreadable source states and
transaction-type filtering also have focused AppTest coverage.

Screenshots of the upper and lower Overview, Data Explorer, narrow layouts, and
CSS zoom were captured and visually inspected. Browser emulation is not a
physical-phone test. CSS zoom is not an OS magnifier test. These checks are not
a complete accessibility certification or production deployment assessment.

## UI delivery gate

- **Hard gate PASS:** real data and named sources only; all five destinations and
  built controls exercised; missing, loading, error, and empty states present;
  no fabricated metrics, testimonials, media, or live-data claims. Native
  semantics, explicit focus treatment, and tested responsive layouts retained.
- **Purpose gate PASS:** the supplied palette and reference drive hierarchy;
  chart accents separate series, semantic icons identify measures/actions, and
  only the peer KPI surfaces have a small shadow. No gradients, decorative
  animation, unrelated imagery, ghost links, or application JavaScript added.
- **Liveliness PASS:** ENERGY 1 / RHYTHM 2 / MOTION 1, one clear revenue focal
  point, indigo/teal identity, spacing that separates controls from results, and
  chart widths allocated to their content rather than equal template tiles.
- **Craftsmanship PASS:** positive-sales and credit definitions are visible;
  source records reconcile with calculations; four KPI cards align; native
  navigation and filtered export work; the reviewed desktop and narrow layouts
  preserve readable values. Verification limits are stated above.

## Reproduce local checks

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall -q app.py src tests
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Browser QA tooling and temporary exports are kept under the ignored
`.venv/qa/` directory and are not runtime dependencies. The application requires
only the existing Python requirements. No deployment, commit, or push is part of
this implementation.

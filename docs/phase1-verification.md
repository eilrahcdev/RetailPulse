# Phase 1 verification

This supplements the earlier [validation](validation.md) and
[interface review](ui-review.md). Formulas and interpretation are in
[Phase 1 analytics](phase1-analytics.md).

## Automated verification

The final analytical and Streamlit AppTest suite passes **84 tests**. Features
were added and tested separately: source quality, bounded drilldowns, then credit
composition. The original 45 tests remain. New coverage includes overlapping
findings, raw evidence, invalid and undated inputs, scoped denominators,
reconciliation failures, credit grouping, prior-series rejection, leading-zero
stock codes, partial weeks, leap months, Back navigation, source changes,
zero-sales recovery, and grouping initialization after navigation/filter reset.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall -q app.py src tests
```

Dependency checking found no broken requirements; compilation succeeded.
No dependencies were added or upgraded.

## Real-data reconciliation

Installed Chrome exercised the local Streamlit application against the complete
official UCI workbook. Direct Pandas multiplication on the actual browser CSV
downloads independently reconciles the selected chart values, within GBP 0.005:

| Browser selection | Exported sale lines | Export arithmetic and plotted total |
| --- | ---: | ---: |
| November 2011, stock code DOT | 47 | GBP 36,905.40 |
| November 2011, United Kingdom | 77,475 | GBP 1,325,346.21 |
| 14 November 2011 | 3,521 | GBP 114,419.89 |

Each export contains Sale records only and matches the selected stock code,
country, or date. The monthly-credit CSV reconciles with the original selected
credit KPI, GBP 47,740.08. The missing-customer evidence export contains all
135,080 matching original-source records, each with a unique valid workbook row
and missing CustomerID, rather than only the 50 rows shown on a page.

The default four sales KPIs remain GBP 1,509,496.33, 2,769 orders, GBP 545.14 AOV,
and 754,507 units. The source audit shows 541,909 rows, 140,345 distinct rows with
findings, 2,517 excluded/review rows, and 5,268 exact repeats after the first.
Missing customer IDs account for 24.93% of source rows. Of those rows, 132,220
are usable sales with GBP 1,755,276.64 of recorded sales value; missing IDs do
not erase that revenue. Repeated usable sales lines carry GBP 24,573.74; their
legitimacy is not inferred.

SHA-256 comparisons confirm ten original files are unchanged: the workbook,
both notebooks, processing, metrics, utilities, stylesheet, theme configuration,
requirements, and project metadata. The workbook checksum remains
`43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d`.

## Interaction and rendered checks

| Action | Verified behavior |
| --- | --- |
| Actual product and country bar clicks | Inspect opens matching Sale records in Explorer; full CSV totals match the clicked bar |
| Actual blue revenue point click | Opens 14 November records; comparison-series targets are rejected by focused tests |
| Record drilldown selector | Native keyboard interaction selects the 31 October weekly bucket; Explorer clips it to 1-6 November |
| Back to Overview | Restores original sales totals and global context; weekly selection is restored |
| Entire-workbook audit | Includes all source rows before duplicate policy; shared filters are visibly disabled |
| Missing-customer quality selection | Shows and exports all 135,080 matching evidence rows |
| Evidence pagination and search | Page 2 displays; a no-match query shows recovery guidance; clearing restores evidence |
| Current-filter audit | Shared controls enable; France narrows the source audit |
| Sales navigation and Reset filters | Restores default sales scope without a grouping initialization error |
| Credit composition, Countries, Items, Monthly credits | All four real-data tabs render; monthly CSV matches the recorded-credit KPI |
| Monthly performance axes | Revenue, orders, and AOV each label the observed November bucket once |
| 375px viewport with reduced motion | No document-level horizontal overflow or clipped metric values |
| Browser runtime | No page exceptions or console errors in the completed sequence |

Browser inspection caught two functional/presentation issues: line-only scatter
traces did not support point selection, and single-month performance charts had
repeated automatic date labels. Small current-series markers enable selection;
monthly ticks now use observed bucket dates. A navigation initialization
regression was corrected and covered by an additional AppTest case.

## Design delivery review

- **Hard gate PASS:** observed UCI records and computed values only; existing
  loading/error recovery retained; native controls and named fields; actual
  chart clicks, exports, scope changes, credit tabs, and responsive layout tested.
- **Purpose gate PASS:** current-period markers enable selection; gray dashed
  comparison remains distinct; Back identifies navigation; tabs group different
  views of recorded credits. No gradients, effects, imagery, or animations added.
- **Liveliness PASS:** existing ENERGY 1 / RHYTHM 2 / MOTION 1 retained. Revenue
  remains the sales focal point; scope and the issue-summary strip lead auditing.
  The restrained blue accent, typography, spacing, and tabular pattern are shared.
- **Craftsmanship PASS:** original design tokens, stylesheet, calculations, and
  data preserved; native table alternatives and keyboard record selection added;
  real exports reconcile and empty selections retain recovery.

## Limitations and evidence location

Actually inspected screenshots: [audit overview](evidence/phase1/quality-center.png),
[business interpretation and validation](evidence/phase1/quality-evidence.png),
[credit analysis](evidence/phase1/credit-analysis.png), and
[375px audit](evidence/phase1/quality-mobile.png). The
[browser results](evidence/phase1/browser-results.json) and
[download reconciliation](evidence/phase1/reconciliation-results.json) are saved
alongside them.

Browser automation, exports, checksums, and screenshots are retained under the
ignored `.venv/qa/phase1/` directory. This uses installed desktop Chrome and an
emulated narrow viewport, not a physical mobile device or full accessibility
certification. Native wide tables retain internal horizontal scrolling. No
deployment, real-user performance measurement, or accounting audit was performed.
Streamlit logs a default/session-state warning when Back restores a chart
control; the browser checks confirm its selected value and resulting totals are
restored. This server warning is separate from the clean browser error checks.

All delivered analysis is observed and deterministic. Phase 2 and Phase 3 remain
queued; there are no fitted forecasts, customer segments, anomaly claims,
associations, or simulated revenue mixed into the sales KPIs.

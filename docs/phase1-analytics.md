# Phase 1: analytical foundations

The audit found working shared filters, equal-duration comparisons, explicit
sales/credit classification, and metric definitions. These remain the analytical
contract. The highest-value missing feature was source-level quality evidence:
customer analytics would otherwise conceal incomplete customer attribution.

## Architecture and design

`src/data_processing.py` still loads and classifies a copy of the original eight
UCI columns. `src/metrics.py` still owns the established sales formulas.
`src/data_quality.py`, `src/drilldowns.py`, and `src/returns_analysis.py` add pure
analytical operations. `src/quality_views.py`, `src/drilldown_views.py`, and
`src/views.py` present their results with native Streamlit components.

The existing interface master remains authoritative: neutral surfaces, one blue
accent, Arial, an 8px spacing grid, subtle borders, compact tables, and a prominent
revenue trend. No new CSS, external fonts, dependencies, or frontend framework
are needed. The five main usability improvements are explicit audit scope,
source-row evidence, chart-to-record navigation, a keyboard alternative with
context-restoring Back navigation, and separate usable credits versus review
lines.

## Data Quality Center

**Business problem:** distinguish unusable records from missing attribution and
review findings before making operational or customer decisions.

Required data: all eight original UCI columns, with their original row order.
`SourceRow = original zero-based position + 2` includes the Excel header.
Evidence retains the original cells as read by Pandas, not Excel formatting,
formulas, or an audit of subsequent workbook edits. Exports use the existing
spreadsheet formula protection for text cells; this can add an apostrophe to
formula-like source text. No corrections are written to the workbook.

Fourteen overlapping checks cover identifiers, date validity, finite quantities
and prices, nonpositive prices, zero quantities, multiplication overflow,
missing customers/descriptions/countries, exact repeats, C-prefixed positive
quantities, and negative quantities without a C prefix.

- Finding percentage = rows triggering that check / all source rows in scope.
  Affected rows count each row once; check counts must not be added together.
- Entire workbook includes undated rows and ignores global filters. Those
  controls are visibly disabled while their selections are retained.
- Current filters applies inclusive dates, countries, and stock codes to source
  rows; undated rows cannot match a date range. Both audit scopes run before the
  optional duplicate exclusion and say so explicitly.
- Missing customer IDs, descriptions, and countries do not invalidate an
  otherwise eligible sale. Missing-customer sales value is attribution exposure,
  not lost revenue. Customer coverage must be considered before Phase 2.
- Exact-repeat sales value covers repeats after the first across all eight
  original columns. It is neither proven overstatement nor a deletion rule.

Seven runtime checks validate known classifications, sales/credit admission
rules, distinct sales invoice counts, product and country revenue reconciliation,
and AOV. Monetary reconciliation uses an absolute tolerance of GBP 0.005 and
rejects non-finite totals. These checks assess internal consistency, not source
authenticity, source completeness, or accounting accuracy.

## Chart drilldowns

**Business problem:** trace an aggregate to the invoice lines supporting it.

Required data: valid dated positive-sales records, invoice numbers, stock codes,
countries, quantities, and prices. Select one current-period point or bar, then
choose Inspect selected records. Chart data disclosures also offer a native
Record drilldown selector for keyboard access.

Revenue targets use actual plotted buckets. Daily targets select one date;
weekly targets run Monday through Sunday; monthly targets use calendar months.
Every target is clipped to the global inclusive date range. Prior-period points,
multiple points, malformed events, and values absent from the current chart do
not create a target. Country/product selections preserve the other global
filters. Explorer starts with Sale records only, no text search, and page 1;
the CSV contains every matching record, not merely the displayed page.

Back restores the originating page, dates, countries, products, aggregation,
ranking, and duplicate policy. Source changes clear the drilldown context.
Changing filters or search in Explorer labels the context as changed. A
zero-sales bucket may have no matching sale records; it is not an application
error and Back remains available.

## Recorded credits and cancellation review

**Business problem:** separate interpretable recorded credits from ambiguous
negative lines or cancellation conflicts without claiming verified refunds.

Required data: invoice number/prefix, quantity, unit price, date, stock code, and
country. Existing credit eligibility remains unchanged: negative quantity,
positive unit price, finite value, valid date, and present invoice/stock IDs.

- Recorded credit value = `-sum(Quantity * UnitPrice)` over eligible credits.
- Credited units = `-sum(Quantity)` over eligible credits.
- Credit invoices = distinct eligible invoice numbers within the grouping.
  Distinct counts across items or countries must not be added to get a total.
- Composition partitions candidates into usable C-prefixed credits, usable
  unprefixed negative lines, excluded C-prefixed lines, and other excluded
  negative lines. Review categories have no usable monetary valuation.
- Country, stock-code, and calendar-month tables summarize eligible credits.
  Partial edge months include selected dates only.
- Observed sales less credits retains its existing signed dataset subtotal
  definition. A credit may refer to a sale outside the selection. No original-sale
  linkage, completed refund, return reason, return rate, cost, or margin is known.

## Existing metrics and comparisons

Gross positive sales = sum of `Quantity * UnitPrice` on eligible sales; orders =
distinct selected sales invoices; units = selected sales quantities; AOV = sales
value / orders (zero when no orders). Positive non-merchandise invoice lines
remain eligible. With a product filter, AOV covers matching item value per
matching invoice, rather than whole-order value.

For an inclusive selection of N days, the comparison is the immediately previous
N calendar days using the same country/product/duplicate policy. It is shown
only when that whole range lies in recorded date coverage. Percentage change =
`100 * (current - prior) / prior`, undefined for a zero baseline. Date coverage
does not prove that every business transaction was supplied. No-sales dates
inside coverage are zero-filled for the trend under the existing convention.

## Scope of delivery

Phase 1 presents observed records and deterministic arithmetic only. RFM,
cohorts, ABC/Pareto, expanded automated insights, forecasting, anomaly detection,
market baskets, and optional simulations remain in the
[prioritized checklist](implementation-checklist.md). Future modeled and
simulated outputs must be labeled and kept separate from observed KPIs.

Verification evidence is recorded in [Phase 1 verification](phase1-verification.md).

# RetailPulse analytics implementation checklist

## Audit and order of work

The existing Streamlit app has a source-preserving Excel loader, explicit
positive-sales/credit/review classification, date/country/product filters,
equal-calendar-day comparisons with coverage checks, duplicate-policy control,
Plotly figures, paginated CSV export, a metric glossary, and regression tests.
The source remains the official UCI Online Retail workbook. The current Swiss
interface system remains the visual authority.

### Phase 1: reliable analytical foundations

- [x] Audit the loader, classifications, metrics, filters, comparisons, and tests.
- [x] P1. Data Quality Center: overlapping quality checks, source-row evidence,
  full-workbook and filtered scopes, impact on customer attribution, and metric
  reconciliation. Include undated records in full-source auditing. This is first
  because subsequent customer and predictive analyses depend on coverage.
- [x] P2. Chart drilldowns: explicitly select a current-period revenue bucket,
  product, or country and inspect its matching positive-sales invoice lines.
  Preserve other filters and provide a predictable path back.
- [x] P3. Validate and clarify recorded credits/cancellations: distinguish usable
  credits, cancellation-prefix conflicts, and unmarked negative quantities.
  Keep credits separate from gross positive sales; do not infer return reasons,
  an original-sale match, or reconciled accounting net revenue.
- [x] P4. Recheck shared filters, inclusive date boundaries, previous-period
  coverage, zero baselines, duplicate policy, and chart/explorer reconciliation.
- [x] P5. Document formulas and limitations, run focused and regression tests,
  and inspect the real rendered UI and interactions before completing Phase 1.

Features are implemented and tested in this order, one at a time. Existing
working calculations are retained; a missing feature is not grounds to redefine
revenue, orders, credits, or duplicate treatment.

Completed evidence: [analytical contract](phase1-analytics.md) and
[84-test, real-data, and browser verification](phase1-verification.md).

### Phase 2: advanced business intelligence, after Phase 1

- [ ] RFM: known customer IDs; recency anchored to the historical selection's
  reference date, distinct invoices for frequency, positive sales for monetary
  value. Report customer-attribution coverage and tie handling. No invented IDs.
- [ ] Cohorts: first observed purchase month, distinct active known customers,
  cohort denominators, and right-censored observation windows. Label first
  observed purchase rather than proven customer acquisition.
- [ ] ABC/Pareto: stock-code revenue share and cumulative share; document cutoffs
  and ties, and separate merchandise interpretation from fees/non-product items.
- [ ] Automated insights: deterministic, source-backed facts with period, filters,
  denominator, and supporting values; distinguish observations from explanations.

### Phase 3: predictive and decision support, after observed analytics

- [ ] Revenue forecasting: regular time series, training-only preprocessing,
  rolling/expanding time-based backtests, seasonal-naive baseline, held-out error
  metrics, and labeled modeled outputs. Avoid random train/test splitting.
- [ ] Anomalies: robust time-aware baselines, minimum history, documented
  thresholds, and reviewable flags; an unusual sale is not proof of fraud.
- [ ] Market baskets: valid sales grouped by invoice, deduplicated stock-code
  presence per basket, support/confidence/lift, and minimum counts. Association
  does not imply causation; cancellation/return lines do not form purchases.
- [ ] Optional what-if: explicitly simulated assumptions and outputs, isolated
  from observed KPIs and saved source records; not an elasticity claim.

No Phase 2 or 3 model, segmentation, or scenario result is implemented as part of
the initial Phase 1 increment.

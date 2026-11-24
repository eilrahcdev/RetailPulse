import pandas as pd
import pytest

from src.data_processing import clean_transactions, filter_transactions
from src.metrics import (
    change_percent, comparison_is_available, country_summary, daily_sales,
    period_summary, previous_period, product_summary, return_summary, sales_metrics,
)


def test_positive_sales_metrics_and_distinct_orders(transactions):
    result = sales_metrics(transactions)
    assert result.revenue == 57
    assert result.orders == 2
    assert result.average_order_value == 28.5
    assert result.units == 8


def test_explicit_duplicate_exclusion_changes_only_repeated_line(transactions):
    result = sales_metrics(transactions.loc[~transactions.IsExactDuplicate])
    assert result.revenue == 37
    assert result.orders == 2
    assert result.units == 6


def test_credits_remain_separate_and_observed_net_is_signed(transactions):
    result = return_summary(transactions)
    assert result["credit_value"] == 20
    assert result["credit_invoices"] == 2
    assert result["observed_net"] == 37


def test_empty_metrics_are_zero(transactions):
    result = sales_metrics(transactions.iloc[:0])
    assert result.revenue == result.orders == result.average_order_value == result.units == 0
    assert country_summary(transactions.iloc[:0]).empty
    assert product_summary(transactions.iloc[:0]).empty
    assert period_summary(transactions.iloc[:0]).empty


def test_comparison_preserves_inclusive_length_across_leap_day():
    start, end = previous_period("2024-02-29", "2024-03-02")
    assert start == pd.Timestamp("2024-02-26")
    assert end == pd.Timestamp("2024-02-28")


def test_comparison_requires_full_prior_coverage(transactions):
    assert not comparison_is_available(transactions, "2011-01-01", "2011-01-02")
    assert comparison_is_available(transactions, "2011-01-03", "2011-01-04")


@pytest.mark.parametrize("current,prior,expected", [(120, 100, 20), (50, 100, -50), (0, 100, -100), (5, 0, None)])
def test_percent_changes_never_invent_a_zero_baseline(current, prior, expected):
    assert change_percent(current, prior) == expected


def test_daily_series_includes_zero_sales_days(transactions):
    series = daily_sales(transactions, "2011-01-01", "2011-01-04")
    assert series.Revenue.tolist() == [45, 12, 0, 0]
    assert series.Orders.tolist() == [1, 1, 0, 0]


def test_product_and_country_totals_reconcile_with_kpis(transactions):
    assert product_summary(transactions).Revenue.sum() == sales_metrics(transactions).revenue
    assert country_summary(transactions).Revenue.sum() == sales_metrics(transactions).revenue
    assert country_summary(transactions).Share.sum() == pytest.approx(100)
    assert len(product_summary(transactions).query("StockCode == 'A'")) == 1


def test_product_filter_changes_revenue_not_invoice_line_count(transactions):
    selected = filter_transactions(transactions, "2011-01-01", "2011-01-04", products=["B"])
    assert sales_metrics(selected).revenue == 5
    assert sales_metrics(selected).orders == 1


def test_monthly_orders_are_unique_invoices_not_sum_of_daily_counts(raw_transactions):
    # One invoice can have lines on different dates; month-level distinct counts still count it once.
    raw_transactions.loc[1, "InvoiceDate"] = "2011-01-02 09:00"
    result = period_summary(clean_transactions(raw_transactions))
    assert result.Orders.iloc[0] == 2
    assert result.AOV.iloc[0] == 28.5

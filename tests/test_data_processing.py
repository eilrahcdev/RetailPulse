"""Check that the project is importable before adding data processing."""

import importlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.data_processing import (
    EXCLUDED, RETURN, SALE, clean_transactions, filter_transactions, quality_summary,
    read_workbook, search_transactions, transactions_csv,
)

def test_data_processing_imports_from_this_project():
    module = importlib.import_module("src.data_processing")
    expected_file = Path(__file__).resolve().parents[1] / "src" / "data_processing.py"

    assert Path(module.__file__).resolve() == expected_file


def test_duplicates_are_marked_and_retained(transactions):
    assert len(transactions) == 7
    assert transactions.IsExactDuplicate.sum() == 1
    assert transactions.TransactionType.eq(SALE).sum() == 4


def test_missing_customer_and_description_preserve_sale(transactions):
    row = transactions.loc[transactions.InvoiceNo.eq("200")].iloc[0]
    assert row.TransactionType == SALE
    assert row.Description == "Unknown product"
    assert pd.isna(row.CustomerID)
    assert row.MissingCustomerID and row.MissingDescription


def test_both_negative_quantities_and_cancellation_prefix_are_handled(transactions):
    credits = transactions.loc[transactions.TransactionType.eq(RETURN)]
    assert set(credits.InvoiceNo) == {"c100", "300"}
    assert credits.Revenue.sum() == -20
    assert transactions.loc[transactions.InvoiceNo.eq("c100"), "IsCancellation"].all()


@pytest.mark.parametrize("column,value", [
    ("InvoiceDate", "not a date"), ("InvoiceNo", ""), ("StockCode", None),
    ("Quantity", "not a number"), ("Quantity", np.inf), ("Quantity", 0),
    ("UnitPrice", -5), ("UnitPrice", 0), ("UnitPrice", np.inf), ("InvoiceNo", "C999"),
])
def test_invalid_lines_are_excluded(raw_transactions, column, value):
    row = raw_transactions.iloc[[0]].astype(object).copy()
    row.loc[row.index[0], column] = value
    result = clean_transactions(row)
    assert result.TransactionType.iloc[0] == EXCLUDED
    assert result.ExclusionReason.iloc[0]


def test_cleaning_does_not_modify_source(raw_transactions):
    before = raw_transactions.copy(deep=True)
    clean_transactions(raw_transactions)
    pd.testing.assert_frame_equal(raw_transactions, before)


def test_quality_report_partition_and_missing_values(transactions):
    report = quality_summary(transactions)
    assert report["Source rows"] == 7
    assert report["Missing customer IDs"] == 1
    assert report["Missing descriptions"] == 1
    assert report["Valid positive-sales lines"] == 4
    assert report["Usable return / cancellation lines"] == 2
    assert report["Excluded / review lines"] == 1


def test_filters_include_end_of_day_and_combine_conditions(transactions):
    result = filter_transactions(transactions, "2011-01-02", "2011-01-02", ["France"], ["A"])
    assert result.InvoiceNo.tolist() == ["200"]
    assert filter_transactions(transactions, "2011-01-02", "2011-01-02", ["France"], ["B"]).empty


def test_search_is_literal(transactions):
    assert len(search_transactions(transactions, "cup")) == 4
    assert search_transactions(transactions, "[").empty


def test_excel_loading_preserves_leading_zero_codes(raw_transactions, tmp_path):
    raw_transactions.loc[0, "StockCode"] = "00123"
    path = tmp_path / "workbook.xlsx"
    raw_transactions.to_excel(path, index=False)
    assert read_workbook(path).StockCode.iloc[0] == "00123"


def test_missing_schema_has_actionable_error(tmp_path):
    path = tmp_path / "wrong.xlsx"
    pd.DataFrame({"Other": [1]}).to_excel(path, index=False)
    with pytest.raises(ValueError, match="required columns"):
        read_workbook(path)


def test_csv_contains_all_filtered_rows_and_neutralizes_formulas(transactions):
    transactions.loc[0, "Description"] = "=1+1"
    result = transactions_csv(transactions).decode("utf-8-sig")
    assert "'=1+1" in result
    assert len(result.splitlines()) == len(transactions) + 1


def test_empty_data_has_a_valid_cleaned_schema(raw_transactions):
    result = clean_transactions(raw_transactions.iloc[:0])
    assert result.empty
    assert "TransactionType" in result

import pandas as pd
import pytest

from src.data_processing import clean_transactions, filter_transactions
from src.metrics import return_summary
from src.returns_analysis import credit_composition, credits_by, monthly_credits


def test_prefixed_and_unprefixed_credits_remain_distinct(transactions):
    table = credit_composition(transactions).set_index("Category")
    assert table.loc["Usable C-prefixed credits", "UsableCreditValue"] == 10
    assert table.loc["Usable unprefixed negative lines", "UsableCreditValue"] == 10
    assert table.UsableCreditValue.sum() == return_summary(transactions)["credit_value"]


def test_review_candidates_have_no_monetary_claim(raw_transactions):
    raw_transactions.loc[0, "InvoiceNo"] = "C-positive"
    raw_transactions.loc[1, "Quantity"] = -1
    raw_transactions.loc[1, "UnitPrice"] = 0
    table = credit_composition(clean_transactions(raw_transactions)).set_index("Category")
    assert table.loc["C-prefixed lines requiring review", "Lines"] == 1
    assert table.loc["Other excluded negative lines", "Lines"] == 1
    assert pd.isna(table.loc["C-prefixed lines requiring review", "UsableCreditValue"])
    assert pd.isna(table.loc["Other excluded negative lines", "UsableCreditValue"])


@pytest.mark.parametrize("dimension", ["Country", "StockCode"])
def test_breakdowns_reconcile_with_existing_credit_summary(transactions, dimension):
    table = credits_by(transactions, dimension)
    assert table.CreditValue.sum() == return_summary(transactions)["credit_value"]
    assert table.CreditUnits.sum() == 3
    assert table.Lines.sum() == 2


def test_monthly_credits_respect_selected_dates(transactions):
    selected = filter_transactions(transactions, "2011-01-03", "2011-01-03")
    table = monthly_credits(selected)
    assert table.CreditValue.iloc[0] == 20
    assert table.CreditInvoices.iloc[0] == 2
    assert table.Period.iloc[0] == pd.Timestamp("2011-01-01")


def test_credit_tables_handle_no_credits(transactions):
    empty = transactions.iloc[:0]
    assert credits_by(empty, "Country").empty
    assert monthly_credits(empty).empty
    assert credit_composition(empty).Lines.sum() == 0


def test_invalid_credit_dimension_is_rejected(transactions):
    with pytest.raises(ValueError, match="Credit dimension"):
        credits_by(transactions, "CustomerID")

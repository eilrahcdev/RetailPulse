"""Small artificial records used only for analytical regression tests."""

import pandas as pd
import pytest

from src.data_processing import clean_transactions


@pytest.fixture
def raw_transactions():
    columns = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]
    return pd.DataFrame([
        ["100", "A", "Cup", 2, "2011-01-01 09:00", 10, "1", "United Kingdom"],
        ["100", "B", "Plate", 1, "2011-01-01 09:00", 5, "1", "United Kingdom"],
        ["100", "A", "Cup", 2, "2011-01-01 09:00", 10, "1", "United Kingdom"],
        ["200", "A", None, 3, "2011-01-02 23:59", 4, None, "France"],
        ["c100", "A", "Cup", -1, "2011-01-03 10:00", 10, "1", "United Kingdom"],
        ["300", "B", "Plate", -2, "2011-01-03 11:00", 5, "1", "United Kingdom"],
        ["400", "A", "Cup", 1, "2011-01-04 09:00", 0, "1", "United Kingdom"],
    ], columns=columns)


@pytest.fixture
def transactions(raw_transactions):
    return clean_transactions(raw_transactions)

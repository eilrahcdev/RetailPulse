"""Load the UCI workbook and classify invoice lines without changing the source."""

from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = [
    "InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate",
    "UnitPrice", "CustomerID", "Country",
]
SALE = "Sale"
RETURN = "Return / cancellation"
EXCLUDED = "Excluded / review"


def read_workbook(source: Path | bytes) -> pd.DataFrame:
    """Read identifiers as strings so their leading zeros are preserved."""
    workbook = BytesIO(source) if isinstance(source, bytes) else source
    frame = pd.read_excel(
        workbook,
        engine="openpyxl",
        dtype={"InvoiceNo": "string", "StockCode": "string", "CustomerID": "string"},
    )
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError("The workbook is missing required columns: " + ", ".join(missing))
    return frame


def clean_transactions(raw: pd.DataFrame) -> pd.DataFrame:
    """Keep every source line, add quality flags, and separate sales from credits.

    Exact duplicates are marked before normalization. They remain in this result.
    Missing customers/descriptions do not invalidate an otherwise usable sale.
    """
    missing = sorted(set(REQUIRED_COLUMNS) - set(raw.columns))
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    frame = raw[REQUIRED_COLUMNS].copy().reset_index(drop=True)
    frame["SourceRow"] = np.arange(2, len(frame) + 2)
    frame["IsExactDuplicate"] = frame.duplicated(subset=REQUIRED_COLUMNS, keep="first")

    for column in ["InvoiceNo", "StockCode", "CustomerID", "Country", "Description"]:
        frame[column] = frame[column].astype("string").str.strip().replace("", pd.NA)
    for column in ["InvoiceNo", "StockCode", "CustomerID"]:
        frame[column] = frame[column].str.replace(r"^(\d+)\.0$", r"\1", regex=True)

    frame["MissingDescription"] = frame["Description"].isna()
    frame["MissingCustomerID"] = frame["CustomerID"].isna()
    frame["Country"] = frame["Country"].fillna("Unknown country")
    frame["Description"] = frame["Description"].fillna("Unknown product")
    frame["ProductLabel"] = frame["Description"] + " [" + frame["StockCode"].fillna("no code") + "]"
    frame["InvoiceDate"] = pd.to_datetime(frame["InvoiceDate"], errors="coerce", format="mixed")
    for column in ["Quantity", "UnitPrice"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["Revenue"] = frame["Quantity"] * frame["UnitPrice"]
    frame["IsCancellation"] = frame["InvoiceNo"].str.upper().str.startswith("C", na=False)

    finite = pd.Series(
        np.isfinite(frame[["Quantity", "UnitPrice", "Revenue"]].to_numpy(dtype=float)).all(axis=1),
        index=frame.index,
    )
    valid_identity = frame["InvoiceNo"].notna() & frame["StockCode"].notna()
    valid = valid_identity & frame["InvoiceDate"].notna() & finite & frame["UnitPrice"].gt(0)
    sales = valid & frame["Quantity"].gt(0) & ~frame["IsCancellation"]
    returns = valid & frame["Quantity"].lt(0)

    frame["TransactionType"] = EXCLUDED
    frame.loc[sales, "TransactionType"] = SALE
    frame.loc[returns, "TransactionType"] = RETURN
    frame["ExclusionReason"] = ""
    reasons = [
        (~valid_identity, "Missing invoice or stock code"),
        (frame["InvoiceDate"].isna(), "Invalid or missing date"),
        (~finite, "Invalid or non-finite quantity, price, or revenue"),
        (frame["UnitPrice"].le(0), "Zero or negative unit price"),
        (frame["Quantity"].eq(0), "Zero quantity"),
        (frame["IsCancellation"] & frame["Quantity"].gt(0), "Cancellation with positive quantity"),
    ]
    for mask, reason in reasons:
        first_reason = frame["ExclusionReason"].eq("") & mask
        frame.loc[first_reason, "ExclusionReason"] = reason
    return frame


def quality_summary(frame: pd.DataFrame) -> dict[str, int]:
    """Report quality before any date, country, or product filter is applied."""
    return {
        "Source rows": len(frame),
        "Exact duplicates beyond first": int(frame["IsExactDuplicate"].sum()),
        "Missing customer IDs": int(frame["MissingCustomerID"].sum()),
        "Missing descriptions": int(frame["MissingDescription"].sum()),
        "Invalid or missing dates": int(frame["InvoiceDate"].isna().sum()),
        "Cancellation-prefixed rows": int(frame["IsCancellation"].sum()),
        "Valid positive-sales lines": int(frame["TransactionType"].eq(SALE).sum()),
        "Usable return / cancellation lines": int(frame["TransactionType"].eq(RETURN).sum()),
        "Excluded / review lines": int(frame["TransactionType"].eq(EXCLUDED).sum()),
    }


def filter_transactions(
    frame: pd.DataFrame,
    start,
    end,
    countries: list[str] | None = None,
    products: list[str] | None = None,
) -> pd.DataFrame:
    """Filter inclusive calendar dates; an empty country/product list means all."""
    start = pd.Timestamp(start).normalize()
    stop = pd.Timestamp(end).normalize() + pd.Timedelta(days=1)
    mask = frame["InvoiceDate"].ge(start) & frame["InvoiceDate"].lt(stop)
    if countries:
        mask &= frame["Country"].isin(countries)
    if products:
        mask &= frame["StockCode"].isin(products)
    return frame.loc[mask].copy()


def search_transactions(frame: pd.DataFrame, query: str) -> pd.DataFrame:
    """Search identifiers and descriptions literally, never as regular expressions."""
    query = query.strip()
    if not query:
        return frame
    mask = pd.Series(False, index=frame.index)
    for column in ["InvoiceNo", "StockCode", "Description", "CustomerID", "Country"]:
        mask |= frame[column].astype("string").str.contains(query, case=False, regex=False, na=False)
    return frame.loc[mask].copy()


def dataframe_csv(frame: pd.DataFrame) -> bytes:
    """Export a table and neutralize formula-like text without changing numeric values."""
    exported = frame.copy()
    for column in exported.select_dtypes(include=["object", "string"]).columns:
        values = exported[column].astype("string")
        formula = values.str.match(r"^[\s]*[=+@-]", na=False)
        exported[column] = values.mask(formula, "'" + values)
    return exported.to_csv(index=False).encode("utf-8-sig")


def transactions_csv(frame: pd.DataFrame) -> bytes:
    columns = REQUIRED_COLUMNS + ["Revenue", "TransactionType", "IsExactDuplicate", "ExclusionReason", "SourceRow"]
    return dataframe_csv(frame[columns])

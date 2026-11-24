"""Observed credit composition; never infer refunds or original-sale matches."""

import pandas as pd

from src.data_processing import EXCLUDED, RETURN


def credit_composition(frame: pd.DataFrame) -> pd.DataFrame:
    usable = frame["TransactionType"].eq(RETURN)
    excluded = frame["TransactionType"].eq(EXCLUDED)
    prefixed = frame["IsCancellation"]
    categories = [
        ("Usable C-prefixed credits", usable & prefixed, True),
        ("Usable unprefixed negative lines", usable & ~prefixed, True),
        ("C-prefixed lines requiring review", excluded & prefixed, False),
        ("Other excluded negative lines", excluded & ~prefixed & frame["Quantity"].lt(0), False),
    ]
    return pd.DataFrame([
        {"Category": label, "Lines": int(mask.sum()), "Invoices": int(frame.loc[mask, "InvoiceNo"].nunique()),
         "UsableCreditValue": float(-frame.loc[mask, "Revenue"].sum()) if valued else None}
        for label, mask, valued in categories
    ])


def credits_by(frame: pd.DataFrame, dimension: str) -> pd.DataFrame:
    if dimension not in {"Country", "StockCode"}:
        raise ValueError("Credit dimension must be Country or StockCode.")
    credits = frame.loc[frame["TransactionType"].eq(RETURN)].copy()
    credits["CreditValue"] = -credits["Revenue"]
    credits["CreditUnits"] = -credits["Quantity"]
    grouped = credits.groupby(dimension, as_index=False).agg(
        CreditValue=("CreditValue", "sum"), CreditUnits=("CreditUnits", "sum"),
        CreditInvoices=("InvoiceNo", "nunique"), Lines=("InvoiceNo", "size"),
    )
    return grouped.sort_values("CreditValue", ascending=False, kind="stable").reset_index(drop=True)


def monthly_credits(frame: pd.DataFrame) -> pd.DataFrame:
    credits = frame.loc[frame["TransactionType"].eq(RETURN)].copy()
    credits["Period"] = credits["InvoiceDate"].dt.to_period("M").dt.start_time
    credits["CreditValue"] = -credits["Revenue"]
    return credits.groupby("Period", as_index=False).agg(
        CreditValue=("CreditValue", "sum"), CreditInvoices=("InvoiceNo", "nunique"), Lines=("InvoiceNo", "size"),
    )

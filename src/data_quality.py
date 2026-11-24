"""Source-row diagnostics and reconciliation, independent of Streamlit."""

import numpy as np
import pandas as pd

from src.data_processing import EXCLUDED, REQUIRED_COLUMNS, RETURN, SALE, search_transactions
from src.metrics import sales_metrics


# Severity describes the issue, not whether an entire invoice should be deleted.
QUALITY_RULES = {
    "missing_invoice": ("Missing invoice number", "Invalid", "Cannot identify an order."),
    "missing_stock": ("Missing stock code", "Invalid", "Cannot attribute an item."),
    "invalid_date": ("Missing or invalid invoice date", "Invalid", "Cannot place the line in a sales period."),
    "invalid_quantity": ("Missing, invalid, or non-finite quantity", "Invalid", "Cannot calculate usable units or line value."),
    "invalid_price": ("Missing, invalid, or non-finite price", "Invalid", "Cannot calculate a usable line value."),
    "nonpositive_price": ("Zero or negative unit price", "Invalid", "Excluded from positive sales and usable credits."),
    "zero_quantity": ("Zero quantity", "Invalid", "No sold or credited units."),
    "invalid_value": ("Non-finite calculated line value", "Invalid", "Finite inputs overflow when multiplied."),
    "missing_customer": ("Missing customer ID", "Completeness", "Sales remain valid; customer attribution is unavailable."),
    "missing_description": ("Missing description", "Completeness", "Keep valid sales; identify the product by stock code."),
    "missing_country": ("Missing country", "Completeness", "Sales remain valid; geographic attribution is unknown."),
    "exact_repeat": ("Exact repeated row after first", "Review", "May be legitimate. Retained unless explicitly excluded."),
    "cancellation_conflict": ("Cancellation with positive quantity", "Review", "Requires review; not a sale or a usable credit."),
    "unmarked_negative": ("Negative quantity without C prefix", "Review", "Not proof of a return; credit eligibility still follows price/date rules."),
}


def quality_evidence(raw: pd.DataFrame, prepared: pd.DataFrame) -> pd.DataFrame:
    """Retain source cells for affected rows and mark every applicable check.

    Call after clean_transactions on the same unmodified, ordered input. SourceRow
    includes the Excel header: the first data row is row 2.
    """
    missing = set(REQUIRED_COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError("Quality audit requires all eight UCI source columns.")
    if len(raw) != len(prepared) or not np.array_equal(prepared["SourceRow"], np.arange(2, len(raw) + 2)):
        raise ValueError("Source and prepared rows must retain the same order and length.")
    source = raw[REQUIRED_COLUMNS].reset_index(drop=True)
    frame = prepared.reset_index(drop=True)
    quantity_finite = pd.Series(np.isfinite(frame["Quantity"].to_numpy(dtype=float)))
    price_finite = pd.Series(np.isfinite(frame["UnitPrice"].to_numpy(dtype=float)))
    value_finite = pd.Series(np.isfinite(frame["Revenue"].to_numpy(dtype=float)))
    masks = pd.DataFrame({
        "missing_invoice": frame["InvoiceNo"].isna(),
        "missing_stock": frame["StockCode"].isna(),
        "invalid_date": frame["InvoiceDate"].isna(),
        "invalid_quantity": ~quantity_finite,
        "invalid_price": ~price_finite,
        "nonpositive_price": frame["UnitPrice"].le(0),
        "zero_quantity": frame["Quantity"].eq(0),
        "invalid_value": quantity_finite & price_finite & ~value_finite,
        "missing_customer": frame["MissingCustomerID"],
        "missing_description": frame["MissingDescription"],
        "missing_country": source["Country"].astype("string").str.strip().replace("", pd.NA).isna(),
        "exact_repeat": frame["IsExactDuplicate"],
        "cancellation_conflict": frame["IsCancellation"] & frame["Quantity"].gt(0),
        "unmarked_negative": ~frame["IsCancellation"] & frame["Quantity"].lt(0),
    }).fillna(False).astype(bool)
    affected = masks.any(axis=1)
    records = source.loc[affected].copy()
    records.insert(0, "SourceRow", frame.loc[affected, "SourceRow"])
    records["TransactionType"] = frame.loc[affected, "TransactionType"]
    records = records.join(masks.loc[affected])
    records["QualityIssues"] = ""
    for code, (label, _, _) in QUALITY_RULES.items():
        records.loc[records[code], "QualityIssues"] += label + "; "
    records["QualityIssues"] = records["QualityIssues"].str.rstrip("; ")
    return records.reset_index(drop=True)


def quality_counts(evidence: pd.DataFrame, total_rows: int) -> pd.DataFrame:
    """Counts overlap; percentages all use the selected source-row denominator."""
    rows = []
    for code, (label, severity, interpretation) in QUALITY_RULES.items():
        count = int(evidence[code].sum())
        rows.append({"Code": code, "Check": label, "Severity": severity, "Rows": count,
                     "Percent": count / total_rows * 100 if total_rows else 0.0,
                     "Interpretation": interpretation})
    return pd.DataFrame(rows)


def filter_quality_evidence(evidence: pd.DataFrame, check: str = "All checks", query: str = "") -> pd.DataFrame:
    if check != "All checks":
        if check not in QUALITY_RULES:
            raise ValueError("Unknown quality check.")
        evidence = evidence.loc[evidence[check]]
    return search_transactions(evidence, query)


def quality_impact(frame: pd.DataFrame, evidence: pd.DataFrame) -> dict[str, float | int]:
    sales = frame["TransactionType"].eq(SALE)
    missing_customer = sales & frame["MissingCustomerID"]
    repeated_sales = sales & frame["IsExactDuplicate"]
    return {
        "source_rows": len(frame),
        "affected_rows": len(evidence),
        "excluded_rows": int(frame["TransactionType"].eq(EXCLUDED).sum()),
        "duplicate_rows": int(frame["IsExactDuplicate"].sum()),
        "unattributed_sales_rows": int(missing_customer.sum()),
        "unattributed_sales_value": float(frame.loc[missing_customer, "Revenue"].sum()),
        "repeated_sales_value": float(frame.loc[repeated_sales, "Revenue"].sum()),
    }


def validate_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Reconcile independent groupings; monetary tolerance is half a penny."""
    metrics = sales_metrics(frame)
    sales = frame.loc[frame["TransactionType"].eq(SALE)]
    credits = frame.loc[frame["TransactionType"].eq(RETURN)]
    by_product = float(sales.groupby("StockCode")["Revenue"].sum().sum())
    by_country = float(sales.groupby("Country")["Revenue"].sum().sum())

    def money_matches(left, right):
        return bool(np.isfinite(left) and np.isfinite(right) and abs(left - right) <= 0.005)

    valid_sales = (
        sales["Quantity"].gt(0) & sales["UnitPrice"].gt(0) & ~sales["IsCancellation"]
        & sales["InvoiceDate"].notna() & sales["InvoiceNo"].notna() & sales["StockCode"].notna()
        & np.isfinite(sales[["Quantity", "UnitPrice", "Revenue"]]).all(axis=1)
    ).all()
    valid_credits = (
        credits["Quantity"].lt(0) & credits["UnitPrice"].gt(0)
        & credits["InvoiceDate"].notna() & credits["InvoiceNo"].notna() & credits["StockCode"].notna()
        & np.isfinite(credits[["Quantity", "UnitPrice", "Revenue"]]).all(axis=1)
    ).all()
    checks = [
        ("Known row classifications", frame["TransactionType"].isin([SALE, RETURN, EXCLUDED]).all(), "Every line is a sale, usable credit, or excluded/review record."),
        ("Positive-sales admission rules", valid_sales, "Positive quantity/price, finite value, dated identifiers, and no C prefix."),
        ("Usable-credit admission rules", valid_credits, "Negative quantity, positive price, finite value, and dated identifiers."),
        ("Unique order count", metrics.orders == sales["InvoiceNo"].nunique(), "Orders count distinct selected sales invoices, not rows."),
        ("Product revenue reconciliation", money_matches(metrics.revenue, by_product), "Product totals match the sales KPI within £0.005."),
        ("Country revenue reconciliation", money_matches(metrics.revenue, by_country), "Country totals match the sales KPI within £0.005."),
        ("AOV identity", money_matches(metrics.average_order_value, metrics.revenue / metrics.orders if metrics.orders else 0), "Revenue divided by distinct sales invoices; zero when no orders."),
    ]
    return pd.DataFrame([{"Validation": label, "Result": "PASS" if passed else "FAIL", "Definition": definition}
                         for label, passed, definition in checks])

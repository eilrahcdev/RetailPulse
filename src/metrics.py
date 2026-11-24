"""Small, testable business calculations shared by every dashboard page."""

from dataclasses import dataclass

import pandas as pd

from src.data_processing import RETURN, SALE


@dataclass(frozen=True)
class SalesMetrics:
    revenue: float
    orders: int
    average_order_value: float
    units: float


def sales_metrics(frame: pd.DataFrame) -> SalesMetrics:
    sales = frame.loc[frame["TransactionType"].eq(SALE)]
    revenue = float(sales["Revenue"].sum())
    orders = int(sales["InvoiceNo"].nunique())
    return SalesMetrics(
        revenue=revenue,
        orders=orders,
        average_order_value=revenue / orders if orders else 0.0,
        units=float(sales["Quantity"].sum()),
    )


def change_percent(current: float, previous: float) -> float | None:
    return (current - previous) / previous * 100 if previous > 0 else None


def previous_period(start, end):
    """Use the same number of inclusive calendar days immediately before selection."""
    start, end = pd.Timestamp(start).normalize(), pd.Timestamp(end).normalize()
    days = (end - start).days + 1
    previous_end = start - pd.Timedelta(days=1)
    return previous_end - pd.Timedelta(days=days - 1), previous_end


def comparison_is_available(frame: pd.DataFrame, start, end) -> bool:
    previous_start, previous_end = previous_period(start, end)
    dates = frame["InvoiceDate"].dropna()
    return bool(
        not dates.empty
        and previous_start >= dates.min().normalize()
        and previous_end <= dates.max().normalize()
    )


def daily_sales(frame: pd.DataFrame, start, end) -> pd.DataFrame:
    """Include zero-sales dates so charts do not connect across missing days."""
    sales = frame.loc[frame["TransactionType"].eq(SALE)].copy()
    sales["Date"] = sales["InvoiceDate"].dt.normalize()
    grouped = sales.groupby("Date").agg(
        Revenue=("Revenue", "sum"),
        Orders=("InvoiceNo", "nunique"),
        Units=("Quantity", "sum"),
    )
    index = pd.date_range(start, end, freq="D", name="Date")
    return grouped.reindex(index, fill_value=0).reset_index()


def period_summary(frame: pd.DataFrame, aggregation: str = "Monthly") -> pd.DataFrame:
    sales = frame.loc[frame["TransactionType"].eq(SALE)].copy()
    frequency = {"Daily": "D", "Weekly": "W-SUN", "Monthly": "M"}[aggregation]
    sales["Period"] = sales["InvoiceDate"].dt.to_period(frequency).dt.start_time
    grouped = sales.groupby("Period", as_index=False).agg(
        Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique"), Units=("Quantity", "sum"),
    )
    grouped["AOV"] = grouped["Revenue"].div(grouped["Orders"].replace(0, float("nan"))).fillna(0)
    return grouped


def product_summary(frame: pd.DataFrame) -> pd.DataFrame:
    sales = frame.loc[frame["TransactionType"].eq(SALE)]
    grouped = sales.groupby("StockCode", as_index=False).agg(
        Description=("Description", "first"), Revenue=("Revenue", "sum"),
        Units=("Quantity", "sum"), Orders=("InvoiceNo", "nunique"),
    )
    return grouped.sort_values("Revenue", ascending=False, kind="stable").reset_index(drop=True)


def country_summary(frame: pd.DataFrame) -> pd.DataFrame:
    sales = frame.loc[frame["TransactionType"].eq(SALE)]
    grouped = sales.groupby("Country", as_index=False).agg(
        Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique"), Units=("Quantity", "sum"),
    )
    total = grouped["Revenue"].sum()
    grouped["Share"] = grouped["Revenue"] / total * 100 if total else 0.0
    return grouped.sort_values("Revenue", ascending=False, kind="stable").reset_index(drop=True)


def return_summary(frame: pd.DataFrame) -> dict[str, float | int]:
    returns = frame.loc[frame["TransactionType"].eq(RETURN)]
    gross = sales_metrics(frame).revenue
    credits = float(-returns["Revenue"].sum())
    return {
        "credit_value": credits,
        "credit_invoices": int(returns["InvoiceNo"].nunique()),
        "credit_units": float(-returns["Quantity"].sum()),
        "observed_net": gross - credits,
    }

"""Display helpers that do not depend on Streamlit."""

import pandas as pd


def money(value: float, compact: bool = False) -> str:
    if compact and abs(value) >= 1_000_000:
        return f"£{value / 1_000_000:,.2f}m"
    if compact and abs(value) >= 100_000:
        return f"£{value / 1_000:,.1f}k"
    return f"£{value:,.2f}"


def number(value: float) -> str:
    return f"{value:,.0f}" if float(value).is_integer() else f"{value:,.2f}"


def date_label(start, end) -> str:
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    return f"{start:%d %b %Y} - {end:%d %b %Y}"


def default_period(frame: pd.DataFrame):
    """Default to the latest fully covered calendar month when one exists."""
    earliest = frame["InvoiceDate"].min().normalize()
    latest = frame["InvoiceDate"].max().normalize()
    month_end = latest.replace(day=1) - pd.Timedelta(days=1)
    month_start = month_end.replace(day=1)
    if month_start >= earliest:
        return month_start.date(), month_end.date()
    return earliest.date(), latest.date()

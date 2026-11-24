"""Pure mappings from plotted, observed values to bounded record filters."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass(frozen=True)
class DrilldownTarget:
    start: date
    end: date
    countries: tuple[str, ...]
    products: tuple[str, ...]
    label: str


def bar_target(kind, point, allowed_values, start, end, countries=(), products=()):
    """Narrow only the selected dimension; reject stale or unplotted values."""
    if kind not in {"product", "country"}:
        raise ValueError("Unsupported bar drilldown.")
    if not isinstance(point, Mapping):
        return None
    value = str(point.get("y", ""))
    if value not in {str(item) for item in allowed_values}:
        return None
    return DrilldownTarget(
        pd.Timestamp(start).date(), pd.Timestamp(end).date(),
        (value,) if kind == "country" else tuple(countries),
        (value,) if kind == "product" else tuple(products),
        f"{'Stock code' if kind == 'product' else 'Country'}: {value}",
    )


def revenue_target(point, current_curve, allowed_periods, start, end, aggregation, countries=(), products=()):
    """Clip a current-period bucket to the active inclusive date selection."""
    if aggregation not in {"Daily", "Weekly", "Monthly"}:
        raise ValueError("Unsupported revenue aggregation.")
    if not isinstance(point, Mapping) or point.get("curve_number") != current_curve:
        return None
    try:
        bucket = pd.Timestamp(point.get("x"))
    except (TypeError, ValueError):
        return None
    if pd.isna(bucket) or bucket.date() not in {pd.Timestamp(value).date() for value in allowed_periods}:
        return None
    bucket = pd.Timestamp(bucket.date())
    bucket_end = bucket
    if aggregation == "Weekly":
        bucket_end += pd.Timedelta(days=6)
    elif aggregation == "Monthly":
        bucket_end += pd.offsets.MonthEnd(0)
    first = max(bucket.date(), pd.Timestamp(start).date())
    last = min(bucket_end.date(), pd.Timestamp(end).date())
    if first > last:
        return None
    return DrilldownTarget(first, last, tuple(countries), tuple(products), f"{aggregation} sales: {first:%d %b %Y} - {last:%d %b %Y}")

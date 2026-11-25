"""Native chart selection and session-state navigation; no analytical formulas."""

import streamlit as st
import pandas as pd

from src.data_processing import SALE
from src.drilldowns import bar_target, revenue_target


def open_records(target):
    """Run as a widget callback, before shared filters are instantiated."""
    st.session_state["drilldown_origin"] = {
        "page": st.session_state["navigation"],
        "dates": tuple(st.session_state["date_range"]),
        "countries": list(st.session_state.get("countries", [])),
        "products": list(st.session_state.get("products", [])),
        "source_id": st.session_state.get("source_id"),
        "aggregation": st.session_state.get("revenue_aggregation", "Daily"),
        "ranking": st.session_state.get("product_ranking", "Revenue"),
        "exclude_duplicates": st.session_state.get("exclude_duplicates", False),
    }
    st.session_state["drilldown_target"] = target
    st.session_state["navigation"] = "Data Explorer"
    st.session_state["date_range"] = (target.start, target.end)
    st.session_state["countries"] = list(target.countries)
    st.session_state["products"] = list(target.products)
    st.session_state["transaction_types"] = [SALE]
    st.session_state["transaction_search"] = ""
    st.session_state["transaction_page"] = 1


def clear_drilldown():
    st.session_state.pop("drilldown_origin", None)
    st.session_state.pop("drilldown_target", None)


def return_to_chart():
    origin = st.session_state.get("drilldown_origin")
    if origin and origin["source_id"] == st.session_state.get("source_id"):
        st.session_state["navigation"] = origin["page"]
        st.session_state["date_range"] = origin["dates"]
        st.session_state["countries"] = origin["countries"]
        st.session_state["products"] = origin["products"]
        st.session_state["revenue_aggregation"] = origin["aggregation"]
        st.session_state["product_ranking"] = origin["ranking"]
        st.session_state["exclude_duplicates"] = origin["exclude_duplicates"]
        st.session_state["transaction_page"] = 1
    clear_drilldown()


def drilldown_context():
    origin = st.session_state.get("drilldown_origin")
    target = st.session_state.get("drilldown_target")
    if not origin or target is None:
        return
    matches = (
        tuple(st.session_state["date_range"]) == (target.start, target.end)
        and tuple(st.session_state.get("countries", [])) == target.countries
        and tuple(st.session_state.get("products", [])) == target.products
        and st.session_state.get("transaction_types", [SALE]) == [SALE]
        and not st.session_state.get("transaction_search", "")
        and st.session_state.get("exclude_duplicates", False) == origin["exclude_duplicates"]
    )
    st.caption(f"Observed positive-sales drilldown · {target.label}" if matches
               else "Filters changed since chart selection. Back restores the source view's filters.")
    st.button(f"Back to {origin['page']}", on_click=return_to_chart, icon=":material/arrow_back:", key="drilldown_back")


def selected_target(figure, kind, point, aggregation="Daily"):
    dates = st.session_state.get("date_range", ())
    if len(dates) != 2:
        return None
    countries = st.session_state.get("countries", [])
    products = st.session_state.get("products", [])
    if kind == "revenue":
        return revenue_target(point, len(figure.data) - 1, figure.data[-1].x, *dates, aggregation, countries, products)
    return bar_target(kind, point, figure.data[0].y, *dates, countries, products)


def chart_selection(figure, kind, event, key, aggregation="Daily"):
    points = event.get("selection", {}).get("points", [])
    st.caption("Select one current-period point on the solid line, then inspect its records." if kind == "revenue"
               else "Select one bar, then inspect its matching positive-sales records.")
    if not points:
        return
    if len(points) != 1:
        st.info("Select one point or bar at a time to keep the record scope precise.")
        return
    target = selected_target(figure, kind, points[0], aggregation)
    if target is None:
        st.info("Choose a current-period point or a value still present in this chart.")
        return
    st.caption(target.label)
    st.button("Inspect selected records", key=f"inspect_{key}", on_click=open_records, args=(target,))


def keyboard_picker(figure, kind, key, aggregation="Daily"):
    """Provide the same navigation without requiring mouse access to Plotly."""
    values = list(figure.data[-1].x) if kind == "revenue" else list(figure.data[0].y)
    choice = st.selectbox("Record drilldown", [None, *values],
                          format_func=lambda value: "Choose a plotted value" if value is None else
                          pd.Timestamp(value).strftime("%d %b %Y") if kind == "revenue" else str(value),
                          key=f"record_picker_{key}")
    if choice is None:
        return
    point = {"x": choice, "curve_number": len(figure.data) - 1} if kind == "revenue" else {"y": choice}
    target = selected_target(figure, kind, point, aggregation)
    if target is not None:
        st.caption(target.label)
        st.button("Inspect chosen records", key=f"inspect_picker_{key}", on_click=open_records, args=(target,))

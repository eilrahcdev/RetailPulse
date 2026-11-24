"""Native Streamlit presentation of source quality diagnostics."""

import math

import streamlit as st

from src.data_processing import REQUIRED_COLUMNS, dataframe_csv
from src.data_quality import (
    QUALITY_RULES, filter_quality_evidence, quality_counts, quality_impact, validate_metrics,
)
from src.utils import money, number


def data_quality_center(frame, evidence):
    impact = quality_impact(frame, evidence)
    with st.container(key="kpi_grid"):
        for column, (label, value) in zip(st.columns([1.4, 1, 1, 1]), [
            ("Source rows", impact["source_rows"]), ("Rows with findings", impact["affected_rows"]),
            ("Excluded / review rows", impact["excluded_rows"]), ("Exact repeats", impact["duplicate_rows"]),
        ]):
            column.metric(label, number(value))
    st.caption("A row may trigger several checks. Findings do not automatically invalidate a sale or remove a source record.")
    if frame.empty:
        st.info("No source rows are available in this audit scope. Choose Entire workbook or adjust the filters.")
        return

    with st.container(border=True, key="panel_quality_checks"):
        st.header("Quality checks")
        counts = quality_counts(evidence, len(frame))
        st.dataframe(
            counts, hide_index=True, width="stretch", row_height=32,
            column_order=["Check", "Severity", "Rows", "Percent", "Interpretation"],
            column_config={"Percent": st.column_config.NumberColumn("Source rows (%)", format="%.2f%%")},
        )
        st.caption("Each percentage uses all source rows in the chosen scope. Counts overlap and must not be added to estimate affected rows.")

    with st.container(border=True, key="panel_quality_impact"):
        st.header("Business interpretation")
        left, right = st.columns(2)
        left.metric("Sales without customer attribution", money(impact["unattributed_sales_value"]))
        left.caption(f"{impact['unattributed_sales_rows']:,} valid sales lines lack a customer ID. Included in sales KPIs; unsuitable for attributing RFM or cohorts to a known customer.")
        right.metric("Sales value on exact repeated rows", money(impact["repeated_sales_value"]))
        right.caption("Observed sales line value on repeats after the first. This is not proven overstatement or a recommendation to delete legitimate repeat items.")
        st.caption("Excluded records are counted rather than presented as lost revenue. Invalid inputs cannot establish a reliable revenue loss.")

    with st.container(border=True, key="panel_quality_validation"):
        st.header("Metric validation")
        validation = validate_metrics(frame)
        if validation["Result"].eq("FAIL").any():
            st.error("A metric consistency check failed. Review the affected classifications and source records before interpreting the totals.")
        st.dataframe(validation, hide_index=True, width="stretch", row_height=32)
        st.caption("Consistency checks validate the recorded arithmetic and rules, not issuer authenticity, transaction completeness, or accounting reconciliation.")

    with st.container(border=True, key="panel_quality_evidence"):
        st.header("Source evidence")
        check_column, search_column = st.columns([1, 1.4])
        check = check_column.selectbox(
            "Quality check", ["All checks", *QUALITY_RULES], key="quality_check",
            format_func=lambda code: QUALITY_RULES[code][0] if code in QUALITY_RULES else code,
        )
        query = search_column.text_input("Search source evidence", key="quality_search", placeholder="Invoice, stock code, description, customer or country")
        shown = filter_quality_evidence(evidence, check, query)
        st.caption(f"{len(shown):,} source rows match this evidence selection.")
        if shown.empty:
            st.info("No source rows match this quality check and search. Choose another check or clear the search.")
            return
        pages = max(1, math.ceil(len(shown) / 50))
        if st.session_state.get("quality_page", 1) > pages:
            st.session_state["quality_page"] = 1
        page = st.number_input("Evidence page", min_value=1, max_value=pages, step=1, key="quality_page")
        columns = ["SourceRow", *REQUIRED_COLUMNS, "TransactionType", "QualityIssues"]
        # Strings let genuinely malformed source cells remain readable in Arrow tables.
        display = shown.iloc[(page - 1) * 50:page * 50][columns].copy()
        for column in REQUIRED_COLUMNS:
            display[column] = display[column].astype("string")
        st.dataframe(
            display, hide_index=True, width="stretch", row_height=32, height=400,
            column_order=["SourceRow", "QualityIssues", "InvoiceNo", "StockCode", "InvoiceDate", "Quantity", "UnitPrice", "Description", "CustomerID", "Country", "TransactionType"],
            column_config={
                "SourceRow": st.column_config.NumberColumn("Workbook row", format="%d"),
                "QualityIssues": st.column_config.TextColumn("All findings", width=320),
                "InvoiceDate": st.column_config.TextColumn("Source invoice date", width=180),
                "Quantity": st.column_config.TextColumn("Source quantity"),
                "UnitPrice": st.column_config.TextColumn("Source unit price"),
            },
        )
        st.caption(f"Page {page:,} of {pages:,} · 50 rows per page · Source cells as read by Pandas; workbook row includes the header. No source corrections are written.")
        st.download_button(
            "Download quality evidence", dataframe_csv(shown[columns]), "retailpulse-quality-evidence.csv",
            "text/csv", icon=":material/download:",
        )

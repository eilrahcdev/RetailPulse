"""RetailPulse entry point: cached data, shared filters, and native navigation."""

from pathlib import Path
from zipfile import BadZipFile

import pandas as pd
import streamlit as st

from src.data_processing import clean_transactions, filter_transactions, quality_summary, read_workbook
from src.data_quality import quality_evidence
from src.quality_views import data_quality_center
from src.drilldown_views import clear_drilldown, drilldown_context
from src.metrics import comparison_is_available, previous_period
from src.utils import date_label, default_period
from src import views


ROOT = Path(__file__).resolve().parent
LOGO_PATH = ROOT / "assets" / "retailpulse-logo.png"
DATA_PATH = ROOT / "data" / "raw" / "Online Retail.xlsx"
PAGES = {
    "Overview": ("Sales Overview", "Positive sales, order activity, and recorded credits."),
    "Sales Analysis": ("Sales Analysis", "Revenue trends, monthly performance, and recorded credits."),
    "Product Performance": ("Product Performance", "Invoice items ranked by revenue and units sold."),
    "Geographic Analysis": ("Geographic Analysis", "Revenue, order volume, and sales concentration by country."),
    "Data Explorer": ("Data Explorer", "Inspect invoice lines and export the records behind your results."),
    "Data Quality Center": ("Data Quality Center", "Inspect source findings, customer attribution gaps, and metric consistency."),
}


def source_attribution():
    st.caption("Source: UCI Online Retail · Chen, D. (2015) · CC BY 4.0 · All monetary values in GBP")

st.set_page_config(
    page_title="RetailPulse | Retail Sales Intelligence", page_icon=str(LOGO_PATH), layout="wide",
)
st.logo(str(LOGO_PATH), size="large", icon_image=str(LOGO_PATH))
st.markdown(f"<style>{(ROOT / 'assets' / 'styles.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def dataset_bundle(raw):
    frame = clean_transactions(raw)
    catalog = (
        frame.loc[frame.StockCode.notna(), ["StockCode", "ProductLabel", "MissingDescription"]]
        .sort_values("MissingDescription", kind="stable")
        .drop_duplicates("StockCode")
        .sort_values("ProductLabel")
    )
    return frame, quality_summary(frame), catalog, quality_evidence(raw, frame)


@st.cache_data(show_spinner="Loading the workbook and checking transaction quality…", max_entries=1)
def load_local_workbook(path: str, modified_ns: int):
    # The file timestamp invalidates the cache when the local workbook changes.
    return dataset_bundle(read_workbook(Path(path)))


@st.cache_data(show_spinner="Checking the uploaded workbook…", max_entries=1)
def load_uploaded_workbook(content: bytes):
    return dataset_bundle(read_workbook(content))


def reset_filters():
    # Explicit assignments also clear the browser's widget values on the next run.
    st.session_state["date_range"] = st.session_state["default_dates"]
    st.session_state["countries"] = []
    st.session_state["products"] = []
    st.session_state["transaction_page"] = 1


with st.sidebar:
    with st.container(key="sidebar_brand", horizontal=True, wrap=False, vertical_alignment="center"):
        st.image(str(LOGO_PATH), width=44)
        with st.container(key="sidebar_brand_text"):
            st.markdown("## RetailPulse")
            st.caption("Retail Sales Intelligence")
    page = st.radio("Analysis", list(PAGES), key="navigation", width="stretch", label_visibility="collapsed")
    with st.container(key="sidebar_tools"):
        with st.expander("Dataset & methodology"):
            uploaded = st.file_uploader("Upload UCI Online Retail workbook", type=["xlsx"], key="workbook_upload")
            exclude_duplicates = st.toggle(
                "Exclude exact duplicate rows", value=False, key="exclude_duplicates",
                help="Off by default. Exact repeated source rows may be legitimate invoice lines.",
            )
            st.caption("Uploads are used in memory and do not replace the local workbook.")
            st.link_button("Official UCI dataset", "https://archive.ics.uci.edu/dataset/352/online+retail", icon=":material/open_in_new:")
    with st.container(key="sidebar_footer"):
        st.markdown("**UCI Online Retail**")
        st.caption("Historical transactions · Currency: GBP")
        st.caption("Python analytics portfolio project")

title, subtitle = PAGES[page]
with st.container(key=f"page_header_{page.replace(' ', '_')}"):
    st.title(title)
    st.caption(subtitle)

if uploaded is None and not DATA_PATH.exists():
    st.info("Add the Online Retail workbook to begin. No sample data is substituted.")
    st.markdown(
        "Download **Online Retail.xlsx** from the [official UCI source]"
        "(https://archive.ics.uci.edu/dataset/352/online+retail), extract the ZIP, and save the workbook "
        "to `data/raw/Online Retail.xlsx`. You can also upload it using **Dataset & methodology** in the sidebar."
    )
    st.stop()

try:
    if uploaded is not None:
        content = uploaded.getvalue()
        frame, report, product_options, evidence = load_uploaded_workbook(content)
        source_name = uploaded.name
        source_id = ("upload", uploaded.file_id)
    else:
        modified = DATA_PATH.stat().st_mtime_ns
        frame, report, product_options, evidence = load_local_workbook(str(DATA_PATH), modified)
        source_name = DATA_PATH.name
        source_id = ("local", modified)
except (ValueError, OSError, BadZipFile, TypeError, OverflowError) as error:
    st.error(f"The workbook could not be loaded: {error}")
    st.info("Use the original UCI Online Retail .xlsx file with all eight required columns. Remove an invalid upload to return to the local workbook.")
    st.stop()

if st.session_state.get("source_id") != source_id:
    clear_drilldown()

if frame.empty or frame["InvoiceDate"].dropna().empty:
    if page == "Data Quality Center":
        st.caption(f"{source_name} · Audit scope: entire source workbook, before duplicate policy. Undated rows remain available here.")
        data_quality_center(frame, evidence)
        source_attribution()
        st.stop()
    st.warning("This workbook has no dated transactions to display. Choose a workbook with valid InvoiceDate values.")
    st.stop()

st.session_state["default_dates"] = default_period(frame)
if st.session_state.get("source_id") != source_id:
    reset_filters()
    clear_drilldown()
    st.session_state["source_id"] = source_id

earliest = frame["InvoiceDate"].min().date()
latest = frame["InvoiceDate"].max().date()
st.caption(
    f"{source_name} · Historical data: {earliest:%d %b %Y} - {latest:%d %b %Y} · "
    f"Last transaction: {latest:%d %b %Y} · GBP"
)

product_labels = product_options.set_index("StockCode")["ProductLabel"].to_dict()
quality_page = page == "Data Quality Center"
full_source_audit = False
if quality_page:
    scope = st.radio("Audit scope", ["Entire workbook", "Current filters"], horizontal=True, key="quality_scope")
    full_source_audit = scope == "Entire workbook"
    st.caption("Source auditing runs before duplicate exclusions. Entire workbook includes undated rows; Current filters includes only matching dated source rows.")

with st.container(key="filters"):
    date_column, country_column, product_column, reset_column = st.columns(
        [1.25, 1, 1.4, 0.65], gap="small", vertical_alignment="bottom",
    )
    selected_dates = date_column.date_input(
        "Date range", min_value=earliest, max_value=latest,
        key="date_range", format="DD/MM/YYYY",
        disabled=full_source_audit,
    )
    countries = country_column.multiselect(
        "Country", sorted(frame.Country.unique().tolist()), placeholder="All countries", key="countries", disabled=full_source_audit,
    )
    products = product_column.multiselect(
        "Product", product_options.StockCode.tolist(), format_func=lambda code: product_labels[code],
        placeholder="All products", key="products", disabled=full_source_audit,
    )
    reset_column.button("Reset filters", on_click=reset_filters, icon=":material/filter_alt_off:", width="stretch", disabled=full_source_audit)

if full_source_audit:
    data_quality_center(frame, evidence)
    views.methodology(report)
    source_attribution()
    st.stop()

if len(selected_dates) != 2:
    st.info("Choose both a start date and an end date to apply the range.")
    st.stop()
start, end = selected_dates
if quality_page:
    audit_frame = filter_transactions(frame, start, end, countries, products)
    scoped_evidence = evidence.loc[evidence["SourceRow"].isin(audit_frame["SourceRow"])]
    data_quality_center(audit_frame, scoped_evidence)
    views.methodology(report)
    source_attribution()
    st.stop()
working = frame.loc[~frame.IsExactDuplicate] if exclude_duplicates else frame
selected = filter_transactions(working, start, end, countries, products)
previous = None
previous_start, previous_end = previous_period(start, end)
if comparison_is_available(frame, start, end):
    previous = filter_transactions(working, previous_start, previous_end, countries, products)

policy = "Exact repeats excluded" if exclude_duplicates else "Exact repeats retained"
st.caption(f"{date_label(start, end)} · {len(selected):,} transaction lines · {policy}")
if page == "Data Explorer":
    drilldown_context()

if selected.empty:
    st.info("No transactions match these filters. Select another date range, country, or product, or use Reset filters.")
    views.methodology(report)
    st.stop()

if page != "Data Explorer":
    views.kpi_cards(selected, previous, start, end, date_label(previous_start, previous_end))
    if not selected.TransactionType.eq("Sale").any():
        st.info("This selection has no valid positive sales. Sales KPIs are zero; recorded credits and review lines remain available in Data Explorer and Sales Analysis.")

if page == "Overview":
    views.overview(selected, previous, start, end)
elif page == "Sales Analysis":
    views.sales_analysis(selected, previous, start, end)
elif page == "Product Performance":
    views.products_panel(selected, full=True)
elif page == "Geographic Analysis":
    views.country_panel(selected, full=True)
else:
    views.data_explorer(selected, start, end)

views.methodology(report)
source_attribution()

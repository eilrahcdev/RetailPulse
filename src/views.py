"""Streamlit presentation; all analytical calculations live in metrics.py."""

import math

import pandas as pd
import streamlit as st

from src import charts
from src.drilldown_views import chart_selection, keyboard_picker
from src.returns_analysis import credit_composition, credits_by, monthly_credits
from src.data_processing import EXCLUDED, REQUIRED_COLUMNS, RETURN, SALE, dataframe_csv, search_transactions, transactions_csv
from src.metrics import (
    change_percent, country_summary, period_summary, product_summary,
    return_summary, sales_metrics,
)
from src.utils import date_label, money, number


PLOT_CONFIG = {"displayModeBar": False, "responsive": True, "scrollZoom": False}


def show_chart(figure, key, description, kind=None, aggregation="Daily"):
    if kind:
        figure.update_layout(clickmode="event+select")
        event = st.plotly_chart(
            figure, width="stretch", theme=None, key=key, config=PLOT_CONFIG, alt=description,
            on_select="rerun", selection_mode="points",
        )
        chart_selection(figure, kind, event, key, aggregation)
    else:
        st.plotly_chart(figure, width="stretch", theme=None, key=key, config=PLOT_CONFIG, alt=description)


def kpi_cards(selected, previous, start, end, previous_label):
    metrics = sales_metrics(selected)
    prior = sales_metrics(previous) if previous is not None else None
    entries = [
        ("Total Revenue", metrics.revenue, money(metrics.revenue), "Gross positive-sales revenue in GBP."),
        ("Total Orders", metrics.orders, number(metrics.orders), "Distinct invoices with at least one valid positive-sales line."),
        ("Average Order Value", metrics.average_order_value, money(metrics.average_order_value), "Selected positive-sales revenue divided by distinct selected sales invoices."),
        ("Units Sold", metrics.units, number(metrics.units), "Sum of quantity on valid positive-sales lines."),
    ]
    prior_values = [prior.revenue, prior.orders, prior.average_order_value, prior.units] if prior else [None] * 4
    with st.container(key="kpi_grid"):
        for index, column in enumerate(st.columns([1.4, 1, 1, 1])):
            label, value, formatted, definition = entries[index]
            change = change_percent(value, prior_values[index]) if prior else None
            delta = f"{change:+.1f}%" if change is not None else None
            if prior is None:
                help_text = definition + " A full previous equivalent period is outside dataset coverage."
            elif change is None:
                help_text = definition + " No positive sales in the previous period; percentage change is undefined."
            else:
                help_text = definition + " Compared with " + previous_label + "."
            with column:
                st.metric(
                    label, formatted, delta=delta, border=False, help=help_text,
                )
    if prior is None:
        st.caption("KPIs use positive sales; credits are separate. Comparison unavailable: the full preceding period is outside coverage.")
    else:
        st.caption(f"Positive-sales KPIs · Compared with {previous_label} · Credits reported separately · Zero baselines have no percentage")


def trend_panel(selected, previous, start, end):
    with st.container(border=True, key="panel_trend"):
        heading, controls = st.columns([1.6, 1], vertical_alignment="center")
        heading.header("Revenue Over Time")
        aggregation = controls.segmented_control(
            "Group revenue by", ["Daily", "Weekly", "Monthly"], default="Daily",
            required=True, key="revenue_aggregation",
        )
        figure = charts.revenue_chart(selected, start, end, aggregation, previous)
        show_chart(
            figure,
            "revenue_chart", "Positive-sales revenue over time with the previous period aligned when available.",
            kind="revenue", aggregation=aggregation,
        )
        st.caption("GBP · Positive sales · Weeks start Monday · Edge buckets include selected dates only")
        with st.expander("View revenue data"):
            # Use the plotted series so the accessible table cannot diverge from the chart.
            table = pd.DataFrame({"Period": figure.data[-1].x, "Selected sales": figure.data[-1].y})
            if previous is not None:
                table["Previous sales (aligned)"] = figure.data[0].y
            st.dataframe(
                table, hide_index=True, width="stretch", row_height=32,
                column_config={
                    "Period": st.column_config.DateColumn("Period start", format="DD MMM YYYY"),
                    "Selected sales": st.column_config.NumberColumn("Selected sales (GBP)", format="£%,.2f"),
                    "Previous sales (aligned)": st.column_config.NumberColumn("Previous sales, aligned (GBP)", format="£%,.2f"),
                },
            )
            keyboard_picker(figure, "revenue", "revenue_chart", aggregation)


def products_panel(selected, full=False):
    products = product_summary(selected)
    with st.container(border=True, key="panel_products"):
        st.header("Top 10 Best-Selling Products")
        ranking = st.segmented_control(
            "Rank products by", ["Revenue", "Units"], default="Revenue", required=True, key="product_ranking",
        )
        if products.empty:
            st.info("No positive-sales products match these filters.")
        else:
            figure = charts.products_chart(products, ranking)
            show_chart(figure, "products_chart", f"Top ten products ranked by {ranking.lower()}.", kind="product")
        st.caption("Positive invoice items include postage and charges. Ranked by stock code; descriptions are labels.")
        if not full and not products.empty:
            with st.expander("View product data"):
                st.dataframe(
                    products.sort_values(ranking, ascending=False, kind="stable").head(10),
                    hide_index=True, width="stretch", row_height=32,
                    column_config={"Revenue": st.column_config.NumberColumn("Revenue (GBP)", format="£%,.2f")},
                )
                keyboard_picker(figure, "product", "products_chart")
    if full and not products.empty:
        with st.expander("Record drilldown options"):
            keyboard_picker(figure, "product", "products_chart")
        st.header("Product performance detail")
        st.caption(f"{len(products):,} products · First 100 shown · Full results available below")
        st.dataframe(
            products.head(100), hide_index=True, width="stretch", row_height=32,
            column_config={
                "StockCode": st.column_config.TextColumn("Stock code", width=100),
                "Description": st.column_config.TextColumn("Item description", width=300),
                "Revenue": st.column_config.NumberColumn("Revenue (GBP)", format="£%,.2f"),
                "Units": st.column_config.NumberColumn("Units sold", format="localized"),
                "Orders": st.column_config.NumberColumn("Orders", format="localized"),
            },
        )
        st.download_button("Download product performance", dataframe_csv(products),
                           "retailpulse-products.csv", "text/csv", icon=":material/download:")


def country_panel(selected, full=False):
    countries = country_summary(selected)
    with st.container(border=True, key="panel_countries"):
        st.header("Revenue by Country")
        if countries.empty:
            st.info("No positive-sales countries match these filters.")
        else:
            figure = charts.countries_chart(countries, 15 if full else 7)
            show_chart(figure, "countries_chart", "Countries ranked by positive-sales revenue in GBP.", kind="country")
            top = countries.iloc[0]
            st.caption(f"{top.Country} contributes {top.Share:.1f}% of selected revenue. Top {min(len(countries), 15 if full else 7)} countries shown.")
            if not full:
                with st.expander("View country data"):
                    st.dataframe(
                        countries.head(7), hide_index=True, width="stretch", row_height=32,
                        column_config={
                            "Revenue": st.column_config.NumberColumn("Revenue (GBP)", format="£%,.2f"),
                            "Share": st.column_config.NumberColumn("Revenue share (%)", format="%.1f%%"),
                        },
                    )
                    keyboard_picker(figure, "country", "countries_chart")
    if full and not countries.empty:
        with st.expander("Record drilldown options"):
            keyboard_picker(figure, "country", "countries_chart")
        st.header("Country performance detail")
        st.dataframe(
            countries, hide_index=True, width="stretch", row_height=32,
            column_config={
                "Revenue": st.column_config.NumberColumn("Revenue (GBP)", format="£%,.2f"),
                "Orders": st.column_config.NumberColumn("Orders", format="localized"),
                "Units": st.column_config.NumberColumn("Units sold", format="localized"),
                "Share": st.column_config.NumberColumn("Revenue share (%)", format="%.1f%%"),
            },
        )
        st.download_button("Download country performance", dataframe_csv(countries),
                           "retailpulse-countries.csv", "text/csv", icon=":material/download:")


def insights_panel(selected, start, end):
    metrics = sales_metrics(selected)
    credits = return_summary(selected)
    products = product_summary(selected)
    monthly = period_summary(selected)
    with st.container(key="panel_insights"):
        st.header("Period insights")
        with st.container(key="overview_insights"):
            item, month, credit = st.columns(3, gap="medium")
            with item:
                if not products.empty:
                    top = products.iloc[0]
                    st.markdown(f"**Leading invoice item**  \n{top.Description}")
                    st.caption(f"{top.StockCode} · {money(top.Revenue)} · {top.Revenue / metrics.revenue:.1%} of revenue")
            with month:
                if not monthly.empty:
                    best = monthly.loc[monthly.Revenue.idxmax()]
                    st.markdown(f"**Strongest selected month**  \n{best.Period:%B %Y} · {money(best.Revenue)}")
                    st.caption("Includes selected dates only.")
            with credit:
                st.markdown(f"**Recorded credits**  \n{money(credits['credit_value'])} across {credits['credit_invoices']:,} credit invoices")
        excluded = int(selected.TransactionType.eq(EXCLUDED).sum())
        st.caption(f"{excluded:,} selected lines are excluded from sales and usable credits. See Data Explorer for reasons.")


def overview(selected, previous, start, end):
    trend_panel(selected, previous, start, end)
    with st.container(key="overview_charts"):
        left, right = st.columns([1.4, 1], gap="medium")
        with left:
            products_panel(selected)
        with right:
            country_panel(selected)
    insights_panel(selected, start, end)


def sales_analysis(selected, previous, start, end):
    trend_panel(selected, previous, start, end)
    monthly = period_summary(selected)
    with st.container(key="performance_charts"):
        for column, (measure, title) in zip(st.columns(3), [
            ("Revenue", "Monthly revenue"), ("Orders", "Monthly orders"), ("AOV", "Monthly average order value"),
        ]):
            with column, st.container(border=True, key=f"panel_monthly_{measure}"):
                st.header(title)
                if monthly.empty:
                    st.info("No positive sales in this selection.")
                else:
                    show_chart(charts.performance_chart(monthly, measure), f"monthly_{measure}", title)
    st.caption("Calendar-month totals use selected dates only; the first or last month may be partial.")
    credits = return_summary(selected)
    with st.container(border=True, key="panel_returns"):
        st.header("Returns & cancellations")
        columns = st.columns(3)
        columns[0].metric("Recorded credit value", money(credits["credit_value"]))
        columns[1].metric("Credit invoices", number(credits["credit_invoices"]))
        columns[2].metric("Observed sales less credits", money(credits["observed_net"]))
        st.caption(
            "Credits are valid negative-quantity lines at positive prices, including C-prefixed invoices. "
            "Observed sales less credits is a signed dataset subtotal, not reconciled accounting net revenue. "
            "A credit may refer to a sale outside the selected dates."
        )
        composition, countries, items, monthly_tab = st.tabs(["Credit composition", "Countries", "Items", "Monthly credits"])
        credit_columns = {
            "CreditValue": st.column_config.NumberColumn("Recorded credit value (GBP)", format="£%,.2f"),
            "UsableCreditValue": st.column_config.NumberColumn("Usable credit value (GBP)", format="£%,.2f"),
            "CreditUnits": st.column_config.NumberColumn("Credited units", format="localized"),
            "CreditInvoices": st.column_config.NumberColumn("Credit invoices", format="localized"),
            "Period": st.column_config.DateColumn("Month", format="MMM YYYY"),
        }
        with composition:
            st.dataframe(credit_composition(selected), hide_index=True, width="stretch", row_height=32, column_config=credit_columns)
            st.caption("Review lines have no usable credit valuation. Categories describe recorded signs/prefixes, not return reasons or completed refunds.")
        with countries:
            st.dataframe(credits_by(selected, "Country"), hide_index=True, width="stretch", row_height=32, column_config=credit_columns)
        with items:
            st.dataframe(credits_by(selected, "StockCode"), hide_index=True, width="stretch", row_height=32, column_config=credit_columns)
        with monthly_tab:
            monthly_credit_table = monthly_credits(selected)
            st.dataframe(monthly_credit_table, hide_index=True, width="stretch", row_height=32, column_config=credit_columns)
            st.caption("Only the selected dates contribute to each calendar month; edge months may be partial.")
            st.download_button("Download monthly credits", dataframe_csv(monthly_credit_table), "retailpulse-monthly-credits.csv", "text/csv", icon=":material/download:")


def data_explorer(selected, start, end):
    with st.container(border=True, key="panel_explorer"):
        st.header("Transaction records")
        controls = st.columns([1, 1.4])
        if "transaction_search" not in st.session_state:
            st.session_state["transaction_search"] = ""
        if "transaction_types" not in st.session_state:
            st.session_state["transaction_types"] = [SALE, RETURN, EXCLUDED]
        query = controls[0].text_input("Search transactions", value=None, key="transaction_search",
                                       placeholder="Invoice, stock code, description, customer or country") or ""
        types = controls[1].multiselect(
            "Transaction types", [SALE, RETURN, EXCLUDED], key="transaction_types",
        )
        shown = search_transactions(selected, query)
        shown = shown.loc[shown.TransactionType.isin(types)].sort_values("InvoiceDate", ascending=False, kind="stable")
        st.caption(f"{len(shown):,} matching transactions · {date_label(start, end)}")
        if shown.empty:
            st.info("No transactions match this search and transaction type selection. Clear the search or select another type.")
            return
        pagination = st.columns([1, 1, 2])
        size = pagination[0].selectbox("Rows per page", [25, 50, 100], index=1, key="rows_per_page")
        pages = max(1, math.ceil(len(shown) / size))
        if st.session_state.get("transaction_page", 1) > pages:
            st.session_state["transaction_page"] = 1
        page = pagination[1].number_input("Page", min_value=1, max_value=pages, step=1, key="transaction_page")
        st.caption(f"Page {page:,} of {pages:,}. Download includes every matching row, beyond the current page.")
        columns = REQUIRED_COLUMNS + ["Revenue", "TransactionType", "IsExactDuplicate", "ExclusionReason", "SourceRow"]
        st.dataframe(
            shown.iloc[(page - 1) * size:page * size][columns], hide_index=True, width="stretch",
            height=440, row_height=32,
            column_order=[
                "InvoiceDate", "InvoiceNo", "Description", "Quantity", "UnitPrice", "Revenue",
                "Country", "TransactionType", "StockCode", "CustomerID", "IsExactDuplicate", "ExclusionReason", "SourceRow",
            ],
            column_config={
                "InvoiceDate": st.column_config.DatetimeColumn("Invoice date", format="DD MMM YYYY, HH:mm", width=160),
                "InvoiceNo": st.column_config.TextColumn("Invoice", width=100),
                "Description": st.column_config.TextColumn("Item description", width=240),
                "Quantity": st.column_config.NumberColumn("Quantity", format="localized", width=88),
                "Country": st.column_config.TextColumn("Country", width=120),
                "TransactionType": st.column_config.TextColumn("Record type", width=180),
                "StockCode": st.column_config.TextColumn("Stock code", width=100),
                "CustomerID": st.column_config.TextColumn("Customer", width=100),
                "ExclusionReason": st.column_config.TextColumn("Review reason", width=240),
                "UnitPrice": st.column_config.NumberColumn("Unit price (GBP)", format="£%,.2f"),
                "Revenue": st.column_config.NumberColumn("Line value (GBP)", format="£%,.2f"),
                "IsExactDuplicate": st.column_config.CheckboxColumn("Exact repeat"),
                "SourceRow": st.column_config.NumberColumn("Workbook row", format="%d"),
            },
        )
        st.download_button(
            "Download filtered transactions", transactions_csv(shown),
            f"retailpulse-transactions-{start}-{end}.csv", "text/csv", icon=":material/download:",
        )


def methodology(report):
    with st.expander("Data quality & metric definitions"):
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("**Source workbook quality**")
            st.caption("Counts describe the full loaded workbook before filters and duplicate policy.")
            st.dataframe(pd.DataFrame(report.items(), columns=["Check", "Rows"]), hide_index=True, width="stretch")
        with right:
            st.markdown("**How to read the numbers**")
            st.markdown(
                "- **Revenue:** Quantity × UnitPrice on valid, positive-quantity, positive-price sales lines. Prices are GBP.\n"
                "- **Orders:** unique sale invoice numbers, not transaction row counts. With a product filter, revenue and AOV cover only matching invoice lines.\n"
                "- **Credits:** valid negative quantities at positive prices. Positive-quantity cancellation invoices require review.\n"
                "- **Duplicates:** retained unless you enable the explicit exclusion option. Repeated lines can be legitimate.\n"
                "- **Missing values:** missing customers and descriptions do not remove valid sales. Invalid dates, identifiers, quantities, and prices exclude lines from KPIs.\n"
                "- **Comparisons:** the immediately preceding equal number of calendar days, using the same country/product/duplicate choices. Uncovered periods and zero baselines have no percentage.\n"
                "- **Scope:** positive charges and non-merchandise invoice lines remain if they meet the rules. Product categories, costs, margin, and verified return rates are not inferred."
            )

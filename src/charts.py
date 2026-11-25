"""Plotly figures with a shared visual language and real aggregated values."""

from html import escape

import pandas as pd
import plotly.graph_objects as go

from src.metrics import daily_sales


ACCENT = "#2759FB"
INK = "#070C27"
MUTED = "#56617B"
COMPARISON = "#717B94"
GRID = "#E8ECF5"
FONT = "Arial, Helvetica, sans-serif"


def finish(figure: go.Figure, height: int = 300, money_axis: bool = True) -> go.Figure:
    figure.update_layout(
        height=height,
        margin=dict(l=8, r=24, t=40, b=16),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=INK, size=12),
        hoverlabel=dict(bgcolor="white", bordercolor="#DCE2F0", font_color=INK, font_size=13),
        legend=dict(orientation="h", y=1.12, x=0, font_size=12),
        hovermode="x unified",
        dragmode=False,
    )
    figure.update_xaxes(showgrid=False, zeroline=False, automargin=True, tickfont_color=MUTED, nticks=6)
    figure.update_yaxes(gridcolor=GRID, zeroline=False, automargin=True, tickfont_color=MUTED, nticks=5)
    if money_axis:
        figure.update_yaxes(tickprefix="£", tickformat="~s")
    return figure


def revenue_chart(frame, start, end, aggregation="Daily", previous=None):
    current = daily_sales(frame, start, end)
    figure = go.Figure()
    frequency = {"Daily": "D", "Weekly": "W-SUN", "Monthly": "M"}[aggregation]

    def buckets(daily):
        daily = daily.copy()
        daily["Period"] = daily["Date"].dt.to_period(frequency).dt.start_time
        return daily.groupby("Period", as_index=False)["Revenue"].sum()

    if previous is not None:
        previous_start = pd.Timestamp(start) - pd.Timedelta(days=len(current))
        previous_end = pd.Timestamp(start) - pd.Timedelta(days=1)
        prior_daily = daily_sales(previous, previous_start, previous_end)
        prior_daily["Date"] += pd.Timedelta(days=len(current))
        prior = buckets(prior_daily)
        figure.add_trace(go.Scatter(
            x=prior["Period"], y=prior["Revenue"], name="Previous period (aligned)",
            mode="lines+markers" if len(prior) < 3 else "lines",
            line=dict(color=COMPARISON, width=1.8, dash="dash"),
            marker=dict(size=8, symbol="diamond"),
            hovertemplate="Previous: £%{y:,.2f}<extra></extra>",
        ))
    current = buckets(current)
    figure.add_trace(go.Scatter(
        x=current["Period"], y=current["Revenue"], name="Selected period",
        mode="lines+markers",
        line=dict(color=ACCENT, width=2.6), marker=dict(size=8 if len(current) < 3 else 4, symbol="circle"),
        hovertemplate="Sales: £%{y:,.2f}<extra></extra>",
    ))
    figure = finish(figure)
    figure.update_xaxes(tickformat="%d %b" if aggregation != "Monthly" else "%b %Y")
    figure.update_yaxes(rangemode="tozero")
    if len(current) < 3:
        figure.update_xaxes(tickmode="array", tickvals=current["Period"])
    return figure


def products_chart(products: pd.DataFrame, ranking: str = "Revenue", limit: int = 10):
    chosen = products.sort_values(ranking, ascending=False, kind="stable").head(limit).iloc[::-1].copy()
    chosen["Label"] = [
        escape(description if len(description) <= 25 else description[:24] + "…") + "<br>" + escape(code)
        for description, code in zip(chosen["Description"], chosen["StockCode"])
    ]
    currency = "£" if ranking == "Revenue" else ""
    figure = go.Figure(go.Bar(
        x=chosen[ranking], y=chosen["StockCode"], orientation="h",
        marker_color=[ACCENT if index == len(chosen) - 1 else COMPARISON for index in range(len(chosen))],
        texttemplate=f"{currency}%{{x:,.0f}}", textposition="outside", cliponaxis=False,
        customdata=chosen[["Description", "StockCode"]].to_numpy(),
        hovertemplate=f"%{{customdata[0]}}<br>Code: %{{customdata[1]}}<br>{ranking}: {currency}%{{x:,.2f}}<extra></extra>",
    ))
    figure = finish(figure, height=max(300, len(chosen) * 34 + 32), money_axis=False)
    figure.update_layout(hovermode="closest", showlegend=False, bargap=0.4, margin=dict(t=12, r=72))
    figure.update_xaxes(showgrid=True, gridcolor=GRID, tickprefix=currency, tickformat="~s")
    figure.update_yaxes(
        type="category", categoryorder="array", categoryarray=chosen["StockCode"],
        showgrid=False, tickmode="array", tickvals=chosen["StockCode"], ticktext=chosen["Label"], nticks=None,
    )
    return figure


def countries_chart(countries: pd.DataFrame, limit: int = 8):
    chosen = countries.head(limit).iloc[::-1]
    figure = go.Figure(go.Bar(
        x=chosen["Revenue"], y=chosen["Country"], orientation="h",
        marker_color=[ACCENT if index == len(chosen) - 1 else COMPARISON for index in range(len(chosen))],
        texttemplate="£%{x:.3s}", textposition="outside", cliponaxis=False,
        customdata=chosen[["Share", "Orders"]].to_numpy(),
        hovertemplate="%{y}<br>Revenue: £%{x:,.2f}<br>Share: %{customdata[0]:.1f}%<br>Orders: %{customdata[1]:,.0f}<extra></extra>",
    ))
    figure = finish(figure, height=max(310, len(chosen) * 30 + 30), money_axis=False)
    figure.update_layout(hovermode="closest", showlegend=False, bargap=0.4, margin=dict(t=12, r=72))
    figure.update_xaxes(showgrid=True, gridcolor=GRID, tickprefix="£", tickformat="~s")
    figure.update_yaxes(type="category", categoryorder="array", categoryarray=chosen["Country"], showgrid=False, dtick=1, nticks=None)
    return figure


def performance_chart(monthly: pd.DataFrame, measure: str):
    money_axis = measure in ["Revenue", "AOV"]
    hover = "%{x|%b %Y}<br>" + ("£" if money_axis else "") + "%{y:,.2f}<extra></extra>"
    figure = go.Figure(go.Bar(
        x=monthly["Period"], y=monthly[measure],
        marker_color=ACCENT, hovertemplate=hover,
    ))
    figure = finish(figure, height=280, money_axis=money_axis)
    step = max(1, (len(monthly) + 5) // 6)
    figure.update_xaxes(tickmode="array", tickvals=monthly["Period"].iloc[::step], tickformat="%b %Y")
    return figure

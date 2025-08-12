"""
Cash flow report page.

This page displays cash inflows and outflows grouped by period and
visualises the net cash flow over time.  Users can filter by
account and choose the aggregation period (monthly, quarterly or
yearly).  Export buttons provide the ability to download the
underlying cash flow data.
"""

from __future__ import annotations

from datetime import date
from typing import List

import pandas as pd
import streamlit as st
import plotly.express as px

import utils


@st.cache_data(ttl=3600)  # 1 hour cache
def get_data() -> pd.DataFrame:
    return utils.load_enhanced_transactions()


def render() -> None:
    st.title("Cash Flow")
    df = get_data()
    if df.empty:
        st.info("No transaction data found.  Please add files to the data directory and reload.")
        return
    st.sidebar.markdown("### Filters")
    # Extract bank name and last 4 digits from Bank_Account column
    def extract_account_info(bank_account):
        """Extract bank name and last 4 digits from Bank_Account column."""
        if pd.isna(bank_account):
            return "Unknown Account"
        parts = str(bank_account).split('_')
        if len(parts) >= 2:
            bank_name = parts[0].upper()
            last4 = parts[1][-4:] if len(parts[1]) >= 4 else parts[1]
            return f"{bank_name} {last4}"
        return str(bank_account).upper()
    
    df['AccountDisplay'] = df['Bank_Account'].apply(extract_account_info)
    accounts = sorted(df['AccountDisplay'].unique())
    selected_accounts = st.sidebar.multiselect(
        "Select accounts", options=accounts, default=accounts
    )
    filtered = df[df['AccountDisplay'].isin(selected_accounts)]
    min_date = filtered["Date"].min().date() if pd.notnull(filtered["Date"].min()) else date.today()
    max_date = filtered["Date"].max().date() if pd.notnull(filtered["Date"].max()) else date.today()
    start_date, end_date = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM-DD",
    )
    if isinstance(start_date, tuple) or isinstance(start_date, list):
        start_date, end_date = start_date
    filtered = filtered[(filtered["Date"] >= pd.to_datetime(start_date)) & (filtered["Date"] <= pd.to_datetime(end_date))]
    # Period selection
    period = st.sidebar.selectbox("Aggregation period", ["Monthly", "Quarterly", "Yearly"], index=0)
    if period == "Monthly":
        period_index = filtered["Date"].dt.to_period("M")
    elif period == "Quarterly":
        period_index = filtered["Date"].dt.to_period("Q")
    else:
        period_index = filtered["Date"].dt.to_period("Y")
    grouped = filtered.copy()
    grouped["Period"] = period_index
    cash_flow = (
        grouped.groupby("Period")
        .agg(NetCash=("Amount", "sum"))
        .reset_index()
    )
    cash_flow["Period"] = cash_flow["Period"].dt.to_timestamp()
    
    # Format dates to remove time component
    if period == "Monthly":
        cash_flow["PeriodDisplay"] = cash_flow["Period"].dt.strftime("%Y-%m")
    elif period == "Quarterly":
        cash_flow["PeriodDisplay"] = cash_flow["Period"].dt.strftime("%Y-Q%q")
    else:
        cash_flow["PeriodDisplay"] = cash_flow["Period"].dt.strftime("%Y")
    
    # Display metrics with accounting formatting
    total_net = cash_flow["NetCash"].sum()
    def format_accounting(value):
        if value < 0:
            return f"({abs(value):,.2f})"
        return f"{value:,.2f}"
    
    utils.create_metric_row([
        {"label": f"Total net cash ({period})", "value": f"${format_accounting(total_net)}"}
    ], columns=1)
    st.markdown(f"### {period} cash flow")
    
    # Format display dataframe
    display_df = cash_flow.copy()
    display_df["NetCash"] = display_df["NetCash"].apply(lambda x: f"${format_accounting(x)}")
    period_label = {"Monthly": "Month", "Quarterly": "Quarter", "Yearly": "Year"}.get(period, "Period")
    utils.display_dataframe(display_df.rename(columns={"PeriodDisplay": period_label, "NetCash": "Net Cash Flow"}))
    
    # Line chart with error handling
    try:
        fig = px.bar(cash_flow, x="PeriodDisplay", y="NetCash", title="Net Cash Flow")
        fig.update_layout(**utils.get_chart_config())
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning("Unable to display chart. Please check your data.")
        st.info("Chart error details: " + str(e))
    # Export
    st.markdown("### Export data")
    utils.add_download_button(cash_flow, "cash_flow.csv", "Download Cash Flow CSV")
    utils.add_excel_download_button(cash_flow, "cash_flow.xlsx", "Download Cash Flow Excel")
"""
Profit and Loss report page.

This page summarises income and expenses over a selected date range.
Users can filter by account and drill down into monthly or quarterly
views.  A simple table displays totals for income, expenses and
net income.  Charts visualise the trend of income and expenses
over time.  Export buttons allow you to download the underlying
data for further analysis.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

import pandas as pd
import numpy as np
import streamlit as st

import utils
import plotly.express as px


@st.cache_data(ttl=3600)  # 1 hour cache
def get_data() -> pd.DataFrame:
    """Cached helper to load all transactions."""
    return utils.load_enhanced_transactions()


def render() -> None:
    """Render the profit and loss page."""
    st.title("Profit & Loss")
    df = get_data()
    if df.empty:
        st.info("No transaction data found.  Please add files to the data directory and reload.")
        return
    # Sidebar filters
    st.sidebar.markdown("### Filters")
    # Account filter - extract bank name and last 4 digits from Bank_Account column
    def extract_account_info(bank_account):
        """Extract bank name and last 4 digits from Bank_Account column."""
        if pd.isna(bank_account):
            return "Unknown Account"
        # Bank_Account format is like "BOA_7259"
        parts = str(bank_account).split('_')
        if len(parts) >= 2:
            bank_name = parts[0].upper()
            last4 = parts[1][-4:] if len(parts[1]) >= 4 else parts[1]
            return f"{bank_name} {last4}"
        return str(bank_account).upper()
    
    # Create account display names
    df['AccountDisplay'] = df['Bank_Account'].apply(extract_account_info)
    accounts = sorted(df['AccountDisplay'].unique())
    selected_accounts = st.sidebar.multiselect(
        "Select accounts", options=accounts, default=accounts
    )
    # Filter data for selected accounts
    filtered = df[df['AccountDisplay'].isin(selected_accounts)]
    # Date range filter
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
        start_date, end_date = start_date  # older versions return tuple
    filtered = filtered[(filtered["Date"] >= pd.to_datetime(start_date)) & (filtered["Date"] <= pd.to_datetime(end_date))]
    # Create Type column based on Amount (positive = income, negative = expense)
    filtered['Type'] = filtered['Amount'].apply(lambda x: 'Income' if x > 0 else 'Expense')
    
    # Summarise by month
    summary = (
        filtered.groupby([filtered["Date"].dt.to_period("M"), "Type"])["Amount"].sum().reset_index()
    )
    summary["Amount"] = summary["Amount"].astype(float)
    # Pivot to income/expense columns
    pivot = summary.pivot_table(index="Date", columns="Type", values="Amount", aggfunc="sum").fillna(0)
    pivot = pivot.rename(columns={"Income": "Income", "Expense": "Expenses"})
    pivot["Net Income"] = pivot.get("Income", 0) + pivot.get("Expenses", 0)
    pivot = pivot.reset_index()
    pivot["Date"] = pivot["Date"].dt.to_timestamp()
    
    # Format dates to remove time component
    pivot["Period"] = pivot["Date"].dt.strftime("%Y-%m")
    
    # Display metrics
    total_income = pivot["Income"].sum() if "Income" in pivot else 0
    total_expenses = -pivot["Expenses"].sum() if "Expenses" in pivot else 0
    net_income = total_income - total_expenses
    
    # Format numbers in accounting style (with parentheses for negative numbers)
    def format_accounting(value):
        if value < 0:
            return f"({abs(value):,.2f})"
        return f"{value:,.2f}"
    
    utils.create_metric_row(
        [
            {"label": "Total Income", "value": f"${format_accounting(total_income)}"},
            {"label": "Total Expenses", "value": f"${format_accounting(total_expenses)}"},
            {"label": "Net Income", "value": f"${format_accounting(net_income)}"},
        ],
        columns=3,
    )
    st.markdown("### Monthly Income & Expenses")
    
    # Format the display dataframe with accounting style
    display_df = pivot.copy()
    display_df["Income"] = display_df["Income"].apply(lambda x: f"${format_accounting(x)}")
    display_df["Expenses"] = display_df["Expenses"].apply(lambda x: f"${format_accounting(x)}")
    display_df["Net Income"] = display_df["Net Income"].apply(lambda x: f"${format_accounting(x)}")
    
    utils.display_dataframe(display_df[["Period", "Income", "Expenses", "Net Income"]])
    # Bar chart
    st.markdown("### Trend")
    try:
        chart_df = pivot.melt(id_vars=["Date"], value_vars=["Income", "Expenses", "Net Income"], var_name="Metric", value_name="Value")
        fig = px.bar(chart_df, x="Date", y="Value", color="Metric", barmode="group")
        fig.update_layout(**utils.get_chart_config())
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning("Unable to display chart. Please check your data.")
        st.info("Chart error details: " + str(e))
    # Export options
    st.markdown("### Export data")
    utils.add_download_button(pivot, "profit_loss.csv", "Download P&L CSV")
    utils.add_excel_download_button(pivot, "profit_loss.xlsx", "Download P&L Excel")
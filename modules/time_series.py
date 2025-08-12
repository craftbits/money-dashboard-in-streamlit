"""
Time series analysis page.

This page allows the user to explore trends of key financial metrics
over time.  A dropdown menu lets you select from metrics such as
cash balance, total assets, credit card balance, total liabilities,
net worth/equity, total income, total expenses and net income.  The
selected metric is plotted as a line chart across the chosen
aggregation period.
"""

from __future__ import annotations

from datetime import date
from typing import List

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

import utils


@st.cache_data(ttl=3600)  # 1 hour cache
def get_data() -> pd.DataFrame:
    return utils.load_enhanced_transactions()


def compute_metrics_over_time(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """Compute various financial metrics over time.

    Parameters
    ----------
    df : pd.DataFrame
        Enhanced transaction data with Date, Amount, and Bank_Account columns.
    period : str
        Aggregation period: 'Daily', 'Monthly' or 'Quarterly'.

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by timestamp with columns for each metric.
    """
    if period == "Daily":
        period_index = df["Date"].dt.floor("D")
    elif period == "Monthly":
        period_index = df["Date"].dt.to_period("M").dt.to_timestamp()
    else:
        period_index = df["Date"].dt.to_period("Q").dt.to_timestamp()
    
    # Create base DataFrame with available columns
    metrics_df = pd.DataFrame({
        "Period": period_index, 
        "Amount": df["Amount"], 
        "Bank_Account": df["Bank_Account"]
    })
    
    # Derive Type from Amount (positive = income, negative = expense)
    metrics_df["Type"] = metrics_df["Amount"].apply(lambda x: "Income" if x > 0 else "Expense")
    
    # Income, expenses and net income
    income_df = metrics_df[metrics_df["Type"] == "Income"].groupby("Period")["Amount"].sum()
    expense_df = metrics_df[metrics_df["Type"] == "Expense"].groupby("Period")["Amount"].sum()
    
    # Calculate running balances by account
    balances = metrics_df.groupby(["Period", "Bank_Account"])["Amount"].sum().unstack().fillna(0)
    
    # Calculate cumulative balances
    cumulative_balances = balances.cumsum()
    
    # Summarise cash (all accounts)
    cash = cumulative_balances.sum(axis=1)
    
    # For demo purposes, assume all accounts are assets (no credit cards in sample data)
    assets = cash
    liabilities = pd.Series(0, index=cash.index)  # No liabilities in sample data
    
    # Build result
    idx = sorted(metrics_df["Period"].unique())
    result = pd.DataFrame(index=idx)
    result.index.name = "Period"
    result["Cash"] = cash
    result["Total Assets"] = assets
    result["Credit Card Balance"] = liabilities
    result["Total Liabilities"] = liabilities
    result["Net Worth"] = assets + liabilities
    result["Total Income"] = income_df
    result["Total Expenses"] = -expense_df  # expenses stored as negative amounts, so invert sign
    result["Net Income"] = result["Total Income"].fillna(0) - result["Total Expenses"].fillna(0)
    result = result.fillna(method="ffill").fillna(0)
    return result.reset_index()


def render() -> None:
    st.title("Time Series Analysis")
    df = get_data()
    if df.empty:
        st.info("No transaction data found.  Please add files to the data directory and reload.")
        return
    st.sidebar.markdown("### Options")
    period = st.sidebar.selectbox("Aggregation period", ["Daily", "Monthly", "Quarterly"], index=1)
    metrics_df = compute_metrics_over_time(df, period)
    metric_choices = [
        "Cash",
        "Total Assets",
        "Credit Card Balance",
        "Total Liabilities",
        "Net Worth",
        "Total Income",
        "Total Expenses",
        "Net Income",
    ]
    selected_metric = st.sidebar.selectbox("Select metric", metric_choices, index=0)
    st.markdown(f"### {selected_metric} over time ({period})")
    chart_df = metrics_df[["Period", selected_metric]].copy()
    try:
        fig = px.line(chart_df, x="Period", y=selected_metric, title=selected_metric)
        fig.update_layout(**utils.get_chart_config())
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning("Unable to display chart. Please check your data.")
        st.info("Chart error details: " + str(e))
    # Display table
    utils.display_dataframe(chart_df)
    st.markdown("### Export data")
    utils.add_download_button(chart_df, f"{selected_metric.lower().replace(' ', '_')}_{period.lower()}.csv", f"Download {selected_metric} CSV")
    utils.add_excel_download_button(chart_df, f"{selected_metric.lower().replace(' ', '_')}_{period.lower()}.xlsx", f"Download {selected_metric} Excel")
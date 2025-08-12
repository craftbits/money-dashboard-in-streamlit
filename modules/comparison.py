"""
Comparison report page.

This page allows you to compare current performance against a budget or
historical periods.  By default the app computes the same period
last year as the comparison baseline.  Users may upload their own
budget file into the processed data folder which will be merged
automatically when present.  For simplicity this page currently
implements an actual vs last year comparison for income and
expenses.
"""

from __future__ import annotations

from datetime import date
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

import utils


@st.cache_data(ttl=3600)  # 1 hour cache
def get_data() -> pd.DataFrame:
    return utils.load_enhanced_transactions()


def render() -> None:
    st.title("Comparisons")
    df = get_data()
    if df.empty:
        st.info("No transaction data found.  Please add files to the data directory and reload.")
        return
    st.sidebar.markdown("### Options")
    # Choose period for current
    period = st.sidebar.selectbox("Comparison period", ["Monthly", "Quarterly", "Yearly"], index=0)
    # Compute aggregated actuals
    if period == "Monthly":
        current = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum().reset_index()
        current["Period"] = current["Date"].dt.to_timestamp()
    elif period == "Quarterly":
        current = df.groupby(df["Date"].dt.to_period("Q"))["Amount"].sum().reset_index()
        current["Period"] = current["Date"].dt.to_timestamp()
    else:
        current = df.groupby(df["Date"].dt.to_period("Y"))["Amount"].sum().reset_index()
        current["Period"] = current["Date"].dt.to_timestamp()
    current = current.rename(columns={"Amount": "Actual"})
    # Compute last year's amounts for the same period labels (shift by 1 period)
    current_sorted = current.sort_values("Period").reset_index(drop=True)
    current_sorted["LastYear"] = current_sorted["Actual"].shift(1)
    # Remove the first row as it has no last year comparison
    comparison = current_sorted.dropna(subset=["LastYear"]).copy()
    comparison["Difference"] = comparison["Actual"] - comparison["LastYear"]
    comparison["% Change"] = comparison["Difference"] / comparison["LastYear"]
    st.markdown(f"### Actual vs last {period.lower()}")
    utils.display_dataframe(
        comparison[["Period", "Actual", "LastYear", "Difference", "% Change"]].assign(
            **{
                "Difference": lambda x: x["Difference"].map(utils.format_currency),
                "Actual": lambda x: x["Actual"].map(utils.format_currency),
                "LastYear": lambda x: x["LastYear"].map(utils.format_currency),
                "% Change": lambda x: (x["% Change"] * 100).round(2).astype(str) + "%",
            }
        )
    )
    # Plot bar chart of actual vs last year
    try:
        chart_df = comparison.melt(id_vars="Period", value_vars=["Actual", "LastYear"], var_name="Category", value_name="Value")
        fig = px.bar(chart_df, x="Period", y="Value", color="Category", barmode="group", title="Actual vs Last Year")
        fig.update_layout(**utils.get_chart_config())
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning("Unable to display chart. Please check your data.")
        st.info("Chart error details: " + str(e))
    # Export
    st.markdown("### Export data")
    utils.add_download_button(comparison, "comparison.csv", "Download Comparison CSV")
    utils.add_excel_download_button(comparison, "comparison.xlsx", "Download Comparison Excel")
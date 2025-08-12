"""
Subscription tracking page.

This page identifies potential recurring transactions (subscriptions)
by analysing your historical transactions.  It groups expenses by
description and highlights those that occur in at least three
separate months.  The results help you spot forgotten subscriptions
that you might want to cancel.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

from collections import Counter
from typing import List

import utils


@st.cache_data(ttl=3600)  # 1 hour cache
def get_data() -> pd.DataFrame:
    return utils.load_enhanced_transactions()


def identify_subscriptions(df: pd.DataFrame, min_occurrences: int = 3) -> pd.DataFrame:
    """Identify recurring expenses by description.

    A simple heuristic groups outgoing transactions by normalised
    description and counts how many unique months the transaction
    appears in.  Entries meeting or exceeding ``min_occurrences``
    are returned as potential subscriptions.
    """
    subs = []
    # Filter for expenses (negative amounts) and use Transaction_Description
    out_df = df[df["Amount"] < 0].copy()
    if "Transaction_Description" in out_df.columns:
        desc_col = "Transaction_Description"
    else:
        # Fallback to any description column
        desc_col = [col for col in out_df.columns if "description" in col.lower()][0] if any("description" in col.lower() for col in out_df.columns) else "Transaction_Description"
    
    out_df["NormDesc"] = out_df[desc_col].str.upper().str.replace(r"[^A-Z0-9 ]", "", regex=True).str.strip()
    out_df["Month"] = out_df["Date"].dt.to_period("M")
    for desc, group in out_df.groupby("NormDesc"):
        months = group["Month"].nunique()
        if months >= min_occurrences:
            total = group["Amount"].sum()
            avg = group["Amount"].mean()
            subs.append({"Description": desc.title(), "Months": months, "Total": total, "Average": avg})
    result = pd.DataFrame(subs).sort_values("Total", ascending=True)
    return result


def render() -> None:
    st.title("Subscription Tracking")
    df = get_data()
    if df.empty:
        st.info("No transaction data found.  Please add files to the data directory and reload.")
        return
    st.markdown("This tool scans your outgoing transactions for recurring charges that appear in at least three different months.")
    min_occ = st.slider("Minimum number of months", min_value=2, max_value=12, value=3)
    subs_df = identify_subscriptions(df, min_occ)
    if subs_df.empty:
        st.info("No recurring transactions found.")
        return
    # Format currency
    subs_df["Total"] = subs_df["Total"].apply(utils.format_currency)
    subs_df["Average"] = subs_df["Average"].apply(utils.format_currency)
    utils.display_dataframe(subs_df)
    # Bar chart of average monthly cost per subscription
    try:
        chart_df = subs_df.rename(columns={"Average": "Monthly Cost"})
        fig = px.bar(chart_df, x="Description", y="Monthly Cost", title="Recurring monthly charges")
        fig.update_layout(xaxis_title="Description", yaxis_title="Cost", **utils.get_chart_config())
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning("Unable to display chart. Please check your data.")
        st.info("Chart error details: " + str(e))
    st.markdown("### Export subscriptions")
    # Convert currency columns back to numeric for export by removing '$' and commas
    export_df = identify_subscriptions(df, min_occ)
    utils.add_download_button(export_df, "subscriptions.csv", "Download Subscriptions CSV")
    utils.add_excel_download_button(export_df, "subscriptions.xlsx", "Download Subscriptions Excel")
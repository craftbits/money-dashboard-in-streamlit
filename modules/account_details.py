"""
Account details page.

This page provides a detailed view of all transactions for a selected
account over a chosen date range.  Users can quickly export the
results to a CSV or Excel file.  This report is useful for
reconciling statement entries with receipts or for preparing tax
documentation.
"""

from __future__ import annotations

from datetime import date
import pandas as pd
import streamlit as st

import utils


@st.cache_data(ttl=3600)  # 1 hour cache
def get_data() -> pd.DataFrame:
    return utils.load_enhanced_transactions()


def render() -> None:
    st.title("Account Details")
    df = get_data()
    if df.empty:
        st.info("No transaction data found.  Please add files to the data directory and reload.")
        return
    # Select account
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
    account = st.sidebar.selectbox("Select an account", accounts)
    acc_df = df[df['AccountDisplay'] == account]
    # Date range
    min_date = acc_df["Date"].min().date() if pd.notnull(acc_df["Date"].min()) else date.today()
    max_date = acc_df["Date"].max().date() if pd.notnull(acc_df["Date"].max()) else date.today()
    start_date, end_date = st.sidebar.date_input(
        "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    if isinstance(start_date, tuple) or isinstance(start_date, list):
        start_date, end_date = start_date
    acc_df = acc_df[(acc_df["Date"] >= pd.to_datetime(start_date)) & (acc_df["Date"] <= pd.to_datetime(end_date))]
    # Display table
    if acc_df.empty:
        st.info("No transactions in the selected period.")
    else:
        utils.display_dataframe(acc_df.sort_values("Date", ascending=False))
    # Export
    st.markdown("### Export data")
    utils.add_download_button(acc_df, f"{account.replace(' ', '_').lower()}_transactions.csv", "Download CSV")
    utils.add_excel_download_button(acc_df, f"{account.replace(' ', '_').lower()}_transactions.xlsx", "Download Excel")
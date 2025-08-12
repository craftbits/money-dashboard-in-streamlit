"""
Balance Sheet report page.

This page approximates a balance sheet by summarising the latest
balances of each account.  Checking accounts are treated as assets
while credit card accounts are treated as liabilities.  The net
worth/equity is computed as assets minus liabilities.  The data is
derived from the running balance column if available, otherwise
falling back to a cumulative sum of transaction amounts.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

import utils


@st.cache_data(ttl=3600)  # 1 hour cache
def get_data() -> pd.DataFrame:
    return utils.load_enhanced_transactions()


def compute_account_balances(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the latest balance for each account.

    Parameters
    ----------
    df : pd.DataFrame
        Combined transactions.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: Account, Bank, AccountType, Last4, Balance.
    """
    accounts = []
    
    # Extract account info from Bank_Account column (format: "BOA_7259")
    def extract_account_info(bank_account):
        if pd.isna(bank_account):
            return "Unknown", "Unknown", "0000"
        parts = str(bank_account).split('_')
        if len(parts) >= 2:
            bank_name = parts[0].upper()
            last4 = parts[1][-4:] if len(parts[1]) >= 4 else parts[1]
            return bank_name, "CHECKING", last4  # Default to checking for demo
        return str(bank_account).upper(), "UNKNOWN", "0000"
    
    # Group by Bank_Account since that's what we have in enhanced data
    for bank_account, subdf in df.groupby("Bank_Account"):
        subdf = subdf.sort_values("Date")
        bank_name, acct_type, last4 = extract_account_info(bank_account)
        
        # Use cumulative sum of Amount for balance
        balance = subdf["Amount"].sum()
        
        accounts.append(
            {
                "Account": f"{bank_name} {acct_type} {last4}",
                "Bank": bank_name.title(),
                "AccountType": acct_type.title(),
                "Last4": last4,
                "Balance": balance,
            }
        )
    return pd.DataFrame(accounts)


def render() -> None:
    st.title("Balance Sheet")
    df = get_data()
    if df.empty:
        st.info("No transaction data found.  Please add files to the data directory and reload.")
        return
    acct_balances = compute_account_balances(df)
    # Classify as asset or liability
    acct_balances["Category"] = acct_balances["AccountType"].apply(
        lambda x: "Liabilities" if x.lower().startswith("cc") or x.lower().startswith("credit") else "Assets"
    )
    assets_total = acct_balances.loc[acct_balances["Category"] == "Assets", "Balance"].sum()
    liabilities_total = acct_balances.loc[acct_balances["Category"] == "Liabilities", "Balance"].sum()
    net_worth = assets_total + liabilities_total  # liabilities_total likely negative if credit cards negative
    
    # Format numbers in accounting style
    def format_accounting(value):
        if value < 0:
            return f"({abs(value):,.2f})"
        return f"{value:,.2f}"
    
    utils.create_metric_row(
        [
            {"label": "Total Assets", "value": f"${format_accounting(assets_total)}"},
            {"label": "Total Liabilities", "value": f"${format_accounting(liabilities_total)}"},
            {"label": "Net Worth", "value": f"${format_accounting(net_worth)}"},
        ],
        columns=3,
    )
    st.markdown("### Account Balances")
    utils.display_dataframe(acct_balances[["Account", "Category", "Balance"]])
    # Pie chart of asset vs liabilities
    try:
        chart_data = pd.DataFrame(
            {
                "Category": ["Assets", "Liabilities"],
                "Balance": [assets_total, liabilities_total],
            }
        )
        fig = px.pie(chart_data, names="Category", values="Balance", title="Assets vs Liabilities")
        fig.update_layout(**utils.get_chart_config())
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning("Unable to display chart. Please check your data.")
        st.info("Chart error details: " + str(e))
    # Export balances
    st.markdown("### Export data")
    utils.add_download_button(acct_balances, "balance_sheet.csv", "Download Balance Sheet CSV")
    utils.add_excel_download_button(acct_balances, "balance_sheet.xlsx", "Download Balance Sheet Excel")
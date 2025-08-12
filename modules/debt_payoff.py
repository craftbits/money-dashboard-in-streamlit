"""
Debt payoff calculator page.

This page assists you in planning the repayment of credit card or
other loan balances.  Select a liability account, enter the
interest rate and choose a monthly payment amount to see how many
months it will take to pay off the balance.  A simple amortisation
table is generated and can be exported.
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
    # reuse logic from balance sheet
    from .balance_sheet import compute_account_balances as bal_fn
    return bal_fn(df)


def payoff_schedule(balance: float, annual_rate: float, monthly_payment: float) -> pd.DataFrame:
    """Compute an amortisation schedule for debt payoff.

    Parameters
    ----------
    balance : float
        Current outstanding balance (positive value).
    annual_rate : float
        Annual percentage rate in decimal form (e.g. 0.18 for 18%).
    monthly_payment : float
        Fixed monthly payment amount.

    Returns
    -------
    pd.DataFrame
        A schedule with columns for period, interest, principal, payment and remaining balance.
    """
    records = []
    monthly_rate = annual_rate / 12.0
    month = 1
    current_balance = balance
    while current_balance > 0 and month <= 1200:  # safety cap to avoid infinite loop
        interest = current_balance * monthly_rate
        principal = monthly_payment - interest
        if principal <= 0:
            # Payment too low; interest accumulates
            break
        new_balance = current_balance - principal
        if new_balance < 0:
            principal += new_balance
            new_balance = 0
        records.append(
            {
                "Month": month,
                "Starting Balance": current_balance,
                "Payment": monthly_payment,
                "Interest": interest,
                "Principal": principal,
                "Ending Balance": new_balance,
            }
        )
        current_balance = new_balance
        month += 1
    return pd.DataFrame(records)


def render() -> None:
    st.title("Debt Payoff Calculator")
    df = get_data()
    if df.empty:
        st.info("No transaction data found.  Please add files to the data directory and reload.")
        return
    bal_df = compute_account_balances(df)
    liabilities = bal_df[bal_df["Category"] == "Liabilities"]
    if liabilities.empty:
        st.info("No liability accounts found.")
        return
    account = st.sidebar.selectbox("Select liability account", liabilities["Account"].tolist())
    balance = float(liabilities.loc[liabilities["Account"] == account, "Balance"].iloc[0])
    st.markdown(f"**Current balance:** {utils.format_currency(balance)}")
    annual_rate = st.number_input("Annual interest rate (%)", min_value=0.0, max_value=50.0, value=18.0, step=0.1) / 100
    monthly_payment = st.number_input(
        "Monthly payment amount", min_value=0.0, value=round(abs(balance) * 0.05, 2), step=10.0
    )
    if monthly_payment <= balance * annual_rate / 12:
        st.warning("Monthly payment is too low to reduce the balance. Increase the payment amount.")
        return
    schedule = payoff_schedule(balance=abs(balance), annual_rate=annual_rate, monthly_payment=monthly_payment)
    if schedule.empty:
        st.warning("Payment is too low to cover the interest. Try increasing your payment amount.")
        return
    total_interest = schedule["Interest"].sum()
    months = schedule.shape[0]
    utils.create_metric_row(
        [
            {"label": "Months to payoff", "value": f"{months}"},
            {"label": "Total interest paid", "value": utils.format_currency(total_interest)},
        ],
        columns=2,
    )
    utils.display_dataframe(
        schedule.assign(
            **{
                "Starting Balance": lambda x: x["Starting Balance"].apply(utils.format_currency),
                "Payment": lambda x: x["Payment"].apply(utils.format_currency),
                "Interest": lambda x: x["Interest"].apply(utils.format_currency),
                "Principal": lambda x: x["Principal"].apply(utils.format_currency),
                "Ending Balance": lambda x: x["Ending Balance"].apply(utils.format_currency),
            }
        )
    )
    st.markdown("### Export schedule")
    utils.add_download_button(schedule, "debt_payoff_schedule.csv", "Download Schedule CSV")
    utils.add_excel_download_button(schedule, "debt_payoff_schedule.xlsx", "Download Schedule Excel")
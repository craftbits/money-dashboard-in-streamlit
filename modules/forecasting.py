"""
Forecasting tools page.

This page implements simple cash flow projections based on historical
data.  Users can choose the number of months to project and
optionally adjust a growth rate.  A line chart shows the projected
cash balance over time.  Scenario analysis can be performed by
tweaking the growth rate parameter.
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


def render() -> None:
    st.title("Cash Flow Forecasting")
    df = get_data()
    if df.empty:
        st.info("No transaction data found.  Please add files to the data directory and reload.")
        return
    # Aggregate monthly net cash
    monthly_net = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum().reset_index()
    monthly_net["Date"] = monthly_net["Date"].dt.to_timestamp()
    if monthly_net.empty:
        st.info("Insufficient data for forecasting.")
        return
    avg_net = monthly_net["Amount"].mean()
    st.markdown(
        "This simple model assumes that future net cash flow equals the average monthly net cash flow "
        "observed in the historical data.  Adjust the growth rate slider to model optimistic or pessimistic scenarios."
    )
    months_ahead = st.slider("Months to forecast", min_value=1, max_value=24, value=6)
    growth_rate = st.slider("Growth rate per month (%)", min_value=-50.0, max_value=50.0, value=0.0, step=1.0)
    # Generate forecast
    last_date = monthly_net["Date"].max()
    dates = pd.date_range(start=last_date + pd.offsets.MonthBegin(1), periods=months_ahead, freq="MS")
    forecast_values = []
    value = avg_net
    for i in range(months_ahead):
        if i == 0:
            val = avg_net * (1 + growth_rate / 100)
        else:
            val = forecast_values[-1] * (1 + growth_rate / 100)
        forecast_values.append(val)
    forecast_df = pd.DataFrame({"Date": dates, "Forecast Net Cash": forecast_values})
    combined = pd.concat(
        [monthly_net.rename(columns={"Amount": "Historical Net Cash"})[["Date", "Historical Net Cash"], forecast_df]],
        ignore_index=True,
    )
    # Plot
    try:
        fig = px.line(combined, x="Date", y=["Historical Net Cash", "Forecast Net Cash"], title="Net Cash Forecast")
        fig.update_layout(**utils.get_chart_config())
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning("Unable to display chart. Please check your data.")
        st.info("Chart error details: " + str(e))
    # Export forecast
    st.markdown("### Export forecast")
    utils.add_download_button(forecast_df, "cash_flow_forecast.csv", "Download Forecast CSV")
    utils.add_excel_download_button(forecast_df, "cash_flow_forecast.xlsx", "Download Forecast Excel")
"""
Home page for the Personal Money Dashboard.

This page introduces the application and provides an overview of the
data pipeline used to ingest, clean and analyse financial
transactions.  A simple diagram illustrates the flow from raw
statements to the rich analytics displayed in subsequent pages.
"""

from __future__ import annotations

import streamlit as st


def render() -> None:
    """Render the home page."""
    st.title("Personal Money Dashboard")
    st.markdown(
        """
        Welcome to your personal finance cockpit!  This dashboard
        helps you stay on top of your cash flows, balances and
        subscriptions across all of your bank accounts and credit cards.  
        
        Upload raw statements into the data folder and explore a
        consolidated view of your income and expenses.  Use the
        navigation sidebar to access detailed reports, graphs and tools
        including budget comparisons, debt payoff calculators and
        forecasting.
        
        The diagram below outlines the data pipeline: raw transaction
        files are ingested, cleaned and enriched with user‑defined
        categories before powering the interactive reports throughout
        this application.
        """
    )
    # Display a placeholder architecture image.  Users can replace this
    # file with a custom diagram in the assets directory.
    try:
        st.image("assets/architecture.png", caption="Data pipeline overview", use_container_width=True)
    except Exception:
        st.info(
            "Add an image named `architecture.png` to the assets directory to display your own data pipeline diagram."
        )
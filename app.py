"""
Main entry point for the Personal Money Dashboard application.

This file sets up the Streamlit configuration, applies custom
styling, constructs the sidebar navigation and routes user
interactions to the appropriate page modules.  Pages are organised
into groups (Reports, Analytics, Tools and Reference) for a clean
sidebar.  The navigation state is preserved in Streamlit session
state.
"""

from __future__ import annotations

import streamlit as st

import config
import utils
from modules import (
    home,
    profit_loss,
    balance_sheet,
    cash_flow,
    comparison,
    time_series,
    account_details,
    forecasting,
    subscription_tracking,
    debt_payoff,
    list_management,
    task_management,
    wiki,
    doc_processing,
    chatbot,
    reference,
    transaction_mapping,
    list_management_admin,
)


def create_sidebar_navigation() -> str:
    """Create sidebar navigation and return the selected page name."""
    st.sidebar.markdown(f"## {config.config.title}")
    st.sidebar.markdown("---")
    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"
    navigation_groups = {
        "Home": {"pages": {"Home": home.render}},
        "Reports": {
            "pages": {
                "Profit & Loss": profit_loss.render,
                "Balance Sheet": balance_sheet.render,
                "Cash Flow": cash_flow.render,
                "Comparisons": comparison.render,
            }
        },
        "Analytics": {
            "pages": {
                "Time Series": time_series.render,
            }
        },
        "Tools": {
            "pages": {
                "Account Details": account_details.render,
                "Forecasting": forecasting.render,
                "Subscription Tracking": subscription_tracking.render,
                "Debt Payoff Calculator": debt_payoff.render,
                "List Management": list_management.render,
                "Task Management": task_management.render,
                "Personal Wiki/Notes": wiki.render,
                "Document Processing": doc_processing.render,
                "Chatbot": chatbot.render,
            }
        },
        "Reference": {
            "pages": {
                "Reference & Resources": reference.render,
            }
        },
        "Admin Center": {
            "pages": {
                "Transaction Mapping": transaction_mapping.render,
                "List Management Admin": list_management_admin.render,
            }
        },
    }
    selected_page = None
    # Render navigation
    for group_name, group_data in navigation_groups.items():
        if group_name == "Home":
            if st.sidebar.button("🏠 Home", key=f"nav_{group_name}"):
                st.session_state.current_page = "Home"
                selected_page = "Home"
        else:
            with st.sidebar.expander(group_name, expanded=True):
                for page_name, render_func in group_data["pages"].items():
                    if st.button(f"• {page_name}", key=f"nav_{page_name}"):
                        st.session_state.current_page = page_name
                        selected_page = page_name
    return selected_page


def main() -> None:
    """Run the main application."""
    st.set_page_config(
        page_title=config.config.title,
        page_icon=config.config.page_icon,
        layout=config.config.layout,
        initial_sidebar_state=config.config.initial_sidebar_state,
    )
    # Hide default menu and footer
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    utils.apply_custom_css()
    
    selected_page = create_sidebar_navigation()
    if selected_page:
        st.session_state.current_page = selected_page
    # Render selected page
    current_page = st.session_state.get("current_page", "Home")
    # Build a mapping of page names to render functions
    all_pages = {
        "Home": home.render,
        "Profit & Loss": profit_loss.render,
        "Balance Sheet": balance_sheet.render,
        "Cash Flow": cash_flow.render,
        "Comparisons": comparison.render,
        "Time Series": time_series.render,
        "Account Details": account_details.render,
        "Forecasting": forecasting.render,
        "Subscription Tracking": subscription_tracking.render,
        "Debt Payoff Calculator": debt_payoff.render,
        "List Management": list_management.render,
        "Task Management": task_management.render,
        "Personal Wiki/Notes": wiki.render,
        "Document Processing": doc_processing.render,
        "Chatbot": chatbot.render,
        "Reference & Resources": reference.render,
        "Transaction Mapping": transaction_mapping.render,
        "List Management Admin": list_management_admin.render,
    }
    render_func = all_pages.get(current_page, home.render)
    render_func()


if __name__ == "__main__":
    main()
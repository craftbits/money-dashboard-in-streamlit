"""
Reference and resource page.

This page collects useful links and quick access resources
relevant to personal finance.  Populate this list with your
favourite budgeting guides, credit monitoring services or other
websites you visit frequently.
"""

from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("Reference & Resources")
    st.markdown(
        """
        ### Useful links
        
        - [AnnualCreditReport.com](https://www.annualcreditreport.com) – Get your free credit report annually.
        - [Consumer Financial Protection Bureau](https://www.consumerfinance.gov/) – Official US government resource for consumer finance.
        - [Investopedia](https://www.investopedia.com) – Learn about investing, budgeting and personal finance.
        - [IRS Tax Publications](https://www.irs.gov/forms-pubs/about-publication-17) – Access US tax information.
        
        ### Quick access
        
        Use the sidebar navigation to jump to tools like the debt payoff
        calculator, subscription tracker or notes.  This page can be
        personalised with your own bookmarks.
        """
    )
"""
Document processing and data extraction page.

This tool allows you to upload documents such as bank statements or
receipts and attempt a simple extraction of tabular data.  The
current implementation supports CSV and Excel files.  Future
enhancements could include PDF parsing and OCR.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
import io
from typing import Optional

import utils


def parse_uploaded_file(uploaded_file) -> Optional[pd.DataFrame]:
    try:
        if uploaded_file.name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx") or uploaded_file.name.endswith(".xls"):
            return pd.read_excel(uploaded_file)
        else:
            st.warning("Unsupported file type.  Please upload CSV or Excel files.")
            return None
    except Exception as e:
        st.error(f"Failed to parse file: {e}")
        return None


def render() -> None:
    st.title("Document Processing & Data Extraction")
    st.markdown(
        "Upload a CSV or Excel document and the app will attempt to display its contents as a DataFrame. "
        "Use this feature to quickly inspect exported statements or other tabular documents."
    )
    uploaded_file = st.file_uploader("Upload document", type=["csv", "xlsx", "xls"])
    if uploaded_file is not None:
        df = parse_uploaded_file(uploaded_file)
        if df is not None:
            utils.display_dataframe(df)
            st.markdown("### Export uploaded data")
            utils.add_download_button(df, uploaded_file.name, "Download CSV")
            utils.add_excel_download_button(df, uploaded_file.name.replace(".csv", ".xlsx"), "Download Excel")
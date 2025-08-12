"""
Utility functions for the Personal Money Dashboard.

This module contains helpers for reading, cleaning and combining raw
transaction data, formatting numbers and dates, generating common
charts and tables and providing download buttons.  The functions
here are intended to be reused across multiple Streamlit page
modules.
"""

from __future__ import annotations

import io
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

import config
from config import get_chart_config, get_table_config


def parse_transaction_filename(filename: str) -> Tuple[str, str, str, str, Tuple[datetime, datetime]]:
    """Parse the standardised transaction filename into its components.

    Filenames follow the pattern:
        ``transactions-raw-import-[bank]_[accountType]_[last4]-YYYY.MM.DD-YYYY.MM.DD.<ext>``

    Where ``accountType`` is ``chk`` for checking or ``cc`` for credit card.  The
    date range indicates the inclusive start and end dates covered by the
    file.  The extension can be csv/xlsx depending on the bank export.

    Parameters
    ----------
    filename : str
        Basename of the file to parse (not including directory path).

    Returns
    -------
    Tuple[str, str, str, str, Tuple[datetime, datetime]]
        A 5‑tuple of ``bank``, ``account_type`` (chk/cc), ``last4``, ``ext``,
        and a tuple of start and end dates.  If the date portion cannot be
        parsed then start and end dates will be ``None``.
    """
    name, ext = os.path.splitext(filename)
    parts = name.split("-")
    # Expected structure: ['transactions', 'raw', 'import', '[bank]_[type]_[last4]', 'YYYY.MM.DD', 'YYYY.MM.DD']
    bank_part = parts[3]
    bank_match = re.match(r"(?P<bank>[^_]+)_(?P<acct_type>[^_]+)_(?P<last4>\d{4})", bank_part)
    bank = bank_match.group("bank") if bank_match else "unknown"
    acct_type = bank_match.group("acct_type") if bank_match else "unknown"
    last4 = bank_match.group("last4") if bank_match else "0000"
    try:
        start_date = datetime.strptime(parts[4], "%Y.%m.%d")
        end_date = datetime.strptime(parts[5], "%Y.%m.%d")
    except Exception:
        start_date = None
        end_date = None
    return bank, acct_type, last4, ext.lstrip("."), (start_date, end_date)


def read_transaction_file(path: str) -> pd.DataFrame:
    """Read a single transaction file and return a cleaned DataFrame.

    This function automatically detects whether the input is a CSV or an
    Excel workbook.  Many banks export statements as Excel files with
    a ``.csv`` extension.  For Excel files the first few rows may
    contain summary lines that should be skipped.  The header row is
    inferred by looking for a row that contains 'Date' and 'Amount'.
    
    The returned DataFrame always contains at minimum the following
    columns: ``Date``, ``Description``, ``Amount``, ``Running Bal.`` (if
    available).  Additional columns from the source file are preserved.

    Parameters
    ----------
    path : str
        Full path to the transaction file.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame ready for further processing.  A ``file_name``
        column is appended with the basename of the file.
    """
    fname = os.path.basename(path)
    bank, acct_type, last4, ext, _ = parse_transaction_filename(fname)
    # Determine file type based on MIME type
    mime = None
    try:
        import mimetypes
        mime, _ = mimetypes.guess_type(path)
    except Exception:
        pass
    is_excel = False
    if ext.lower() in ("xlsx", "xls"):
        is_excel = True
    elif mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        is_excel = True
    # Attempt to read accordingly
    if is_excel:
        xls = pd.ExcelFile(path)
        df = pd.read_excel(xls, sheet_name=0, header=None)
        # Identify header row by scanning for 'Date' and 'Amount'
        header_idx = None
        for i, row in df.iterrows():
            row_strs = row.astype(str).str.lower().tolist()
            if "date" in row_strs and "amount" in row_strs:
                header_idx = i
                break
        if header_idx is None:
            # Fallback: treat first row as header
            header_idx = 0
        df.columns = df.iloc[header_idx].astype(str)
        df = df.iloc[header_idx + 1 :].reset_index(drop=True)
    else:
        # Assume CSV file; attempt reading with utf‑8 first, then latin1
        try:
            df = pd.read_csv(path)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="latin1")
    # Drop completely blank rows
    df = df.dropna(how="all").copy()
    # Standardise column names
    df.columns = [str(c).strip() for c in df.columns]
    # Add account metadata
    df["Bank"] = bank
    df["AccountType"] = acct_type
    df["AccountLast4"] = last4
    df["FileName"] = fname
    # Convert Date column to datetime if present
    date_cols = [c for c in df.columns if c.lower().startswith("date")]
    if date_cols:
        date_col = date_cols[0]
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce").dt.date
        df = df.rename(columns={date_col: "Date"})
    # Ensure Amount column numeric
    amt_cols = [c for c in df.columns if "amount" in c.lower()]
    if amt_cols:
        amt_col = amt_cols[0]
        df[amt_col] = (
            df[amt_col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("$", "", regex=False)
            .astype(float)
        )
        df = df.rename(columns={amt_col: "Amount"})
    # Running balance may have multiple names
    bal_cols = [c for c in df.columns if "running" in c.lower() and "bal" in c.lower()]
    if bal_cols:
        bal_col = bal_cols[0]
        df = df.rename(columns={bal_col: "RunningBalance"})
    else:
        # No running balance; compute cumulative sum for account as approximate
        df["RunningBalance"] = np.nan
    # Description column
    desc_cols = [c for c in df.columns if "description" in c.lower()]
    if desc_cols:
        desc_col = desc_cols[0]
        df = df.rename(columns={desc_col: "Description"})
    else:
        df["Description"] = ""
    return df


def load_all_transactions() -> pd.DataFrame:
    """Load and combine all raw transaction files from the configured directory.

    Uses :func:`read_transaction_file` to parse each file located in
    ``config.data_raw_dir``.  The resulting DataFrame includes all
    transactions with additional metadata columns.  After loading the
    combined dataset, basic derived fields such as ``Type`` (incoming
    vs outgoing), ``PeriodMonth``, ``PeriodQuarter`` and ``PeriodYear``
    are added.

    Returns
    -------
    pd.DataFrame
        Combined and enriched transaction data.
    """
    all_files = []
    for root, _, files in os.walk(config.config.data_raw_dir):
        for f in files:
            if not f.startswith("."):
                all_files.append(os.path.join(root, f))
    data_frames: List[pd.DataFrame] = []
    for path in all_files:
        try:
            df = read_transaction_file(path)
        except Exception as e:
            st.warning(f"Failed to read {os.path.basename(path)}: {e}")
            continue
        data_frames.append(df)
    if not data_frames:
        return pd.DataFrame()
    combined = pd.concat(data_frames, ignore_index=True)
    # Derive incoming/outgoing type based on amount sign
    combined["Type"] = np.where(combined["Amount"] >= 0, "Incoming", "Outgoing")
    # Derive period columns
    combined["Date"] = pd.to_datetime(combined["Date"], errors="coerce")
    combined["PeriodMonth"] = combined["Date"].dt.to_period("M")
    combined["PeriodQuarter"] = combined["Date"].dt.to_period("Q")
    combined["PeriodYear"] = combined["Date"].dt.to_period("Y")
    return combined


def load_enhanced_transactions() -> pd.DataFrame:
    """Load enhanced transaction data with mappings and additional columns.
    
    This function loads the enhanced combined transaction file that includes
    all the additional columns like categories, tags, payers, payees,
    and formatted period columns.
    
    Returns
    -------
    pd.DataFrame
        Enhanced transaction data with mappings applied.
    """
    enhanced_file = os.path.join(config.config.data_processed_dir, "transactions_combined_enhanced.csv")
    
    if os.path.exists(enhanced_file):
        try:
            df = pd.read_csv(enhanced_file)
            # Convert Date column to datetime
            df['Date'] = pd.to_datetime(df['Date'])
            return df
        except Exception as e:
            st.warning(f"Failed to load enhanced transaction file: {e}")
            return pd.DataFrame()
    else:
        st.warning("Enhanced transaction file not found. Please ensure the data processing workflow has been run.")
        return pd.DataFrame()


def save_combined_transactions(df: pd.DataFrame, filename: str = "transactions_combined.csv") -> str:
    """Save the combined transaction DataFrame to the processed directory.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to save.
    filename : str
        Name of the output file (CSV).  Defaults to
        ``transactions_combined.csv``.

    Returns
    -------
    str
        Full path of the written file.
    """
    out_path = os.path.join(config.config.data_processed_dir, filename)
    df.to_csv(out_path, index=False)
    return out_path


def format_currency(value: float, decimals: int = 2) -> str:
    """Format a number as a currency string."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "-"
    if decimals == 0:
        return f"${value:,.0f}"
    return f"${value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format a decimal as a percentage string."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "-"
    return f"{value * 100:.{decimals}f}%"


def create_metric_row(metrics: List[Dict[str, Any]], columns: int = 4) -> None:
    """Render a row of metric widgets using Streamlit columns."""
    cols = st.columns(columns)
    for i, metric in enumerate(metrics):
        with cols[i % columns]:
            st.metric(metric.get("label", ""), metric.get("value", ""), delta=metric.get("delta"))


def create_line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = "") -> None:
    """Render a line chart using Plotly."""
    fig = px.line(df, x=x_col, y=y_col, title=title)
    fig.update_layout(**get_chart_config())
    st.plotly_chart(fig, **get_chart_config())


def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = "") -> None:
    """Render a bar chart using Plotly."""
    fig = px.bar(df, x=x_col, y=y_col, title=title)
    fig.update_layout(**get_chart_config())
    st.plotly_chart(fig, **get_chart_config())


def display_dataframe(df: pd.DataFrame, title: str = "") -> None:
    """Display a DataFrame with an optional title."""
    if title:
        st.subheader(title)
    st.dataframe(df.head(config.config.max_display_rows), **get_table_config())


def add_download_button(df: pd.DataFrame, filename: str, button_text: str = "Download CSV") -> None:
    """Add a CSV download button for a DataFrame."""
    csv = df.to_csv(index=False)
    st.download_button(
        label=button_text,
        data=csv,
        file_name=filename,
        mime="text/csv",
    )


def add_excel_download_button(df: pd.DataFrame, filename: str, button_text: str = "Download Excel") -> None:
    """Add an Excel download button for a DataFrame."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    st.download_button(
        label=button_text,
        data=buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def apply_custom_css() -> None:
    """Apply custom CSS to refine Streamlit's look and feel."""
    # This CSS replicates the clean sidebar styling from the original
    st.markdown(
        """

        <style>
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #f8f9fa;
        }
        /* Sidebar header styling */
        .css-1d391kg h2 {
            color: #1f2937;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #e5e7eb;
            border-radius: 6px;
            padding: 8px 12px;
            margin: 4px 0;
            font-weight: 500;
            color: #374151;
        }
        .streamlit-expanderHeader:hover {
            background-color: #d1d5db;
        }
        /* Button styling in sidebar */
        .css-1d391kg button {
            background-color: transparent;
            border: none;
            padding: 8px 12px;
            margin: 2px 0;
            border-radius: 4px;
            text-align: left;
            width: 100%;
            transition: background-color 0.2s;
        }
        .css-1d391kg button:hover {
            background-color: #e5e7eb;
        }
        /* User info section */
        .css-1d391kg .stMarkdown {
            margin-top: 1rem;
        }
        /* Divider styling */
        .css-1d391kg hr {
            margin: 1rem 0;
            border-color: #d1d5db;
        }
        /* Page content styling */
        .main .block-container {
            padding-top: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
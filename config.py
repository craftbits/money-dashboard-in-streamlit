"""
Configuration settings for the Personal Money Dashboard.

This module centralises all configuration constants including the app
metadata, display preferences and default directories for data
ingestion.  The ``AppConfig`` dataclass exposes sensible defaults
which can be overridden on instantiation if needed.  A global
``config`` instance is created at import time and can be used
throughout the application.  Helper functions expose commonly
consumed subsets of the configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class AppConfig:
    """Application configuration settings.

    Attributes
    ----------
    title: str
        The page title displayed in the browser tab and at the top
        of the Streamlit app.
    page_icon: str
        Emoji or unicode character representing the application.
    layout: str
        Streamlit layout setting.  Set to ``"wide"`` for a wide
        centre column.
    initial_sidebar_state: str
        Determines whether the sidebar is expanded or collapsed on
        initial load.  Accepts ``"expanded"`` or ``"collapsed"``.
    data_raw_dir: str
        Path to the directory containing raw transaction files.  The
        application reads all files matching the naming convention
        from this directory when loading data.
    data_processed_dir: str
        Path to the directory where cleaned and merged data will be
        saved.  This directory is created on demand.
    cache_ttl: int
        Time‑to‑live for any Streamlit caches in seconds.  This
        controls how often expensive computations are recomputed.
    default_user: str
        Name or identifier of the default user.  This is displayed
        in the sidebar and can be used to personalise the app.
    
    chart_height: int
        Default height for charts in pixels.
    table_height: int
        Default height for tables in pixels.
    max_display_rows: int
        Maximum number of rows to show in any interactive table.
    """

    # App metadata
    title: str = "Personal Money Dashboard"
    page_icon: str = "💰"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"

    # Data settings
    data_raw_dir: str = field(default_factory=lambda: os.path.join(os.getcwd(), "data", "raw"))
    data_processed_dir: str = field(default_factory=lambda: os.path.join(os.getcwd(), "data", "processed"))
    cache_ttl: int = 3600  # 1 hour

    # User settings
    default_user: str = "user"

    # Display settings
    chart_height: int = 400
    table_height: int = 450
    max_display_rows: int = 1000

    def __post_init__(self) -> None:
        """Ensure data directories exist."""
        os.makedirs(self.data_raw_dir, exist_ok=True)
        os.makedirs(self.data_processed_dir, exist_ok=True)


# Instantiate a global configuration object
config = AppConfig()


def get_chart_config() -> Dict[str, Any]:
    """Return the default chart configuration for Plotly charts."""
    return {
        "height": config.chart_height,
        "margin": {"l": 50, "r": 50, "t": 50, "b": 50},
        "showlegend": True,
        "hovermode": "closest",
    }


def get_table_config() -> Dict[str, Any]:
    """Return the default table configuration for Streamlit dataframes."""
    return {
        "use_container_width": True,
        "height": config.table_height,
    }
"""
List management page.

Users can maintain master lists for accounts, descriptions, classes,
categories, tags and names.  These lists drive the classification
and aggregation logic in other reports.  The lists are persisted
under the processed data directory in a single JSON file.  Simple
forms allow you to add new entries to existing lists or create
entirely new lists.
"""

from __future__ import annotations

import json
import os
import streamlit as st

from typing import Dict, List

import utils


LISTS_FILE = os.path.join("data", "processed", "user_lists.json")


def load_lists() -> Dict[str, List[str]]:
    if os.path.exists(LISTS_FILE):
        try:
            with open(LISTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_lists(lists: Dict[str, List[str]]) -> None:
    os.makedirs(os.path.dirname(LISTS_FILE), exist_ok=True)
    with open(LISTS_FILE, "w", encoding="utf-8") as f:
        json.dump(lists, f, indent=2)


def render() -> None:
    st.title("List Management")
    st.markdown(
        "Maintain master lists that power the categorisation and tagging logic. "
        "You can add entries to existing lists or create your own new lists to store things like expense categories, "
        "income sources, contact names or any other custom taxonomy."
    )
    lists = load_lists()
    list_names = list(lists.keys())
    # Create new list
    with st.expander("Create new list"):
        new_list_name = st.text_input("New list name")
        if st.button("Create list"):
            if not new_list_name:
                st.warning("Enter a name for the new list.")
            elif new_list_name in lists:
                st.warning("A list with that name already exists.")
            else:
                lists[new_list_name] = []
                save_lists(lists)
                st.success(f"List '{new_list_name}' created.")
    # Select existing list
    if list_names:
        selected_list = st.selectbox("Select list", list_names)
        items = lists.get(selected_list, [])
        st.markdown(f"### {selected_list}")
        st.write(items if items else "(empty)")
        new_item = st.text_input("Add new item", key="new_item")
        if st.button("Add item"):
            if new_item:
                if new_item in items:
                    st.warning("Item already exists.")
                else:
                    items.append(new_item)
                    lists[selected_list] = items
                    save_lists(lists)
                    st.success(f"Added '{new_item}' to {selected_list}.")
                    # Refresh display
                    st.experimental_rerun()
    else:
        st.info("No lists defined.  Create a new list to get started.")
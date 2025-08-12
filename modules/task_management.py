"""
Task management page.

This page provides a simple to‑do list for personal finance tasks.
Tasks persist across sessions using a JSON file in the processed
data directory.  You can add new tasks, mark them complete and
delete completed items.
"""

from __future__ import annotations

import json
import os
import streamlit as st

from typing import List, Dict

import utils


TASK_FILE = os.path.join("data", "processed", "tasks.json")


def load_tasks() -> List[Dict[str, any]]:
    if os.path.exists(TASK_FILE):
        try:
            with open(TASK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_tasks(tasks: List[Dict[str, any]]) -> None:
    os.makedirs(os.path.dirname(TASK_FILE), exist_ok=True)
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


def render() -> None:
    st.title("Task Management")
    tasks = load_tasks()
    # Add new task
    with st.form("Add task"):
        desc = st.text_input("Task description")
        submitted = st.form_submit_button("Add")
        if submitted and desc:
            tasks.append({"description": desc, "complete": False})
            save_tasks(tasks)
            st.success("Task added!")
    # Display tasks
    if tasks:
        st.markdown("### Your tasks")
        for idx, task in enumerate(tasks):
            cols = st.columns([0.05, 0.8, 0.15])
            with cols[0]:
                done = st.checkbox("", value=task["complete"], key=f"task_{idx}")
            with cols[1]:
                st.write(task["description"])
            with cols[2]:
                if st.button("Delete", key=f"del_{idx}"):
                    tasks.pop(idx)
                    save_tasks(tasks)
                    st.experimental_rerun()
            # Update completion state
            if done != task["complete"]:
                task["complete"] = done
                save_tasks(tasks)
    else:
        st.info("No tasks.  Add one using the form above.")
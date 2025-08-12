"""
Personal wiki/notes page.

This page lets you maintain freeform notes in Markdown.  Each note
is stored as an individual file in the processed data directory.  You
can create, view, edit and delete notes.  Use this space to record
financial goals, planning assumptions or any other information you
want to keep handy.
"""

from __future__ import annotations

import os
import streamlit as st

import utils


NOTES_DIR = os.path.join("data", "processed", "notes")
os.makedirs(NOTES_DIR, exist_ok=True)


def list_notes() -> list[str]:
    return [f for f in os.listdir(NOTES_DIR) if f.endswith(".md")]


def load_note(name: str) -> str:
    with open(os.path.join(NOTES_DIR, name), "r", encoding="utf-8") as f:
        return f.read()


def save_note(name: str, content: str) -> None:
    with open(os.path.join(NOTES_DIR, name), "w", encoding="utf-8") as f:
        f.write(content)


def delete_note(name: str) -> None:
    os.remove(os.path.join(NOTES_DIR, name))


def render() -> None:
    st.title("Personal Wiki / Notes")
    notes = list_notes()
    # New note creation
    with st.expander("Create new note"):
        new_title = st.text_input("Note title (no spaces or special characters)")
        if st.button("Create note"):
            if not new_title:
                st.warning("Please provide a note title.")
            else:
                fname = f"{new_title}.md"
                if fname in notes:
                    st.warning("A note with that title already exists.")
                else:
                    save_note(fname, "")
                    st.success(f"Created note {new_title}")
                    st.experimental_rerun()
    if notes:
        selected = st.selectbox("Select a note", notes)
        content = load_note(selected)
        edited = st.text_area("Edit note", value=content, height=300)
        if st.button("Save changes"):
            save_note(selected, edited)
            st.success("Note saved.")
        if st.button("Delete note"):
            delete_note(selected)
            st.success("Note deleted.")
            st.experimental_rerun()
        st.markdown("---")
        st.markdown("### Preview")
        st.markdown(edited, unsafe_allow_html=True)
    else:
        st.info("No notes available.  Create one above.")
"""
Chatbot page.

This is a placeholder chat interface.  In a future enhancement the
chatbot could be connected to a language model to answer questions
about your finances or help you navigate the dashboard.  For now
the bot simply echoes your input back to you.
"""

from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("Chatbot")
    st.markdown(
        "This is a placeholder for a personal finance chatbot.  Type a message below and the bot will echo it back."
    )
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    user_input = st.text_input("You:")
    if st.button("Send") and user_input:
        st.session_state['chat_history'].append(("You", user_input))
        # Echo response
        response = f"Bot: {user_input}"
        st.session_state['chat_history'].append(("Bot", response))
    # Display chat history
    for speaker, msg in st.session_state['chat_history']:
        st.write(f"**{speaker}:** {msg}")
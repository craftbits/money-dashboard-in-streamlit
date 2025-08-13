"""
Authentication module using streamlit-authenticator.

This provides a more robust authentication system with better security
and user management features.
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
import os
from datetime import datetime


def init_auth():
    """Initialize authentication system."""
    # Create config file if it doesn't exist
    config_file = "data/auth_config.yaml"
    os.makedirs("data", exist_ok=True)
    
    if not os.path.exists(config_file):
        # Create default configuration
        config = {
            'credentials': {
                'usernames': {
                    'user1': {
                        'email': 'user1@example.com',
                        'name': 'Demo User',
                        'password': stauth.Hasher(['test1pw']).generate()
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'some_signature_key',
                'name': 'some_cookie_name'
            }
        }
        
        with open(config_file, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
    
    # Load configuration
    with open(config_file) as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)
    
    # Create authenticator
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    return authenticator


def main_auth():
    """Main authentication flow using streamlit-authenticator."""
    authenticator = init_auth()
    
    # Create login widget
    name, authentication_status, username = authenticator.login('Login', 'main')
    
    if authentication_status == False:
        st.error('Username/password is incorrect')
        return False
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        return False
    elif authentication_status:
        # User is authenticated
        st.success(f'Welcome *{name}*')
        return True
    
    return False


def show_user_menu(authenticator):
    """Display user menu in sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"**👤 Logged in as:** {st.session_state.get('name', 'User')}")
        
        # User menu
        user_menu = st.selectbox(
            "User Menu",
            ["Dashboard", "Change Password", "Logout"],
            label_visibility="collapsed"
        )
        
        if user_menu == "Change Password":
            show_change_password_form(authenticator)
        elif user_menu == "Logout":
            if st.button("Confirm Logout"):
                authenticator.logout('Logout', 'main')
                st.rerun()


def show_change_password_form(authenticator):
    """Display change password form."""
    st.sidebar.markdown("### Change Password")
    
    try:
        if authenticator.reset_password(st.session_state.get('username', 'user1'), 'Change password'):
            st.sidebar.success('New password set')
    except Exception as e:
        st.sidebar.error(f'Error: {e}')


def require_auth():
    """Decorator to require authentication for pages."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not st.session_state.get('authentication_status'):
                st.error("Please login to access this page.")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator

"""
Authentication module for the Personal Money Dashboard.

This module provides session-based authentication with secure password
handling and user management. Users can register, login, and logout
with their credentials stored securely.
"""

import streamlit as st
import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pandas as pd


class AuthManager:
    """Manages user authentication and sessions."""
    
    def __init__(self):
        self.users_file = "data/users.json"
        self.sessions_file = "data/sessions.json"
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Ensure authentication data files exist."""
        os.makedirs("data", exist_ok=True)
        
        # Create users file if it doesn't exist
        if not os.path.exists(self.users_file):
            default_users = {
                "user1": {
                    "password_hash": self._hash_password("test1pw"),
                    "email": "user1@example.com",
                    "created_at": datetime.now().isoformat(),
                    "role": "user"
                }
            }
            self._save_users(default_users)
        
        # Create sessions file if it doesn't exist
        if not os.path.exists(self.sessions_file):
            self._save_sessions({})
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_session_token(self) -> str:
        """Generate a secure session token."""
        return secrets.token_urlsafe(32)
    
    def _load_users(self) -> Dict[str, Any]:
        """Load users from file."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users(self, users: Dict[str, Any]):
        """Save users to file."""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def _load_sessions(self) -> Dict[str, Any]:
        """Load sessions from file."""
        try:
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_sessions(self, sessions: Dict[str, Any]):
        """Save sessions to file."""
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
    
    def register_user(self, username: str, password: str, email: str) -> bool:
        """Register a new user."""
        users = self._load_users()
        
        if username in users:
            return False  # Username already exists
        
        users[username] = {
            "password_hash": self._hash_password(password),
            "email": email,
            "created_at": datetime.now().isoformat(),
            "role": "user"
        }
        
        self._save_users(users)
        return True
    
    def login_user(self, username: str, password: str) -> Optional[str]:
        """Login a user and return session token."""
        users = self._load_users()
        
        if username not in users:
            return None
        
        user = users[username]
        if user["password_hash"] != self._hash_password(password):
            return None
        
        # Generate session token
        session_token = self._generate_session_token()
        sessions = self._load_sessions()
        
        sessions[session_token] = {
            "username": username,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        self._save_sessions(sessions)
        return session_token
    
    def logout_user(self, session_token: str):
        """Logout a user by removing their session."""
        sessions = self._load_sessions()
        if session_token in sessions:
            del sessions[session_token]
            self._save_sessions(sessions)
    
    def validate_session(self, session_token: str) -> Optional[str]:
        """Validate a session token and return username if valid."""
        sessions = self._load_sessions()
        
        if session_token not in sessions:
            return None
        
        session = sessions[session_token]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if datetime.now() > expires_at:
            # Session expired, remove it
            del sessions[session_token]
            self._save_sessions(sessions)
            return None
        
        return session["username"]
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information."""
        users = self._load_users()
        return users.get(username)
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password."""
        users = self._load_users()
        
        if username not in users:
            return False
        
        user = users[username]
        if user["password_hash"] != self._hash_password(old_password):
            return False
        
        user["password_hash"] = self._hash_password(new_password)
        self._save_users(users)
        return True


def init_auth():
    """Initialize authentication in Streamlit session state."""
    if "auth_manager" not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    
    if "session_token" not in st.session_state:
        st.session_state.session_token = None
    
    if "current_user" not in st.session_state:
        st.session_state.current_user = None


def login_page() -> bool:
    """Display login page and return True if login successful."""
    st.title("🔐 Login to Personal Money Dashboard")
    st.markdown("Please enter your credentials to access the dashboard.")
    
    # Show default credentials for easy access
    with st.expander("Default Credentials (Click to show)"):
        st.markdown("**Username:** `user1`")
        st.markdown("**Password:** `test1pw`")
        st.info("These are demo credentials for easy access. You can register new accounts or change passwords later.")
    
    # Check if user is already logged in
    if st.session_state.current_user:
        st.success(f"Already logged in as {st.session_state.current_user}")
        if st.button("Continue to Dashboard"):
            return True
        if st.button("Logout"):
            logout()
            st.rerun()
        return False
    
    # Login form
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password.")
                return False
            
            session_token = st.session_state.auth_manager.login_user(username, password)
            if session_token:
                st.session_state.session_token = session_token
                st.session_state.current_user = username
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
                return False
    
    # Registration link
    st.markdown("---")
    st.markdown("Don't have an account?")
    if st.button("Register New Account"):
        st.session_state.show_register = True
        st.rerun()
    
    return False


def register_page() -> bool:
    """Display registration page and return True if registration successful."""
    st.title("📝 Register New Account")
    st.markdown("Create a new account to access the Personal Money Dashboard.")
    
    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a username")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Choose a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        submit = st.form_submit_button("Register")
        
        if submit:
            if not username or not email or not password:
                st.error("Please fill in all fields.")
                return False
            
            if password != confirm_password:
                st.error("Passwords do not match.")
                return False
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters long.")
                return False
            
            success = st.session_state.auth_manager.register_user(username, password, email)
            if success:
                st.success("Account created successfully! You can now login.")
                st.session_state.show_register = False
                st.rerun()
            else:
                st.error("Username already exists. Please choose a different username.")
                return False
    
    # Back to login
    st.markdown("---")
    if st.button("Back to Login"):
        st.session_state.show_register = False
        st.rerun()
    
    return False


def logout():
    """Logout the current user."""
    if st.session_state.session_token:
        st.session_state.auth_manager.logout_user(st.session_state.session_token)
    
    st.session_state.session_token = None
    st.session_state.current_user = None
    st.session_state.show_register = False


def require_auth():
    """Decorator to require authentication for pages."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not st.session_state.current_user:
                st.error("Please login to access this page.")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator


def show_user_menu():
    """Display user menu in sidebar."""
    if st.session_state.current_user:
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"**👤 Logged in as:** {st.session_state.current_user}")
            
            # User menu
            user_menu = st.selectbox(
                "User Menu",
                ["Dashboard", "Change Password", "Logout"],
                label_visibility="collapsed"
            )
            
            if user_menu == "Change Password":
                show_change_password_form()
            elif user_menu == "Logout":
                if st.button("Confirm Logout"):
                    logout()
                    st.rerun()


def show_change_password_form():
    """Display change password form."""
    st.sidebar.markdown("### Change Password")
    
    with st.sidebar.form("change_password_form"):
        old_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submit = st.form_submit_button("Change Password")
        
        if submit:
            if not old_password or not new_password or not confirm_password:
                st.sidebar.error("Please fill in all fields.")
                return
            
            if new_password != confirm_password:
                st.sidebar.error("New passwords do not match.")
                return
            
            if len(new_password) < 6:
                st.sidebar.error("Password must be at least 6 characters long.")
                return
            
            success = st.session_state.auth_manager.change_password(
                st.session_state.current_user, old_password, new_password
            )
            
            if success:
                st.sidebar.success("Password changed successfully!")
            else:
                st.sidebar.error("Current password is incorrect.")


def main_auth():
    """Main authentication flow."""
    init_auth()
    
    # Validate existing session
    if st.session_state.session_token:
        username = st.session_state.auth_manager.validate_session(st.session_state.session_token)
        if username:
            st.session_state.current_user = username
        else:
            # Session expired
            st.session_state.session_token = None
            st.session_state.current_user = None
    
    # Show registration page if requested
    if st.session_state.get("show_register", False):
        if register_page():
            return True
        return False
    
    # Show login page if not authenticated
    if not st.session_state.current_user:
        if login_page():
            return True
        return False
    
    # User is authenticated, show dashboard
    return True

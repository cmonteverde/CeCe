import os
import streamlit as st
import requests
import base64
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Auth0 configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID", "")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET", "")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL", "http://localhost:5000/callback")

def generate_auth_url():
    """
    Generate Auth0 authorization URL
    """
    if not AUTH0_DOMAIN or not AUTH0_CLIENT_ID:
        return None
    
    auth_url = f"https://{AUTH0_DOMAIN}/authorize"
    params = {
        "client_id": AUTH0_CLIENT_ID,
        "redirect_uri": AUTH0_CALLBACK_URL,
        "response_type": "code",
        "scope": "openid profile email",
        "state": generate_state_parameter()
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{auth_url}?{query_string}"

def generate_state_parameter():
    """
    Generate a random state parameter for CSRF protection
    """
    import random
    import string
    
    # Generate a random string
    state = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    # Store in session state
    st.session_state.auth_state = state
    
    return state

def validate_callback(code, state):
    """
    Validate the callback from Auth0
    """
    # Verify state parameter
    if state != st.session_state.get("auth_state"):
        return False, "Invalid state parameter"
    
    # Exchange authorization code for token
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": AUTH0_CALLBACK_URL
    }
    
    try:
        response = requests.post(token_url, json=payload)
        response.raise_for_status()
        
        # Parse token response
        token_data = response.json()
        
        # Get user info with access token
        user_url = f"https://{AUTH0_DOMAIN}/userinfo"
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        user_response = requests.get(user_url, headers=headers)
        user_response.raise_for_status()
        
        user_info = user_response.json()
        
        # Store user info in session state
        st.session_state.user = user_info
        st.session_state.authenticated = True
        
        return True, "Authentication successful"
    
    except Exception as e:
        return False, f"Authentication error: {str(e)}"

def login_button():
    """
    Display login button if not authenticated
    """
    if not st.session_state.get("authenticated", False):
        auth_url = generate_auth_url()
        
        if auth_url:
            st.markdown(f"""
            <a href="{auth_url}" target="_self">
                <button style="
                    background-color: #7B61FF;
                    color: white;
                    padding: 8px 16px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                ">
                    Login with Auth0
                </button>
            </a>
            """, unsafe_allow_html=True)
        else:
            st.warning("Auth0 configuration not found. Please set AUTH0_DOMAIN and AUTH0_CLIENT_ID environment variables.")

def logout_button():
    """
    Display logout button if authenticated
    """
    if st.session_state.get("authenticated", False):
        if st.button("Logout"):
            # Clear session state
            st.session_state.authenticated = False
            if "user" in st.session_state:
                del st.session_state.user
            
            # Redirect to home page
            st.rerun()

def display_user_info():
    """
    Display user information if authenticated
    """
    if st.session_state.get("authenticated", False) and "user" in st.session_state:
        user = st.session_state.user
        
        st.write(f"Logged in as: {user.get('name', 'User')}")
        st.write(f"Email: {user.get('email', 'N/A')}")

def check_callback():
    """
    Check for Auth0 callback parameters in URL
    """
    # Get query parameters
    query_params = st.experimental_get_query_params()
    
    if "code" in query_params and "state" in query_params:
        code = query_params["code"][0]
        state = query_params["state"][0]
        
        # Validate callback
        success, message = validate_callback(code, state)
        
        if success:
            # Clear query parameters
            st.experimental_set_query_params()
            st.success(message)
            st.rerun()
        else:
            st.error(message)

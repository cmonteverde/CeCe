"""
API Status Checker for Climate Copilot

This module provides functions to test the status of various APIs
used by the Climate Copilot application.
"""

import os
import requests
import json
import time
import streamlit as st

def check_openai_api_status(display_message=True):
    """
    Check the status of the OpenAI API and display appropriate messages
    
    Args:
        display_message: Whether to display a message in Streamlit
        
    Returns:
        Tuple of (status_code, is_working)
    """
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            if display_message:
                st.warning("⚠️ Using Guided Responses", icon="⚠️")
            return (None, False)
        
        # Try a minimal API call to check status
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "user", "content": "test"}
            ],
            "max_tokens": 5
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        
        # Check for quota issues
        if response.status_code == 429 and "insufficient_quota" in response.text:
            if display_message:
                st.warning("⚠️ Using Guided Responses", icon="⚠️")
            return (429, False)
        elif response.status_code != 200:
            if display_message:
                st.warning("⚠️ Using Guided Responses", icon="⚠️")
            return (response.status_code, False)
        else:
            if display_message:
                st.success("✅ AI Enhanced Responses", icon="✅")
            return (200, True)
    except Exception as e:
        # Catch all exceptions to prevent crashes
        if display_message:
            st.warning("⚠️ Using Guided Responses", icon="⚠️")
        print(f"API status check error: {str(e)}")
        return (None, False)

if __name__ == "__main__":
    # Test the API status
    print("Testing OpenAI API status...")
    status_code, is_working = check_openai_api_status(display_message=False)
    
    if is_working:
        print(f"✅ OpenAI API is working properly (Status: {status_code})")
    else:
        print(f"❌ OpenAI API is not working (Status: {status_code})")
        
        # Check if it's a quota issue
        if status_code == 429:
            print("The API key has insufficient quota/credits. You may need to:")
            print("1. Add billing information to your OpenAI account")
            print("2. Use a different API key with available credits")
            print("3. Wait for your quota to reset if you're on a free tier")
        elif status_code is None:
            print("Could not connect to the API. This might be due to:")
            print("1. Network connectivity issues")
            print("2. Invalid API key format")
        else:
            print(f"API returned status code {status_code}")
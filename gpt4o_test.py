"""
A direct, simple implementation based on the OpenAI Python GPT-4o Quickstart example
from Replit to verify OpenAI API connectivity.
"""

import os
import requests
import json

def test_openai_api():
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        return False
    
    # Define the API endpoint (direct REST API approach)
    url = "https://api.openai.com/v1/chat/completions"
    
    # Define headers with API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Define the payload (similar to the GPT-4o Quickstart)
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello world"}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    try:
        # Make the request
        print("Sending request to OpenAI API...")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Extract the generated text
            response_json = response.json()
            generated_text = response_json["choices"][0]["message"]["content"]
            
            print(f"✅ SUCCESS: API connection working")
            print(f"Response: {generated_text}")
            return True
        else:
            print(f"❌ ERROR: API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ ERROR: Exception during API request: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing OpenAI API using direct REST API approach")
    test_openai_api()
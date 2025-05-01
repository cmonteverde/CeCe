"""
Test OpenAI API Connection

This script tests the connection to the OpenAI API using the API key
provided in the environment variables.
"""

import os
import sys
from openai import OpenAI

def test_openai_connection():
    """Test the connection to OpenAI API"""
    
    # Get the API key from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        print("❌ ERROR: OPENAI_API_KEY environment variable is not set.")
        print("Please make sure you've added your OpenAI API key in the Secrets tool.")
        return False
    
    try:
        # Initialize the OpenAI client
        client = OpenAI(api_key=openai_api_key)
        
        # Make a simple API request
        response = client.chat.completions.create(
            model="gpt-4o",  # The newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, this is a test message. Please respond with a short greeting."}
            ],
            max_tokens=50,
        )
        
        # Get the response content
        response_content = response.choices[0].message.content
        
        print("✅ OpenAI API connection successful!")
        print(f"Response: {response_content}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to OpenAI API: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing OpenAI API connection...")
    test_openai_connection()
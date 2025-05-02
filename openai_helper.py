"""
OpenAI Helper Module for Climate Copilot

This module provides functions to interact with the OpenAI API,
manage API call retries, and handle errors gracefully.
"""

import os
import time
import sys
from openai import OpenAI, APIError, RateLimitError, APIConnectionError, AuthenticationError

# Maximum number of retries for API calls
MAX_RETRIES = 3
# Base delay for exponential backoff in seconds
BASE_DELAY = 1

def get_openai_client():
    """
    Get an initialized OpenAI client using API key from environment
    
    Returns:
        OpenAI client or None if API key is missing
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    
    return OpenAI(api_key=api_key)

def chat_completion(messages, model="gpt-4o", max_tokens=500, temperature=0.7, 
                   retries=MAX_RETRIES, system_message=None):
    """
    Get a completion from OpenAI Chat API with retry logic
    
    Args:
        messages: List of message objects
        model: Model to use (default: gpt-4o)
        max_tokens: Maximum tokens to generate
        temperature: Temperature for generation
        retries: Number of retries (default: MAX_RETRIES)
        system_message: Optional system message to prepend
    
    Returns:
        Response text string or None if failed
    """
    print(f"DEBUG: chat_completion called with model={model}, max_tokens={max_tokens}")
    client = get_openai_client()
    if not client:
        print("DEBUG: OpenAI API key not found in chat_completion. Cannot make API request.")
        return None
    else:
        print("DEBUG: OpenAI client initialized successfully")
    
    # Add system message if provided
    if system_message and not any(msg.get("role") == "system" for msg in messages):
        print("DEBUG: Adding system message to messages array")
        messages = [{"role": "system", "content": system_message}] + messages
    
    # Direct API approach as a fallback option if we encounter issues with the client
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }
    
    current_retry = 0
    while current_retry <= retries:
        print(f"DEBUG: Attempt {current_retry + 1} of {retries + 1}")
        try:
            # Make the API request using the client
            print("DEBUG: About to call client.chat.completions.create")
            # Import for timeout handling
            import threading
            import queue
            
            response_queue = queue.Queue()
            
            def api_call():
                try:
                    resp = client.chat.completions.create(
                        model=model,  # The newest OpenAI model is "gpt-4o" which was released May 13, 2024
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        timeout=15  # 15 second timeout
                    )
                    response_queue.put(resp)
                except Exception as e:
                    response_queue.put(e)
            
            # Create and start thread
            thread = threading.Thread(target=api_call)
            thread.daemon = True
            thread.start()
            
            # Wait for the thread to complete or timeout
            thread.join(30)  # 30 second total timeout
            
            if thread.is_alive():
                print("DEBUG: API call timeout - taking too long")
                raise Exception("OpenAI API call timed out after 30 seconds")
            
            # Get response from queue
            response_or_error = response_queue.get(block=False)
            
            # Check if we got an error
            if isinstance(response_or_error, Exception):
                raise response_or_error
                
            # Otherwise, we got a response
            response = response_or_error
            print("DEBUG: Successfully got response from OpenAI API")
            return response.choices[0].message.content
            
        except RateLimitError as e:
            delay = BASE_DELAY * (2 ** current_retry)
            print(f"DEBUG: Rate limit exceeded. Retrying in {delay} seconds... Error: {str(e)}")
            time.sleep(delay)
        
        except APIConnectionError as e:
            # Connection error - try direct API approach
            print(f"DEBUG: Connection error with client: {str(e)}. Trying direct API approach...")
            
            try:
                import requests
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                
                if response.status_code == 200:
                    response_json = response.json()
                    return response_json["choices"][0]["message"]["content"]
                elif response.status_code == 429 and "insufficient_quota" in response.text:
                    print("OpenAI API quota exceeded. The API key has insufficient credits.")
                    return "I'm sorry, but the OpenAI API quota has been exceeded. Please check your API key's billing status or try again later."
                else:
                    print(f"Direct API request failed with status code {response.status_code}: {response.text}")
            except Exception as direct_api_error:
                print(f"Direct API approach failed: {str(direct_api_error)}")
            
            # Continue with retry logic
            if current_retry < retries:
                delay = BASE_DELAY * (2 ** current_retry)
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
        
        except AuthenticationError as e:
            # Authentication error - no point in retrying
            print(f"Authentication error: {str(e)}. Check your API key.")
            return "I'm sorry, but there was an authentication error with the OpenAI API. Please check that your API key is valid."
            
        except APIError as e:
            if getattr(e, 'status_code', None) == 429:
                # Try to check if it's a quota issue
                error_message = str(e)
                if "insufficient_quota" in error_message:
                    print("OpenAI API quota exceeded.")
                    return "I'm sorry, but the OpenAI API quota has been exceeded. Please check your API key's billing status or try again later."
                
                # Regular rate limit - retry with backoff
                delay = BASE_DELAY * (2 ** current_retry)
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                # Other API error
                print(f"API error: {str(e)}.")
                if current_retry < retries:
                    delay = BASE_DELAY * (2 ** current_retry)
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    return "I'm sorry, but there was an error communicating with the OpenAI API. Please try again later."
                    
        except Exception as e:
            # Other unexpected error
            print(f"Unexpected error: {str(e)}.")
            if current_retry < retries:
                delay = BASE_DELAY * (2 ** current_retry)
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                return "I'm sorry, but there was an unexpected error when trying to generate a response. Please try again later."
                
        current_retry += 1
    
    # If we've exhausted all retries
    print("Failed to get response after maximum retries.")
    return "I'm sorry, but I couldn't connect to the OpenAI API after multiple attempts. Please try again later."

def generate_climate_response(query, chat_history=None):
    """
    Generate a climate-specific response using OpenAI
    
    Args:
        query: User's query text
        chat_history: Optional chat history for context
    
    Returns:
        Response text or fallback response if API fails
    """
    print(f"DEBUG: generate_climate_response called with query: {query}")
    print(f"DEBUG: chat_history length: {len(chat_history) if chat_history else 0}")
    
    # First check if we have an API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("DEBUG: OpenAI API key not found")
        return (
            "I notice that the OpenAI API key is not set up. To enable my AI-powered responses, "
            "please add your OpenAI API key in the settings. In the meantime, I'll do my best to help "
            "with climate data visualization and analysis using my built-in knowledge."
        )
    else:
        print(f"DEBUG: API key found (starts with: {api_key[:4]}...)")
    
    # System message for CeCe's identity
    system_message = """
    You are CeCe (Climate Copilot), an AI assistant specializing in climate and weather data analysis.
    You help users with climate data visualization, scientific calculations, and understanding weather patterns.
    Your responses should be friendly, helpful, and focused on climate science.
    Include specific details about what data sources you would check and what visualizations you could generate.
    """
    
    # Create messages array
    messages = []
    
    # Add chat history for context if provided
    if chat_history:
        # Add up to 4 previous exchanges for context
        for msg in chat_history[-8:]:  # Limit to prevent token overload
            messages.append(msg)
    
    # Add user query if not already included in history
    if not chat_history or chat_history[-1]["role"] != "user":
        messages.append({"role": "user", "content": query})
    
    print(f"DEBUG: Final messages array has {len(messages)} messages")
    
    try:
        print("DEBUG: About to call chat_completion")
        # Get response from OpenAI
        response = chat_completion(
            messages=messages,
            system_message=system_message,
            max_tokens=500,
            temperature=0.7
        )
        
        # Return the response if successful
        if response:
            print("DEBUG: Got successful response from chat_completion")
            return response
        else:
            print("DEBUG: chat_completion returned None")
    except Exception as e:
        print(f"DEBUG: Error in generate_climate_response: {str(e)}")
        # Continue to fallback logic below
    
    # Fallback logic - use predefined responses
    print("Using fallback response system")
    climate_responses = {
        "temperature": "Temperature is a key climate variable. I can help you analyze temperature trends, calculate anomalies, and visualize temperature data. You can use the preset buttons above to explore temperature-related features.",
        "precipitation": "Precipitation includes rain, snow, and other forms of water falling from the sky. I can help you analyze precipitation patterns and create visualization maps. Try the 'Generate a precipitation map' button above!",
        "climate change": "Climate change refers to significant changes in global temperature, precipitation, wind patterns, and other measures of climate that occur over several decades or longer. I can help you analyze climate data to understand these changes.",
        "weather": "Weather refers to day-to-day conditions, while climate refers to the average weather patterns in an area over a longer period. I can help you analyze both weather data and climate trends.",
        "forecast": "While I don't provide real-time weather forecasts, I can help you analyze historical climate data and identify patterns that might inform future conditions.",
        "hello": "Hello! I'm CeCe, your Climate Copilot. I'm here to help you analyze and visualize climate data. How can I assist you today?",
        "help": "I can help you with climate data analysis, visualization, and scientific calculations. Try one of the preset buttons above to get started, or ask me a specific question about climate data.",
        "rain": "I can help you analyze precipitation patterns, but I don't have access to real-time weather forecasts. For the most accurate rain forecasts, I recommend checking a dedicated weather service. Would you like to explore historical precipitation data for your area instead?"
    }
    
    # Check if the query contains any of our predefined topics
    query_lower = query.lower()
    for topic, response in climate_responses.items():
        if topic in query_lower:
            return response
    
    # Default fallback response
    return "I'm currently using fallback mode due to API limitations. I can still help you analyze climate data - try clicking one of the preset buttons above, or ask me about temperature trends, precipitation patterns, or climate change impacts!"
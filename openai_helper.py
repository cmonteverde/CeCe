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
    client = get_openai_client()
    if not client:
        print("OpenAI API key not found. Cannot make API request.")
        return None
    
    # Add system message if provided
    if system_message and not any(msg.get("role") == "system" for msg in messages):
        messages = [{"role": "system", "content": system_message}] + messages
    
    current_retry = 0
    while current_retry <= retries:
        try:
            # Make the API request
            response = client.chat.completions.create(
                model=model,  # The newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
            
        except RateLimitError as e:
            delay = BASE_DELAY * (2 ** current_retry)
            print(f"Rate limit exceeded. Retrying in {delay} seconds...")
            time.sleep(delay)
        
        except APIConnectionError as e:
            # Connection error - may be temporary
            delay = BASE_DELAY * (2 ** current_retry)
            print(f"Connection error: {str(e)}. Retrying in {delay} seconds...")
            time.sleep(delay)
        
        except AuthenticationError as e:
            # Authentication error - no point in retrying
            print(f"Authentication error: {str(e)}. Check your API key.")
            return None
            
        except APIError as e:
            if e.status_code == 429:
                # Rate limit - retry with backoff
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
                    return None
                    
        except Exception as e:
            # Other unexpected error
            print(f"Unexpected error: {str(e)}.")
            if current_retry < retries:
                delay = BASE_DELAY * (2 ** current_retry)
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                return None
                
        current_retry += 1
    
    # If we've exhausted all retries
    print("Failed to get response after maximum retries.")
    return None

def generate_climate_response(query, chat_history=None):
    """
    Generate a climate-specific response using OpenAI
    
    Args:
        query: User's query text
        chat_history: Optional chat history for context
    
    Returns:
        Response text or fallback response if API fails
    """
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
    
    # Get response from OpenAI
    response = chat_completion(
        messages=messages,
        system_message=system_message,
        max_tokens=500,
        temperature=0.7
    )
    
    # Return the response or a fallback
    if response:
        return response
    else:
        # Fallback logic - use predefined responses
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
        return "I'm CeCe, your Climate Copilot. I can help you analyze climate data, create visualizations, and perform scientific calculations. Try one of the preset buttons above, or ask me a specific question about climate or weather data!"
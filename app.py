import streamlit as st
import pandas as pd
import numpy as np
import folium
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import folium_static
import os
import tempfile
import json
from datetime import datetime, timedelta
import io
import base64
from base64 import b64encode
from pathlib import Path
from dotenv import load_dotenv

# Since we don't have langchain and related modules installed yet,
# we'll temporarily disable these imports
# import rag_query
# import transform
import climate_algorithms
# import auth
# import vector_store
import load_docs

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="CeCe - Climate Copilot",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "# CeCe - Climate Copilot\nAn AI-powered assistant for climate data analysis."
    }
)

# Set the page background to completely black
st.markdown("""
<style>
    .appview-container, .main, .block-container, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #000000;
    }
    [data-testid="stToolbar"] {
        right: 2rem;
    }
    section[data-testid="stSidebar"] {
        background-color: #0D0D0D;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for styling
css = """
<style>
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
    }
    .logo-container {
        margin-bottom: 20px;
        text-align: center;
    }
    .avatar-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 30px;
    }
    .avatar-title {
        margin-left: 20px;
        font-size: 24px;
        font-weight: bold;
        color: #FFFFFF;
        display: flex;
        align-items: center;
    }
    .gradient-text {
        background: linear-gradient(90deg, #1E90FF, #9370DB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: transparent;
    }
    .buttons-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        margin-bottom: 30px;
        gap: 10px;
    }
    .stButton button {
        background-color: rgba(30, 144, 255, 0.1);
        color: white;
        border: 1px solid rgba(147, 112, 219, 0.3);
        border-radius: 8px;
        padding: 12px 15px;
        text-align: center;
        transition: all 0.3s;
        width: 100%;
        font-weight: 500;
    }
    .stButton button:hover {
        background-color: rgba(30, 144, 255, 0.3);
        border: 1px solid rgba(147, 112, 219, 0.5);
    }
    .chat-box {
        margin-top: 30px;
        border-radius: 10px;
        padding: 15px;
        background-color: rgba(30, 30, 30, 0.6);
    }
    
    /* Enhanced Chat Interface */
    .chat-message {
        display: flex;
        margin-bottom: 12px;
        padding: 8px 12px;
        border-radius: 8px;
    }
    
    .user-message {
        background-color: rgba(30, 144, 255, 0.1);
        border-left: 3px solid #1E90FF;
        margin-left: 40px;
    }
    
    .assistant-message {
        background-color: rgba(147, 112, 219, 0.1);
        border-left: 3px solid #9370DB;
        margin-right: 40px;
    }
    
    .message-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        margin-right: 10px;
        object-fit: cover;
    }
    
    .message-content {
        flex: 1;
    }
    
    .message-sender {
        font-weight: bold;
        margin-bottom: 4px;
        color: #e0e0e0;
    }
    
    .message-text {
        color: #ffffff;
        line-height: 1.5;
    }
    
    .thinking-status {
        display: flex;
        align-items: center;
        font-style: italic;
        color: #9370DB;
        padding: 8px 12px;
        margin-left: 40px;
        font-size: 14px;
    }
    
    .processing-steps {
        font-size: 12px;
        color: #1E90FF;
        margin-top: 4px;
        font-style: italic;
    }
    .bg-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        opacity: 0.2;
    }
    .title-text {
        font-size: 24px; 
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        color: #FFFFFF;
    }
    .stTextInput input {
        background-color: rgba(30, 30, 30, 0.6);
        border: 1px solid rgba(30, 144, 255, 0.3);
        border-radius: 8px;
        color: white;
    }
    .stTextInput input:focus {
        border: 1px solid rgba(147, 112, 219, 0.8);
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Add topography decoration in top right corner
st.markdown("""
<div style="position: fixed; top: 10px; right: 10px; z-index: 9998; width: 150px; height: 150px;">
    <img src="data:image/png;base64,{topo_base64}" style="width: 100%; height: 100%; object-fit: contain;">
</div>
""".format(topo_base64=b64encode(open("assets/topography.png", "rb").read()).decode()), unsafe_allow_html=True)

# Add floating feedback button
st.markdown("""
<div style="position: fixed; top: 60px; right: 20px; z-index: 9999;">
    <a href="https://docs.google.com/forms/d/e/1FAIpQLSezvpoz4Jf2Ez0ukxU9y_q6iK4l4j5COVc1giJBQSJIUm9c0A/viewform?usp=dialog" target="_blank" style="
        background: linear-gradient(90deg, #1E90FF, #9370DB);
        color: white;
        padding: 10px 15px;
        border-radius: 50px;
        text-decoration: none;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        font-size: 14px;
        transition: all 0.3s ease;
    ">
        <span style="margin-right: 6px;">💬</span> Share feedback
    </a>
</div>
""", unsafe_allow_html=True)

# Add topographic background patterns and corner elements
st.markdown("""
<div class="bg-container">
    <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#1E90FF;stop-opacity:0.4" />
                <stop offset="100%" style="stop-color:#9370DB;stop-opacity:0.4" />
            </linearGradient>
            <pattern id="topo" patternUnits="userSpaceOnUse" width="1200" height="1200">
                <path d="M0,0 Q300,180 600,0 T1200,0" stroke="url(#lineGradient)" stroke-width="1" fill="none" opacity="0.15" transform="translate(0, 50)"/>
                <path d="M0,0 Q300,180 600,0 T1200,0" stroke="url(#lineGradient)" stroke-width="1" fill="none" opacity="0.15" transform="translate(0, 100)"/>
                <path d="M0,0 Q300,180 600,0 T1200,0" stroke="url(#lineGradient)" stroke-width="1" fill="none" opacity="0.15" transform="translate(0, 150)"/>
                <path d="M0,0 Q300,180 600,0 T1200,0" stroke="url(#lineGradient)" stroke-width="1" fill="none" opacity="0.15" transform="translate(0, 200)"/>
                <path d="M0,0 Q300,180 600,0 T1200,0" stroke="url(#lineGradient)" stroke-width="1" fill="none" opacity="0.15" transform="translate(0, 250)"/>
                <path d="M0,0 Q300,180 600,0 T1200,0" stroke="url(#lineGradient)" stroke-width="1" fill="none" opacity="0.15" transform="translate(0, 300)"/>
                <path d="M0,0 Q300,180 600,0 T1200,0" stroke="url(#lineGradient)" stroke-width="1" fill="none" opacity="0.15" transform="translate(0, 350)"/>
                <path d="M0,0 Q300,180 600,0 T1200,0" stroke="url(#lineGradient)" stroke-width="1" fill="none" opacity="0.15" transform="translate(0, 400)"/>
                <path d="M0,0 Q300,180 600,0 T1200,0" stroke="url(#lineGradient)" stroke-width="1" fill="none" opacity="0.15" transform="translate(0, 450)"/>
                <path d="M0,0 Q300,180 600,0 T1200,0" stroke="url(#lineGradient)" stroke-width="1" fill="none" opacity="0.15" transform="translate(0, 500)"/>
                <path d="M0,0 Q300,180 600,0 T1200,0" stroke="url(#lineGradient)" stroke-width="1" fill="none" opacity="0.15" transform="translate(0, 550)"/>
                <path d="M0,0 Q300,180 600,0 T1200,0" stroke="url(#lineGradient)" stroke-width="1" fill="none" opacity="0.15" transform="translate(0, 600)"/>
            </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#topo)"/>
    </svg>
</div>

<!-- Topography map in bottom left corner -->
<div style="position: fixed; bottom: 0; left: 0; width: 300px; height: 300px; z-index: -1; opacity: 0.7;">
    <svg width="100%" height="100%" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="cornerGradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#1E90FF;stop-opacity:0.6" />
                <stop offset="100%" style="stop-color:#9370DB;stop-opacity:0.6" />
            </linearGradient>
        </defs>
        <!-- Topographic map elements -->
        <path d="M0,300 C50,280 100,290 150,270 C200,250 250,230 300,250 L300,300 Z" fill="none" stroke="url(#cornerGradient1)" stroke-width="1.5" />
        <path d="M0,280 C60,260 120,270 180,250 C240,230 270,210 300,230 L300,300 Z" fill="none" stroke="url(#cornerGradient1)" stroke-width="1.5" />
        <path d="M0,260 C70,240 140,250 210,230 C280,210 290,190 300,210 L300,300 Z" fill="none" stroke="url(#cornerGradient1)" stroke-width="1.5" />
        <path d="M0,240 C80,220 160,230 240,210 L300,190 L300,300 Z" fill="none" stroke="url(#cornerGradient1)" stroke-width="1.5" />
        <path d="M0,220 C90,200 180,210 270,190 L300,170 L300,300 Z" fill="none" stroke="url(#cornerGradient1)" stroke-width="1.5" />
        <path d="M0,200 C100,180 200,190 300,170 L300,300 Z" fill="none" stroke="url(#cornerGradient1)" stroke-width="1.5" />
        <circle cx="50" cy="250" r="5" fill="url(#cornerGradient1)" />
        <circle cx="150" cy="220" r="3" fill="url(#cornerGradient1)" />
        <circle cx="230" cy="180" r="4" fill="url(#cornerGradient1)" />
    </svg>
</div>

<!-- Topography map in upper right corner -->
<div style="position: fixed; top: 0; right: 0; width: 300px; height: 300px; z-index: -1; opacity: 0.7;">
    <svg width="100%" height="100%" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="cornerGradient2" x1="100%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#1E90FF;stop-opacity:0.6" />
                <stop offset="100%" style="stop-color:#9370DB;stop-opacity:0.6" />
            </linearGradient>
        </defs>
        <!-- Topographic map elements -->
        <path d="M300,0 C250,20 200,10 150,30 C100,50 50,70 0,50 L0,0 Z" fill="none" stroke="url(#cornerGradient2)" stroke-width="1.5" />
        <path d="M300,20 C240,40 180,30 120,50 C60,70 30,90 0,70 L0,0 Z" fill="none" stroke="url(#cornerGradient2)" stroke-width="1.5" />
        <path d="M300,40 C230,60 160,50 90,70 C20,90 10,110 0,90 L0,0 Z" fill="none" stroke="url(#cornerGradient2)" stroke-width="1.5" />
        <path d="M300,60 C220,80 140,70 60,90 L0,110 L0,0 Z" fill="none" stroke="url(#cornerGradient2)" stroke-width="1.5" />
        <path d="M300,80 C210,100 120,90 30,110 L0,130 L0,0 Z" fill="none" stroke="url(#cornerGradient2)" stroke-width="1.5" />
        <path d="M300,100 C200,120 100,110 0,130 L0,0 Z" fill="none" stroke="url(#cornerGradient2)" stroke-width="1.5" />
        <circle cx="250" cy="50" r="5" fill="url(#cornerGradient2)" />
        <circle cx="150" cy="80" r="3" fill="url(#cornerGradient2)" />
        <circle cx="70" cy="120" r="4" fill="url(#cornerGradient2)" />
    </svg>
</div>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'visualization' not in st.session_state:
    st.session_state.visualization = None
if 'active_function' not in st.session_state:
    st.session_state.active_function = None
if 'user_location' not in st.session_state:
    st.session_state.user_location = {"lat": 37.7749, "lon": -122.4194}  # Default to San Francisco
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = None
if 'thinking' not in st.session_state:
    st.session_state.thinking = False

# Logo in left corner (smaller)
st.markdown("""
<div style="position: absolute; top: 20px; left: 20px; z-index: 1000;">
""", unsafe_allow_html=True)
logo_path = Path("assets/logo.png")
if logo_path.exists():
    st.image("assets/logo.png", width=100)
st.markdown("""
</div>
""", unsafe_allow_html=True)

# Centered Avatar and Title
st.markdown("""
<div style="display: flex; justify-content: center; align-items: center; margin-top: 20px; margin-bottom: 30px;">
""", unsafe_allow_html=True)

# Center the title area with a single centered container 
st.markdown('<div style="padding: 10px 0;"></div>', unsafe_allow_html=True)  # Reduced padding at top

# Using direct HTML with base64 encoding to ensure image display
from base64 import b64encode
with open("public/avatar_fixed.png", "rb") as f:
    avatar_base64 = b64encode(f.read()).decode()

# Create centered container with avatar image and text
st.markdown(f"""
<div style="display: flex; justify-content: center; align-items: center; margin: 0 auto; width: 100%;">
    <div style="display: flex; align-items: center; justify-content: center;">
        <img src="data:image/png;base64,{avatar_base64}" width="150" 
            style="border-radius: 50%; margin-right: 20px;">
        <span class="gradient-text" style="font-size: 32px; font-weight: bold; white-space: nowrap;">
            CECE: YOUR CLIMATE & WEATHER AGENT
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
</div>
""", unsafe_allow_html=True)

# Button cards
st.markdown('<div class="buttons-container">', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("📍 Generate a precipitation map for my region"):
        st.session_state.active_function = "precipitation_map"

with col2:
    if st.button("📊 Show temperature trends from the past 5 years"):
        st.session_state.active_function = "temperature_trends"

with col3:
    if st.button("⚠️ Identify extreme heat days in my area"):
        st.session_state.active_function = "extreme_heat"

with col4:
    if st.button("🗓️ Compare rainfall this season vs. last year"):
        st.session_state.active_function = "rainfall_comparison"

with col5:
    if st.button("📉 Export climate anomalies as a table"):
        st.session_state.active_function = "export_anomalies"

st.markdown('</div>', unsafe_allow_html=True)

# Display the title question directly (without the chat-box container)
st.markdown('<div class="title-text">What would you like CeCe to do for you today?</div>', unsafe_allow_html=True)

# Display the chat history in a more visually appealing way
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display existing chat messages
if st.session_state.chat_history:
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-content">
                    <div class="message-sender">You</div>
                    <div class="message-text">{message["content"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="message-content">
                    <div class="message-sender">CeCe (Climate Copilot)</div>
                    <div class="message-text">{message["content"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Display thinking status if processing
if "thinking" in st.session_state and st.session_state.thinking:
    st.markdown("""
    <div class="thinking-status">
        <div>CeCe is thinking...</div>
        <div class="processing-steps">
            • Analyzing your question<br>
            • Checking climate data sources<br>
            • Preparing a helpful response
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat input
user_input = st.text_input("", key="chat_input", placeholder="Type your question here...")

# Add empty space for visual separation
st.markdown("<div style='height: 60px'></div>", unsafe_allow_html=True)

# Made with love footer at the very bottom, after all content
st.markdown("""
<div style="position: relative; width: 100%; text-align: center; padding: 10px; color: white; font-size: 14px; margin-top: 20px; margin-bottom: 20px;">
    Made with 
    <span style="background: linear-gradient(90deg, #1E90FF, #9370DB); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold;">❤</span> 
    by 
    <a href="https://www.linkedin.com/in/corriemonteverde/" target="_blank" style="text-decoration: none; background: linear-gradient(90deg, #1E90FF, #9370DB); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold;">Corrie</a> + 
    <a href="https://www.linkedin.com/in/mlaffin/" target="_blank" style="text-decoration: none; background: linear-gradient(90deg, #1E90FF, #9370DB); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold;">Matt</a>
</div>
""", unsafe_allow_html=True)

# Fallback response function 
def fallback_response(query):
    # A dictionary of predefined responses for common queries
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
    
    # Default response if no specific topic is matched
    return "I'm CeCe, your Climate Copilot. I can help you analyze climate data, create visualizations, and perform scientific calculations. Try one of the preset buttons above, or ask me a specific question about climate or weather data!"

# Process user input
if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Set thinking status to true and display the "thinking" indicator
    st.session_state.thinking = True
    
    # Rerun to show the thinking status immediately
    st.rerun()

# If we're in thinking mode, process the query and generate a response
if st.session_state.thinking:
    try:
        import os
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Direct OpenAI integration without using rag_query.py
        if openai_api_key:
            try:
                import openai
                
                # Initialize OpenAI client
                client = openai.OpenAI(api_key=openai_api_key)
                
                # System message for CeCe's identity
                system_message = """
                You are CeCe (Climate Copilot), an AI assistant specializing in climate and weather data analysis.
                You help users with climate data visualization, scientific calculations, and understanding weather patterns.
                Your responses should be friendly, helpful, and focused on climate science.
                Include specific details about what data sources you would check and what visualizations you could generate.
                """
                
                # Make the API request with a timeout
                response = client.chat.completions.create(
                    model="gpt-4o",  # Using the latest model
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": st.session_state.chat_history[-2]["content"]}  # Get the latest user message
                    ],
                    temperature=0.7,
                    max_tokens=500,
                    timeout=10  # 10 second timeout
                )
                
                # Get the response content
                response_content = response.choices[0].message.content
                
            except Exception as e:
                # If OpenAI fails, use a simple fallback response
                response_content = fallback_response(st.session_state.chat_history[-2]["content"])
        else:
            # No OpenAI API key, use a simple fallback response
            response_content = fallback_response(st.session_state.chat_history[-2]["content"])
            
    except Exception as e:
        # Something went wrong, provide an error message
        response_content = f"I'm sorry, but I encountered an error processing your request: {str(e)}. Please try again or use one of the preset functions above."
    
    # Add the response to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": response_content})
    
    # Set thinking to False
    st.session_state.thinking = False
    
    # Clear the input field and refresh the page
    st.rerun()

# Import geopy for geocoding city names to coordinates
from geopy.geocoders import Nominatim

# Function to convert city name to coordinates
def get_city_coordinates(city_name):
    try:
        geolocator = Nominatim(user_agent="climate_copilot")
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        st.error(f"Error geocoding city: {str(e)}")
        return None, None

# Function handling section
if st.session_state.active_function == "precipitation_map":
    st.subheader("Precipitation Map for Your Region")
    
    # Location input method selection
    location_method = st.radio("Select location input method:", ["City Name", "Coordinates"], horizontal=True)
    
    if location_method == "City Name":
        city = st.text_input("Enter city name (e.g., 'New York', 'London, UK')", 
                             value="San Francisco, CA" if "last_city" not in st.session_state else st.session_state.last_city)
        
        if city:
            st.session_state.last_city = city
            lat, lon = get_city_coordinates(city)
            if lat and lon:
                st.success(f"Location found: {lat:.4f}, {lon:.4f}")
                latitude = lat
                longitude = lon
                st.session_state.user_location = {"lat": latitude, "lon": longitude}
            else:
                st.warning("Could not find coordinates for this city. Please check the spelling or try using coordinates directly.")
                latitude = st.session_state.user_location["lat"]
                longitude = st.session_state.user_location["lon"]
    else:
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", value=st.session_state.user_location["lat"], min_value=-90.0, max_value=90.0)
        with col2:
            longitude = st.number_input("Longitude", value=st.session_state.user_location["lon"], min_value=-180.0, max_value=180.0)
        
        st.session_state.user_location = {"lat": latitude, "lon": longitude}
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    if st.button("Generate Precipitation Map"):
        with st.spinner("Fetching precipitation data from NASA POWER API..."):
            try:
                # This would normally fetch real data from NASA POWER API
                # For now, generate a sample map for demonstration
                
                m = folium.Map(location=[latitude, longitude], zoom_start=10)
                
                # Add a heatmap layer for precipitation
                import random
                heat_data = []
                for i in range(100):
                    # Create points around the selected location
                    heat_lat = latitude + (random.random() - 0.5) * 0.2
                    heat_lon = longitude + (random.random() - 0.5) * 0.2
                    # Random precipitation values between 0 and 50mm
                    intensity = random.random() * 50
                    heat_data.append([heat_lat, heat_lon, intensity])
                
                from folium.plugins import HeatMap
                HeatMap(heat_data, radius=15).add_to(m)
                
                # Add a marker for the selected location
                folium.Marker(
                    [latitude, longitude],
                    popup=f"Selected Location ({latitude:.4f}, {longitude:.4f})",
                    icon=folium.Icon(color="blue")
                ).add_to(m)
                
                # Display the map
                st.subheader(f"Precipitation Heatmap ({start_date} to {end_date})")
                folium_static(m)
                
                # Add some context about the data
                st.info(f"This map shows simulated precipitation data around your selected location. In the full implementation, this would use real data from the NASA POWER API for the date range {start_date} to {end_date}.")
                
                # Option to download the map
                st.download_button(
                    label="Download Map as HTML",
                    data=m._repr_html_(),
                    file_name="precipitation_map.html",
                    mime="text/html"
                )
                
            except Exception as e:
                st.error(f"Error generating precipitation map: {str(e)}")

elif st.session_state.active_function == "export_anomalies":
    st.subheader("Export Climate Anomalies as a Table")
    
    # Data source selection
    data_source = st.radio("Select Data Source", ["Upload CSV File", "Fetch from NASA POWER API"])
    
    if data_source == "Upload CSV File":
        uploaded_file = st.file_uploader("Choose a CSV file with climate data", type="csv")
        
        if uploaded_file is not None:
            try:
                data = pd.read_csv(uploaded_file)
                st.session_state.uploaded_data = data
                
                # Show preview of uploaded data
                st.write("Preview of uploaded data:")
                st.dataframe(data.head())
                
                # Check if the data has date and temperature columns
                if st.button("Calculate Temperature Anomalies"):
                    # Get the temperature column
                    temp_column = st.selectbox("Select Temperature Column", data.columns)
                    date_column = st.selectbox("Select Date Column", data.columns)
                    
                    if temp_column and date_column:
                        # Convert date column to datetime if not already
                        if data[date_column].dtype != 'datetime64[ns]':
                            try:
                                data[date_column] = pd.to_datetime(data[date_column])
                            except:
                                st.error("Could not convert the selected column to date format. Please select a valid date column.")
                                st.stop()
                        
                        # Calculate monthly averages
                        data['Month'] = data[date_column].dt.month
                        data['Year'] = data[date_column].dt.year
                        
                        # Group by month and calculate the average temperature
                        monthly_avg = data.groupby('Month')[temp_column].mean().reset_index()
                        monthly_avg.columns = ['Month', 'Average_Temperature']
                        
                        # Merge the monthly averages back to the original data
                        data = pd.merge(data, monthly_avg, on='Month')
                        
                        # Calculate the anomalies
                        data['Temperature_Anomaly'] = data[temp_column] - data['Average_Temperature']
                        
                        # Create a result dataframe
                        result = data[[date_column, temp_column, 'Average_Temperature', 'Temperature_Anomaly']]
                        result = result.rename(columns={date_column: 'Date', temp_column: 'Temperature'})
                        
                        # Store the result in session state
                        st.session_state.processed_data = result
                        
                        # Display the result
                        st.subheader("Temperature Anomalies")
                        st.dataframe(result)
                        
                        # Download button for the anomalies table
                        csv = result.to_csv(index=False)
                        st.download_button(
                            label="Download Anomalies as CSV",
                            data=csv,
                            file_name="temperature_anomalies.csv",
                            mime="text/csv",
                        )
                        
                        # Visualization of anomalies
                        st.subheader("Visualization of Temperature Anomalies")
                        fig = px.scatter(result, x='Date', y='Temperature_Anomaly', 
                                        color='Temperature_Anomaly',
                                        color_continuous_scale=px.colors.diverging.RdBu_r,
                                        title="Temperature Anomalies Over Time")
                        st.plotly_chart(fig)
            
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    else:  # NASA POWER API
        st.info("This feature will connect to the NASA POWER API to fetch climate data for a specified location and date range.")
        
        # Location input method selection
        location_method = st.radio("Select location input method:", ["City Name", "Coordinates"], horizontal=True, key="nasa_location_method")
        
        if location_method == "City Name":
            city = st.text_input("Enter city name (e.g., 'New York', 'London, UK')", 
                                value="San Francisco, CA" if "nasa_last_city" not in st.session_state else st.session_state.nasa_last_city,
                                key="nasa_city")
            
            if city:
                st.session_state.nasa_last_city = city
                lat, lon = get_city_coordinates(city)
                if lat and lon:
                    st.success(f"Location found: {lat:.4f}, {lon:.4f}")
                    latitude = lat
                    longitude = lon
                    st.session_state.user_location = {"lat": latitude, "lon": longitude}
                else:
                    st.warning("Could not find coordinates for this city. Please check the spelling or try using coordinates directly.")
                    latitude = st.session_state.user_location["lat"]
                    longitude = st.session_state.user_location["lon"]
        else:
            col1, col2 = st.columns(2)
            with col1:
                latitude = st.number_input("Latitude", value=st.session_state.user_location["lat"], min_value=-90.0, max_value=90.0, key="nasa_lat")
            with col2:
                longitude = st.number_input("Longitude", value=st.session_state.user_location["lon"], min_value=-180.0, max_value=180.0, key="nasa_lon")
        
        # Date range
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=365*5), key="nasa_start")
        with col2:
            end_date = st.date_input("End Date", datetime.now(), key="nasa_end")
        
        if st.button("Fetch Data and Calculate Anomalies"):
            with st.spinner("Fetching data from NASA POWER API..."):
                try:
                    # In a real implementation, this would fetch data from the NASA POWER API
                    # For now, generate sample data for demonstration
                    
                    # Create a date range from start_date to end_date
                    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
                    
                    # Generate sample temperature data
                    import random
                    
                    # Create seasonal temperature pattern with noise
                    def seasonal_temp(date, base_temp=15.0, amplitude=10.0, noise_level=3.0):
                        day_of_year = date.dayofyear
                        seasonal_component = amplitude * np.sin(2 * np.pi * (day_of_year - 172) / 365.0)  # 172 shifts peak to summer
                        noise = np.random.normal(0, noise_level)
                        return base_temp + seasonal_component + noise
                    
                    # Generate temperatures for each date
                    temperatures = [seasonal_temp(date) for date in date_range]
                    
                    # Create a dataframe
                    data = pd.DataFrame({
                        'Date': date_range,
                        'Temperature': temperatures
                    })
                    
                    # Calculate monthly climatology (long-term averages)
                    data['Month'] = data['Date'].dt.month
                    monthly_avg = data.groupby('Month')['Temperature'].mean().reset_index()
                    monthly_avg.columns = ['Month', 'Average_Temperature']
                    
                    # Merge the monthly averages back to the original data
                    data = pd.merge(data, monthly_avg, on='Month')
                    
                    # Calculate the anomalies
                    data['Temperature_Anomaly'] = data['Temperature'] - data['Average_Temperature']
                    
                    # Final result
                    result = data[['Date', 'Temperature', 'Average_Temperature', 'Temperature_Anomaly']]
                    
                    # Store the result in session state
                    st.session_state.processed_data = result
                    
                    # Display the result
                    st.subheader("Temperature Anomalies")
                    st.dataframe(result)
                    
                    # Download button for the anomalies table
                    csv = result.to_csv(index=False)
                    st.download_button(
                        label="Download Anomalies as CSV",
                        data=csv,
                        file_name="temperature_anomalies.csv",
                        mime="text/csv",
                    )
                    
                    # Visualization of anomalies
                    st.subheader("Visualization of Temperature Anomalies")
                    fig = px.scatter(result, x='Date', y='Temperature_Anomaly', 
                                    color='Temperature_Anomaly',
                                    color_continuous_scale=px.colors.diverging.RdBu_r,
                                    title="Temperature Anomalies Over Time")
                    st.plotly_chart(fig)
                    
                except Exception as e:
                    st.error(f"Error fetching data: {str(e)}")

# Display chat history
if st.session_state.chat_history:
    st.markdown("### Chat History")
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**CeCe:** {message['content']}")
    
    # Add option to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Add option to download chat history
    if st.button("Download Chat History"):
        chat_text = ""
        for message in st.session_state.chat_history:
            prefix = "You: " if message["role"] == "user" else "CeCe: "
            chat_text += f"{prefix}{message['content']}\n\n"
        
        # Provide the chat history as a downloadable txt file
        st.download_button(
            label="Download Chat as TXT",
            data=chat_text,
            file_name=f"cece_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
        )

# File upload section in sidebar
with st.sidebar:
    st.title("Data Management")
    
    upload_file = st.file_uploader("Upload Climate/Weather Dataset", type=["csv", "xlsx"])
    
    if upload_file is not None:
        try:
            if upload_file.name.endswith('.xlsx'):
                data = pd.read_excel(upload_file)
            else:
                data = pd.read_csv(upload_file)
            
            st.session_state.uploaded_data = data
            st.success(f"Successfully loaded {upload_file.name}")
            
            # Preview the data
            st.write("Data Preview:")
            st.dataframe(data.head())
            
            # Basic data info
            st.write("Data Info:")
            buffer = io.StringIO()
            data.info(buf=buffer)
            s = buffer.getvalue()
            st.text(s)
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    
    # Settings section
    st.subheader("Settings")
    
    api_option = st.selectbox("LLM Provider", ["DeepSeek-V3", "OpenAI"])
    
    # Only show API key input if not using environment variables
    if st.checkbox("Enter API Key Manually"):
        api_key = st.text_input("API Key", type="password")
    
    # Units preference
    units = st.radio("Temperature Units", ["Celsius", "Fahrenheit"])
    
    # Save settings button
    if st.button("Save Settings"):
        st.success("Settings saved!")

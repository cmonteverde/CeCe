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

# Add topography decoration 
st.markdown("""
<div style="position: absolute; top: 0; right: 0; width: 45%; min-width: 400px; height: 300px; z-index: 1; overflow: visible; pointer-events: none;">
    <img src="data:image/png;base64,{topo_base64}" style="width: 100%; height: 100%; object-fit: cover; object-position: top right;">
</div>
""".format(topo_base64=b64encode(open("assets/topography.png", "rb").read()).decode()), unsafe_allow_html=True)

# Remove the feedback button from here - we'll add it to the footer below

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
    st.session_state.chat_history = [
        {"role": "assistant", "content": "👋 Hi there! I'm CeCe, your Climate Copilot. I can help you analyze climate data, create visualizations, and understand weather patterns. Try one of the preset buttons above or ask me a question about climate data! For example, you could ask about temperature trends in your area, how to interpret climate anomalies, or what factors contribute to extreme weather events."}
    ]
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
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("📍 Generate a precipitation map for my region"):
        st.session_state.active_function = "precipitation_map"
        st.rerun()

with col2:
    if st.button("📊 Show temperature trends from the past 5 years"):
        st.session_state.active_function = "temperature_trends"
        st.rerun()

with col3:
    if st.button("⚠️ Identify extreme heat days in my area"):
        st.session_state.active_function = "extreme_heat"
        st.rerun()

with col4:
    if st.button("🗓️ Compare rainfall this season vs. last year"):
        st.session_state.active_function = "rainfall_comparison"
        st.rerun()

with col5:
    if st.button("📉 Export climate anomalies as a table"):
        st.session_state.active_function = "export_anomalies"
        st.rerun()
        
with col6:
    if st.button("📝 Generate interactive climate story"):
        st.session_state.active_function = "climate_story"
        st.rerun()

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

# Add significant padding at the bottom to create more space between chat box and footer
st.markdown("<div style='height: 350px'></div>", unsafe_allow_html=True)

# Footer bar at the bottom of the page with both elements
st.markdown("""
<div style="position: absolute; bottom: 0; left: 0; width: 100%; background-color: #000; padding: 20px 0; display: flex; justify-content: space-between; align-items: center;">
    <div style="width: 25%; margin-left: 30px;">
        <!-- Empty left division for spacing -->
    </div>
    <div style="flex-grow: 0; color: white; font-size: 14px; text-align: center;">
        Made with 
        <span style="background: linear-gradient(90deg, #1E90FF, #9370DB); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold;">❤</span> 
        by 
        <a href="https://www.linkedin.com/in/corriemonteverde/" target="_blank" style="text-decoration: none; background: linear-gradient(90deg, #1E90FF, #9370DB); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold;">Corrie</a> + 
        <a href="https://www.linkedin.com/in/mlaffin/" target="_blank" style="text-decoration: none; background: linear-gradient(90deg, #1E90FF, #9370DB); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold;">Matt</a>
    </div>
    <div style="width: 25%; margin-right: 30px; text-align: right;">
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSezvpoz4Jf2Ez0ukxU9y_q6iK4l4j5COVc1giJBQSJIUm9c0A/viewform?usp=dialog" target="_blank" style="
            background: linear-gradient(90deg, #1E90FF, #9370DB);
            color: white;
            padding: 10px 15px;
            border-radius: 50px;
            text-decoration: none;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            font-size: 14px;
            transition: all 0.3s ease;
        ">
            <span style="margin-right: 6px;">💬</span> Share feedback
        </a>
    </div>
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
                # Get real precipitation data from NASA POWER API
                from nasa_data import fetch_precipitation_map_data
                
                # Convert dates to string format for API
                start_date_str = start_date.strftime('%Y-%m-%d')
                end_date_str = end_date.strftime('%Y-%m-%d')
                
                # Status message
                st.text(f"Fetching precipitation data for {city if location_method == 'City Name' else f'({latitude:.2f}, {longitude:.2f})'} from {start_date_str} to {end_date_str}...")
                
                # Fetch NASA POWER precipitation data for a region
                precip_df = fetch_precipitation_map_data(latitude, longitude, start_date_str, end_date_str, radius_degrees=1.0)
                
                # Create a list of [lat, lon, precip] for each grid point
                heat_data = []
                for _, row in precip_df.iterrows():
                    lat = row['latitude']
                    lon = row['longitude']
                    precip = row['precipitation']
                    heat_data.append([lat, lon, precip])
                
                # Get the max value for scaling the heatmap
                max_precip = max([x[2] for x in heat_data]) if heat_data else 100
                
                # Create a base map centered on the location
                m = folium.Map(location=[latitude, longitude], zoom_start=7, 
                              tiles="cartodb dark_matter")
                
                # Add a marker for the selected location
                folium.Marker(
                    [latitude, longitude],
                    popup=f"Selected Location: {city if location_method == 'City Name' else f'({latitude:.2f}, {longitude:.2f})'}",
                    icon=folium.Icon(color="purple")
                ).add_to(m)
                
                # Add the heatmap to the map
                from folium.plugins import HeatMap
                
                # Create a heatmap with string-based gradient values
                # Note: Folium HeatMap gradient keys must be strings representing float values between 0 and 1
                HeatMap(
                    heat_data,
                    radius=15,
                    min_opacity=0.7,
                    blur=10,
                    # max_val parameter is no longer needed (will be calculated automatically)
                    # Using normalized string values for the gradient keys
                    gradient={
                        '0.0': 'blue',
                        '0.2': 'cyan',
                        '0.4': 'lime',
                        '0.6': 'yellow',
                        '0.8': 'orange',
                        '1.0': 'red'
                    }
                ).add_to(m)
                
                # Add a legend
                legend_html = '''
                <div style="position: fixed; 
                            bottom: 50px; right: 50px; 
                            background-color: rgba(0, 0, 0, 0.7);
                            border-radius: 5px;
                            padding: 10px;
                            color: white;
                            font-family: Arial, sans-serif;
                            z-index: 9999;">
                    <p><strong>Precipitation (mm)</strong></p>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="background: blue; width: 20px; height: 20px; margin-right: 5px;"></div>
                        <span>Low (0-20%)</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="background: cyan; width: 20px; height: 20px; margin-right: 5px;"></div>
                        <span>Moderate (20-40%)</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="background: lime; width: 20px; height: 20px; margin-right: 5px;"></div>
                        <span>Significant (40-60%)</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="background: yellow; width: 20px; height: 20px; margin-right: 5px;"></div>
                        <span>Heavy (60-80%)</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="background: red; width: 20px; height: 20px; margin-right: 5px;"></div>
                        <span>Extreme (80-100%)</span>
                    </div>
                </div>
                '''
                
                m.get_root().html.add_child(folium.Element(legend_html))
                
                # Title for the map
                title_html = f'''
                <h3 style="position: absolute; 
                            top: 10px; left: 50%; 
                            transform: translateX(-50%);
                            z-index: 9999; 
                            background-color: rgba(0, 0, 0, 0.7);
                            color: white; 
                            padding: 10px; 
                            border-radius: 5px; 
                            font-family: Arial, sans-serif;">
                    Precipitation Map for {city if location_method == 'City Name' else f'({latitude:.2f}, {longitude:.2f})'}
                </h3>
                '''
                
                m.get_root().html.add_child(folium.Element(title_html))
                
                # Display the map
                st.subheader(f"NASA POWER Precipitation Map ({start_date_str} to {end_date_str})")
                folium_static(m)
                
                # Add context about the data
                st.info(f"This map shows real precipitation data from NASA POWER API around your selected location for the date range {start_date_str} to {end_date_str}. Data source: NASA POWER (Prediction of Worldwide Energy Resources).")
                
                # Add "What is NASA POWER" explanation
                with st.expander("What is NASA POWER data?"):
                    st.markdown("""
                    **NASA POWER** (Prediction of Worldwide Energy Resources) is a project from NASA that provides solar and meteorological data sets from NASA research for support of renewable energy, building energy efficiency and agricultural needs.
                    
                    The data is derived from satellite observations and NASA's GMAO (Global Modeling and Assimilation Office) products, which combine various observational data sources with advanced modeling.
                    
                    Key features of NASA POWER data:
                    - **Global coverage**: Data available for any point on Earth
                    - **Long-term dataset**: Data available from 1981 to present
                    - **Free access**: No registration required for basic access
                    - **Variety of parameters**: Temperature, precipitation, solar radiation, and more
                    
                    The precipitation data shown on this map represents the total accumulated precipitation (rain, snow, etc.) over the selected time period, measured in millimeters.
                    """)
                
                # Option to download the map
                st.download_button(
                    label="Download Map as HTML",
                    data=m._repr_html_(),
                    file_name="precipitation_map.html",
                    mime="text/html"
                )
                
            except Exception as e:
                # If NASA POWER API data fetching fails, display error and fallback to simulated data
                st.error(f"Error fetching NASA POWER data: {str(e)}")
                st.warning("Falling back to simulated precipitation data for demonstration purposes.")
                
                # Note about NASA POWER API
                st.markdown("""
                ### About NASA POWER API:
                The NASA POWER API provides free access to climate data without requiring registration or API keys.
                
                If you're seeing this error, it might be due to:
                1. Temporary API service disruption
                2. Network connectivity issues
                3. Invalid date range or location parameters
                
                Please try again later or try with different parameters.
                """)
                
                # Create a fallback map
                m = folium.Map(location=[latitude, longitude], zoom_start=10, tiles="cartodb dark_matter")
                
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
                HeatMap(heat_data, radius=15, gradient={
                    '0.0': 'blue',
                    '0.2': 'cyan',
                    '0.4': 'lime',
                    '0.6': 'yellow',
                    '0.8': 'orange',
                    '1.0': 'red'
                }).add_to(m)
                
                # Add a marker for the selected location
                folium.Marker(
                    [latitude, longitude],
                    popup=f"Selected Location ({latitude:.4f}, {longitude:.4f})",
                    icon=folium.Icon(color="purple")
                ).add_to(m)
                
                # Display the map
                st.subheader(f"Simulated Precipitation Heatmap (DEMO MODE)")
                folium_static(m)
                
                # Add note about the simulated data
                st.warning("This is simulated data for demonstration purposes only. It does not represent real precipitation patterns.")

elif st.session_state.active_function == "climate_story":
    st.subheader("Interactive Climate Story Generator")
    
    # Location input method selection
    location_method = st.radio("Select location input method:", ["City Name", "Coordinates"], horizontal=True, key="story_location_method")
    
    if location_method == "City Name":
        city = st.text_input("Enter city name (e.g., 'New York', 'London, UK')", 
                           value="San Francisco, CA" if "last_city" not in st.session_state else st.session_state.last_city,
                           key="story_city_input")
        
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
            latitude = st.number_input("Latitude", value=st.session_state.user_location["lat"], 
                                      min_value=-90.0, max_value=90.0, key="story_lat")
        with col2:
            longitude = st.number_input("Longitude", value=st.session_state.user_location["lon"], 
                                       min_value=-180.0, max_value=180.0, key="story_lon")
    
    # Date range
    st.write("Select time period for your climate story:")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=365), key="story_start")
    with col2:
        end_date = st.date_input("End Date", datetime.now(), key="story_end")
    
    # Story type selection
    story_type = st.radio("Select story type:", 
                        ["Personal Experience", "Educational", "Historical Context"], 
                        horizontal=True, key="story_type")
    
    # Map story type to the format expected by the generator function
    story_type_map = {
        "Personal Experience": "personal",
        "Educational": "educational",
        "Historical Context": "historical"
    }
    
    # Generate button
    if st.button("Generate Climate Story"):
        try:
            with st.spinner("Fetching climate data and crafting your story..."):
                # Convert dates to string format
                start_date_str = start_date.strftime('%Y-%m-%d')
                end_date_str = end_date.strftime('%Y-%m-%d')
                
                # Status message
                st.text(f"Fetching climate data for {city if location_method == 'City Name' else f'({latitude:.2f}, {longitude:.2f})'} from {start_date_str} to {end_date_str}...")
                
                # Fetch NASA POWER data
                from nasa_data import fetch_nasa_power_data
                climate_data = fetch_nasa_power_data(
                    latitude, 
                    longitude, 
                    start_date_str, 
                    end_date_str, 
                    parameters=["T2M", "PRECTOTCORR", "RH2M", "WS2M"]
                )
                
                if climate_data is None or len(climate_data) == 0:
                    st.error("Could not fetch climate data for the specified location and time period.")
                    st.stop()
                
                # Prepare location and timeframe data for the story generator
                location_data = {
                    "city": city if location_method == "City Name" else None,
                    "lat": latitude,
                    "lon": longitude
                }
                
                timeframe_data = {
                    "start_date": start_date,
                    "end_date": end_date
                }
                
                # Generate the climate story
                from climate_story_generator import generate_climate_story
                
                # Check if we have the OpenAI API key
                if not os.getenv("OPENAI_API_KEY"):
                    st.warning("OpenAI API key not found. Please provide your API key in the settings to use this feature.")
                    # Provide option to add the API key
                    api_key = st.text_input("Enter your OpenAI API key:", type="password")
                    if api_key:
                        os.environ["OPENAI_API_KEY"] = api_key
                        st.success("API key set! Click the button again to generate your story.")
                        st.rerun()
                    st.stop()
                
                # Generate the story
                story = generate_climate_story(
                    climate_data, 
                    location_data, 
                    timeframe_data, 
                    story_type=story_type_map[story_type]
                )
                
                # Display the story
                if "text" in story and "title" in story:
                    st.title(story["title"])
                    st.markdown(story["text"])
                    
                    # Display insights
                    if "insights" in story and story["insights"]:
                        st.subheader("Key Climate Insights")
                        for insight in story["insights"]:
                            st.markdown(f"- {insight}")
                    
                    # Display visualization suggestions
                    if "visualization_suggestions" in story and story["visualization_suggestions"]:
                        st.subheader("Suggested Visualizations")
                        for suggestion in story["visualization_suggestions"]:
                            st.markdown(f"- {suggestion}")
                    
                    # Option to download the story
                    story_text = f"# {story['title']}\n\n{story['text']}\n\n## Key Climate Insights\n"
                    for insight in story.get("insights", []):
                        story_text += f"- {insight}\n"
                    story_text += f"\n## Suggested Visualizations\n"
                    for suggestion in story.get("visualization_suggestions", []):
                        story_text += f"- {suggestion}\n"
                    
                    st.download_button(
                        label="Download Story as Text",
                        data=story_text,
                        file_name=f"climate_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(f"Error generating story: {story.get('text', 'Unknown error')}")
        
        except Exception as e:
            st.error(f"Error generating climate story: {str(e)}")
            st.info("This feature requires an OpenAI API key. Please check your settings and try again.")

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
                    # Fetch real temperature data from NASA POWER API
                    from nasa_data import fetch_nasa_power_data
                    
                    # Convert dates to string format for API
                    start_date_str = start_date.strftime('%Y-%m-%d')
                    end_date_str = end_date.strftime('%Y-%m-%d')
                    
                    # Status message
                    st.text(f"Fetching temperature data for {city if location_method == 'City Name' else f'({latitude:.2f}, {longitude:.2f})'} from {start_date_str} to {end_date_str}...")
                    
                    # Fetch NASA POWER temperature data
                    nasa_df = fetch_nasa_power_data(
                        latitude, 
                        longitude, 
                        start_date_str, 
                        end_date_str, 
                        parameters=["T2M"]  # Temperature at 2 Meters
                    )
                    
                    # Create a dataframe with the temperature data
                    data = pd.DataFrame({
                        'Date': nasa_df['Date'],
                        'Temperature': nasa_df['T2M']  # Temperature in Celsius
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

# Adding the missing function implementations for the preset buttons
if st.session_state.active_function == "temperature_trends":
    st.subheader("Temperature Trends from the Past 5 Years")
    
    # Location selection similar to precipitation map
    location_method = st.radio("Select location input method:", ["City Name", "Coordinates"], horizontal=True, key="temp_location_method")
    
    if location_method == "City Name":
        city = st.text_input("Enter city name (e.g., 'New York', 'London, UK')", 
                             value="San Francisco, CA" if "last_city" not in st.session_state else st.session_state.last_city,
                             key="temp_city_input")
        
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
            latitude = st.number_input("Latitude", value=st.session_state.user_location["lat"], 
                                      min_value=-90.0, max_value=90.0, key="temp_lat_input")
        with col2:
            longitude = st.number_input("Longitude", value=st.session_state.user_location["lon"], 
                                       min_value=-180.0, max_value=180.0, key="temp_lon_input")
        
        st.session_state.user_location = {"lat": latitude, "lon": longitude}
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        end_date = st.date_input("End Date (Today)", datetime.now(), key="temp_end_date")
    with col2:
        # Calculate start date as 5 years ago from end date
        start_date = st.date_input("Start Date (5 years ago)", end_date - timedelta(days=5*365), key="temp_start_date")
    
    if st.button("Generate Temperature Trends"):
        with st.spinner("Generating temperature trends for the past 5 years..."):
            try:
                # Fetch real temperature data from NASA POWER API
                from nasa_data import get_temperature_trends
                
                # Convert dates to string format for API
                start_date_str = start_date.strftime('%Y-%m-%d')
                end_date_str = end_date.strftime('%Y-%m-%d')
                
                # Status message
                st.text(f"Fetching temperature trends data for {city if location_method == 'City Name' else f'({latitude:.2f}, {longitude:.2f})'} from {start_date_str} to {end_date_str}...")
                
                # Get temperature trends from NASA POWER API
                df, trend_per_decade = get_temperature_trends(latitude, longitude, start_date_str, end_date_str)
                
                # Calculate a 12-month moving average
                df['12-Month Moving Avg'] = df['Temperature (°C)'].rolling(window=12).mean()
                
                # Calculate the trend line using linear regression
                from scipy import stats
                x = np.arange(len(df))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, df['Temperature (°C)'])
                df['Trend'] = intercept + slope * x
                
                # Create a Plotly visualization
                fig = px.line(df, x='Date', y='Temperature (°C)', title=f'Monthly Temperature Trends for {city if location_method == "City Name" else f"({latitude:.2f}, {longitude:.2f})"}')
                
                # Add the moving average line
                fig.add_scatter(x=df['Date'], y=df['12-Month Moving Avg'], mode='lines', name='12-Month Moving Average', line=dict(color='red'))
                
                # Add the trend line
                fig.add_scatter(x=df['Date'], y=df['Trend'], mode='lines', name='Long-term Trend', line=dict(color='green', dash='dash'))
                
                # Customize the layout
                fig.update_layout(
                    xaxis_title='Date',
                    yaxis_title='Temperature (°C)',
                    legend_title='',
                    template='plotly_dark',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                
                # Display the chart
                st.plotly_chart(fig, use_container_width=True)
                
                # Display key insights
                trend_per_decade = slope * 120  # 120 months in a decade
                st.subheader("Key Insights")
                
                insights_col1, insights_col2 = st.columns(2)
                with insights_col1:
                    st.metric("Average Temperature", f"{df['Temperature (°C)'].mean():.1f}°C", delta=None)
                    st.metric("Temperature Range", f"{df['Temperature (°C)'].min():.1f}°C to {df['Temperature (°C)'].max():.1f}°C", delta=None)
                
                with insights_col2:
                    st.metric("Trend per Decade", f"{trend_per_decade:.2f}°C", 
                             delta="warming" if trend_per_decade > 0 else "cooling")
                    st.metric("Seasonal Variation", f"{df['Temperature (°C)'].std():.1f}°C", delta=None)
                
                # Add context about the data
                st.info(f"This chart shows simulated monthly temperature data for your selected location. The trend line indicates an overall temperature change of approximately {trend_per_decade:.2f}°C per decade. In a real implementation, this would use actual climate data from NASA POWER API or similar sources.")
                
                # Option to download the data
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Temperature Data as CSV",
                    data=csv_data,
                    file_name="temperature_trends.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"Error generating temperature trends: {str(e)}")

if st.session_state.active_function == "extreme_heat":
    st.subheader("Identify Extreme Heat Days in Your Area")
    
    # Location selection
    location_method = st.radio("Select location input method:", ["City Name", "Coordinates"], horizontal=True, key="heat_location_method")
    
    if location_method == "City Name":
        city = st.text_input("Enter city name (e.g., 'New York', 'London, UK')", 
                             value="Phoenix, AZ" if "last_city" not in st.session_state else st.session_state.last_city,
                             key="heat_city_input")
        
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
            latitude = st.number_input("Latitude", value=st.session_state.user_location["lat"], 
                                      min_value=-90.0, max_value=90.0, key="heat_lat_input")
        with col2:
            longitude = st.number_input("Longitude", value=st.session_state.user_location["lon"], 
                                       min_value=-180.0, max_value=180.0, key="heat_lon_input")
        
        st.session_state.user_location = {"lat": latitude, "lon": longitude}
    
    # Parameters for extreme heat identification
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("Select Year", list(range(datetime.now().year, datetime.now().year - 10, -1)), key="heat_year")
    with col2:
        percentile = st.slider("Extreme Heat Threshold (Percentile)", min_value=90, max_value=99, value=95, key="heat_percentile")
    
    # Options for analysis
    analysis_type = st.radio("Analysis Type", ["By Maximum Temperature", "By Heat Index (Temperature + Humidity)"], key="heat_analysis_type")
    
    if st.button("Identify Extreme Heat Days"):
        with st.spinner("Analyzing temperature data to identify extreme heat days..."):
            try:
                # Fetch real temperature and heat data from NASA POWER API
                from nasa_data import get_extreme_heat_days
                
                # Convert year to date format
                start_date_str = f"{year}-01-01"
                end_date_str = f"{year}-12-31"
                
                # Status message
                st.text(f"Fetching temperature data for {city if location_method == 'City Name' else f'({latitude:.2f}, {longitude:.2f})'} for year {year}...")
                
                # Get extreme heat days from NASA POWER API
                df, temp_threshold, hi_threshold = get_extreme_heat_days(latitude, longitude, year, percentile)
                
                # Select which value to analyze based on user selection
                if analysis_type == "By Heat Index (Temperature + Humidity)":
                    # Determine extreme heat days based on heat index
                    df['Is Extreme Heat'] = df['Heat Index (°C)'] > hi_threshold
                    
                    # Value to analyze
                    analysis_value = 'Heat Index (°C)'
                    threshold = hi_threshold
                    
                else:  # By Maximum Temperature
                    # Determine extreme heat days based on temperature
                    df['Is Extreme Heat'] = df['T2M_MAX'] > temp_threshold
                    
                    # Value to analyze
                    analysis_value = 'T2M_MAX'
                    threshold = temp_threshold
                    
                # Rename temperature column for display
                df = df.rename(columns={'T2M_MAX': 'Temperature (°C)'})
                
                # Filter to extreme heat days
                extreme_days = df[df['Is Extreme Heat']].copy()
                
                # Display the results
                st.subheader(f"Extreme Heat Days in {year} (Above {percentile}th Percentile)")
                
                # Show the threshold
                st.info(f"Threshold value: {threshold:.1f}°C {analysis_value.split(' ')[0]}")
                
                # Create calendar heatmap
                fig = px.scatter(df, x=df['Date'].dt.month, y=df['Date'].dt.day, 
                               color=df[analysis_value],
                               color_continuous_scale='Turbo',  # Red-hot color scale
                               title=f"Heat Calendar for {year}",
                               labels={'x': 'Month', 'y': 'Day', 'color': analysis_value},
                               size_max=10,
                               height=400)
                
                # Add custom shapes for extreme heat days
                for idx, row in extreme_days.iterrows():
                    month = row['Date'].month
                    day = row['Date'].day
                    fig.add_shape(
                        type="circle",
                        x0=month - 0.3, y0=day - 0.3,
                        x1=month + 0.3, y1=day + 0.3,
                        line=dict(color="red", width=2),
                        fillcolor="rgba(255,0,0,0)"
                    )
                
                # Customize the layout
                fig.update_layout(
                    xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(1, 13)),
                        ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    ),
                    yaxis=dict(
                        autorange="reversed"  # To have day 1 at the top
                    ),
                    template='plotly_dark',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display statistics
                st.subheader("Heat Statistics")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Extreme Heat Days", f"{len(extreme_days)}", delta=None)
                with col2:
                    avg_extreme = extreme_days[analysis_value].mean()
                    st.metric("Average " + analysis_value, f"{avg_extreme:.1f}°C", delta=None)
                with col3:
                    max_extreme = extreme_days[analysis_value].max()
                    max_date = extreme_days.loc[extreme_days[analysis_value].idxmax(), 'Date'].strftime('%b %d')
                    st.metric("Maximum " + analysis_value, f"{max_extreme:.1f}°C on {max_date}", delta=None)
                
                # Display extreme days data table
                st.subheader("List of Extreme Heat Days")
                # Format the table for display
                display_df = extreme_days.copy()
                display_df['Date'] = display_df['Date'].dt.strftime('%b %d, %Y')
                # Round numeric columns to 1 decimal place
                numeric_cols = display_df.select_dtypes(include=[np.number]).columns
                display_df[numeric_cols] = display_df[numeric_cols].round(1)
                
                # Sort by the analysis value in descending order
                display_df = display_df.sort_values(by=analysis_value, ascending=False)
                
                # Show the table
                st.dataframe(display_df)
                
                # Option to download the data
                csv_data = display_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Extreme Heat Days Data as CSV",
                    data=csv_data,
                    file_name="extreme_heat_days.csv",
                    mime="text/csv"
                )
                
                # Add context about the data
                st.info(f"This analysis shows simulated extreme heat days for your selected location. In a real implementation, this would use actual climate data from NASA POWER API or similar sources, and could include more sophisticated heat metrics like wet-bulb temperature for heat stress analysis.")
                
            except Exception as e:
                st.error(f"Error identifying extreme heat days: {str(e)}")

if st.session_state.active_function == "rainfall_comparison":
    st.subheader("Compare Rainfall: This Season vs. Last Year")
    
    # Location selection
    location_method = st.radio("Select location input method:", ["City Name", "Coordinates"], horizontal=True, key="rain_location_method")
    
    if location_method == "City Name":
        city = st.text_input("Enter city name (e.g., 'New York', 'London, UK')", 
                             value="Seattle, WA" if "last_city" not in st.session_state else st.session_state.last_city,
                             key="rain_city_input")
        
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
            latitude = st.number_input("Latitude", value=st.session_state.user_location["lat"], 
                                      min_value=-90.0, max_value=90.0, key="rain_lat_input")
        with col2:
            longitude = st.number_input("Longitude", value=st.session_state.user_location["lon"], 
                                       min_value=-180.0, max_value=180.0, key="rain_lon_input")
        
        st.session_state.user_location = {"lat": latitude, "lon": longitude}
    
    # Define seasons
    current_month = datetime.now().month
    # Approximate seasons (adjust as needed for your application)
    season_mapping = {
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Fall", 10: "Fall", 11: "Fall"
    }
    current_season = season_mapping[current_month]
    
    # Allow user to select a different season
    season = st.selectbox("Select Season to Compare", ["Winter", "Spring", "Summer", "Fall"], 
                         index=list(["Winter", "Spring", "Summer", "Fall"]).index(current_season),
                         key="rain_season")
    
    # Define the current year and last year
    current_year = datetime.now().year
    
    if st.button("Compare Rainfall"):
        with st.spinner("Comparing rainfall data between seasons..."):
            try:
                # Fetch real precipitation data from NASA POWER API
                from nasa_data import get_rainfall_comparison
                
                # Define season date ranges for current and previous year
                season_dates = {
                    "Winter": {"start_month": 12, "start_day": 1, "end_month": 2, "end_day": 28},
                    "Spring": {"start_month": 3, "start_day": 1, "end_month": 5, "end_day": 31},
                    "Summer": {"start_month": 6, "start_day": 1, "end_month": 8, "end_day": 31},
                    "Fall": {"start_month": 9, "start_day": 1, "end_month": 11, "end_day": 30}
                }
                
                # Handle the case where winter spans across years
                if season == "Winter":
                    # Current winter
                    if current_month in [12, 1, 2]:
                        if current_month == 12:
                            current_start = datetime(current_year, 12, 1)
                            current_end = datetime(current_year + 1, 2, 28)
                        else:  # Jan or Feb
                            current_start = datetime(current_year - 1, 12, 1)
                            current_end = datetime(current_year, 2, 28)
                        
                        # Previous winter
                        prev_start = datetime(current_year - 1, 12, 1)
                        prev_end = datetime(current_year, 2, 28)
                    else:
                        # If we're not in winter, compare the most recent winter to the one before
                        current_start = datetime(current_year - 1, 12, 1)
                        current_end = datetime(current_year, 2, 28)
                        prev_start = datetime(current_year - 2, 12, 1)
                        prev_end = datetime(current_year - 1, 2, 28)
                else:
                    # For other seasons
                    start_month = season_dates[season]["start_month"]
                    start_day = season_dates[season]["start_day"]
                    end_month = season_dates[season]["end_month"]
                    end_day = season_dates[season]["end_day"]
                    
                    # Check if the selected season has already passed in the current year
                    if current_month > end_month:
                        # Season has passed, so "current" is this year
                        current_start = datetime(current_year, start_month, start_day)
                        current_end = datetime(current_year, end_month, end_day)
                        prev_start = datetime(current_year - 1, start_month, start_day)
                        prev_end = datetime(current_year - 1, end_month, end_day)
                    elif current_month < start_month:
                        # Season hasn't started yet, so "current" is last year
                        current_start = datetime(current_year - 1, start_month, start_day)
                        current_end = datetime(current_year - 1, end_month, end_day)
                        prev_start = datetime(current_year - 2, start_month, start_day)
                        prev_end = datetime(current_year - 2, end_month, end_day)
                    else:
                        # We're in the season now, so it's ongoing
                        current_start = datetime(current_year, start_month, start_day)
                        current_end = datetime.now()
                        prev_start = datetime(current_year - 1, start_month, start_day)
                        prev_end = datetime(current_year - 1, end_month, end_day)
                
                # Convert dates to string format for API
                current_start_str = current_start.strftime('%Y-%m-%d')
                current_end_str = current_end.strftime('%Y-%m-%d')
                prev_start_str = prev_start.strftime('%Y-%m-%d')
                prev_end_str = prev_end.strftime('%Y-%m-%d')
                
                # Status message
                st.text(f"Fetching precipitation data for {city if location_method == 'City Name' else f'({latitude:.2f}, {longitude:.2f})'} for {season} season...")
                
                # Get rainfall comparison from NASA POWER API
                current_df, prev_df = get_rainfall_comparison(
                    latitude, 
                    longitude, 
                    current_start_str, 
                    current_end_str, 
                    prev_start_str, 
                    prev_end_str
                )
                
                # Combine the data
                combined_df = pd.concat([current_df, prev_df])
                
                # Calculate cumulative precipitation
                current_cumulative = current_df['Precipitation (mm)'].cumsum()
                prev_cumulative = prev_df['Precipitation (mm)'].cumsum()
                
                # Calculate statistics
                current_total = current_df['Precipitation (mm)'].sum()
                prev_total = prev_df['Precipitation (mm)'].sum()
                current_days_with_rain = len(current_df[current_df['Precipitation (mm)'] > 0])
                prev_days_with_rain = len(prev_df[prev_df['Precipitation (mm)'] > 0])
                
                # Normalize the dates to display them on the same x-axis (days from start of season)
                current_df['Day of Season'] = range(len(current_df))
                prev_df['Day of Season'] = range(len(prev_df))
                
                # Create the comparison plots
                
                # 1. Daily precipitation comparison
                fig1 = px.bar(combined_df, x='Date', y='Precipitation (mm)', color='Year',
                             barmode='group', title=f"{season} Daily Precipitation Comparison",
                             color_discrete_map={'This Year': '#1E90FF', 'Last Year': '#9370DB'})
                
                fig1.update_layout(
                    xaxis_title='Date',
                    yaxis_title='Precipitation (mm)',
                    legend_title='',
                    template='plotly_dark',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                
                st.plotly_chart(fig1, use_container_width=True)
                
                # 2. Cumulative precipitation comparison
                fig2 = go.Figure()
                
                # Add current year line
                fig2.add_trace(go.Scatter(
                    x=current_df['Day of Season'],
                    y=current_cumulative,
                    mode='lines',
                    name='This Year',
                    line=dict(color='#1E90FF', width=3)
                ))
                
                # Add previous year line
                fig2.add_trace(go.Scatter(
                    x=prev_df['Day of Season'],
                    y=prev_cumulative,
                    mode='lines',
                    name='Last Year',
                    line=dict(color='#9370DB', width=3)
                ))
                
                # Update layout
                fig2.update_layout(
                    title=f"{season} Cumulative Precipitation Comparison",
                    xaxis_title='Days from Start of Season',
                    yaxis_title='Cumulative Precipitation (mm)',
                    legend_title='',
                    template='plotly_dark',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
                # Display statistics
                st.subheader("Rainfall Statistics")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    percent_change = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
                    st.metric("Total Precipitation", 
                             f"{current_total:.1f} mm", 
                             delta=f"{percent_change:.1f}% vs last year")
                
                with col2:
                    st.metric("Days with Rain", 
                             f"{current_days_with_rain}", 
                             delta=f"{current_days_with_rain - prev_days_with_rain} days vs last year")
                
                with col3:
                    current_avg = current_total / max(1, len(current_df))
                    prev_avg = prev_total / max(1, len(prev_df))
                    avg_percent_change = ((current_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
                    st.metric("Avg. Daily Precipitation", 
                             f"{current_avg:.1f} mm", 
                             delta=f"{avg_percent_change:.1f}% vs last year")
                
                # Context about the data
                comparison_result = "wetter" if current_total > prev_total else "drier"
                st.info(f"Based on NASA POWER climate data, the {season.lower()} season this year is {comparison_result} than last year. This analysis uses real precipitation data for your selected location.")
                
                # Option to download the data
                csv_data = combined_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Rainfall Comparison Data as CSV",
                    data=csv_data,
                    file_name="rainfall_comparison.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"Error comparing rainfall data: {str(e)}")

if st.session_state.active_function == "export_anomalies":
    st.subheader("Export Climate Anomalies as a Table")
    
    # Location selection
    location_method = st.radio("Select location input method:", ["City Name", "Coordinates"], horizontal=True, key="anomaly_location_method")
    
    if location_method == "City Name":
        city = st.text_input("Enter city name (e.g., 'New York', 'London, UK')", 
                             value="Boulder, CO" if "last_city" not in st.session_state else st.session_state.last_city,
                             key="anomaly_city_input")
        
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
            latitude = st.number_input("Latitude", value=st.session_state.user_location["lat"], 
                                      min_value=-90.0, max_value=90.0, key="anomaly_lat_input")
        with col2:
            longitude = st.number_input("Longitude", value=st.session_state.user_location["lon"], 
                                       min_value=-180.0, max_value=180.0, key="anomaly_lon_input")
        
        st.session_state.user_location = {"lat": latitude, "lon": longitude}
    
    # Date range selection
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_period = st.selectbox("Time Period", 
                                     ["Last 5 Years", "Last 10 Years", "Last 30 Years", "Custom Range"],
                                     key="anomaly_period")
    
    # Set the date range based on the selected period
    end_date = datetime.now()
    
    if selected_period == "Last 5 Years":
        start_date = datetime(end_date.year - 5, 1, 1)
    elif selected_period == "Last 10 Years":
        start_date = datetime(end_date.year - 10, 1, 1)
    elif selected_period == "Last 30 Years":
        start_date = datetime(end_date.year - 30, 1, 1)
    else:  # Custom Range
        with col2:
            start_date = st.date_input("Start Date", 
                                      datetime(end_date.year - 10, 1, 1),
                                      key="anomaly_start_date")
        with col3:
            end_date = st.date_input("End Date", 
                                    end_date,
                                    key="anomaly_end_date")
    
    # Variable selection
    variable = st.selectbox("Climate Variable", 
                          ["Temperature", "Precipitation", "Humidity", "Wind Speed"],
                          key="anomaly_variable")
    
    # Baseline selection
    baseline_period = st.selectbox("Baseline Period", 
                                 ["1951-1980", "1971-2000", "1981-2010", "1991-2020"],
                                 key="anomaly_baseline")
    
    # Calculate button
    if st.button("Calculate and Export Anomalies"):
        with st.spinner("Calculating climate anomalies..."):
            try:
                # Fetch real climate data from NASA POWER API
                from nasa_data import calculate_climate_anomalies
                
                # Convert dates to string format for API
                start_date_str = start_date.strftime('%Y-%m-%d') 
                end_date_str = end_date.strftime('%Y-%m-%d')
                
                # Status message
                st.text(f"Fetching climate data for {city if location_method == 'City Name' else f'({latitude:.2f}, {longitude:.2f})'} for {variable.lower()}...")
                
                # Get climate anomalies data from NASA POWER API
                df = calculate_climate_anomalies(
                    latitude,
                    longitude,
                    start_date_str,
                    end_date_str,
                    variable.lower(),
                    baseline_period
                )
                
                # Display the anomalies table
                st.subheader(f"{variable} Anomalies Relative to {baseline_period}")
                
                # Format the dataframe for display
                display_df = df.copy()
                display_df['Date'] = display_df['Date'].dt.strftime('%b %Y')
                
                # Round values for display
                value_cols = [col for col in display_df.columns if col not in ['Date', 'Year', 'Month', 'Anomaly', 'Anomaly Unit']]
                if len(value_cols) > 0:
                    for col in value_cols:
                        display_df[col] = display_df[col].round(1)
                
                # Round anomaly values
                display_df['Anomaly'] = display_df['Anomaly'].round(1)
                
                # Create a color-coded dataframe for the anomalies
                st.dataframe(
                    display_df,
                    column_config={
                        'Anomaly': st.column_config.NumberColumn(
                            f"{variable} Anomaly ({display_df['Anomaly Unit'].iloc[0]})",
                            format="%.1f" + (" °C" if variable == "Temperature" else " %"),
                            help=f"Difference from {baseline_period} baseline",
                        )
                    },
                    hide_index=True
                )
                
                # Create visualization of anomalies
                if variable == "Temperature":
                    # Color mapping for temperature anomalies
                    colors = ['blue' if a < -1 else 'lightblue' if a < 0 
                             else 'salmon' if a < 1 else 'red' for a in df['Anomaly']]
                    
                    # Create plot
                    fig = px.bar(
                        df, 
                        x='Date', 
                        y='Anomaly',
                        title=f"Monthly Temperature Anomalies Relative to {baseline_period}",
                        labels={'Anomaly': 'Temperature Anomaly (°C)', 'Date': ''},
                        color='Anomaly',
                        color_continuous_scale='RdBu_r'
                    )
                else:
                    # For non-temperature variables, use a diverging color scale centered at 0
                    fig = px.bar(
                        df, 
                        x='Date', 
                        y='Anomaly',
                        title=f"Monthly {variable} Anomalies Relative to {baseline_period}",
                        labels={'Anomaly': f'{variable} Anomaly (%)', 'Date': ''},
                        color='Anomaly',
                        color_continuous_scale='RdBu'
                    )
                
                # Layout customization
                fig.update_layout(
                    xaxis=dict(
                        tickmode='array',
                        tickvals=df['Date'][::12],  # Show tick every 12 months
                        ticktext=[d.strftime('%Y') for d in df['Date'][::12]]
                    ),
                    template='plotly_dark',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate some statistics about the anomalies
                mean_anomaly = df['Anomaly'].mean()
                trend_per_decade = df['Anomaly'].iloc[-60:].mean() - df['Anomaly'].iloc[:60].mean() if len(df) > 120 else np.nan
                
                # Display statistics
                st.subheader("Anomaly Statistics")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if variable == "Temperature":
                        st.metric("Mean Anomaly", f"{mean_anomaly:.2f} °C", 
                                 delta=f"{mean_anomaly:.2f} °C" if mean_anomaly != 0 else None)
                    else:
                        st.metric("Mean Anomaly", f"{mean_anomaly:.1f}%", 
                                 delta=f"{mean_anomaly:.1f}%" if mean_anomaly != 0 else None)
                
                with col2:
                    if not np.isnan(trend_per_decade):
                        if variable == "Temperature":
                            st.metric("Recent Trend (per decade)", f"{trend_per_decade:.2f} °C", 
                                     delta=f"{trend_per_decade:.2f} °C" if trend_per_decade != 0 else None)
                        else:
                            st.metric("Recent Trend (per decade)", f"{trend_per_decade:.1f}%", 
                                     delta=f"{trend_per_decade:.1f}%" if trend_per_decade != 0 else None)
                
                with col3:
                    extreme_anomalies = len(df[abs(df['Anomaly']) > (2 if variable == "Temperature" else 50)])
                    st.metric("Extreme Anomalies", f"{extreme_anomalies}", 
                             delta=None)
                
                # Allow downloading the data
                csv = df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label=f"Download {variable} Anomalies as CSV",
                    data=csv,
                    file_name=f"{variable.lower()}_anomalies_{baseline_period}.csv",
                    mime="text/csv"
                )
                
                # Add Excel export option
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Anomalies', index=False)
                    
                    # Add a summary sheet
                    summary_data = {
                        'Statistic': ['Mean Anomaly', 'Trend per Decade', 'Extreme Anomalies', 
                                     'Baseline Period', 'Data Period'],
                        'Value': [
                            f"{mean_anomaly:.2f} {display_df['Anomaly Unit'].iloc[0]}", 
                            f"{trend_per_decade:.2f} {display_df['Anomaly Unit'].iloc[0]} per decade" if not np.isnan(trend_per_decade) else "N/A",
                            str(extreme_anomalies),
                            baseline_period,
                            f"{start_date.strftime('%b %Y')} to {end_date.strftime('%b %Y')}"
                        ]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                excel_data = excel_buffer.getvalue()
                
                st.download_button(
                    label=f"Download {variable} Anomalies as Excel",
                    data=excel_data,
                    file_name=f"{variable.lower()}_anomalies_{baseline_period}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Add context about the data
                st.info(f"This chart shows {variable.lower()} anomalies for your selected location relative to a {baseline_period} baseline using NASA POWER climate data. Positive anomalies indicate values above the baseline, while negative anomalies indicate values below the baseline.")
                
            except Exception as e:
                st.error(f"Error calculating climate anomalies: {str(e)}")

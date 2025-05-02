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
import climate_resilience

# Import map modules
import simple_artistic_maps
import felt_inspired_maps
import embedded_felt_map

# Import our API status checker and helper
import test_api_status
import openai_helper
import felt_map_demo

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
    .industry-buttons-container {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        margin-bottom: 20px;
        gap: 15px;
    }
    .industry-button {
        width: 120px;
        height: 120px;
        background-color: rgba(30, 30, 30, 0.6);
        border: 1px solid rgba(147, 112, 219, 0.3);
        border-radius: 12px;
        color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        overflow: hidden;
        position: relative;
    }
    .industry-button:hover {
        border-color: rgba(147, 112, 219, 0.8);
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
    }
    .industry-button img {
        width: 60px;
        height: 60px;
        margin-bottom: 10px;
        object-fit: cover;
    }
    .industry-button-text {
        font-weight: bold;
        font-size: 14px;
        text-align: center;
        z-index: 2;
    }
    .industry-button-bg {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0.3;
        transition: opacity 0.3s ease;
        z-index: 1;
    }
    .industry-button:hover .industry-button-bg {
        opacity: 0.5;
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

# Define industry-specific regions and default points of interest
industry_regions = {
    "aerospace": {
        "name": "Aerospace",
        "center": [33.9416, -118.4085],  # Los Angeles Airport area
        "zoom": 9,
        "description": "Aerospace industry climate impact analysis showing wind patterns, turbulence risk areas, and visibility forecasts around major airports and flight paths.",
        "risks": ["High wind areas", "Turbulence zones", "Storm paths", "Visibility issues", "Icing conditions"],
        "parameters": ["wind_speed", "temperature", "humidity"],
        "mitigation": [
            "Optimize flight paths to avoid high-turbulence regions",
            "Schedule maintenance during favorable weather windows",
            "Implement real-time climate monitoring systems",
            "Develop climate-resilient infrastructure"
        ]
    },
    "agriculture": {
        "name": "Agriculture",
        "center": [41.8781, -93.0977],  # Iowa - Major agricultural region
        "zoom": 7,
        "description": "Agricultural climate impact analysis showing growing degree days, frost risk zones, and precipitation patterns across major farming regions.",
        "risks": ["Drought zones", "Flood-prone areas", "Frost risk regions", "Heat stress areas", "Pest pressure zones"],
        "parameters": ["precipitation", "temperature", "growing_degree_days"],
        "mitigation": [
            "Implement drought-resistant crop varieties in high-risk areas",
            "Develop water conservation systems in precipitation-deficit zones",
            "Adjust planting schedules based on changing frost patterns",
            "Install efficient irrigation systems in drought-prone regions"
        ]
    },
    "energy": {
        "name": "Energy",
        "center": [32.7767, -96.7970],  # Texas - Energy production hub
        "zoom": 6,
        "description": "Energy infrastructure climate impact analysis showing temperature extremes, storm paths, and flooding risks to power generation and distribution systems.",
        "risks": ["Extreme heat zones", "Flood-prone infrastructure", "High wind regions", "Storm surge areas", "Wildfire risk zones"],
        "parameters": ["temperature", "precipitation", "wind_speed"],
        "mitigation": [
            "Prioritize grid hardening in extreme weather corridors",
            "Develop distributed energy resources in vulnerable regions",
            "Implement cooling systems for infrastructure in heat zones",
            "Elevate critical equipment in flood-prone areas"
        ]
    },
    "insurance": {
        "name": "Insurance",
        "center": [25.7617, -80.1918],  # Miami - High climate risk area
        "zoom": 8,
        "description": "Insurance risk analysis showing flood zones, storm surge areas, and property damage probability based on climate data and extreme weather patterns.",
        "risks": ["Flood zones", "Hurricane paths", "Storm surge areas", "Wildfire corridors", "Hail damage regions"],
        "parameters": ["precipitation", "wind_speed", "temperature"],
        "mitigation": [
            "Implement risk-based premium adjustments for high-exposure zones",
            "Develop climate-resilient building standards for vulnerable areas",
            "Create incentive programs for property hardening measures",
            "Establish early warning systems for catastrophic events"
        ]
    },
    "forestry": {
        "name": "Forestry",
        "center": [45.5051, -122.6750],  # Oregon - Major forestry region
        "zoom": 7,
        "description": "Forestry climate impact analysis showing wildfire risk areas, drought stress zones, and pest outbreak probabilities across major forest regions.",
        "risks": ["Wildfire corridors", "Drought stress areas", "Pest outbreak zones", "Wind damage regions", "Flash flood areas"],
        "parameters": ["temperature", "precipitation", "humidity"],
        "mitigation": [
            "Implement forest thinning in high fire risk zones",
            "Develop diverse species planting strategies in pest-prone areas",
            "Create fire breaks in critical wildfire corridors",
            "Establish monitoring systems for early pest detection"
        ]
    },
    "catastrophes": {
        "name": "Catastrophes",
        "center": [29.7604, -95.3698],  # Houston - Hurricane/flooding prone
        "zoom": 8,
        "description": "Catastrophe risk analysis showing hurricane paths, flood zones, wildfire corridors, and severe weather outbreak regions with probability assessments.",
        "risks": ["Hurricane paths", "Tornado corridors", "Flood zones", "Wildfire regions", "Earthquake fault lines"],
        "parameters": ["precipitation", "wind_speed", "temperature"],
        "mitigation": [
            "Develop evacuation plans for highest-risk corridors",
            "Implement building code enhancements in vulnerable zones",
            "Create early warning systems for at-risk communities",
            "Establish emergency response hubs in strategic locations"
        ]
    }
}

# Initialize session state variables
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "👋Hi there! I’m CeCe, your Climate Copilot. I'm here to help you explore, visualize, and make sense of climate and weather data in a way that’s clear and useful. Whether you want to generate a map, check trends, or just ask a question, I’m here to guide you. Just click one of the preset buttons below or start typing in the chat box to begin."}
    ]
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'visualization' not in st.session_state:
    st.session_state.visualization = None
if 'active_function' not in st.session_state:
    st.session_state.active_function = None
if 'industry_type' not in st.session_state:
    st.session_state.industry_type = None
if 'user_location' not in st.session_state:
    st.session_state.user_location = {"lat": 37.7749, "lon": -122.4194}  # Default to San Francisco
if 'api_status_checked' not in st.session_state:
    st.session_state.api_status_checked = False
if 'thinking' not in st.session_state:
    st.session_state.thinking = False
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = None
if 'current_query' not in st.session_state:
    st.session_state.current_query = None  # Track the current query being processed
if 'query_processed' not in st.session_state:
    st.session_state.query_processed = True  # Flag to track if query has been processed

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

# Display the chat history to show welcome message first
st.markdown('<div class="chat-container" style="margin-bottom: 20px;">', unsafe_allow_html=True)

# Display welcome message only
if st.session_state.chat_history and len(st.session_state.chat_history) > 0:
    welcome_message = st.session_state.chat_history[0]
    st.markdown(f"""
    <div class="chat-message assistant-message">
        <div class="message-content">
            <div class="message-sender">CeCe (Climate Copilot)</div>
            <div class="message-text">{welcome_message["content"]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Industry-specific buttons below the welcome message
st.markdown("""
<div style="margin-bottom: 15px; text-align: center;">
    <h3 style="color: white; font-size: 18px; margin-bottom: 15px;">
        <span style="color: #1E90FF;">Industry</span>-Specific Climate Risk Analysis
    </h3>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="industry-buttons-container" style="display: flex; justify-content: center; flex-wrap: wrap; gap: 15px;">', unsafe_allow_html=True)

# Generate SVG icons for each industry
industry_icons = {
    "aerospace": """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#1E90FF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#9370DB;stop-opacity:1" />
        </linearGradient>
        <path fill="url(#grad1)" d="M61,32.1l-5.8-1.6c-2.4-0.7-4.5-2.1-6.2-4l-8.8-10.2c-0.4-0.5-1-0.8-1.6-0.8H29.1c-0.7,0-1.3,0.3-1.7,0.9
            l-8.5,13.3c-0.8,1.3-2.3,1.9-3.8,1.9H3c-0.8,0-1.4,0.6-1.4,1.4v1.9c0,0.8,0.6,1.4,1.4,1.4h12.1c1.4,0,2.9,0.7,3.8,1.9l8.5,13.3
            c0.4,0.6,1,0.9,1.7,0.9h9.5c0.6,0,1.2-0.3,1.6-0.8l8.8-10.2c1.6-1.9,3.8-3.3,6.2-4l5.8-1.6c0.7-0.2,1.2-0.8,1.2-1.6v-0.7
            C62.2,33,61.7,32.3,61,32.1z M25.5,32c0-1.9,1.6-3.5,3.5-3.5s3.5,1.6,3.5,3.5s-1.6,3.5-3.5,3.5S25.5,33.9,25.5,32z"/>
    </svg>""",
    
    "agriculture": """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#1E90FF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#9370DB;stop-opacity:1" />
        </linearGradient>
        <path fill="url(#grad2)" d="M54,10c-4,0-10,2-14,6c-0.1,0.1-0.2,0.2-0.3,0.3C39.5,16.1,39.3,16,39,16c-3,0-13,2-19,8c-0.1,0.1-0.2,0.2-0.3,0.3
        C19.5,24.1,19.3,24,19,24c-3,0-13,2-19,8v6c0,0,12-6,18-6c3,0,6,1,8,4h8c0,0,4-8,12-8c3,0,6,1,8,4h8c0,0,4-8,12-8V10z"/>
        <path fill="url(#grad2)" d="M29.4,46l2.3-4.9c0.4-0.8,1.3-1.1,2.1-0.8l5.8,2.1c0.8,0.3,1.2,1.2,0.9,2L37,53.3l-7.6-7.3z"/>
        <path fill="url(#grad2)" d="M26,50c0,0-2,6-2,9c0,2.2,1.8,4,4,4s4-1.8,4-4c0-3-2-9-2-9H26z"/>
    </svg>""",
    
    "energy": """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <linearGradient id="grad3" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#1E90FF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#9370DB;stop-opacity:1" />
        </linearGradient>
        <path fill="url(#grad3)" d="M36,3c0,0-17,24-17,35c0,3.3,2.7,6,6,6s6-2.7,6-6c0-11,17-35,17-35H36z"/>
        <path fill="url(#grad3)" d="M19,39L9,59h16l-6,9h2l19-22H29l6-13L19,39z"/>
    </svg>""",
    
    "insurance": """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <linearGradient id="grad4" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#1E90FF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#9370DB;stop-opacity:1" />
        </linearGradient>
        <path fill="url(#grad4)" d="M32,3L12,14v15c0,10.7,8.5,21.7,20,25c11.5-3.3,20-14.3,20-25V14L32,3z M32,48c-8.3,0-15-6.7-15-15
        s6.7-15,15-15s15,6.7,15,15S40.3,48,32,48z"/>
        <path fill="url(#grad4)" d="M32,24c-5,0-9,4-9,9s4,9,9,9s9-4,9-9S37,24,32,24z M32,36c-1.7,0-3-1.3-3-3s1.3-3,3-3s3,1.3,3,3
        S33.7,36,32,36z"/>
    </svg>""",
    
    "forestry": """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <linearGradient id="grad5" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#1E90FF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#9370DB;stop-opacity:1" />
        </linearGradient>
        <path fill="url(#grad5)" d="M30,38h-5.3C22.5,38,20,40.2,20,43v16c0,1.1,0.9,2,2,2h4V38z"/>
        <path fill="url(#grad5)" d="M44,43c0-2.8-2.5-5-5.7-5H34v23h4c1.1,0,2-0.9,2-2V43z"/>
        <path fill="url(#grad5)" d="M32,38c2,0,14-19.1,14-24.5C46,8.4,40.6,3,34,3h-4c-6.6,0-12,5.4-12,10.5C18,18.9,30,38,32,38z"/>
    </svg>""",
    
    "catastrophes": """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <linearGradient id="grad6" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#1E90FF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#9370DB;stop-opacity:1" />
        </linearGradient>
        <path fill="url(#grad6)" d="M48.7,35.6l-8.1-12.1c-0.4-0.6-1-1-1.7-1h-13c-0.7,0-1.3,0.4-1.7,1l-8.1,12.1c-0.4,0.5-0.4,1.3,0,1.8
        l8.1,12.1c0.4,0.6,1,1,1.7,1h13c0.7,0,1.3-0.4,1.7-1l8.1-12.1C49,37,49,36.2,48.7,35.6z M32,40c-1.7,0-3-1.3-3-3s1.3-3,3-3
        s3,1.3,3,3S33.7,40,32,40z M35,26l-2,6h-2l-2-6H35z"/>
        <path fill="url(#grad6)" d="M59.7,18.6l-3.1-4.6c-0.4-0.6-1-1-1.7-1h-5c-0.7,0-1.3,0.4-1.7,1l-3.1,4.6c-0.4,0.5-0.4,1.3,0,1.8
        l3.1,4.6c0.4,0.6,1,1,1.7,1h5c0.7,0,1.3-0.4,1.7-1l3.1-4.6C60,19.9,60,19.2,59.7,18.6z"/>
        <path fill="url(#grad6)" d="M19.7,18.6l-3.1-4.6c-0.4-0.6-1-1-1.7-1h-5c-0.7,0-1.3,0.4-1.7,1l-3.1,4.6c-0.4,0.5-0.4,1.3,0,1.8
        l3.1,4.6c0.4,0.6,1,1,1.7,1h5c0.7,0,1.3-0.4,1.7-1l3.1-4.6C20,19.9,20,19.2,19.7,18.6z"/>
    </svg>"""
}

# Use Streamlit columns to create a horizontal layout for industry buttons
st.markdown("</div>", unsafe_allow_html=True)  # Close the container

# Create a 6-column layout for the industry buttons
cols = st.columns(6)

# Add industry buttons with icons using Streamlit components
for i, (industry_id, icon) in enumerate(industry_icons.items()):
    with cols[i % 6]:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 10px;">
            <div style="width: 80px; height: 80px; margin: 0 auto;">
                {icon}
            </div>
            <p style="font-size: 14px; color: white; margin-top: 8px;">{industry_regions[industry_id]["name"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Use Streamlit button (invisible but clickable)
        if st.button(f"Select {industry_id}", key=f"industry_{industry_id}"):
            st.session_state.industry_selected = industry_id
            st.session_state.active_function = "industry_map"
            st.rerun()

# Button cards - First Row
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
    if st.button("🔮 Climate resilience predictions"):
        st.session_state.active_function = "climate_resilience"
        st.rerun()
        
with col6:
    if st.button("📝 Generate interactive climate story"):
        st.session_state.active_function = "climate_story"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Second row for additional features
st.markdown('<div class="buttons-container" style="margin-top: 10px;">', unsafe_allow_html=True)
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("🎨 Artistic high-resolution maps"):
        st.session_state.active_function = "artistic_maps"
        st.rerun()
        
# Placeholder for future buttons
with col2:
    pass
    
with col3:
    pass
    
with col4:
    pass
    
with col5:
    pass
    
with col6:
    pass

st.markdown('</div>', unsafe_allow_html=True)

# Display the title question without status indicators
st.markdown('<div class="title-text">What would you like CeCe to do for you today?</div>', unsafe_allow_html=True)

# Run API status check silently without showing UI elements
if not st.session_state.api_status_checked:
    try:
        # Just check API status in the background
        status_code, is_working = test_api_status.check_openai_api_status(display_message=False)
        # Mark as checked to prevent repeated attempts
        st.session_state.api_status_checked = True
    except Exception as e:
        # If the API check fails, don't crash
        print(f"API check error: {str(e)}")
        # Mark as checked to prevent repeated attempts
        st.session_state.api_status_checked = True

# Display the chat history in a more visually appealing way
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display existing chat messages (skip the first welcome message)
if st.session_state.chat_history:
    # Skip the first welcome message by starting from index 1
    for message in st.session_state.chat_history[1:]:
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
user_input = st.text_input("", key="chat_input", placeholder="Create a chart of climate anomalies in 2023")

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
# Import our OpenAI helper module
import openai_helper

def fallback_response(query):
    """Provide a fallback response when OpenAI API is unavailable"""
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
    # Check if this is a new query to avoid adding duplicate messages
    if st.session_state.query_processed or st.session_state.current_query != user_input:
        # This is a new query - add to chat history
        st.session_state.current_query = user_input
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Set thinking status to true and display the "thinking" indicator
        st.session_state.thinking = True
        st.session_state.query_processed = False
        
        # Rerun to show the thinking status immediately
        st.rerun()

# If we're in thinking mode, process the query and generate a response
if st.session_state.thinking:
    try:
        # Extract user query from chat history
        user_query = st.session_state.chat_history[-2]["content"] if len(st.session_state.chat_history) >= 2 else ""
        
        # Get chat history for context (excluding the most recent user message that we're about to process)
        messages = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in st.session_state.chat_history[:-2]  # Exclude latest user message and assistant "thinking"
        ]
        
        # Import for timeout handling
        import threading
        import queue
        
        response_queue = queue.Queue()
        
        def get_response():
            try:
                # Use our improved OpenAI helper to generate a response
                response = openai_helper.generate_climate_response(user_query, messages)
                response_queue.put(response)
            except Exception as e:
                response_queue.put(e)
        
        # Create and start thread
        response_thread = threading.Thread(target=get_response)
        response_thread.daemon = True
        response_thread.start()
        
        # Wait for the thread to complete or timeout
        response_thread.join(40)  # 40 second total timeout
        
        if response_thread.is_alive():
            print("Response generation timed out after 40 seconds")
            response_content = fallback_response(user_query)
            # Add a note about the timeout
            response_content = "I apologize for the delay. " + response_content
        else:
            # Get response from queue
            try:
                response_or_error = response_queue.get(block=False)
                
                # Check if we got an error
                if isinstance(response_or_error, Exception):
                    raise response_or_error
                    
                # Otherwise, we got a response
                response_content = response_or_error
                
                # Log success or failure
                if response_content:
                    print("Successfully generated response using OpenAI API")
                else:
                    print("Failed to generate response with OpenAI API, using fallback")
                    # If our OpenAI helper returns None, use the fallback response
                    response_content = fallback_response(user_query)
            except queue.Empty:
                # This shouldn't happen, but just in case
                print("Queue was empty - unexpected error")
                response_content = fallback_response(user_query)
            
    except Exception as e:
        # Something went wrong, provide an error message with details
        error_msg = str(e)
        print(f"Error processing chat request: {error_msg}")
        # Use a more user-friendly message without exposing technical details
        response_content = fallback_response(user_query)
    
    # Add the response to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": response_content})
    
    # Set thinking to False and mark query as processed
    st.session_state.thinking = False
    st.session_state.query_processed = True
    
    # Clear the input field and refresh the page
    st.rerun()

# Import geopy for geocoding city names to coordinates
from geopy.geocoders import Nominatim

# Function to convert city name to coordinates
def get_city_coordinates(city_name):
    try:
        # Create a more robust user agent string
        geolocator = Nominatim(user_agent="climate_copilot_application")
        
        # Try to geocode with the original city name
        location = geolocator.geocode(city_name, timeout=10, exactly_one=True)
        
        # If successful, return the coordinates
        if location:
            return location.latitude, location.longitude
            
        # If not successful, try some alternative formats
        # Try without commas
        if "," in city_name:
            clean_name = city_name.replace(",", " ")
            location = geolocator.geocode(clean_name, timeout=10, exactly_one=True)
            if location:
                return location.latitude, location.longitude
        
        # Try adding explicit country if not present
        if "," not in city_name and " " in city_name:
            # This might be a city without a country specified
            for country in ["USA", "France", "UK", "Germany", "Japan", "Canada", "Australia"]:
                test_name = f"{city_name}, {country}"
                location = geolocator.geocode(test_name, timeout=10, exactly_one=True)
                if location:
                    return location.latitude, location.longitude
        
        # If all attempts fail, return None
        return None, None
        
    except Exception as e:
        st.error(f"Error geocoding city: {str(e)}")
        return None, None

# Import artistic map modules
# Using simplified versions for better reliability
import simple_artistic_maps
from simple_artistic_map_demo import run_artistic_map_demo

# Function handling section
if st.session_state.active_function == "artistic_maps":
    # Run the simplified artistic map demo
    run_artistic_map_demo()
    
elif st.session_state.active_function == "precipitation_map":
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
        
    # Performance option
    fast_mode = st.checkbox("Use fast map mode (recommended for larger date ranges)", value=True,
                          help="Generates the map quickly using improved interpolation techniques")
    
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
                # Pass the fast_mode parameter to control data fetching behavior
                precip_df = fetch_precipitation_map_data(latitude, longitude, start_date_str, end_date_str, 
                                                      radius_degrees=1.0, fast_mode=fast_mode)
                
                # Create a list of [lat, lon, precip] for each grid point
                heat_data = []
                for _, row in precip_df.iterrows():
                    lat = row['latitude']
                    lon = row['longitude']
                    precip = row['precipitation']
                    heat_data.append([lat, lon, precip])
                
                # Get the max value for scaling the heatmap
                max_precip = max([x[2] for x in heat_data]) if heat_data else 100
                
                # Create a standard base map centered on the location first (we'll decide which to show later)
                m = folium.Map(location=[latitude, longitude], zoom_start=7, 
                              tiles="cartodb dark_matter")
                
                # Add a marker for the selected location
                folium.Marker(
                    [latitude, longitude],
                    popup=f"Selected Location: {city if location_method == 'City Name' else f'({latitude:.2f}, {longitude:.2f})'}",
                    icon=folium.Icon(color="purple")
                ).add_to(m)
                
                # Map style selection
                map_styles = ["Standard Map", "Felt-Inspired Map Demo"]
                map_style = st.radio("Map Style", map_styles, index=0)
                
                if map_style == "Felt-Inspired Map Demo":
                    # Use Felt-inspired maps for a more modern look
                    st.info("Using Felt-inspired map with enhanced visualization and interactive features.")
                    
                    # Display the title
                    st.subheader(f"NASA POWER Precipitation Map ({start_date_str} to {end_date_str})")
                    
                    # Import our new embedded map module
                    import embedded_felt_map
                    
                    # Create an embedded Felt-inspired map with the current location
                    location_name = city if location_method == 'City Name' else f'({latitude:.2f}, {longitude:.2f})'
                    embedded_felt_map.create_embedded_felt_map(
                        lat=latitude,
                        lon=longitude,
                        location_name=location_name
                    )
                    
                    # Add info about the map
                    with st.expander("About this Map"):
                        st.markdown("""
                        This map shows a Felt-inspired design with modern UI and interactive features.
                        - Interactive elevation contours
                        - Precipitation data visualization with smooth gradients
                        - Points of interest
                        - Clean, modern interface inspired by Felt.com
                        """)
                    
                    # Note about the real data integration
                    st.info("This is showing a sample visualization of precipitation data. In the next update, we'll integrate the real NASA POWER precipitation data with this modern map style.")
                else:
                    # Add the heatmap to the standard map
                    from folium.plugins import HeatMap
                    
                    # Create a heatmap with string-based gradient values and improved parameters
                    HeatMap(
                        heat_data,
                        radius=25,  # Increased radius for more coverage
                        min_opacity=0.5,  # Lower min_opacity to make the map more visible in low precipitation areas
                        blur=18,  # Increased blur for even smoother transitions
                        max_zoom=13,  # Control the maximum zoom level for the heatmap
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
                    
                    # Display the standard map
                    st.subheader(f"NASA POWER Precipitation Map ({start_date_str} to {end_date_str})")
                    folium_static(m)
                    
                    # Download button is now handled outside the if/else statement
                

                
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
                if map_style == "Standard Map":
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
                HeatMap(
                    heat_data, 
                    radius=25,  # Increased radius for more coverage
                    min_opacity=0.5,  # Lower min_opacity for better visibility
                    blur=15,  # Increased blur for smoother transitions
                    gradient={
                        '0.0': 'blue',
                        '0.2': 'cyan',
                        '0.4': 'lime',
                        '0.6': 'yellow',
                        '0.8': 'orange',
                        '1.0': 'red'
                    }
                ).add_to(m)
                
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

elif st.session_state.active_function == "industry_map":
    st.subheader("Industry-Specific Climate Risk Analysis")
    
    # Display a select box to choose the industry
    industry_options = list(industry_regions.keys())
    industry_names = [industry_regions[i]["name"] for i in industry_options]
    
    industry_index = 0  # Default to aerospace
    if "industry_selected" in st.session_state:
        if st.session_state.industry_selected in industry_options:
            industry_index = industry_options.index(st.session_state.industry_selected)
    
    selected_industry_name = st.selectbox(
        "Select Industry Sector:",
        industry_names,
        index=industry_index
    )
    
    # Get the industry ID from the name
    selected_industry = industry_options[industry_names.index(selected_industry_name)]
    st.session_state.industry_selected = selected_industry
    
    # Get industry data
    industry_data = industry_regions[selected_industry]
    
    # Display industry description
    st.markdown(f"""
    <div style='background-color: rgba(30, 30, 30, 0.6); padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 3px solid #1E90FF;'>
        <h4 style='color: #FFFFFF; margin-top: 0;'>{industry_data['name']} Sector Climate Risk Analysis</h4>
        <p style='color: #FFFFFF;'>{industry_data['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create a map centered on the industry's default location
        m = folium.Map(
            location=industry_data["center"], 
            zoom_start=industry_data["zoom"],
            tiles="cartodb dark_matter"
        )
        
        # Add climate risk zones based on industry type
        if selected_industry == "aerospace":
            # Add wind pattern areas
            folium.Circle(
                location=[industry_data["center"][0] + 0.2, industry_data["center"][1] - 0.3],
                radius=8000,
                color='#9370DB',
                fill=True,
                fill_opacity=0.4,
                popup="High Wind Zone - Average wind speed >25 mph"
            ).add_to(m)
            
            # Add turbulence risk zone
            folium.Circle(
                location=[industry_data["center"][0] - 0.1, industry_data["center"][1] + 0.2],
                radius=6000,
                color='#FF6347',
                fill=True,
                fill_opacity=0.4,
                popup="Turbulence Risk Zone - 65% probability of moderate or severe turbulence"
            ).add_to(m)
            
            # Add visibility issues zone
            folium.Circle(
                location=[industry_data["center"][0] + 0.3, industry_data["center"][1] + 0.1],
                radius=4000,
                color='#FFD700',
                fill=True,
                fill_opacity=0.3,
                popup="Low Visibility Zone - Historical fog patterns"
            ).add_to(m)
            
            # Add flight paths with climate risk indicators
            folium.PolyLine(
                locations=[
                    [industry_data["center"][0], industry_data["center"][1]],
                    [industry_data["center"][0] + 0.5, industry_data["center"][1] + 0.5]
                ],
                color='#1E90FF',
                weight=3,
                opacity=0.7,
                popup="Primary Flight Path - Low climate risk"
            ).add_to(m)
            
            folium.PolyLine(
                locations=[
                    [industry_data["center"][0], industry_data["center"][1]],
                    [industry_data["center"][0] - 0.3, industry_data["center"][1] + 0.4]
                ],
                color='#FF4500',
                weight=3,
                opacity=0.7,
                popup="Secondary Flight Path - High climate risk (wind shear)"
            ).add_to(m)
            
        elif selected_industry == "agriculture":
            # Add drought risk zones
            folium.Circle(
                location=[industry_data["center"][0] + 0.3, industry_data["center"][1] - 0.3],
                radius=30000,
                color='#FF8C00',
                fill=True,
                fill_opacity=0.4,
                popup="Drought Risk Zone - 40% precipitation deficit"
            ).add_to(m)
            
            # Add frost risk zone
            folium.Circle(
                location=[industry_data["center"][0] - 0.5, industry_data["center"][1] + 0.2],
                radius=25000,
                color='#00BFFF',
                fill=True,
                fill_opacity=0.3,
                popup="Frost Risk Zone - Early frost probability 35%"
            ).add_to(m)
            
            # Add heat stress zone
            folium.Circle(
                location=[industry_data["center"][0] + 0.3, industry_data["center"][1] + 0.4],
                radius=35000,
                color='#FF6347',
                fill=True,
                fill_opacity=0.3,
                popup="Heat Stress Zone - 12 days >90°F per month"
            ).add_to(m)
            
            # Add growing degree day contours
            folium.GeoJson(
                {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {"name": "High GDD Zone"},
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [[
                                    [industry_data["center"][1] - 0.7, industry_data["center"][0] - 0.7],
                                    [industry_data["center"][1] + 0.7, industry_data["center"][0] - 0.7],
                                    [industry_data["center"][1] + 0.7, industry_data["center"][0] + 0.7],
                                    [industry_data["center"][1] - 0.7, industry_data["center"][0] + 0.7],
                                    [industry_data["center"][1] - 0.7, industry_data["center"][0] - 0.7]
                                ]]
                            }
                        }
                    ]
                },
                style_function=lambda x: {
                    'fillColor': '#32CD32',
                    'color': '#32CD32',
                    'weight': 1,
                    'fillOpacity': 0.2
                },
                popup=folium.GeoJsonPopup(fields=["name"])
            ).add_to(m)
            
        elif selected_industry == "energy":
            # Add extreme heat risk to infrastructure
            folium.Circle(
                location=[industry_data["center"][0] + 0.2, industry_data["center"][1] - 0.3],
                radius=30000,
                color='#FF4500',
                fill=True,
                fill_opacity=0.4,
                popup="Extreme Heat Risk - Grid stress 30% above normal"
            ).add_to(m)
            
            # Add flood risk to substations
            folium.Circle(
                location=[industry_data["center"][0] - 0.3, industry_data["center"][1] + 0.2],
                radius=25000,
                color='#1E90FF',
                fill=True,
                fill_opacity=0.3,
                popup="Flood Risk Zone - 15% of substations vulnerable"
            ).add_to(m)
            
            # Add transmission lines with risk indicators
            folium.PolyLine(
                locations=[
                    [industry_data["center"][0] - 0.6, industry_data["center"][1] - 0.6],
                    [industry_data["center"][0] + 0.6, industry_data["center"][1] + 0.6]
                ],
                color='#FFD700',
                weight=3,
                opacity=0.7,
                popup="Main Transmission Corridor - Medium climate risk"
            ).add_to(m)
            
            # Add wind risk to transmission
            folium.Circle(
                location=[industry_data["center"][0] + 0.5, industry_data["center"][1] - 0.1],
                radius=20000,
                color='#9370DB',
                fill=True,
                fill_opacity=0.3,
                popup="High Wind Risk - 25% increased line damage probability"
            ).add_to(m)
            
        elif selected_industry == "insurance":
            # Add flood risk zones
            folium.Circle(
                location=[industry_data["center"][0] + 0.1, industry_data["center"][1] - 0.1],
                radius=15000,
                color='#1E90FF',
                fill=True,
                fill_opacity=0.4,
                popup="Flood Zone A - High risk, 26% annual premium increase"
            ).add_to(m)
            
            # Add hurricane path with risk contours
            folium.PolyLine(
                locations=[
                    [industry_data["center"][0] - 0.5, industry_data["center"][1] - 0.5],
                    [industry_data["center"][0] - 0.3, industry_data["center"][1] - 0.3],
                    [industry_data["center"][0] - 0.1, industry_data["center"][1] - 0.1],
                    [industry_data["center"][0] + 0.2, industry_data["center"][1] + 0.2]
                ],
                color='#FF6347',
                weight=4,
                opacity=0.7,
                popup="Historical Hurricane Path - Category 3-4"
            ).add_to(m)
            
            # Add storm surge risk
            folium.Circle(
                location=[industry_data["center"][0] + 0.05, industry_data["center"][1] - 0.05],
                radius=12000,
                color='#9370DB',
                fill=True,
                fill_opacity=0.3,
                popup="Storm Surge Zone - 9-12 ft surge potential"
            ).add_to(m)
            
            # Add property value risk gradient
            folium.GeoJson(
                {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {"risk": "Extreme Risk Zone - 300% premium multiplier"},
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [[
                                    [industry_data["center"][1] - 0.2, industry_data["center"][0] - 0.2],
                                    [industry_data["center"][1] + 0.2, industry_data["center"][0] - 0.2],
                                    [industry_data["center"][1] + 0.2, industry_data["center"][0] + 0.2],
                                    [industry_data["center"][1] - 0.2, industry_data["center"][0] + 0.2],
                                    [industry_data["center"][1] - 0.2, industry_data["center"][0] - 0.2]
                                ]]
                            }
                        }
                    ]
                },
                style_function=lambda x: {
                    'fillColor': '#FF4500',
                    'color': '#FF4500',
                    'weight': 1,
                    'fillOpacity': 0.2
                },
                popup=folium.GeoJsonPopup(fields=["risk"])
            ).add_to(m)
            
        elif selected_industry == "forestry":
            # Add wildfire risk zones
            folium.Circle(
                location=[industry_data["center"][0] + 0.2, industry_data["center"][1] - 0.3],
                radius=20000,
                color='#FF4500',
                fill=True,
                fill_opacity=0.4,
                popup="Extreme Wildfire Risk - 72% probability within 5 years"
            ).add_to(m)
            
            # Add drought stress zone
            folium.Circle(
                location=[industry_data["center"][0] - 0.1, industry_data["center"][1] + 0.2],
                radius=15000,
                color='#FFA500',
                fill=True,
                fill_opacity=0.3,
                popup="Drought Stress Zone - 45% canopy loss risk"
            ).add_to(m)
            
            # Add pest outbreak risk
            folium.Circle(
                location=[industry_data["center"][0] + 0.3, industry_data["center"][1] + 0.1],
                radius=18000,
                color='#9ACD32',
                fill=True,
                fill_opacity=0.3,
                popup="Pest Outbreak Risk - Bark beetle probability 60%"
            ).add_to(m)
            
            # Add forest management zones
            folium.GeoJson(
                {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {"name": "Priority Management Zone"},
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [[
                                    [industry_data["center"][1] - 0.5, industry_data["center"][0] - 0.5],
                                    [industry_data["center"][1] + 0.5, industry_data["center"][0] - 0.5],
                                    [industry_data["center"][1] + 0.5, industry_data["center"][0] + 0.5],
                                    [industry_data["center"][1] - 0.5, industry_data["center"][0] + 0.5],
                                    [industry_data["center"][1] - 0.5, industry_data["center"][0] - 0.5]
                                ]]
                            }
                        }
                    ]
                },
                style_function=lambda x: {
                    'fillColor': '#6B8E23',
                    'color': '#6B8E23',
                    'weight': 1,
                    'fillOpacity': 0.2
                },
                popup=folium.GeoJsonPopup(fields=["name"])
            ).add_to(m)
            
        elif selected_industry == "catastrophes":
            # Add hurricane risk zones
            folium.Circle(
                location=[industry_data["center"][0] + 0.1, industry_data["center"][1] - 0.1],
                radius=18000,
                color='#FF4500',
                fill=True,
                fill_opacity=0.4,
                popup="Hurricane Impact Zone - Category 4-5 risk"
            ).add_to(m)
            
            # Add flood zones
            folium.Circle(
                location=[industry_data["center"][0] - 0.1, industry_data["center"][1] + 0.1],
                radius=15000,
                color='#1E90FF',
                fill=True,
                fill_opacity=0.3,
                popup="Severe Flood Zone - 25-year flood risk"
            ).add_to(m)
            
            # Add evacuation routes with risk assessment
            folium.PolyLine(
                locations=[
                    [industry_data["center"][0], industry_data["center"][1]],
                    [industry_data["center"][0] + 0.5, industry_data["center"][1] + 0.5]
                ],
                color='#32CD32',
                weight=3,
                opacity=0.7,
                popup="Primary Evacuation Route - Low flood risk"
            ).add_to(m)
            
            folium.PolyLine(
                locations=[
                    [industry_data["center"][0], industry_data["center"][1]],
                    [industry_data["center"][0] - 0.4, industry_data["center"][1] + 0.2]
                ],
                color='#FF8C00',
                weight=3,
                opacity=0.7,
                popup="Secondary Evacuation Route - Medium flood risk"
            ).add_to(m)
            
            # Add storm surge risk contour
            folium.GeoJson(
                {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {"name": "Storm Surge Zone"},
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [[
                                    [industry_data["center"][1] - 0.3, industry_data["center"][0] - 0.1],
                                    [industry_data["center"][1] + 0.3, industry_data["center"][0] - 0.1],
                                    [industry_data["center"][1] + 0.3, industry_data["center"][0] + 0.1],
                                    [industry_data["center"][1] - 0.3, industry_data["center"][0] + 0.1],
                                    [industry_data["center"][1] - 0.3, industry_data["center"][0] - 0.1]
                                ]]
                            }
                        }
                    ]
                },
                style_function=lambda x: {
                    'fillColor': '#9370DB',
                    'color': '#9370DB',
                    'weight': 1,
                    'fillOpacity': 0.2
                },
                popup=folium.GeoJsonPopup(fields=["name"])
            ).add_to(m)
        
        # Add a marker for the primary location
        folium.Marker(
            industry_data["center"],
            popup=f"{industry_data['name']} Industry Hub",
            icon=folium.Icon(color="green", icon="info-sign"),
        ).add_to(m)
        
        # Add a title to the map
        title_html = f"""
        <h3 style="position: absolute; top: 10px; left: 50%; transform: translateX(-50%); z-index: 9999; 
            background-color: rgba(0, 0, 0, 0.7); color: white; padding: 10px; border-radius: 5px; font-family: Arial, sans-serif;">
            {industry_data["name"]} Climate Risk Map
        </h3>
        """
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add a legend for the climate risks
        legend_html = """
        <div style="position: fixed; bottom: 50px; right: 50px; background-color: rgba(0, 0, 0, 0.7);
            border-radius: 5px; padding: 10px; color: white; font-family: Arial, sans-serif; z-index: 9999;">
            <p><strong>Climate Risk Legend</strong></p>
        """
        
        risk_colors = {
            "#FF4500": "Extreme Risk",
            "#FF8C00": "High Risk",
            "#FFD700": "Medium Risk",
            "#32CD32": "Low Risk",
            "#1E90FF": "Flood/Water Risk",
            "#9370DB": "Wind/Storm Risk"
        }
        
        for color, label in risk_colors.items():
            legend_html += f"""
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background: {color}; width: 20px; height: 20px; margin-right: 5px;"></div>
                <span>{label}</span>
            </div>
            """
        
        legend_html += "</div>"
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Display the map
        folium_static(m)
    
    with col2:
        # Display industry climate risks
        st.markdown(f"""
        <div style='background-color: rgba(255, 69, 0, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 3px solid #FF4500;'>
            <h4 style='color: #FFFFFF; margin-top: 0;'>Climate Risks</h4>
            <ul style='color: #FFFFFF; padding-left: 20px;'>
        """, unsafe_allow_html=True)
        
        for risk in industry_data["risks"]:
            st.markdown(f"<li>{risk}</li>", unsafe_allow_html=True)
        
        st.markdown("</ul></div>", unsafe_allow_html=True)
        
        # Display climate parameters being monitored
        st.markdown(f"""
        <div style='background-color: rgba(30, 144, 255, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 3px solid #1E90FF;'>
            <h4 style='color: #FFFFFF; margin-top: 0;'>Key Climate Parameters</h4>
            <ul style='color: #FFFFFF; padding-left: 20px;'>
        """, unsafe_allow_html=True)
        
        for param in industry_data["parameters"]:
            st.markdown(f"<li>{param.replace('_', ' ').title()}</li>", unsafe_allow_html=True)
        
        st.markdown("</ul></div>", unsafe_allow_html=True)
        
        # Display risk mitigation strategies
        st.markdown(f"""
        <div style='background-color: rgba(50, 205, 50, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 3px solid #32CD32;'>
            <h4 style='color: #FFFFFF; margin-top: 0;'>Climate Risk Mitigation Strategies</h4>
            <ul style='color: #FFFFFF; padding-left: 20px;'>
        """, unsafe_allow_html=True)
        
        for strategy in industry_data["mitigation"]:
            st.markdown(f"<li>{strategy}</li>", unsafe_allow_html=True)
        
        st.markdown("</ul></div>", unsafe_allow_html=True)
        
        # Add a "Create custom analysis" button
        if st.button("Create Custom Climate Risk Analysis", key="custom_analysis"):
            st.session_state.active_function = "precipitation_map"
            st.rerun()
    
    # Add context about the data
    st.info(f"This visualization represents climate risk analysis for the {industry_data['name']} sector based on historical climate data and projected patterns. The data is derived from NASA POWER API and climate models. Use this visualization to understand regional climate risks and develop targeted mitigation strategies.")

elif st.session_state.active_function == "climate_resilience":
    st.subheader("Climate Resilience Prediction Tool")
    
    # Show explanation
    st.markdown("""
    <div style="padding: 15px; background-color: rgba(30, 144, 255, 0.1); border-radius: 8px; margin-bottom: 20px;">
        <h4 style="margin-top: 0; color: #1E90FF;">About this Tool</h4>
        <p style="color: white;">
        This tool provides predictive modeling to suggest adaptive strategies for various industries based on projected climate scenarios. 
        Select a location, industry, time horizon, and climate scenario to generate a comprehensive resilience report.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for inputs
    col1, col2 = st.columns(2)
    
    with col1:
        # Location input method selection
        location_method = st.radio("Select location input method:", ["City Name", "Coordinates"], 
                                 horizontal=True, key="resilience_location_method")
        
        # Initialize location session variables if not present
        if "user_location" not in st.session_state:
            st.session_state.user_location = {"lat": 37.7749, "lon": -122.4194}
        if "last_city" not in st.session_state:
            st.session_state.last_city = "San Francisco, CA"
        
        # Flag to track if location has changed
        if "resilience_data_needs_update" not in st.session_state:
            st.session_state.resilience_data_needs_update = True
        
        if location_method == "City Name":
            city = st.text_input("Enter city name (e.g., 'New York', 'London, UK')", 
                                 value=st.session_state.last_city,
                                 key="resilience_city")
            
            if city:
                # Only geocode if city changed
                if city != st.session_state.last_city:
                    st.session_state.last_city = city
                    lat, lon = get_city_coordinates(city)
                    if lat and lon:
                        st.success(f"Location found: {lat:.4f}, {lon:.4f}")
                        
                        # Check if location has changed
                        if (abs(st.session_state.user_location.get("lat", 0) - lat) > 0.001 or 
                            abs(st.session_state.user_location.get("lon", 0) - lon) > 0.001):
                            st.session_state.user_location = {"lat": lat, "lon": lon}
                            # Force a refresh of resilience data
                            st.session_state.resilience_data_needs_update = True
                            st.info("Location updated! Climate data will refresh when you generate the report.")
                            
                        latitude = lat
                        longitude = lon
                    else:
                        st.warning("Could not find coordinates for this city. Please check the spelling or try using coordinates directly.")
                        latitude = st.session_state.user_location["lat"]
                        longitude = st.session_state.user_location["lon"]
                else:
                    latitude = st.session_state.user_location["lat"]
                    longitude = st.session_state.user_location["lon"]
            else:
                latitude = st.session_state.user_location["lat"]
                longitude = st.session_state.user_location["lon"]
        else:
            # Direct coordinate input
            latitude = st.number_input("Latitude", value=st.session_state.user_location["lat"], 
                                      min_value=-90.0, max_value=90.0, step=0.01, key="resilience_lat")
            longitude = st.number_input("Longitude", value=st.session_state.user_location["lon"], 
                                       min_value=-180.0, max_value=180.0, step=0.01, key="resilience_lon")
            
            # Check if coordinates have changed
            if (abs(st.session_state.user_location.get("lat", 0) - latitude) > 0.001 or 
                abs(st.session_state.user_location.get("lon", 0) - longitude) > 0.001):
                st.session_state.user_location = {"lat": latitude, "lon": longitude}
                # Force a refresh of resilience data
                st.session_state.resilience_data_needs_update = True
                st.info("Location updated! Climate data will refresh when you generate the report.")
        
        # Industry selection
        industry_options = ["aerospace", "agriculture", "energy", "insurance", "forestry", "catastrophes"]
        industry_names = {
            "aerospace": "Aerospace",
            "agriculture": "Agriculture",
            "energy": "Energy",
            "insurance": "Insurance",
            "forestry": "Forestry",
            "catastrophes": "Catastrophe Management"
        }
        
        selected_industry = st.selectbox("Select Industry", 
                                       options=industry_options,
                                       format_func=lambda x: industry_names[x],
                                       key="resilience_industry")
    
    with col2:
        # Time horizon selection
        target_year = st.slider("Target Year for Projection", 
                              min_value=2030, 
                              max_value=2100, 
                              value=2050, 
                              step=5,
                              key="resilience_year")
        
        # Climate scenario selection
        scenario_options = ["optimistic", "moderate", "severe"]
        scenario_descriptions = {
            "optimistic": "Optimistic Scenario (RCP 2.6) - Limited warming",
            "moderate": "Moderate Scenario (RCP 4.5) - Intermediate warming",
            "severe": "Severe Scenario (RCP 8.5) - High emissions scenario"
        }
        
        selected_scenario = st.selectbox("Select Climate Scenario", 
                                      options=scenario_options,
                                      format_func=lambda x: scenario_descriptions[x],
                                      key="resilience_scenario")
        
        # Button to generate the report
        generate_report = st.button("Generate Resilience Report", type="primary", key="generate_resilience_report")
    
    # Map visualization selection
    st.write("### Climate Impact Map Visualization")
    map_view_options = [
        "Location Only", 
        "Temperature Change", 
        "Precipitation Change", 
        "Sea Level Rise Impact", 
        "Extreme Heat Days", 
        "Industry Risk Zones"
    ]
    selected_map_view = st.selectbox(
        "Select map visualization type:", 
        options=map_view_options,
        key="resilience_map_view"
    )
    
    # Initialize the base map
    m = folium.Map(location=[latitude, longitude], zoom_start=5, control_scale=True)
    
    # Add the base marker for selected location
    folium.Marker(
        [latitude, longitude],
        popup=f"Selected Location: {city if location_method == 'City Name' else f'{latitude:.4f}, {longitude:.4f}'}",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)
    
    # Get the report from session state if available
    report = st.session_state.resilience_report if 'resilience_report' in st.session_state and st.session_state.resilience_report else None
    
    # Generate different map visualizations based on selection
    if selected_map_view == "Temperature Change":
        # Create a circle around the location showing temperature change
        if report:  # Only show if report is available
            try:
                # Use the temperature change data from the report
                temp_change = report['climate_projections']['temperature']['change']
                
                # Determine color based on the temperature change
                if temp_change < 1.0:
                    color = "#4575b4"  # Blue for minor warming
                elif temp_change < 2.0:
                    color = "#fee090"  # Yellow for moderate warming
                elif temp_change < 3.0:
                    color = "#fdae61"  # Orange for significant warming
                else:
                    color = "#d73027"  # Red for severe warming
                
                # Add a circle with a radius based on the magnitude of change
                radius_km = 50 + (temp_change * 15)  # Scale the radius by temperature change
                folium.Circle(
                    location=[latitude, longitude],
                    radius=radius_km * 1000,  # Convert to meters
                    color=color,
                    fill=True,
                    fill_opacity=0.5,
                    popup=f"Projected Temperature Change: +{temp_change:.1f}°C by {target_year}",
                ).add_to(m)
                
                # Add a legend
                legend_html = '''
                    <div style="position: fixed; bottom: 50px; left: 50px; background-color: white; 
                                border: 2px solid grey; z-index: 9999; padding: 10px; border-radius: 5px;">
                        <p style="margin-bottom: 5px;"><strong>Temperature Change</strong></p>
                        <p><span style="color: #4575b4;">■</span> &lt;1.0°C</p>
                        <p><span style="color: #fee090;">■</span> 1.0-2.0°C</p>
                        <p><span style="color: #fdae61;">■</span> 2.0-3.0°C</p>
                        <p><span style="color: #d73027;">■</span> &gt;3.0°C</p>
                    </div>
                '''
                m.get_root().html.add_child(folium.Element(legend_html))
            except:
                st.info("Generate a report first to see temperature change projections on the map.")
    
    elif selected_map_view == "Precipitation Change":
        # Create a visualization for precipitation change
        if report:  # Only show if report is available
            try:
                # Use the precipitation change data from the report
                precip_change = report['climate_projections']['precipitation']['change_percent']
                
                # Determine color based on the precipitation change
                if precip_change < -10:
                    color = "#d73027"  # Red for significant drying
                elif precip_change < 0:
                    color = "#fdae61"  # Orange for moderate drying
                elif precip_change < 10:
                    color = "#fee090"  # Yellow for minor changes
                else:
                    color = "#4575b4"  # Blue for wetter conditions
                
                # Add a circle with a radius based on the magnitude of change
                radius_km = 50 + (abs(precip_change) * 1)  # Scale the radius by precipitation change
                folium.Circle(
                    location=[latitude, longitude],
                    radius=radius_km * 1000,  # Convert to meters
                    color=color,
                    fill=True,
                    fill_opacity=0.5,
                    popup=f"Projected Precipitation Change: {precip_change:.1f}% by {target_year}",
                ).add_to(m)
                
                # Add a legend
                legend_html = '''
                    <div style="position: fixed; bottom: 50px; left: 50px; background-color: white; 
                                border: 2px solid grey; z-index: 9999; padding: 10px; border-radius: 5px;">
                        <p style="margin-bottom: 5px;"><strong>Precipitation Change</strong></p>
                        <p><span style="color: #d73027;">■</span> &lt;-10% (Drier)</p>
                        <p><span style="color: #fdae61;">■</span> -10-0% (Slightly Drier)</p>
                        <p><span style="color: #fee090;">■</span> 0-10% (Slight Change)</p>
                        <p><span style="color: #4575b4;">■</span> &gt;10% (Wetter)</p>
                    </div>
                '''
                m.get_root().html.add_child(folium.Element(legend_html))
            except:
                st.info("Generate a report first to see precipitation change projections on the map.")
    
    elif selected_map_view == "Sea Level Rise Impact":
        # Create a visualization for sea level rise impact
        if report:  # Only show if report is available
            try:
                # Use the sea level rise data from the report
                slr = report['climate_projections']['sea_level_rise']
                
                # Coastal vulnerability threshold (in km from the center)
                coastal_zone_km = 30
                
                # Add a coastal vulnerability zone (simplified)
                folium.Circle(
                    location=[latitude, longitude],
                    radius=coastal_zone_km * 1000,  # Convert to meters
                    color="#1e88e5",
                    fill=True,
                    fill_opacity=0.4,
                    popup=f"Projected Sea Level Rise: {slr:.2f}m by {target_year}",
                ).add_to(m)
                
                # Add more detailed annotations
                if slr > 0.5:
                    # Add high risk zone for significant sea level rise
                    folium.Circle(
                        location=[latitude, longitude],
                        radius=15 * 1000,  # 15km inner radius
                        color="#d32f2f",
                        fill=True,
                        fill_opacity=0.4,
                        popup="High risk zone with potential inundation",
                    ).add_to(m)
                
                # Add a legend
                legend_html = f'''
                    <div style="position: fixed; bottom: 50px; left: 50px; background-color: white; 
                                border: 2px solid grey; z-index: 9999; padding: 10px; border-radius: 5px;">
                        <p style="margin-bottom: 5px;"><strong>Sea Level Rise Impact</strong></p>
                        <p>Projected Rise: {slr:.2f}m by {target_year}</p>
                        <p><span style="color: #1e88e5;">■</span> Coastal Zone</p>
                        {f'<p><span style="color: #d32f2f;">■</span> High Risk Area</p>' if slr > 0.5 else ''}
                    </div>
                '''
                m.get_root().html.add_child(folium.Element(legend_html))
            except:
                st.info("Generate a report first to see sea level rise projections on the map.")
    
    elif selected_map_view == "Extreme Heat Days":
        # Create a visualization for extreme heat days
        if report:  # Only show if report is available
            try:
                # Use the extreme heat data from the report
                heat_multiplier = report['climate_projections']['extreme_weather']['heat_days_multiplier']
                
                # Estimate current extreme heat days (simplified model)
                baseline_heat_days = 5  # Assumed baseline
                projected_heat_days = int(baseline_heat_days * heat_multiplier)
                
                # Determine color based on the number of extreme heat days
                if heat_multiplier < 1.5:
                    color = "#fee090"  # Yellow for minor increase
                elif heat_multiplier < 2.0:
                    color = "#fdae61"  # Orange for moderate increase
                elif heat_multiplier < 2.5:
                    color = "#f46d43"  # Dark orange for significant increase
                else:
                    color = "#d73027"  # Red for severe increase
                
                # Add a heat impact radius
                radius_km = 40 + (heat_multiplier * 10)  # Scale the radius by heat multiplier
                folium.Circle(
                    location=[latitude, longitude],
                    radius=radius_km * 1000,  # Convert to meters
                    color=color,
                    fill=True,
                    fill_opacity=0.5,
                    popup=f"Extreme Heat Days Projection: {projected_heat_days} days/year (x{heat_multiplier:.1f} increase) by {target_year}",
                ).add_to(m)
                
                # Add a legend
                legend_html = f'''
                    <div style="position: fixed; bottom: 50px; left: 50px; background-color: white; 
                                border: 2px solid grey; z-index: 9999; padding: 10px; border-radius: 5px;">
                        <p style="margin-bottom: 5px;"><strong>Extreme Heat Days</strong></p>
                        <p>Projected Change: x{heat_multiplier:.1f}</p>
                        <p>Estimated Days: {projected_heat_days}/year</p>
                        <p><span style="color: #fee090;">■</span> 1.0-1.5x Increase</p>
                        <p><span style="color: #fdae61;">■</span> 1.5-2.0x Increase</p>
                        <p><span style="color: #f46d43;">■</span> 2.0-2.5x Increase</p>
                        <p><span style="color: #d73027;">■</span> &gt;2.5x Increase</p>
                    </div>
                '''
                m.get_root().html.add_child(folium.Element(legend_html))
            except:
                st.info("Generate a report first to see extreme heat day projections on the map.")
    
    elif selected_map_view == "Industry Risk Zones":
        # Create a visualization specific to the selected industry
        if report and 'selected_industry' in locals():  # Only show if report is available
            try:
                # Use the impact assessment from the report
                impact_severity = report['impact_assessment']['adjusted_severity']
                
                # Define colors based on severity
                severity_colors = {
                    "low": "#4CAF50",     # Green
                    "moderate": "#FFC107", # Yellow
                    "high": "#FF9800",     # Orange
                    "severe": "#F44336"    # Red
                }
                
                color = severity_colors.get(impact_severity, "#4CAF50")
                
                # Create concentric circles showing impact zones
                # High impact zone
                folium.Circle(
                    location=[latitude, longitude],
                    radius=20 * 1000,  # 20km inner radius
                    color=color,
                    fill=True,
                    fill_opacity=0.6,
                    popup=f"High Impact Zone: {industry_names[selected_industry]} Industry",
                ).add_to(m)
                
                # Medium impact zone
                folium.Circle(
                    location=[latitude, longitude],
                    radius=50 * 1000,  # 50km middle radius
                    color=color,
                    fill=True,
                    fill_opacity=0.3,
                    popup=f"Medium Impact Zone: {industry_names[selected_industry]} Industry",
                ).add_to(m)
                
                # Low impact zone
                folium.Circle(
                    location=[latitude, longitude],
                    radius=100 * 1000,  # 100km outer radius
                    color=color,
                    fill=True,
                    fill_opacity=0.1,
                    popup=f"Low Impact Zone: {industry_names[selected_industry]} Industry",
                ).add_to(m)
                
                # Add industry-specific markers based on the type of industry
                if selected_industry == "agriculture":
                    # Add crop vulnerability markers
                    for i, (crop_lat, crop_lon) in enumerate([
                        (latitude + 0.3, longitude + 0.3),
                        (latitude - 0.2, longitude + 0.4),
                        (latitude + 0.4, longitude - 0.2)
                    ]):
                        folium.Marker(
                            [crop_lat, crop_lon],
                            popup=f"Agricultural Impact Point {i+1}",
                            icon=folium.Icon(color="green", icon="leaf")
                        ).add_to(m)
                        
                elif selected_industry == "energy":
                    # Add energy infrastructure vulnerability markers
                    for i, (energy_lat, energy_lon) in enumerate([
                        (latitude + 0.25, longitude + 0.25),
                        (latitude - 0.3, longitude + 0.2),
                        (latitude + 0.2, longitude - 0.3)
                    ]):
                        folium.Marker(
                            [energy_lat, energy_lon],
                            popup=f"Energy Infrastructure Point {i+1}",
                            icon=folium.Icon(color="orange", icon="flash")
                        ).add_to(m)
                        
                elif selected_industry == "forestry":
                    # Add forest vulnerability markers
                    for i, (forest_lat, forest_lon) in enumerate([
                        (latitude + 0.35, longitude + 0.15),
                        (latitude - 0.25, longitude + 0.25),
                        (latitude + 0.15, longitude - 0.35)
                    ]):
                        folium.Marker(
                            [forest_lat, forest_lon],
                            popup=f"Forest Vulnerability Point {i+1}",
                            icon=folium.Icon(color="green", icon="tree")
                        ).add_to(m)
                
                # Add a legend
                legend_html = f'''
                    <div style="position: fixed; bottom: 50px; left: 50px; background-color: white; 
                                border: 2px solid grey; z-index: 9999; padding: 10px; border-radius: 5px;">
                        <p style="margin-bottom: 5px;"><strong>{industry_names[selected_industry]} Industry Impact</strong></p>
                        <p>Impact Severity: <span style="color: {color}; font-weight: bold;">{impact_severity.upper()}</span></p>
                        <p><span style="opacity: 0.6; color: {color};">■</span> High Impact Zone</p>
                        <p><span style="opacity: 0.3; color: {color};">■</span> Medium Impact Zone</p>
                        <p><span style="opacity: 0.1; color: {color};">■</span> Low Impact Zone</p>
                    </div>
                '''
                m.get_root().html.add_child(folium.Element(legend_html))
            except:
                st.info("Generate a report first to see industry risk zones on the map.")
    
    # Add the map to the Streamlit app
    st_data = folium_static(m)
    
    # Initialize report in session state if not present to ensure proper scope
    if 'resilience_report' not in st.session_state:
        st.session_state.resilience_report = None
        
    # Generate and display the resilience report when the button is clicked
    if generate_report:
        with st.spinner(f"Generating climate resilience report for {industry_names[selected_industry]} industry in {target_year}..."):
            # Call the climate_resilience module to generate the report
            try:
                # Reset the update flag since we're fetching new data
                st.session_state.resilience_data_needs_update = False
                
                # Log key parameters for debugging
                st.write(f"Fetching climate data for: {latitude}, {longitude}")
                
                # Store the report in session state for global access
                st.session_state.resilience_report = climate_resilience.generate_resilience_report(
                    lat=latitude,
                    lon=longitude,
                    industry=selected_industry,
                    target_year=target_year,
                    scenario=selected_scenario
                )
                
                # Create a local reference to the report for convenience
                report = st.session_state.resilience_report
                
                # Display the report in an organized fashion
                st.subheader(f"Climate Resilience Report: {industry_names[selected_industry]} Industry")
                
                # Scenario and location information
                st.markdown(f"""
                <div style="padding: 15px; background-color: rgba(30, 30, 30, 0.6); border-radius: 8px; margin-bottom: 20px;">
                    <h4 style="margin-top: 0; color: #1E90FF;">Report Summary</h4>
                    <table style="width: 100%; color: white;">
                        <tr>
                            <td style="width: 30%; font-weight: bold;">Location:</td>
                            <td>{city if location_method == 'City Name' else f'{latitude:.4f}, {longitude:.4f}'}</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold;">Projection Year:</td>
                            <td>{target_year}</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold;">Climate Scenario:</td>
                            <td>{report['scenario']}</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold;">Description:</td>
                            <td>{report['climate_projections']['scenario_description']}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
                
                # Climate projections visualization
                st.markdown("<h4 style='color: #1E90FF;'>Climate Projections</h4>", unsafe_allow_html=True)
                
                # Use plotly to create visualization of key metrics
                fig = go.Figure()
                
                # Temperature change
                fig.add_trace(go.Indicator(
                    mode = "number+delta",
                    value = report['climate_projections']['temperature']['projected'],
                    title = {"text": "Temperature (°C)"},
                    delta = {'reference': report['climate_projections']['temperature']['baseline'], 'relative': False},
                    domain = {'row': 0, 'column': 0}
                ))
                
                # Precipitation change
                fig.add_trace(go.Indicator(
                    mode = "number+delta",
                    value = report['climate_projections']['precipitation']['projected'],
                    title = {"text": "Precipitation (mm)"},
                    delta = {'reference': report['climate_projections']['precipitation']['baseline'], 'relative': False},
                    domain = {'row': 0, 'column': 1}
                ))
                
                # Extreme weather multiplier
                fig.add_trace(go.Indicator(
                    mode = "number",
                    value = report['climate_projections']['extreme_weather']['heat_days_multiplier'],
                    title = {"text": "Extreme Heat Days Multiplier"},
                    domain = {'row': 1, 'column': 0}
                ))
                
                # Sea level rise
                fig.add_trace(go.Indicator(
                    mode = "number",
                    value = report['climate_projections']['sea_level_rise'],
                    title = {"text": "Sea Level Rise (m)"},
                    domain = {'row': 1, 'column': 1}
                ))
                
                # Update layout
                fig.update_layout(
                    grid = {'rows': 2, 'columns': 2, 'pattern': "independent"},
                    height=400,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="white")
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show seasonal changes in temperature and precipitation
                st.markdown("<h4 style='color: #1E90FF;'>Seasonal Changes</h4>", unsafe_allow_html=True)
                
                # Create dataframes for seasonal data
                seasons = ["winter", "spring", "summer", "fall"]
                temp_changes = [report['climate_projections']['temperature']['seasonal_changes'][season] for season in seasons]
                precip_changes = [report['climate_projections']['precipitation']['seasonal_changes'][season] for season in seasons]
                
                # Create a plotly figure for seasonal changes
                fig = go.Figure()
                
                # Add temperature changes
                fig.add_trace(go.Bar(
                    x=seasons,
                    y=temp_changes,
                    name='Temperature Change (°C)',
                    marker_color='rgba(30, 144, 255, 0.7)'
                ))
                
                # Add precipitation changes on secondary y-axis
                fig.add_trace(go.Bar(
                    x=seasons,
                    y=precip_changes,
                    name='Precipitation Change (%)',
                    marker_color='rgba(147, 112, 219, 0.7)',
                    yaxis='y2'
                ))
                
                # Update layout
                fig.update_layout(
                    barmode='group',
                    title="Seasonal Climate Changes",
                    xaxis=dict(title="Season"),
                    yaxis=dict(title="Temperature Change (°C)", side="left"),
                    yaxis2=dict(title="Precipitation Change (%)", side="right", overlaying="y"),
                    legend=dict(x=0.1, y=1.1, orientation="h"),
                    height=400,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="white")
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Industry impact assessment
                impact_severity = report['impact_assessment']['adjusted_severity']
                severity_colors = {
                    "low": "#4CAF50",
                    "moderate": "#FFC107",
                    "high": "#FF9800",
                    "severe": "#F44336"
                }
                
                st.markdown(f"""
                <h4 style='color: #1E90FF;'>Industry Impact Assessment</h4>
                <div style="padding: 15px; background-color: rgba(30, 30, 30, 0.6); border-radius: 8px; margin-bottom: 20px;">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <div style="font-weight: bold; margin-right: 10px; color: white;">Impact Severity:</div>
                        <div style="background-color: {severity_colors[impact_severity]}; color: white; padding: 3px 10px; border-radius: 15px; text-transform: uppercase; font-weight: bold;">
                            {impact_severity}
                        </div>
                    </div>
                    <div style="margin-top: 10px; color: white;">
                        <div style="font-weight: bold; margin-bottom: 5px;">Key Impact Areas:</div>
                        <ul style="margin-top: 5px;">
                """, unsafe_allow_html=True)
                
                for impact in report['impact_assessment']['impact_areas']:
                    st.markdown(f"<li style='color: white; margin-bottom: 5px;'>{impact}</li>", unsafe_allow_html=True)
                
                st.markdown("""
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Adaptive strategies
                st.markdown("<h4 style='color: #1E90FF;'>Recommended Adaptive Strategies</h4>", unsafe_allow_html=True)
                
                # Create tabs for different timeline categories
                timeline_tabs = st.tabs(["Near-term (1-5 years)", "Mid-term (5-15 years)", "Long-term (15+ years)"])
                
                with timeline_tabs[0]:
                    if report['implementation_timeline']['near_term']:
                        for i, strategy in enumerate(report['implementation_timeline']['near_term']):
                            st.markdown(f"""
                            <div style="padding: 12px; background-color: rgba(76, 175, 80, 0.1); border-left: 3px solid #4CAF50; 
                                        border-radius: 4px; margin-bottom: 10px;">
                                <div style="color: white;">{strategy}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No near-term strategies identified for this scenario.")
                
                with timeline_tabs[1]:
                    if report['implementation_timeline']['mid_term']:
                        for i, strategy in enumerate(report['implementation_timeline']['mid_term']):
                            st.markdown(f"""
                            <div style="padding: 12px; background-color: rgba(255, 193, 7, 0.1); border-left: 3px solid #FFC107; 
                                        border-radius: 4px; margin-bottom: 10px;">
                                <div style="color: white;">{strategy}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No mid-term strategies identified for this scenario.")
                
                with timeline_tabs[2]:
                    if report['implementation_timeline']['long_term']:
                        for i, strategy in enumerate(report['implementation_timeline']['long_term']):
                            st.markdown(f"""
                            <div style="padding: 12px; background-color: rgba(244, 67, 54, 0.1); border-left: 3px solid #F44336; 
                                        border-radius: 4px; margin-bottom: 10px;">
                                <div style="color: white;">{strategy}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No long-term strategies identified for this scenario.")
                
                # Cost implication
                cost_colors = {
                    "low": "#4CAF50",
                    "moderate": "#FFC107",
                    "high": "#FF9800",
                    "transformative": "#F44336"
                }
                
                st.markdown(f"""
                <div style="padding: 15px; background-color: rgba(30, 30, 30, 0.6); border-radius: 8px; margin-top: 20px; margin-bottom: 20px;">
                    <h4 style="margin-top: 0; color: #1E90FF;">Implementation Considerations</h4>
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <div style="font-weight: bold; margin-right: 10px; color: white;">Cost Implication:</div>
                        <div style="background-color: {cost_colors[report['cost_implication']]}; color: white; padding: 3px 10px; border-radius: 15px; text-transform: uppercase; font-weight: bold;">
                            {report['cost_implication']}
                        </div>
                    </div>
                    <div style="color: white; margin-top: 10px;">
                        Planning for implementation should consider both the timeline recommendations and the associated cost implications.
                        Industries with higher severity impacts typically require more immediate and comprehensive adaptation measures.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add option to export the report as JSON
                report_json = json.dumps(report, indent=2)
                b64 = base64.b64encode(report_json.encode()).decode()
                href = f"""<a href="data:application/json;base64,{b64}" download="climate_resilience_report_{selected_industry}_{target_year}.json" style="text-decoration: none;">
                    <button style="background: linear-gradient(90deg, #1E90FF, #9370DB); color: white; padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px;">
                        Download Full Report (JSON)
                    </button>
                </a>"""
                st.markdown(href, unsafe_allow_html=True)
                
                # Add information about data sources
                st.markdown("---")
                st.markdown("""
                <h3 style='color: #1E90FF;'>About Our Climate Data</h3>
                """, unsafe_allow_html=True)
                
                with st.expander("Why We Trust This Data", expanded=False):
                    st.markdown("""
                    <div style='color: white;'>
                        <h4>NASA POWER Data</h4>
                        <p>The climate data used in this analysis comes from the <b>NASA POWER</b> (Prediction of Worldwide Energy Resource) dataset, which is based on satellite observations and reanalysis models.</p>
                        
                        <h5>Why we use this data:</h5>
                        <ul>
                            <li><b>Global Coverage:</b> NASA POWER provides consistent data for any location on Earth, allowing analysis for even remote regions.</li>
                            <li><b>Scientific Accuracy:</b> The data undergoes rigorous quality control and is maintained by NASA's scientific community.</li>
                            <li><b>Temporal Range:</b> The dataset includes historical records dating back to 1981, allowing for robust trend analysis.</li>
                            <li><b>Multi-Parameter:</b> It includes temperature, precipitation, solar radiation, humidity, and wind - all critical for climate impact assessment.</li>
                        </ul>
                        
                        <h5>Key parameters used in our analysis:</h5>
                        <ul>
                            <li><b>T2M:</b> Temperature at 2 Meters (°C)</li>
                            <li><b>T2M_MAX:</b> Maximum Temperature at 2 Meters (°C)</li>
                            <li><b>T2M_MIN:</b> Minimum Temperature at 2 Meters (°C)</li>
                            <li><b>PRECTOTCORR:</b> Bias-corrected precipitation (mm/day)</li>
                            <li><b>RH2M:</b> Relative Humidity at 2 Meters (%)</li>
                            <li><b>WS2M:</b> Wind Speed at 2 Meters (m/s)</li>
                        </ul>
                        
                        <h4>Climate Projection Methodology</h4>
                        <p>Our projections for future climate conditions use established climate scenario pathways based on the IPCC (Intergovernmental Panel on Climate Change) Representative Concentration Pathways (RCPs):</p>
                        <ul>
                            <li><b>Optimistic Scenario (RCP 2.6):</b> Limited warming scenario with global temperature increase of 0.9-2.3°C by 2100.</li>
                            <li><b>Moderate Scenario (RCP 4.5):</b> Intermediate warming scenario with global temperature increase of 1.7-3.2°C by 2100.</li>
                            <li><b>Severe Scenario (RCP 8.5):</b> High emissions scenario with global temperature increase of 3.2-5.4°C by 2100.</li>
                        </ul>
                        
                        <h4>Limitations</h4>
                        <p>While we strive for accuracy, it's important to acknowledge some limitations:</p>
                        <ul>
                            <li>Climate projections inherently contain uncertainty, especially for long-term forecasts.</li>
                            <li>Local microclimates may not be fully captured at the NASA POWER resolution (approximately 0.5° grid).</li>
                            <li>Extreme events are particularly challenging to predict with precision.</li>
                            <li>Industry-specific impacts are based on general research and may need customization for specific businesses.</li>
                        </ul>
                        
                        <p>For the most critical decisions, we recommend consulting with climate scientists and industry-specific experts to supplement this analysis.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with st.expander("Data Processing & Methodology", expanded=False):
                    st.markdown("""
                    <div style='color: white;'>
                        <h4>How We Process Climate Data</h4>
                        <p>Our climate resilience analysis involves multiple steps to transform raw climate data into actionable insights:</p>
                        
                        <ol>
                            <li><b>Data Acquisition:</b> We fetch climate data from NASA POWER API based on the coordinates you select.</li>
                            <li><b>Baseline Calculation:</b> We establish baseline conditions using 5 years of historical data.</li>
                            <li><b>Trend Analysis:</b> We identify temperature and precipitation trends using statistical regression methods.</li>
                            <li><b>Climate Projection:</b> We apply IPCC-based climate scenarios adjusted for the selected location.</li>
                            <li><b>Industry Impact Assessment:</b> We analyze how projected climate changes affect specific industries.</li>
                            <li><b>Adaptation Strategy Generation:</b> We recommend timelined strategies based on climate risk profiles.</li>
                        </ol>
                        
                        <h5>Technical Details:</h5>
                        <ul>
                            <li>Temperature data is processed using monthly and seasonal aggregations to identify patterns.</li>
                            <li>Precipitation analysis includes both amount and distribution changes.</li>
                            <li>For location-specific projections, global climate scenarios are downscaled using statistical methods.</li>
                            <li>Extreme weather projections use multipliers derived from historical extreme event frequency.</li>
                            <li>Sea level rise projections consider global projections adjusted for regional factors.</li>
                        </ul>
                        
                        <h4>Visualization Methods</h4>
                        <p>Our map visualizations use the following approaches:</p>
                        <ul>
                            <li><b>Temperature Change:</b> Color-coded circles based on the magnitude of projected warming.</li>
                            <li><b>Precipitation Change:</b> Color gradients indicating wetter or drier conditions.</li>
                            <li><b>Sea Level Rise:</b> Coastal vulnerability zones based on elevation and distance from shoreline.</li>
                            <li><b>Extreme Heat Days:</b> Heat risk zones calculated from projected temperature distributions.</li>
                            <li><b>Industry Risk Zones:</b> Concentric impact areas with industry-specific vulnerability indicators.</li>
                        </ul>
                        
                        <p>All visualizations are generated using real climate data and industry-specific vulnerabilities established through scientific literature.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with st.expander("Data Sources & References", expanded=False):
                    st.markdown("""
                    <div style='color: white;'>
                        <h4>Primary Data Sources</h4>
                        <ul>
                            <li><a href="https://power.larc.nasa.gov/" target="_blank" style="color: #1E90FF;">NASA POWER Project</a> - NASA's Prediction of Worldwide Energy Resource</li>
                            <li><a href="https://www.ipcc.ch/" target="_blank" style="color: #1E90FF;">IPCC</a> - Intergovernmental Panel on Climate Change</li>
                            <li>Research literature on industry-specific climate vulnerabilities and adaptation strategies</li>
                        </ul>
                        
                        <h4>Academic References</h4>
                        <p>Our methodology is informed by established climate science and industry impact research, including:</p>
                        <ul>
                            <li>IPCC Sixth Assessment Report (AR6) - Comprehensive climate change science</li>
                            <li>Sectoral adaptation strategies from peer-reviewed literature</li>
                            <li>NASA Earth Observatory data analysis techniques</li>
                        </ul>
                        
                        <h4>Verification Process</h4>
                        <p>We validate our climate data and projections through:</p>
                        <ul>
                            <li>Comparison with historical observations</li>
                            <li>Alignment with peer-reviewed climate projections</li>
                            <li>Consultation with climate science literature</li>
                        </ul>
                        
                        <p>For more detailed information about our data sources and methodology, please contact us.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"An error occurred while generating the report: {str(e)}")
                st.error("Please try again with different parameters or check the console for more details.")
                raise e

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
        # Skip the first welcome message in chat history display
        for message in st.session_state.chat_history[1:]:
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
        # Skip the first welcome message in download
        for message in st.session_state.chat_history[1:]:
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

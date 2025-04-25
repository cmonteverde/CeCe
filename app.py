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

# Custom CSS for styling
css = """
<style>
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
    }
    .logo-container {
        margin-bottom: 20px;
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
    }
    .buttons-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        margin-bottom: 30px;
    }
    .button-card {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
        cursor: pointer;
        text-align: center;
        transition: all 0.3s;
        flex: 1;
        min-width: 150px;
    }
    .button-card:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    .chat-box {
        margin-top: 30px;
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
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Add topographic background pattern
st.markdown("""
<div class="bg-container">
    <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <pattern id="topo" patternUnits="userSpaceOnUse" width="1000" height="1000">
                <path d="M0,0 Q250,150 500,0 T1000,0" stroke="#4B3EFF" stroke-width="1" fill="none" opacity="0.3" transform="translate(0, 50)"/>
                <path d="M0,0 Q250,150 500,0 T1000,0" stroke="#4B3EFF" stroke-width="1" fill="none" opacity="0.3" transform="translate(0, 100)"/>
                <path d="M0,0 Q250,150 500,0 T1000,0" stroke="#4B3EFF" stroke-width="1" fill="none" opacity="0.3" transform="translate(0, 150)"/>
                <path d="M0,0 Q250,150 500,0 T1000,0" stroke="#4B3EFF" stroke-width="1" fill="none" opacity="0.3" transform="translate(0, 200)"/>
                <path d="M0,0 Q250,150 500,0 T1000,0" stroke="#4B3EFF" stroke-width="1" fill="none" opacity="0.3" transform="translate(0, 250)"/>
                <path d="M0,0 Q250,150 500,0 T1000,0" stroke="#4B3EFF" stroke-width="1" fill="none" opacity="0.3" transform="translate(0, 300)"/>
                <path d="M0,0 Q250,150 500,0 T1000,0" stroke="#4B3EFF" stroke-width="1" fill="none" opacity="0.3" transform="translate(0, 350)"/>
                <path d="M0,0 Q250,150 500,0 T1000,0" stroke="#4B3EFF" stroke-width="1" fill="none" opacity="0.3" transform="translate(0, 400)"/>
            </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#topo)"/>
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

# Logo and Avatar section
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.markdown("""
    <div class="logo-container">
        <svg width="120" height="120" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#1E90FF;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#9370DB;stop-opacity:1" />
                </linearGradient>
            </defs>
            <path d="M100,40 C70,40 45,60 45,85 C45,100 55,115 70,120 L70,140 C70,145 75,150 80,150 L120,150 C125,150 130,145 130,140 L130,120 C145,115 155,100 155,85 C155,60 130,40 100,40 Z" fill="url(#logoGradient)"/>
            <circle cx="150" cy="50" r="15" fill="url(#logoGradient)"/>
            <path d="M145,35 L155,25 M160,45 L170,35 M155,60 L165,70" stroke="url(#logoGradient)" stroke-width="4"/>
            <text x="50" y="190" font-family="Arial" font-size="24" fill="url(#logoGradient)">CeCe</text>
        </svg>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="avatar-container">
        <svg width="60" height="60" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="avatarGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#1E90FF;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#9370DB;stop-opacity:1" />
                </linearGradient>
            </defs>
            <circle cx="100" cy="100" r="90" fill="#1E1E1E" stroke="url(#avatarGradient)" stroke-width="5"/>
            <path d="M100,40 C70,40 45,60 45,85 C45,100 55,115 70,120 L70,140 C70,145 75,150 80,150 L120,150 C125,150 130,145 130,140 L130,120 C145,115 155,100 155,85 C155,60 130,40 100,40 Z" fill="url(#avatarGradient)"/>
            <circle cx="150" cy="50" r="15" fill="url(#avatarGradient)"/>
            <path d="M145,35 L155,25 M160,45 L170,35 M155,60 L165,70" stroke="url(#avatarGradient)" stroke-width="4"/>
        </svg>
        <div class="avatar-title">CECE: YOUR CLIMATE & WEATHER AGENT</div>
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

# Main chat input
st.markdown('<div class="title-text">What would you like CeCe to do for you today?</div>', unsafe_allow_html=True)
user_input = st.text_input("", key="chat_input", placeholder="Type here!")

# Process user input
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Since we don't have the RAG system working yet, provide a default response
    response = "I'm CeCe, your Climate Copilot. I'd love to help you with that! Currently, my AI features are being set up. In the meantime, you can try out the preset buttons above for climate data visualizations and analysis."
    
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Clear the input field
    st.rerun()

# Function handling section
if st.session_state.active_function == "precipitation_map":
    st.subheader("Precipitation Map for Your Region")
    
    # Location input
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
        
        # Location input
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

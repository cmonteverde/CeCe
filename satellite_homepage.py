"""
Satellite Map Homepage for Climate Copilot

This module creates a full-screen satellite map homepage similar to Felt.com
with the Climate Copilot interface overlaid on top.
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import base64

def get_logo_base64():
    """Get the Climate Copilot logo as base64"""
    try:
        with open("attached_assets/CeCe_Climate Copilot_logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        try:
            with open("public/avatar_fixed.png", "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            try:
                with open("assets/logo.png", "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except:
                return None

def create_satellite_homepage():
    """
    Create a full-screen satellite map homepage with Climate Copilot interface
    """
    
    # Minimal styling to preserve scrollability
    st.markdown("""
    <style>
    .main > div {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .block-container {
        padding: 1rem;
        max-width: 100%;
    }
    
    .satellite-homepage {
        position: relative;
        height: 100vh;
        width: 100vw;
        margin: 0;
        padding: 0;
    }
    
    .overlay-header {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: linear-gradient(180deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 50%, transparent 100%);
        padding: 20px 40px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .logo-image {
        width: 50px;
        height: 50px;
        border-radius: 8px;
    }
    
    .logo-text {
        color: white;
        font-size: 24px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .header-nav {
        display: flex;
        gap: 30px;
        align-items: center;
    }
    
    .nav-item {
        color: white;
        text-decoration: none;
        font-size: 16px;
        font-weight: 500;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        cursor: pointer;
        transition: color 0.3s ease;
    }
    
    .nav-item:hover {
        color: #64B5F6;
    }
    
    .cta-button {
        background: linear-gradient(135deg, #1E88E5, #1565C0);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 6px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
        transition: all 0.3s ease;
    }
    
    .cta-button:hover {
        background: linear-gradient(135deg, #1565C0, #0D47A1);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 136, 229, 0.4);
    }
    
    .hero-overlay {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 1000;
        text-align: center;
        color: white;
        background: rgba(0, 0, 0, 0.6);
        padding: 40px 60px;
        border-radius: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .hero-title {
        font-size: 48px;
        font-weight: bold;
        margin-bottom: 20px;
        background: linear-gradient(135deg, #64B5F6, #1E88E5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none;
    }
    
    .hero-subtitle {
        font-size: 24px;
        margin-bottom: 30px;
        color: #E3F2FD;
        font-weight: 300;
    }
    
    .hero-description {
        font-size: 18px;
        margin-bottom: 40px;
        color: #BBDEFB;
        line-height: 1.6;
        max-width: 600px;
    }
    
    .hero-buttons {
        display: flex;
        gap: 20px;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .hero-button {
        background: linear-gradient(135deg, #1E88E5, #1565C0);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 6px 20px rgba(30, 136, 229, 0.3);
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-block;
    }
    
    .hero-button:hover {
        background: linear-gradient(135deg, #1565C0, #0D47A1);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(30, 136, 229, 0.4);
    }
    
    .hero-button.secondary {
        background: transparent;
        border: 2px solid #64B5F6;
        color: #64B5F6;
    }
    
    .hero-button.secondary:hover {
        background: #64B5F6;
        color: white;
    }
    
    .feature-pills {
        position: absolute;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .feature-pill {
        background: rgba(255, 255, 255, 0.9);
        color: #1565C0;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 500;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    @media (max-width: 768px) {
        .hero-overlay {
            padding: 30px 20px;
            margin: 0 20px;
        }
        
        .hero-title {
            font-size: 36px;
        }
        
        .hero-subtitle {
            font-size: 20px;
        }
        
        .hero-description {
            font-size: 16px;
        }
        
        .overlay-header {
            padding: 15px 20px;
        }
        
        .header-nav {
            display: none;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show logo and title first
    logo_base64 = get_logo_base64()
    if logo_base64:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(f"data:image/png;base64,{logo_base64}", width=150)
            st.markdown("<h1 style='text-align: center; color: #1E88E5;'>Climate CoPilot</h1>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #1E88E5;'>Climate CoPilot</h1>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; font-size: 18px; margin-bottom: 30px;'>AI-Powered Climate Intelligence Platform</p>", unsafe_allow_html=True)
    
    # Create the base satellite map with dark styling
    m = folium.Map(
        location=[20.0, 0.0],  # Global view centered on equator
        zoom_start=2,
        tiles=None,
        zoomControl=True,
        scrollWheelZoom=True,
        doubleClickZoom=True,
        dragging=True
    )
    
    # Add dark-themed base map
    folium.TileLayer(
        tiles='https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png',
        attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>',
        name='Dark Base',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add climate data layer - temperature anomalies
    try:
        import climate_data_sources
        temp_data = climate_data_sources.generate_global_temperature_grid(resolution=5)
        
        # Add temperature data points to map
        for _, row in temp_data.iterrows():
            color = 'red' if row['temperature'] > 0 else 'blue'
            opacity = min(abs(row['temperature']) / 2.0, 1.0)
            
            folium.CircleMarker(
                location=[float(row['lat']), float(row['lon'])],
                radius=3,
                color=color,
                fillColor=color,
                fillOpacity=opacity * 0.7,
                popup=f"Temperature Anomaly: {row['temperature']:.1f}°C",
                tooltip=f"Temp: {row['temperature']:.1f}°C"
            ).add_to(m)
            
    except Exception as e:
        st.warning(f"Could not load climate data: {e}")
    
    # Add country boundaries for context
    folium.TileLayer(
        tiles='https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Boundaries',
        overlay=True,
        control=True,
        opacity=0.3
    ).add_to(m)
    
    # Add legend for climate data
    st.markdown("""
    <div style="background: rgba(0,0,0,0.8); color: white; padding: 15px; border-radius: 10px; margin: 20px 0;">
        <h4 style="margin: 0 0 10px 0; color: #64B5F6;">Global Temperature Anomalies</h4>
        <div style="display: flex; align-items: center; gap: 20px;">
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 12px; height: 12px; background: red; border-radius: 50%;"></div>
                <span>Above Average</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 12px; height: 12px; background: blue; border-radius: 50%;"></div>
                <span>Below Average</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the scrollable map
    map_data = st_folium(
        m, 
        height=600,
        width=None,
        returned_objects=["last_clicked"],
        key="satellite_homepage_map"
    )
    
    # Add chat interface below the map
    st.markdown("---")
    st.markdown("### Ask CeCe about Climate Data")
    
    # Initialize chat history if not exists
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hi! I'm CeCe, your Climate Copilot. Ask me about climate patterns, weather data, or explore the temperature anomalies shown on the map above."}
        ]
    
    # Display chat messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about climate data, weather patterns, or map features..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing climate data..."):
                try:
                    import openai_helper
                    response = openai_helper.get_openai_response(prompt)
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    fallback = f"I can help you understand the climate data shown on the map. The red dots indicate areas with above-average temperatures, while blue dots show below-average temperatures. You can click on any dot to see specific temperature anomaly values. What would you like to know more about?"
                    st.write(fallback)
                    st.session_state.chat_history.append({"role": "assistant", "content": fallback})
    
    return map_data

if __name__ == "__main__":
    create_satellite_homepage()
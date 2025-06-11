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
    
    # Remove default Streamlit styling
    st.markdown("""
    <style>
    .main > div {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    
    .block-container {
        padding: 0rem;
        max-width: 100%;
    }
    
    header[data-testid="stHeader"] {
        display: none;
    }
    
    .stApp {
        margin: 0;
        padding: 0;
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
    
    # Create the base satellite map
    # Default to a nice global view
    m = folium.Map(
        location=[40.0, -20.0],  # Atlantic Ocean view
        zoom_start=3,
        tiles=None,
        zoomControl=False,
        scrollWheelZoom=True,
        doubleClickZoom=True,
        dragging=True
    )
    
    # Add satellite imagery
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False,
        control=False
    ).add_to(m)
    
    # Add a subtle label overlay
    folium.TileLayer(
        tiles='https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Labels',
        overlay=True,
        control=False,
        opacity=0.6
    ).add_to(m)
    
    # Get logo for header
    logo_base64 = get_logo_base64()
    logo_img = f'<img src="data:image/png;base64,{logo_base64}" class="logo-image">' if logo_base64 else ''
    
    # Create the overlay HTML
    overlay_html = f"""
    <div class="satellite-homepage">
        <div class="overlay-header">
            <div class="logo-section">
                {logo_img}
                <div class="logo-text">Climate CoPilot</div>
            </div>
            <div class="header-nav">
                <div class="nav-item">Climate Data</div>
                <div class="nav-item">Visualizations</div>
                <div class="nav-item">Analysis</div>
                <div class="nav-item">About</div>
                <button class="cta-button" onclick="document.querySelector('[data-testid=stSidebar]').style.display='block'">Get Started</button>
            </div>
        </div>
        
        <div class="hero-overlay">
            <div class="hero-title">Climate Intelligence,<br>Everywhere</div>
            <div class="hero-subtitle">Powered by Real-Time Earth Data</div>
            <div class="hero-description">
                Explore climate patterns, analyze environmental trends, and make data-driven decisions 
                with our AI-powered climate analysis platform. Built on authentic NASA and global climate datasets.
            </div>
            <div class="hero-buttons">
                <button class="hero-button" onclick="window.scrollTo(0, document.body.scrollHeight)">Start Exploring</button>
                <button class="hero-button secondary" onclick="document.querySelector('[data-testid=stSidebar]').style.display='block'">View Tools</button>
            </div>
        </div>
        
        <div class="feature-pills">
            <div class="feature-pill">🌡️ Temperature Analysis</div>
            <div class="feature-pill">🌧️ Precipitation Maps</div>
            <div class="feature-pill">🗺️ Terrain Contours</div>
            <div class="feature-pill">📊 Climate Trends</div>
            <div class="feature-pill">🤖 AI Insights</div>
        </div>
    </div>
    """
    
    # Display the map with overlay
    map_data = st_folium(
        m, 
        height=700,
        width=None,
        returned_objects=["last_clicked"],
        key="satellite_homepage_map"
    )
    
    # Add overlay after map
    st.markdown(overlay_html, unsafe_allow_html=True)
    
    # Add JavaScript for interactions
    st.markdown("""
    <script>
    // Hide Streamlit elements
    const style = document.createElement('style');
    style.textContent = `
        .main .block-container {
            padding: 0 !important;
        }
        footer {
            display: none !important;
        }
        .stApp > header {
            display: none !important;
        }
    `;
    document.head.appendChild(style);
    
    // Scroll to tools when button is clicked
    function scrollToTools() {
        const toolsSection = document.querySelector('.climate-tools-section');
        if (toolsSection) {
            toolsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
    </script>
    """, unsafe_allow_html=True)
    
    return map_data

if __name__ == "__main__":
    create_satellite_homepage()
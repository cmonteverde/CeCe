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
    
    # Prominent purple/violet ambient glow background
    st.markdown("""
    <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; z-index: 0;">
        <div style="position: absolute; top: 15%; left: 50%; transform: translateX(-50%); width: 1000px; height: 800px; background: radial-gradient(ellipse at center, rgba(147,112,219,0.25) 0%, rgba(139,92,246,0.15) 25%, rgba(99,102,241,0.08) 50%, transparent 70%); filter: blur(40px);"></div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation header (Gladia-style)
    st.markdown("""
    <div style="position: relative; z-index: 1; display: flex; justify-content: space-between; align-items: center; padding: 20px 40px; max-width: 1200px; margin: 0 auto;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" style="opacity: 0.9;">
                <circle cx="12" cy="12" r="10" stroke="#ffffff" stroke-width="1.5" fill="none"/>
                <ellipse cx="12" cy="12" rx="4" ry="10" stroke="#ffffff" stroke-width="1.5" fill="none"/>
                <line x1="2" y1="12" x2="22" y2="12" stroke="#ffffff" stroke-width="1.5"/>
            </svg>
            <span style="font-size: 26px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px;">CeCe</span>
        </div>
        <nav style="display: flex; gap: 32px; align-items: center;">
            <a href="#features" style="color: #94a3b8; text-decoration: none; font-size: 15px; font-weight: 500;">Features</a>
            <a href="#data" style="color: #94a3b8; text-decoration: none; font-size: 15px; font-weight: 500;">Data Sources</a>
            <a href="#about" style="color: #94a3b8; text-decoration: none; font-size: 15px; font-weight: 500;">About</a>
            <a href="https://github.com" target="_blank" style="color: #94a3b8; text-decoration: none; font-size: 15px; font-weight: 500;">GitHub</a>
        </nav>
    </div>
    """, unsafe_allow_html=True)

    # Add vertical breathing room before hero
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

    # Beta pill badge
    st.markdown("""
    <div style="position: relative; z-index: 1; text-align: center; margin-bottom: 28px;">
        <span style="display: inline-flex; align-items: center; gap: 8px; background: rgba(139,92,246,0.15); border: 1px solid rgba(139,92,246,0.3); border-radius: 50px; padding: 8px 18px; font-size: 13px; color: #a78bfa; font-weight: 500;">
            <span style="width: 6px; height: 6px; background: #22c55e; border-radius: 50%; display: inline-block;"></span>
            BETA — Research Preview
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Hero section with larger typography
    st.markdown("""
    <div style="position: relative; z-index: 1; text-align: center;">
        <h1 style='font-size: 88px; font-weight: 600; margin-bottom: 24px; color: #ffffff; letter-spacing: -4px; line-height: 0.95;'>
            Climate CoPilot
        </h1>
        <p style='font-size: 15px; margin-bottom: 20px; color: #c4b5fd; font-weight: 500; letter-spacing: 1px; text-transform: uppercase;'>
            CC — aka CeCe, your climate & weather agent
        </p>
        <p style='font-size: 20px; margin-bottom: 40px; color: #a1a1aa; font-weight: 400; max-width: 520px; margin-left: auto; margin-right: auto; line-height: 1.6;'>
            Climate is complicated. Your workflow shouldn't be.
        </p>
        <div style="display: flex; justify-content: center; gap: 16px; margin-bottom: 50px;">
            <a href="#" style="display: inline-block; padding: 14px 32px; background: #8b5cf6; color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 15px; font-weight: 600;">Get Started</a>
            <a href="#" style="display: inline-block; padding: 14px 32px; background: transparent; color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 15px; font-weight: 500; border: 1px solid rgba(255,255,255,0.2);">Learn More</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Blurred preview of the main CeCe interface as a teaser ---
    st.markdown("""
    <div style="position: relative; max-width: 900px; margin: 0 auto 40px auto;">
        <!-- Blurred mock preview of the main interface -->
        <div style="
            background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 40%, #1b1040 100%);
            border-radius: 20px;
            padding: 40px;
            filter: blur(3px);
            -webkit-filter: blur(3px);
            border: 1px solid rgba(100,181,246,0.15);
            pointer-events: none;
            user-select: none;
        ">
            <!-- Mock header -->
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 30px;">
                <span style="font-size: 22px; font-weight: bold; color: #64B5F6;">CECE: YOUR CLIMATE & WEATHER AGENT</span>
            </div>
            <!-- Mock welcome message -->
            <div style="background: rgba(30,136,229,0.15); border-radius: 12px; padding: 20px; margin-bottom: 25px; max-width: 700px; margin-left: auto; margin-right: auto;">
                <p style="color: #B0BEC5; font-size: 14px; margin: 0;">CeCe (Climate Copilot)</p>
                <p style="color: #E0E0E0; font-size: 15px; margin: 8px 0 0 0;">Welcome! I can help you analyze climate data, weather patterns, and environmental risks across industries...</p>
            </div>
            <!-- Mock earth visualization placeholder -->
            <div style="background: rgba(0,0,0,0.4); border-radius: 12px; height: 180px; display: flex; align-items: center; justify-content: center; margin-bottom: 25px;">
                <span style="color: #37474F; font-size: 48px;">&#127758;</span>
            </div>
            <!-- Mock industry buttons -->
            <div style="display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
                <div style="background: rgba(147,112,219,0.2); border: 1px solid rgba(147,112,219,0.3); border-radius: 10px; padding: 12px 18px; color: #9370DB; font-size: 13px;">Agriculture</div>
                <div style="background: rgba(147,112,219,0.2); border: 1px solid rgba(147,112,219,0.3); border-radius: 10px; padding: 12px 18px; color: #9370DB; font-size: 13px;">Energy</div>
                <div style="background: rgba(147,112,219,0.2); border: 1px solid rgba(147,112,219,0.3); border-radius: 10px; padding: 12px 18px; color: #9370DB; font-size: 13px;">Insurance</div>
                <div style="background: rgba(147,112,219,0.2); border: 1px solid rgba(147,112,219,0.3); border-radius: 10px; padding: 12px 18px; color: #9370DB; font-size: 13px;">Transportation</div>
            </div>
        </div>
        <!-- Overlay gradient fade at bottom to blend into background -->
        <div style="
            position: absolute;
            bottom: 0; left: 0; right: 0;
            height: 80px;
            background: linear-gradient(transparent, #000000);
            border-radius: 0 0 20px 20px;
            pointer-events: none;
        "></div>
    </div>
    """, unsafe_allow_html=True)

    # --- COMMENTED OUT: Temperature anomalies, legend, and Folium map ---
    # These are disabled for a cleaner landing page. Uncomment to restore.
    #
    # # Create the base map with dark styling
    # m = folium.Map(
    #     location=[20.0, 0.0],  # Global view centered on equator
    #     zoom_start=2,
    #     tiles='cartodbdark_matter',
    #     zoomControl=True,
    #     scrollWheelZoom=True,
    #     doubleClickZoom=True,
    #     dragging=True
    # )
    #
    # # Add sample climate data points for demonstration
    # import numpy as np
    #
    # # Create sample temperature anomaly data points
    # np.random.seed(42)  # For consistent results
    # sample_locations = [
    #     (60.0, -105.0, 2.3),   # Northern Canada - warm anomaly
    #     (45.0, -75.0, 1.8),    # Eastern US - warm anomaly
    #     (55.0, 37.0, 3.1),     # Moscow region - warm anomaly
    #     (35.0, 139.0, 1.2),    # Tokyo region - warm anomaly
    #     (-15.0, -60.0, -0.8),  # Brazil - cool anomaly
    #     (-25.0, 135.0, 2.7),   # Australia - warm anomaly
    #     (70.0, 20.0, 4.2),     # Northern Europe - warm anomaly
    #     (0.0, 20.0, 0.5),      # Central Africa - slight warm
    #     (-35.0, -70.0, -1.2),  # Chile - cool anomaly
    #     (25.0, 55.0, 2.9),     # Middle East - warm anomaly
    # ]
    #
    # # Add temperature data points to map
    # for lat, lon, temp_anomaly in sample_locations:
    #     color = '#FF4444' if temp_anomaly > 0 else '#4444FF'
    #     opacity = min(abs(temp_anomaly) / 3.0, 1.0)
    #     radius = 4 + abs(temp_anomaly)
    #
    #     folium.CircleMarker(
    #         location=[lat, lon],
    #         radius=radius,
    #         color=color,
    #         fillColor=color,
    #         fillOpacity=opacity * 0.8,
    #         popup=f"Temperature Anomaly: {temp_anomaly:+.1f}°C",
    #         tooltip=f"Temp Anomaly: {temp_anomaly:+.1f}°C"
    #     ).add_to(m)
    #
    # # Add layer control for map switching
    # folium.LayerControl().add_to(m)
    #
    # # Add legend for climate data
    # st.markdown("""
    # <div style="background: rgba(0,0,0,0.8); color: white; padding: 15px; border-radius: 10px; margin: 20px 0;">
    #     <h4 style="margin: 0 0 10px 0; color: #64B5F6;">Global Temperature Anomalies</h4>
    #     <div style="display: flex; align-items: center; gap: 20px;">
    #         <div style="display: flex; align-items: center; gap: 5px;">
    #             <div style="width: 12px; height: 12px; background: red; border-radius: 50%;"></div>
    #             <span>Above Average</span>
    #         </div>
    #         <div style="display: flex; align-items: center; gap: 5px;">
    #             <div style="width: 12px; height: 12px; background: blue; border-radius: 50%;"></div>
    #             <span>Below Average</span>
    #         </div>
    #     </div>
    # </div>
    # """, unsafe_allow_html=True)
    #
    # # Display the scrollable map
    # map_data = st_folium(
    #     m,
    #     height=600,
    #     width=None,
    #     returned_objects=["last_clicked"],
    #     key="satellite_homepage_map"
    # )

    # --- COMMENTED OUT: Chat interface on homepage ---
    # Chat is available in the main interface after clicking Launch.
    #
    # # Add chat interface below the map
    # st.markdown("---")
    # st.markdown("### Ask CeCe about Climate Data")
    #
    # # Initialize chat history if not exists
    # if 'chat_history' not in st.session_state:
    #     st.session_state.chat_history = [
    #         {"role": "assistant", "content": "Hi! I'm CeCe, your Climate Copilot. Ask me about climate patterns, weather data, or explore the temperature anomalies shown on the map above."}
    #     ]
    #
    # # Display chat messages
    # for message in st.session_state.chat_history:
    #     with st.chat_message(message["role"]):
    #         st.write(message["content"])
    #
    # # Chat input
    # if prompt := st.chat_input("Ask about climate data, weather patterns, or map features..."):
    #     # Add user message to chat history
    #     st.session_state.chat_history.append({"role": "user", "content": prompt})
    #
    #     # Display user message
    #     with st.chat_message("user"):
    #         st.write(prompt)
    #
    #     # Generate and display assistant response
    #     with st.chat_message("assistant"):
    #         with st.spinner("Analyzing climate data..."):
    #             try:
    #                 import openai_helper
    #                 messages = [{"role": "user", "content": prompt}]
    #                 system_message = "You are CeCe, a climate data assistant. Help users understand climate patterns, weather data, and the temperature anomalies shown on the interactive map. Keep responses concise and informative."
    #                 response = openai_helper.chat_completion(messages, system_message=system_message)
    #                 if response:
    #                     st.write(response)
    #                     st.session_state.chat_history.append({"role": "assistant", "content": response})
    #                 else:
    #                     fallback = "I can help you understand the climate data shown on the map. The red dots indicate areas with above-average temperatures, while blue dots show below-average temperatures. You can click on any dot to see specific temperature anomaly values. What would you like to know more about?"
    #                     st.write(fallback)
    #                     st.session_state.chat_history.append({"role": "assistant", "content": fallback})
    #             except Exception as e:
    #                 fallback = "I can help you understand the climate data shown on the map. The red dots indicate areas with above-average temperatures, while blue dots show below-average temperatures. You can click on any dot to see specific temperature anomaly values. What would you like to know more about?"
    #                 st.write(fallback)
    #                 st.session_state.chat_history.append({"role": "assistant", "content": fallback})

    return None

if __name__ == "__main__":
    create_satellite_homepage()
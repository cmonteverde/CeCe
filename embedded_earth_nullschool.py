"""
Embedded Earth Nullschool Module

This module integrates the Earth Nullschool visualization by Cameron Beccario
(https://github.com/cambecc/earth) directly into the Climate Copilot application
using Streamlit components for better mouse interaction.
"""

import streamlit as st
import nullschool_component  # Import our custom component

def display_earth_nullschool(height=600, mode="wind", overlay="wind", 
                            projection="orthographic", location="0.00,0.00,409", 
                            date="current", map_detail="high"):
    """
    Display embedded Earth Nullschool visualization in an iframe
    
    Args:
        height: Height of the iframe in pixels
        mode: Visualization mode (wind, ocean, chem, particulates, etc.)
        overlay: Data overlay (total_precipitable_water, temp, etc.)
        projection: Map projection (orthographic, waterman, patterson, etc.)
        location: Format "lat,lon,zoom" (e.g., "0.00,0.00,409")
        date: Date for the data (current, YYYY/MM/DD, etc.)
        map_detail: Level of map detail ("high", "medium", "low")
    """
    # Earth Nullschool URL creation using the exact format from the site
    base_url = "https://earth.nullschool.net"
    
    # Use the correct URL format for Earth Nullschool
    # Format example: https://earth.nullschool.net/#current/wind/surface/level/orthographic=-97.01,39.68,897
    if mode == "wind":
        level_param = "level"
    elif mode == "ocean":
        level_param = "currents"
    elif mode == "chem" or mode == "particulates":
        level_param = "particles"
    else:
        level_param = "level"
    
    # Add map detail parameter
    map_detail_param = ""
    if map_detail == "high":
        map_detail_param = "detail=true"
    elif map_detail == "low":
        map_detail_param = "detail=false"
        
    base_url_with_detail = f"{base_url}" + (f"?{map_detail_param}" if map_detail_param else "")
    url = f"{base_url_with_detail}/#{date}/{mode}/surface/{level_param}/{projection}={location}"
    
    # Create a stylish container with header
    st.markdown("""
    <div style="margin-top: 30px; margin-bottom: 30px; border-radius: 15px; 
              overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); width: 100%;">
        <div style="background: linear-gradient(90deg, #1E90FF, #9370DB); height: 4px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display visualization title
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #1E90FF, #9370DB); 
                  -webkit-background-clip: text;
                  -webkit-text-fill-color: transparent;
                  font-weight: bold;
                  font-size: 18px;
                  margin-top: 5px; margin-bottom: 15px;">
            CeCe Global Climate Explorer (Earth Nullschool)
        </div>
        """, unsafe_allow_html=True)
    
    # Use our custom component for better mouse interaction
    nullschool_component.display_nullschool_earth(url=url, height=height)
    
    # Add attribution
    st.markdown("""
    <div style="text-align: right; font-size: 12px; color: #888; margin-top: -8px; margin-bottom: 15px;">
        Visualization powered by <a href="https://earth.nullschool.net" target="_blank" style="color: #1E90FF;">earth.nullschool.net</a>
    </div>
    """, unsafe_allow_html=True)
    
    # Add visualization controls
    with st.expander("Visualization Controls"):
        col1, col2 = st.columns(2)
        
        with col1:
            selected_mode = st.selectbox(
                "Mode", 
                ["wind", "ocean", "chem", "particulates", "space"],
                index=0
            )
            
            # Update overlay options to match Earth Nullschool expected parameters
            overlay_options = {
                "wind": ["wind", "temp", "rh", "tpw", "tcw", "precip", "mslp"],
                "ocean": ["currents", "waves", "temp", "primary", "sst"],
                "chem": ["co2", "cosc", "so2", "o3", "no2", "pm2p5", "pm10", "duexttau"],
                "particulates": ["dust", "carbon", "so4ext", "aod550"],
                "space": ["aurora", "clouds_ir", "tdso"]
            }
            
            selected_overlay = st.selectbox(
                "Data Overlay",
                overlay_options.get(selected_mode, ["wind"]),
                index=0
            )
            
        with col2:
            selected_projection = st.selectbox(
                "Projection", 
                ["orthographic", "waterman", "patterson", "equirectangular", "stereographic", "mercator"],
                index=0
            )
            
            date_options = ["current", "2023/12/25", "2023/09/01", "2023/06/01", "2023/03/01"]
            selected_date = st.selectbox("Date", date_options, index=0)
            
            selected_map_detail = st.selectbox(
                "Map Detail",
                ["medium", "high", "low"],
                index=0
            )
        
        if st.button("Update Visualization"):
            # Generate new URL based on selections, consistent with the same logic as above
            if selected_mode == "wind":
                level_param = "level" 
            elif selected_mode == "ocean":
                level_param = "currents"
            elif selected_mode == "chem" or selected_mode == "particulates":
                level_param = "particles"
            else:
                level_param = "level"
                
            # Add map detail parameter
            map_detail_param = ""
            if selected_map_detail == "high":
                map_detail_param = "detail=true"
            elif selected_map_detail == "low":
                map_detail_param = "detail=false"
                
            base_url_with_detail = f"{base_url}" + (f"?{map_detail_param}" if map_detail_param else "")
            new_url = f"{base_url_with_detail}/#{selected_date}/{selected_mode}/surface/{level_param}/{selected_projection}={location}"
            
            # Update the iframe (via Streamlit rerun)
            st.session_state.earth_nullschool_url = new_url
            st.session_state.earth_nullschool_config = {
                "mode": selected_mode,
                "overlay": selected_overlay,
                "projection": selected_projection,
                "date": selected_date,
                "map_detail": selected_map_detail
            }
            st.rerun()


if __name__ == "__main__":
    st.set_page_config(page_title="Earth Nullschool Visualization", layout="wide")
    display_earth_nullschool(height=700)
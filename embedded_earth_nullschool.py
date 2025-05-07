"""
Earth Visualization Module

This module provides an interactive globe visualization with wind patterns
inspired by Earth Nullschool, but implemented directly with D3.js to allow
for full mouse interaction (zoom, rotate) within the Streamlit app.
"""

import streamlit as st
import custom_earth_wind  # Import our custom D3.js-based visualization
import math

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
    
    # Use our custom D3.js-based Earth visualization with full mouse interaction
    # Generate URL for reference (we still use it in links)
    custom_earth_wind.custom_earth_wind_visualization(height=height)
    
    # Add information about the visualization features
    st.success("""
    ### Interactive Earth Visualization
    
    This custom visualization supports:
    - **Zoom in/out** using your mouse scroll wheel
    - **Rotate** the globe by clicking and dragging
    - **View wind patterns** with animated particles
    
    The controls in the bottom right allow you to zoom in/out and reset the view.
    """)
    
    # Add links to Earth Nullschool for additional features
    st.markdown("""
    <div style="text-align: center; margin: 15px 0; padding: 15px; background-color: rgba(0,0,0,0.5); border-radius: 10px;">
        <h4 style="color: white; margin-bottom: 10px; font-size: 16px;">Additional Earth Visualization Options</h4>
        <div style="display: flex; justify-content: space-around; margin-top: 10px;">
            <a href="https://earth.nullschool.net/#current/wind/surface/level/orthographic" target="_blank" style="color: #1E90FF; text-decoration: none; font-size: 14px;">Winds</a>
            <a href="https://earth.nullschool.net/#current/ocean/surface/currents/orthographic" target="_blank" style="color: #1E90FF; text-decoration: none; font-size: 14px;">Oceans</a>
            <a href="https://earth.nullschool.net/#current/chem/surface/level/orthographic" target="_blank" style="color: #1E90FF; text-decoration: none; font-size: 14px;">Chemistry</a>
            <a href="https://earth.nullschool.net/#current/particulates/surface/level/orthographic" target="_blank" style="color: #1E90FF; text-decoration: none; font-size: 14px;">Particulates</a>
        </div>
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
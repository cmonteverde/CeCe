"""
Embedded Earth Nullschool Module

This module integrates the Earth Nullschool visualization by Cameron Beccario
(https://github.com/cambecc/earth) directly into the Climate Copilot application
through an iframe.
"""

import streamlit as st

def display_earth_nullschool(height=600, mode="wind", overlay="wind", 
                            projection="orthographic", location="0.00,0.00,409", 
                            date="current"):
    """
    Display embedded Earth Nullschool visualization in an iframe
    
    Args:
        height: Height of the iframe in pixels
        mode: Visualization mode (wind, ocean, chem, particulates, etc.)
        overlay: Data overlay (total_precipitable_water, temp, etc.)
        projection: Map projection (orthographic, waterman, patterson, etc.)
        location: Format "lat,lon,zoom" (e.g., "0.00,0.00,409")
        date: Date for the data (current, YYYY/MM/DD, etc.)
    """
    # Earth Nullschool URL creation
    base_url = "https://earth.nullschool.net"
    # Always use "current" for reliable data availability
    url = f"{base_url}/#current/{mode}/{overlay}/orthographic={location}"
    
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
    
    # Create iframe with Earth Nullschool
    iframe_html = f"""
    <div style="width: 100%; height: {height}px; overflow: hidden; border-radius: 15px; margin-bottom: 10px;">
        <iframe src="{url}" 
                width="100%" 
                height="{height}" 
                frameborder="0"
                style="border-radius: 15px; border: none; overflow: hidden;">
        </iframe>
    </div>
    <div style="text-align: right; font-size: 12px; color: #888; margin-top: -8px; margin-bottom: 15px;">
        Visualization powered by <a href="https://earth.nullschool.net" target="_blank" style="color: #1E90FF;">earth.nullschool.net</a>
    </div>
    """
    
    st.markdown(iframe_html, unsafe_allow_html=True)
    
    # Add visualization controls
    with st.expander("Visualization Controls"):
        col1, col2 = st.columns(2)
        
        with col1:
            selected_mode = st.selectbox(
                "Mode", 
                ["wind", "ocean", "chem", "particulates", "space"],
                index=0
            )
            
            overlay_options = {
                "wind": ["wind", "temp", "relative_humidity", "total_precipitable_water", "total_cloud_water", "3hr_precipitation", "mean_sea_level_pressure"],
                "ocean": ["currents", "waves", "temp", "primary_waves", "sea_surface_temp"],
                "chem": ["co2", "cosc", "so2", "o3", "no2", "pm2.5", "pm10", "duexttau"],
                "particulates": ["dust", "carbon", "so4ext", "aod550"],
                "space": ["aurora", "clouds_ir", "tdso"]
            }
            
            selected_overlay = st.selectbox(
                "Data Overlay",
                overlay_options.get(selected_mode, ["total_precipitable_water"]),
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
        
        if st.button("Update Visualization"):
            # Generate new URL based on selections, always use "current" for reliable data
            new_url = f"{base_url}/#current/{selected_mode}/{selected_overlay}/{selected_projection}={location}"
            
            # Update the iframe (via Streamlit rerun)
            st.session_state.earth_nullschool_url = new_url
            st.session_state.earth_nullschool_config = {
                "mode": selected_mode,
                "overlay": selected_overlay,
                "projection": selected_projection,
                "date": "current"  # Always use current data
            }
            st.rerun()


if __name__ == "__main__":
    st.set_page_config(page_title="Earth Nullschool Visualization", layout="wide")
    display_earth_nullschool(height=700)
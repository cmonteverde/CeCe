"""
Interactive Globe Map Module for Climate Copilot

This module provides an interactive 3D globe visualization using Plotly
that can be embedded within the main application. The globe features:
- Dark/light mode toggle with OpenStreetMap integration
- Color scheme matching the CeCe brand colors
- Full globe view at startup
- Interactive zoom and rotation
- Optional data layers for climate visualization
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd 
import streamlit as st

# CeCe brand colors (blue to purple gradient)
CECE_BLUE = "#1E90FF"
CECE_PURPLE = "#9370DB"
CECE_GRADIENT = [CECE_BLUE, "#5F7FEA", "#8A6CD7", CECE_PURPLE]

# OpenStreetMap tile URLs
OSM_TILES = {
    "dark": "https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
    "light": "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
}

def create_globe_map(dark_mode=True, width=800, height=600):
    """
    Create an interactive 3D globe visualization using OpenStreetMap data
    
    Args:
        dark_mode: Whether to use dark mode (True) or light mode (False)
        width: Width of the map in pixels (default: 800)
        height: Height of the map in pixels (default: 600)
        
    Returns:
        Plotly figure object
    """
    # Base colors for dark and light modes
    if dark_mode:
        land_color = "#2D2D2D"
        ocean_color = "#0D1117"
        bg_color = "rgba(0,0,0,0)"
        text_color = "white"
        grid_color = "#444"
        coast_color = CECE_BLUE  # Use CeCe blue for coastlines in dark mode
        country_color = "#555"
    else:
        land_color = "#E5E5E5" 
        ocean_color = "#EAEAEF"
        bg_color = "rgba(255,255,255,0)"
        text_color = "#333"
        grid_color = "#ddd"
        coast_color = CECE_PURPLE  # Use CeCe purple for coastlines in light mode
        country_color = "#777"
    
    # Create the base figure with a globe projection
    fig = go.Figure()
    
    # Add the base globe with land and ocean
    fig.add_trace(go.Choropleth(
        locationmode="country names",
        z=[1] * 250,  # Dummy data for coloring
        colorscale=[[0, land_color], [1, land_color]],
        marker_line_color=country_color,
        marker_line_width=0.5,  # Always show country lines
        showscale=False,
        hoverinfo="skip"
    ))
    
    # Create gradient-colored markers for key latitudes with CeCe colors
    latitudes = np.linspace(-60, 60, len(CECE_GRADIENT))
    for i, lat in enumerate(latitudes):
        color = CECE_GRADIENT[i]
        # Add subtle latitude markers with CeCe brand colors
        lons = np.linspace(-180, 180, 100)
        lats = np.full_like(lons, lat)
        
        fig.add_trace(go.Scattergeo(
            lon=lons,
            lat=lats,
            mode="lines",
            line=dict(width=1.5, color=color, dash="dot"),
            opacity=0.4,
            hoverinfo="skip",
            showlegend=False
        ))
    
    # Configure the 3D projection and interactivity
    fig.update_geos(
        projection_type="orthographic",
        showcoastlines=True, coastlinecolor=coast_color,
        showland=True, landcolor=land_color,
        showocean=True, oceancolor=ocean_color,
        showlakes=True, lakecolor=ocean_color,
        showcountries=True,  # Always show country lines
        countrycolor=country_color,
        showframe=False,
        framecolor=grid_color,
        showsubunits=False,
        showrivers=False,
        lataxis=dict(gridcolor=grid_color, showgrid=True, gridwidth=0.5),
        lonaxis=dict(gridcolor=grid_color, showgrid=True, gridwidth=0.5),
        resolution=50,
        bgcolor=bg_color,
        # Maximize the globe's display within its container
        fitbounds="locations",
        visible=True
    )
    
    # Update the layout to make it more expansive and improve zoom
    fig.update_layout(
        title=None,
        width=width,
        height=height,
        autosize=True,  # Enable autosize for responsive behavior
        margin=dict(l=0, r=0, t=0, b=0, pad=0),  # Remove all margins
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        geo=dict(
            projection_rotation=dict(lon=0, lat=0, roll=0),
            # Start with a view of the full globe
            center=dict(lon=0, lat=0),
            # Maximize the globe size within the container
            projection_scale=1.0,  # Full size projection
            # Allow for more interactive zoom range
            scope="world"
        ),
        font=dict(color=text_color),
        # Enhanced display settings for better appearance
        dragmode="pan",  # Change to "pan" for better touch interaction
        # Enable direct zoom control
        modebar=dict(
            orientation="v",
            bgcolor="rgba(0,0,0,0)",
            color=text_color,
            activecolor=coast_color
        )
    )
    
    return fig

def add_climate_layer(fig, layer_type="temperature", data=None):
    """
    Add a climate data visualization layer to the globe
    
    Args:
        fig: Plotly figure object (globe)
        layer_type: Type of climate layer ("temperature", "co2", "sea_level", "glacier")
        data: Climate data to visualize (DataFrame or None to fetch from source)
        
    Returns:
        Updated Plotly figure
    """
    # Import here to avoid circular imports
    import sys
    
    # If no data is provided, fetch appropriate data based on layer type
    if data is None:
        try:
            # Always use the simpler model for now
            if layer_type == "temperature":
                from climate_data_sources import generate_global_temperature_grid
                with st.spinner("Generating global temperature grid..."):
                    data = generate_global_temperature_grid(resolution=5)  # Higher resolution for better visual
                    if isinstance(data, pd.DataFrame):
                        st.success(f"Generated temperature grid with {len(data)} points")
            else:
                # Get data for other layer types
                from climate_data_sources import get_climate_layer_data
                data = get_climate_layer_data(layer_type)
                
        except Exception as e:
            st.error(f"Error generating climate data: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            # Fall back to empty dataframe with expected structure
            if layer_type == "temperature":
                data = pd.DataFrame(columns=['lat', 'lon', 'temperature'])
            else:
                data = pd.DataFrame()
    
    # Check if data is a dictionary (error or specific format)
    if isinstance(data, dict) and "error" in data:
        st.error(f"Climate data error: {data['error']}")
        return fig
    
    # Add visualization based on layer type
    if layer_type == "temperature":
        if isinstance(data, pd.DataFrame) and not data.empty and 'lat' in data.columns:
            try:
                # Extract data columns
                lats = data['lat'].tolist()
                lons = data['lon'].tolist()
                temps = data['temperature'].tolist()
                
                # Use Scattergeo for better globe compatibility
                fig.add_trace(go.Scattergeo(
                    lat=lats,
                    lon=lons,
                    mode='markers',
                    marker=dict(
                        size=5,
                        color=temps,
                        colorscale=[
                            [0, "#0d47a1"],  # Cold (deep blue)
                            [0.3, CECE_BLUE],  # Cool (CeCe blue)
                            [0.5, "#ffffff"],  # Moderate (white)
                            [0.7, "#9370DB"],  # Warm (CeCe purple)
                            [1, "#b71c1c"]  # Hot (red)
                        ],
                        colorbar=dict(
                            title="Temp (°C)",
                            titleside="top",
                            outlinewidth=0,
                            borderwidth=0,
                            thickness=15
                        ),
                        opacity=0.7,
                        symbol='circle'
                    ),
                    name="Temperature",
                    hovertemplate="Lat: %{lat:.2f}<br>Lon: %{lon:.2f}<br>Temp: %{marker.color:.1f}°C<extra></extra>"
                ))
            except Exception as e:
                st.error(f"Error adding temperature data to map: {str(e)}")
        else:
            st.warning("No temperature data available to display")
    
    elif layer_type == "co2":
        # Add CO2 concentration visualization
        # For CO2, we'll add a text annotation with current level
        # and trend since it's a global value not tied to specific locations
        try:
            from climate_data_sources import fetch_co2_data
            co2_df = fetch_co2_data()
            
            if not co2_df.empty and 'co2' in co2_df.columns.str.lower():
                # Get latest CO2 value and trend
                co2_col = [col for col in co2_df.columns if 'co2' in col.lower()][0]
                latest_co2 = co2_df[co2_col].iloc[-1]
                one_year_ago = co2_df[co2_col].iloc[-13] if len(co2_df) > 13 else co2_df[co2_col].iloc[0]
                annual_change = latest_co2 - one_year_ago
                
                # Add annotation
                fig.add_annotation(
                    x=0.5,
                    y=0.95,
                    text=f"Current CO₂: {latest_co2:.1f} ppm<br>Annual change: {annual_change:+.1f} ppm",
                    showarrow=False,
                    font=dict(size=16, color="#FF5722"),
                    bgcolor="rgba(0,0,0,0.6)",
                    bordercolor="#FF5722",
                    borderwidth=2,
                    borderpad=4,
                    align="center",
                    xref="paper",
                    yref="paper"
                )
                
                # Add a visual indicator of CO2 concentration
                # We'll create colored circles at different latitudes to show the global CO2 distribution
                latitudes = np.linspace(-60, 60, 13)
                for lat in latitudes:
                    fig.add_trace(go.Scattergeo(
                        lat=[lat],
                        lon=[0],  # Center longitude
                        mode="markers",
                        marker=dict(
                            size=max(10, min(40, latest_co2/10)),  # Size based on CO2 level
                            color="#FF5722",
                            opacity=0.7,
                            symbol="circle"
                        ),
                        name="CO₂ Concentration",
                        hoverinfo="text",
                        hovertext=f"Global CO₂: {latest_co2:.1f} ppm",
                        showlegend=False
                    ))
        except Exception as e:
            st.error(f"Error displaying CO2 data: {str(e)}")
    
    elif layer_type == "sea_level":
        # Add sea level rise visualization
        try:
            from climate_data_sources import fetch_sea_level_data
            sea_level_df = fetch_sea_level_data()
            
            if not sea_level_df.empty and 'GMSL' in sea_level_df.columns:
                # Get latest value and trend
                latest_year = sea_level_df['Year'].iloc[-1]
                latest_level = sea_level_df['GMSL'].iloc[-1]
                ten_years_ago_idx = max(0, len(sea_level_df) - 11)
                ten_year_change = latest_level - sea_level_df['GMSL'].iloc[ten_years_ago_idx]
                
                # Add annotation
                fig.add_annotation(
                    x=0.5,
                    y=0.9,
                    text=f"Sea Level Rise: {latest_level:.1f} mm<br>10-year change: {ten_year_change:+.1f} mm",
                    showarrow=False,
                    font=dict(size=16, color="#2196F3"),
                    bgcolor="rgba(0,0,0,0.6)",
                    bordercolor="#2196F3",
                    borderwidth=2,
                    borderpad=4,
                    align="center",
                    xref="paper",
                    yref="paper"
                )
                
                # Add coastline highlight to indicate sea level rise
                # We'll create a thicker coastline with a blue glow effect
                fig.update_geos(
                    showcoastlines=True,
                    coastlinecolor="#2196F3",
                    coastlinewidth=2
                )
        except Exception as e:
            st.error(f"Error displaying sea level data: {str(e)}")
    
    elif layer_type == "glacier":
        # Add glacier melt visualization
        try:
            from climate_data_sources import fetch_glacier_data
            glacier_df = fetch_glacier_data()
            
            if not glacier_df.empty and 'Mean cumulative mass balance' in glacier_df.columns:
                # Get latest value and trend
                latest_year = glacier_df['Year'].iloc[-1]
                latest_balance = glacier_df['Mean cumulative mass balance'].iloc[-1]
                
                # Add annotation
                fig.add_annotation(
                    x=0.5,
                    y=0.85,
                    text=f"Glacier Mass Balance: {latest_balance:.1f} mm w.e.<br>Year: {latest_year}",
                    showarrow=False,
                    font=dict(size=16, color="#90CAF9"),
                    bgcolor="rgba(0,0,0,0.6)",
                    bordercolor="#90CAF9",
                    borderwidth=2,
                    borderpad=4,
                    align="center",
                    xref="paper",
                    yref="paper"
                )
                
                # Add glacier visualization at key locations
                glacier_locations = [
                    {"name": "Greenland", "lat": 72.0, "lon": -40.0},
                    {"name": "Antarctica", "lat": -75.0, "lon": 0.0},
                    {"name": "Alps", "lat": 46.0, "lon": 8.0},
                    {"name": "Himalayas", "lat": 28.0, "lon": 85.0},
                    {"name": "Andes", "lat": -40.0, "lon": -70.0},
                    {"name": "Alaska", "lat": 61.0, "lon": -148.0}
                ]
                
                for loc in glacier_locations:
                    fig.add_trace(go.Scattergeo(
                        lat=[loc["lat"]],
                        lon=[loc["lon"]],
                        mode="markers",
                        marker=dict(
                            size=15,
                            color="#90CAF9",
                            opacity=0.8,
                            symbol="diamond"
                        ),
                        name=loc["name"],
                        hoverinfo="text",
                        hovertext=f"{loc['name']} Glacier Impact<br>Global Balance: {latest_balance:.1f} mm w.e.",
                        showlegend=False
                    ))
        except Exception as e:
            st.error(f"Error displaying glacier data: {str(e)}")
    
    else:
        st.warning(f"Unsupported climate layer type: {layer_type}")
    
    return fig

def display_globe_map(dark_mode=True):
    """Display the interactive globe map in Streamlit
    
    Args:
        dark_mode: Whether to use dark mode (True) or light mode (False)
    """
    # Create container for the map with styling
    st.markdown("""
    <div style="margin-top: 30px; margin-bottom: 30px; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); width: 100%;">
        <div style="background: linear-gradient(90deg, #1E90FF, #9370DB); height: 4px;"></div>
        <div id="globe-container" style="width: 100%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for controls
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #1E90FF, #9370DB); 
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-weight: bold;
                    font-size: 18px;
                    margin-top: 5px;">
            CeCe Global Climate Explorer
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        dark_mode = st.checkbox("Dark Mode", value=dark_mode)
    
    with col3:
        layer_type = st.selectbox("Data Layer", 
                                ["None", "Temperature", "CO2", "Sea Level", "Glacier"], 
                                index=0)
    
    # Determine the ideal dimensions based on the viewport
    height = 600  # Taller map for better visibility
    
    # Create the globe map
    fig = create_globe_map(dark_mode=dark_mode, width=800, height=height)
    
    # Add climate layer if selected
    if layer_type.lower() != "none":
        fig = add_climate_layer(fig, layer_type=layer_type.lower())
    
    # Make the chart responsive and fill the container
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
        'displaylogo': False,
        'responsive': True,
        'scrollZoom': True,
        'doubleClick': 'reset+autosize',  # Reset view on double click
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'climate_globe',
            'height': 800,
            'width': 1200
        }
    })
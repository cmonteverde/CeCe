import streamlit as st
import custom_earth_wind

# Set up a simple test page
st.set_page_config(page_title="Interactive Earth Visualization Test", layout="wide")
st.title("Interactive Earth Visualization Test")

# Display the visualization directly
st.write("### Testing Direct D3.js Earth Visualization")
custom_earth_wind.custom_earth_wind_visualization(height=600)
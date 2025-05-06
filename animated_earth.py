"""
Animated Earth Visualization Module (Earth Nullschool Style)

This module creates an interactive, animated globe visualization similar to 
earth.nullschool.net using D3.js. It renders wind patterns and other climate data
on an interactive 3D globe.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
import numpy as np
import pandas as pd

def generate_wind_data(resolution=2):
    """
    Generate sample wind data in the format expected by the visualization
    
    Args:
        resolution: Grid resolution in degrees
        
    Returns:
        Dictionary with wind data
    """
    # Create a grid of points
    lats = np.arange(-90, 91, resolution)
    lons = np.arange(-180, 181, resolution)
    
    # Generate wind vectors (u, v components)
    data = []
    for lat in lats:
        for lon in lons:
            # Create simple wind pattern based on latitude and longitude
            # This is a simplified model - in reality, would use actual climate data
            u = 5 * np.cos(np.radians(lat)) * np.sin(np.radians(lon))
            v = 5 * np.cos(np.radians(lat)) * np.cos(np.radians(lon))
            
            # Add some variation based on latitude
            if abs(lat) > 60:  # polar regions
                u *= 0.5
                v *= 0.5
            elif abs(lat) < 15:  # equatorial regions
                u *= 1.2
                v *= 0.8
                
            data.append({
                "lat": lat,
                "lon": lon,
                "u": u,  # east-west component
                "v": v   # north-south component
            })
    
    return {"data": data, "date": "2025-05-06", "resolution": resolution}

def animated_earth_html(wind_data, dark_mode=True, width=800, height=600):
    """
    Create HTML for the animated earth visualization
    
    Args:
        wind_data: Dictionary with wind data
        dark_mode: Whether to use dark mode
        width: Visualization width
        height: Visualization height
        
    Returns:
        HTML string for the visualization
    """
    # Convert wind_data to JSON
    wind_data_json = json.dumps(wind_data)
    
    # Define the HTML content with embedded CSS and JavaScript
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Animated Earth</title>
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; background-color: {('#000' if dark_mode else '#fff')}; }}
            #map {{ width: 100%; height: 100%; position: absolute; }}
            #animation {{ width: 100%; height: 100%; position: absolute; }}
            #overlay {{ width: 100%; height: 100%; position: absolute; }}
            .fill-screen {{ width: 100%; height: 100%; position: absolute; }}
            #status {{ 
                position: absolute; 
                bottom: 20px; 
                left: 50%; 
                transform: translateX(-50%); 
                color: {'#fff' if dark_mode else '#333'}; 
                font-family: sans-serif; 
                font-size: 12px; 
            }}
        </style>
    </head>
    <body>
        <div id="viz-container" style="width: {width}px; height: {height}px; position: relative; margin: 0 auto;">
            <svg id="map" class="fill-screen" xmlns="http://www.w3.org/2000/svg" version="1.1"></svg>
            <canvas id="animation" class="fill-screen"></canvas>
            <canvas id="overlay" class="fill-screen"></canvas>
            <div id="status"></div>
        </div>
        
        <!-- Load D3 and TopoJSON -->
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <script src="https://d3js.org/topojson.v3.min.js"></script>
        <script src="https://d3js.org/d3-geo-projection.v4.min.js"></script>
        
        <script>
        (function() {{
            "use strict";
            
            // Constants for visualization
            const WIDTH = {width};
            const HEIGHT = {height};
            const VELOCITY_SCALE = 0.015;
            const MAX_PARTICLE_AGE = 100;
            const PARTICLE_LINE_WIDTH = 1.0;
            const PARTICLE_MULTIPLIER = 8;
            const FRAME_RATE = 40;
            const NULL_WIND_VECTOR = [NaN, NaN, null];
            
            // Background color based on mode
            const backgroundColor = "{('#000' if dark_mode else '#fff')}";
            const globeColor = "{('#303030' if dark_mode else '#e0e0e0')}";
            const coastColor = "{('#505050' if dark_mode else '#808080')}";
            
            // Wind data from Python
            const windData = {wind_data_json};
            
            // SVG and Canvas contexts
            const svg = d3.select("#map");
            const animationCanvas = document.getElementById("animation");
            const animationContext = animationCanvas.getContext("2d");
            const overlayCanvas = document.getElementById("overlay");
            const overlayContext = overlayCanvas.getContext("2d");
            
            // Set canvas dimensions
            animationCanvas.width = WIDTH;
            animationCanvas.height = HEIGHT;
            overlayCanvas.width = WIDTH;
            overlayCanvas.height = HEIGHT;
            
            // D3 projection and path generators
            const projection = d3.geoOrthographic()
                .scale(Math.min(WIDTH, HEIGHT) / 2.5)
                .translate([WIDTH / 2, HEIGHT / 2]);
                
            const path = d3.geoPath()
                .projection(projection);
            
            // Create the globe base
            svg.append("circle")
                .attr("cx", WIDTH / 2)
                .attr("cy", HEIGHT / 2)
                .attr("r", projection.scale())
                .attr("fill", globeColor);
                
            // Load world map data
            d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json").then(world => {{
                // Draw countries
                svg.append("g")
                    .selectAll("path")
                    .data(topojson.feature(world, world.objects.countries).features)
                    .enter().append("path")
                    .attr("d", path)
                    .attr("fill", "none")
                    .attr("stroke", coastColor)
                    .attr("stroke-width", 0.5);
                    
                // Set up the particle system
                initializeParticles();
                
                // Make the globe interactive
                setupInteractivity();
                
                // Start the animation
                startAnimation();
            }}).catch(error => {{
                document.getElementById("status").innerText = "Error loading map data: " + error;
            }});
            
            // Vector field from raw data
            let vectorField = buildVectorField(windData);
            
            // Particle system
            let particles = [];
            
            function buildVectorField(data) {{
                // Build a grid from the raw data
                const points = data.data;
                const field = {{
                    getVector: (lon, lat) => {{
                        // Find the nearest point in our dataset
                        let closest = null;
                        let closestDist = Infinity;
                        
                        for (const point of points) {{
                            const dist = Math.sqrt(
                                Math.pow(point.lon - lon, 2) + 
                                Math.pow(point.lat - lat, 2)
                            );
                            
                            if (dist < closestDist) {{
                                closestDist = dist;
                                closest = point;
                            }}
                        }}
                        
                        if (!closest || closestDist > 10) {{
                            return NULL_WIND_VECTOR;
                        }}
                        
                        return [closest.u, closest.v, Math.sqrt(closest.u * closest.u + closest.v * closest.v)];
                    }}
                }};
                
                return field;
            }}
            
            function initializeParticles() {{
                const numParticles = Math.round(projection.scale() * PARTICLE_MULTIPLIER);
                particles = [];
                
                for (let i = 0; i < numParticles; i++) {{
                    particles.push(randomParticle());
                }}
            }}
            
            function randomParticle() {{
                // Random position on the globe
                const lambda = Math.random() * 360 - 180;  // longitude
                const phi = Math.random() * 180 - 90;      // latitude
                
                return {{
                    x: lambda,
                    y: phi,
                    age: Math.floor(Math.random() * MAX_PARTICLE_AGE),
                    xt: 0,
                    yt: 0
                }};
            }}
            
            function evolve() {{
                const projection = d3.geoOrthographic()
                    .scale(Math.min(WIDTH, HEIGHT) / 2.5)
                    .translate([WIDTH / 2, HEIGHT / 2]);
                
                particles.forEach(particle => {{
                    if (particle.age > MAX_PARTICLE_AGE) {{
                        Object.assign(particle, randomParticle());
                        return;
                    }}
                    
                    const vector = vectorField.getVector(particle.x, particle.y);
                    
                    if (vector[2] === null) {{
                        // No wind vector found, retire this particle
                        particle.age = MAX_PARTICLE_AGE;
                        return;
                    }}
                    
                    // Update position using wind vector
                    const x = particle.x + vector[0] * VELOCITY_SCALE;
                    const y = particle.y + vector[1] * VELOCITY_SCALE;
                    
                    // Save positions for drawing
                    const pos1 = projection([particle.x, particle.y]);
                    const pos2 = projection([x, y]);
                    
                    if (pos1 && pos2) {{
                        particle.xt = pos1[0];
                        particle.yt = pos1[1];
                        particle.x = x;
                        particle.y = y;
                    }} else {{
                        // Off the visible globe, retire this particle
                        particle.age = MAX_PARTICLE_AGE;
                    }}
                    
                    particle.age += 1;
                }});
            }}
            
            function draw() {{
                // Clear the canvas
                animationContext.clearRect(0, 0, WIDTH, HEIGHT);
                
                // Set drawing style
                animationContext.lineWidth = PARTICLE_LINE_WIDTH;
                animationContext.strokeStyle = "{('#76b6f4' if dark_mode else '#4682b4')}";
                animationContext.globalAlpha = 0.8;
                
                // Draw the particles
                animationContext.beginPath();
                particles.forEach(particle => {{
                    if (particle.age < MAX_PARTICLE_AGE) {{
                        // Calculate vector
                        const vector = vectorField.getVector(particle.x, particle.y);
                        if (vector[2] !== null) {{
                            // Get next position
                            const x = particle.x + vector[0] * VELOCITY_SCALE;
                            const y = particle.y + vector[1] * VELOCITY_SCALE;
                            
                            // Project to screen coordinates
                            const pos = projection([x, y]);
                            if (pos) {{
                                animationContext.moveTo(particle.xt, particle.yt);
                                animationContext.lineTo(pos[0], pos[1]);
                                
                                // Update position for next frame
                                particle.xt = pos[0];
                                particle.yt = pos[1];
                            }}
                        }}
                    }}
                }});
                animationContext.stroke();
            }}
            
            function startAnimation() {{
                let lastFrameTime = Date.now();
                
                function frame() {{
                    const now = Date.now();
                    const elapsed = now - lastFrameTime;
                    
                    if (elapsed > (1000 / FRAME_RATE)) {{
                        evolve();
                        draw();
                        lastFrameTime = now;
                    }}
                    
                    requestAnimationFrame(frame);
                }}
                
                frame();
            }}
            
            function setupInteractivity() {{
                let drag = d3.drag()
                    .on("drag", event => {{
                        const rotate = projection.rotate();
                        projection.rotate([
                            rotate[0] + event.dx / 4,
                            rotate[1] - event.dy / 4
                        ]);
                        
                        // Update the map paths
                        svg.selectAll("path").attr("d", path);
                        
                        // Force regenerate particles
                        particles.forEach(p => p.age = MAX_PARTICLE_AGE);
                    }});
                
                svg.call(drag);
            }}
        }})();
        </script>
    </body>
    </html>
    """
    
    return html

def display_animated_earth(dark_mode=True, width=800, height=600):
    """
    Display the animated earth visualization in Streamlit
    
    Args:
        dark_mode: Whether to use dark mode
        width: Visualization width
        height: Visualization height
    """
    # Create container for the visualization with styling
    st.markdown("""
    <div style="margin-top: 30px; margin-bottom: 30px; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); width: 100%;">
        <div style="background: linear-gradient(90deg, #1E90FF, #9370DB); height: 4px;"></div>
        <div id="animated-earth-container" style="width: 100%;"></div>
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
                             ["Wind", "Temperature", "CO2", "Sea Level", "Glacier"], 
                             index=0)
    
    # Generate sample wind data
    wind_data = generate_wind_data()
    
    # Create the animated earth HTML
    html = animated_earth_html(wind_data, dark_mode=dark_mode, width=width, height=height)
    
    # Display using Streamlit components
    components.html(html, height=height+50, scrolling=False)

if __name__ == "__main__":
    display_animated_earth()
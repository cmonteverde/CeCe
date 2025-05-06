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
    # Create a grid of lat/lon coordinates
    lats = np.arange(-90, 90 + resolution, resolution)
    lons = np.arange(-180, 180 + resolution, resolution)
    
    # Sample wind data (u and v components for each grid point)
    grid_data = []
    
    for lat in lats:
        for lon in lons:
            # Create a simple wind pattern (this is placeholder data)
            # In a real application, this would be real climate data
            u = 5 * np.cos(np.radians(lat)) * np.sin(np.radians(lon))
            v = 5 * np.sin(np.radians(lat)) * np.cos(np.radians(lon))
            
            # Add wind magnitude for coloring
            magnitude = np.sqrt(u**2 + v**2)
            
            grid_data.append({
                "lat": float(lat),
                "lon": float(lon),
                "u": float(u),
                "v": float(v),
                "magnitude": float(magnitude)
            })
    
    return {
        "date": "2023-05-06",
        "grid_resolution": resolution,
        "data": grid_data
    }

def animated_earth_html(wind_data=None, dark_mode=True, width=800, height=600):
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
    if wind_data is None:
        wind_data = generate_wind_data()
    
    # Convert wind data to JSON string
    wind_data_json = json.dumps(wind_data)
    
    # HTML and JavaScript for the visualization - using triple quotes rather than f-string
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Animated Earth Visualization</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <script src="https://d3js.org/d3-geo.v2.min.js"></script>
        <script src="https://d3js.org/topojson.v3.min.js"></script>
        <style>
            body { 
                margin: 0; 
                padding: 0; 
                font-family: Arial, sans-serif; 
                background-color: """ + ('#111' if dark_mode else '#fff') + """; 
            }
            .earth-container { 
                position: relative; 
                width: """ + str(width) + """px; 
                height: """ + str(height) + """px; 
                margin: 0 auto; 
            }
            .earth-canvas { 
                position: absolute; 
                top: 0; 
                left: 0; 
            }
            .earth-svg {
                position: absolute;
                top: 0;
                left: 0;
                z-index: 10;
            }
            .controls {
                position: absolute;
                bottom: 10px;
                left: 10px;
                z-index: 20;
                background-color: """ + ('rgba(0, 0, 0, 0.5)' if dark_mode else 'rgba(255, 255, 255, 0.5)') + """;
                padding: 5px;
                border-radius: 5px;
                color: """ + ('#fff' if dark_mode else '#333') + """;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="earth-container">
            <canvas class="earth-canvas" id="earth-canvas" width=\"""" + str(width) + """\" height=\"""" + str(height) + """\"></canvas>
            <svg class="earth-svg" id="earth-svg" width=\"""" + str(width) + """\" height=\"""" + str(height) + """\"></svg>
            <div class="controls">
                <div>Drag to rotate | Scroll to zoom</div>
            </div>
        </div>

        <script>
            // Wind data from Python
            const windData = """ + wind_data_json + """;
            
            // Visualization configuration
            const config = {
                width: """ + str(width) + """,
                height: """ + str(height) + """,
                darkMode: """ + str(dark_mode).lower() + """,
                particleCount: 3000,
                particleMaxAge: 100,
                particleSpeedFactor: 0.25,
                globeColor: """ + ('"#0C2B66"' if dark_mode else '"#4169E1"') + """,
                landColor: """ + ('"#2A3C4D"' if dark_mode else '"#C0D6E4"') + """,
                particleColor: d3.scaleLinear()
                    .domain([0, 10, 20, 30])
                    .range(['"#1E90FF", "#4169E1", "#7B68EE", "#9370DB"'])
            };

            // Create the visualization
            document.addEventListener('DOMContentLoaded', function() {{
                // Setup canvas and WebGL context
                const canvas = document.getElementById('earth-canvas');
                const context = canvas.getContext('2d');
                
                // Setup SVG for the globe outline
                const svg = d3.select('#earth-svg');
                
                // Create a rotating globe
                const projection = d3.geoOrthographic()
                    .scale(Math.min(config.width, config.height) * 0.45)
                    .translate([config.width / 2, config.height / 2]);
                
                // Path generator for land masses
                const path = d3.geoPath().projection(projection);
                
                // Create and initialize particles
                let particles = [];
                
                // Load world map data
                d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
                    .then(function(world) {{
                        // Extract land topojson
                        const land = topojson.feature(world, world.objects.land);
                        
                        // Draw land contours
                        svg.append('path')
                            .datum({{type: 'Sphere'}})
                            .attr('class', 'ocean')
                            .attr('fill', config.globeColor)
                            .attr('stroke', config.darkMode ? '#555' : '#999')
                            .attr('stroke-width', 1)
                            .attr('d', path);
                            
                        svg.append('path')
                            .datum(land)
                            .attr('class', 'land')
                            .attr('fill', config.landColor)
                            .attr('d', path);
                            
                        // Add country borders
                        svg.append('path')
                            .datum(topojson.mesh(world, world.objects.countries, (a, b) => a !== b))
                            .attr('class', 'boundary')
                            .attr('fill', 'none')
                            .attr('stroke', config.darkMode ? '#555' : '#999')
                            .attr('stroke-width', 0.5)
                            .attr('d', path);
                            
                        // Initialize particles
                        initParticles();
                        
                        // Add rotation controls
                        let v0, q0, r0;
                        const drag = d3.drag()
                            .on('start', (event) => {{
                                v0 = versor.cartesian(projection.invert([event.x, event.y]));
                                q0 = versor(r0 = projection.rotate());
                            }})
                            .on('drag', (event) => {{
                                const v1 = versor.cartesian(projection.invert([event.x, event.y]));
                                const q1 = versor.multiply(q0, versor.delta(v0, v1));
                                projection.rotate(r0 = versor.rotation(q1));
                                updateProjection();
                            }});
                            
                        svg.call(drag);
                        
                        // Add zoom controls
                        svg.call(d3.zoom()
                            .scaleExtent([0.75, 5])
                            .on('zoom', (event) => {{
                                projection.scale(Math.min(config.width, config.height) * 0.45 * event.transform.k);
                                updateProjection();
                            }}));
                            
                        // Start animation loop
                        d3.timer(animate);
                    });
                
                // Versor math for smooth rotation (from D3 examples)
                const versor = {{
                    cartesian: (λ, φ) => {{
                        λ = λ * Math.PI / 180;
                        φ = φ * Math.PI / 180;
                        const cosφ = Math.cos(φ);
                        return [
                            cosφ * Math.cos(λ),
                            cosφ * Math.sin(λ),
                            Math.sin(φ)
                        ];
                    }},
                    rotation: (q) => {{
                        return [
                            Math.atan2(2 * (q[0] * q[1] + q[3] * q[2]), 1 - 2 * (q[1] * q[1] + q[2] * q[2])) * 180 / Math.PI,
                            Math.asin(Math.max(-1, Math.min(1, 2 * (q[0] * q[2] - q[3] * q[1])))) * 180 / Math.PI,
                            Math.atan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] * q[2] + q[3] * q[3])) * 180 / Math.PI
                        ];
                    }},
                    multiply: (a, b) => {{
                        return [
                            a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
                            a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
                            a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
                            a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]
                        ];
                    }},
                    delta: (a, b) => {{
                        const d = [0, 0, 0, 0];
                        const c = versor.cartesian;
                        a = typeof a[0] === 'number' ? c(a[0], a[1]) : a;
                        b = typeof b[0] === 'number' ? c(b[0], b[1]) : b;
                        const dot = a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
                        const d_tan = Math.acos(Math.max(-1, Math.min(1, dot)));
                        const d_a = d_tan ? Math.sin(d_tan) : null;
                        if (d_a) {{
                            for (let i = 0; i < 3; ++i) {{
                                d[i + 1] = (a[(i + 1) % 3] * b[(i + 2) % 3] - a[(i + 2) % 3] * b[(i + 1) % 3]) / d_a;
                            }}
                            d[0] = Math.cos(d_tan);
                        }} else {{
                            d[0] = 1;
                        }}
                        return d;
                    }}
                }};
                
                // Update paths when projection changes
                function updateProjection() {{
                    svg.selectAll('path').attr('d', path);
                }}
                
                // Initialize particles for wind animation
                function initParticles() {{
                    particles = [];
                    for (let i = 0; i < config.particleCount; i++) {{
                        // Random position on the globe
                        particles.push({{
                            x: Math.random() * config.width,
                            y: Math.random() * config.height,
                            age: Math.floor(Math.random() * config.particleMaxAge),
                            active: false
                        }});
                    }}
                }}
                
                // Find wind vector at given position using bilinear interpolation
                function getWindVector(λ, φ) {{
                    // Convert to grid coordinates
                    const lat = Math.round(φ / windData.grid_resolution) * windData.grid_resolution;
                    const lon = Math.round(λ / windData.grid_resolution) * windData.grid_resolution;
                    
                    // Find data points
                    const point = windData.data.find(d => d.lat === lat && d.lon === lon);
                    
                    if (point) {{
                        return {{
                            u: point.u,
                            v: point.v,
                            magnitude: point.magnitude
                        }};
                    }}
                    
                    // Default if not found
                    return {{ u: 0, v: 0, magnitude: 0 }};
                }}
                
                // Animation loop
                function animate() {{
                    // Clear canvas
                    context.clearRect(0, 0, config.width, config.height);
                    
                    // Update particles
                    particles.forEach((p, i) => {{
                        p.age += 1;
                        
                        if (p.age > config.particleMaxAge) {{
                            // Reset expired particle to a new random position
                            p.x = Math.random() * config.width;
                            p.y = Math.random() * config.height;
                            p.age = 0;
                            p.active = false;
                        }}
                        
                        // Get the lat/lon from the current x/y position
                        const λφ = projection.invert([p.x, p.y]);
                        
                        // Check if particle is on the front side of the globe
                        if (λφ) {{
                            // Particle is in view
                            const λ = λφ[0];  // longitude
                            const φ = λφ[1];  // latitude
                            
                            // Get wind vector at this position
                            const wind = getWindVector(λ, φ);
                            
                            // Apply wind force to move the particle
                            if (wind.magnitude > 0) {{
                                // Adjust particle position based on wind
                                const projected = projection([
                                    λ + wind.u * config.particleSpeedFactor, 
                                    φ + wind.v * config.particleSpeedFactor
                                ]);
                                
                                if (projected) {{
                                    // Store previous position for drawing
                                    p.px = p.x;
                                    p.py = p.y;
                                    
                                    // Update position
                                    p.x = projected[0];
                                    p.y = projected[1];
                                    p.active = true;
                                    
                                    // Set color based on wind magnitude
                                    p.color = config.particleColor(wind.magnitude);
                                }}
                            }}
                            
                            // Draw particle as a line from previous to current position
                            if (p.active) {{
                                context.beginPath();
                                context.moveTo(p.px, p.py);
                                context.lineTo(p.x, p.y);
                                context.strokeStyle = p.color;
                                context.lineWidth = 1.5;
                                context.globalAlpha = (1 - p.age / config.particleMaxAge) * 0.85;
                                context.stroke();
                            }}
                        }} else {{
                            // Particle is not in view (behind the globe)
                            p.active = false;
                        }}
                    }});
                }}
            }});
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
    header_color = "white" if dark_mode else "#333"
    st.markdown("""
    <div style="margin-top: 20px; margin-bottom: 20px; border-radius: 10px; 
              overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);">
        <div style="background: linear-gradient(90deg, #1E90FF, #9370DB); height: 4px;"></div>
        <h3 style="margin: 10px 15px; color: """ + header_color + """;">
            <span style="background: linear-gradient(90deg, #1E90FF, #9370DB); 
                        -webkit-background-clip: text; 
                        -webkit-text-fill-color: transparent;">
                CeCe Global Wind Patterns
            </span>
        </h3>
    """, unsafe_allow_html=True)
    
    # Generate the visualization HTML
    html = animated_earth_html(dark_mode=dark_mode, width=width, height=height)
    
    # Display in Streamlit
    components.html(html, height=height+40, scrolling=False)
    
    footer_color = "#BBB" if dark_mode else "#777"
    # Add information about the visualization
    st.markdown("""
    <div style="padding: 0 15px 10px; color: """ + footer_color + """; font-size: 12px; text-align: right;">
        Interactive 3D globe visualization - Drag to rotate, scroll to zoom
    </div>
    </div>
    """, unsafe_allow_html=True)


# Run as standalone for testing
if __name__ == "__main__":
    st.set_page_config(page_title="Animated Earth", layout="wide")
    
    st.title("Animated Earth Visualization")
    
    col1, col2 = st.columns([4, 1])
    
    with col2:
        dark_mode = st.checkbox("Dark Mode", value=True)
    
    with col1:
        display_animated_earth(dark_mode=dark_mode, width=800, height=500)
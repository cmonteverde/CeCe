"""
Nullschool-Style Earth Visualization Module

This module provides a simplified version of the earth.nullschool.net visualization,
featuring animated wind patterns on a dark background globe.
"""

import streamlit as st
import streamlit.components.v1 as components

def nullschool_earth(width=800, height=600):
    """
    Create a Nullschool-style Earth visualization with animated wind patterns
    
    Args:
        width: Width of the visualization in pixels
        height: Height of the visualization in pixels
    """
    # The HTML content with inline D3.js and plain JS implementation
    # This is a simplified version inspired by earth.nullschool.net
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Nullschool Earth</title>
        <style>
            body {{ 
                margin: 0; 
                padding: 0; 
                overflow: hidden; 
                background-color: #000; 
                width: 100%;
                height: 100%;
            }}
            #earth-container {{
                width: {width}px; 
                height: {height}px; 
                position: relative; 
                margin: 0 auto;
            }}
            .earth-canvas {{ 
                width: 100%; 
                height: 100%; 
                position: absolute; 
                top: 0; 
                left: 0; 
            }}
            .overlay {{
                position: absolute;
                bottom: 10px;
                right: 10px;
                color: #fff;
                font-family: sans-serif;
                font-size: 12px;
                background: rgba(0,0,0,0.5);
                padding: 5px 10px;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div id="earth-container">
            <canvas id="earth-canvas" class="earth-canvas"></canvas>
            <canvas id="wind-canvas" class="earth-canvas"></canvas>
            <div class="overlay">Climate Copilot</div>
        </div>
        
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <script src="https://d3js.org/d3-geo.v3.min.js"></script>
        <script>
        (function() {{
            // Canvas setup
            const container = document.getElementById('earth-container');
            const earthCanvas = document.getElementById('earth-canvas');
            const windCanvas = document.getElementById('wind-canvas');
            
            // Set canvas dimensions
            earthCanvas.width = {width};
            earthCanvas.height = {height};
            windCanvas.width = {width};
            windCanvas.height = {height};
            
            // Get canvas contexts
            const earthCtx = earthCanvas.getContext('2d');
            const windCtx = windCanvas.getContext('2d');
            
            // Constants
            const width = {width};
            const height = {height};
            const scale = Math.min(width, height) * 0.4;
            const center = [width / 2, height / 2];
            
            // Projection
            const projection = d3.geoOrthographic()
                .scale(scale)
                .translate(center)
                .rotate([0, 0, 0]);
                
            const path = d3.geoPath()
                .projection(projection)
                .context(earthCtx);
            
            // Earth colors
            const oceanColor = "#151515";
            const landColor = "#222";
            const landStrokeColor = "#444";
            const graticuleColor = "#333";
            
            // Wind particle system
            let particles = [];
            const maxParticles = 3000;
            const particleBaseSpeed = 0.7;
            const maxAge = 100;
            const fadeInDuration = 10;
            const fadeOutDuration = 30;
            
            // Wind field
            function createWindField() {{
                // Simplified wind field function based on sine/cosine
                // This is just for visualization purposes
                return {{
                    getWind: function(lon, lat) {{
                        // Convert to radians
                        const lonRad = lon * Math.PI / 180;
                        const latRad = lat * Math.PI / 180;
                        
                        // Create simple vector field with curl
                        const u = Math.sin(latRad) * Math.cos(lonRad + Date.now() * 0.0001) * 0.5;
                        const v = Math.cos(latRad) * Math.sin(lonRad + Date.now() * 0.0001) * 0.5;
                        
                        return [u, v, Math.sqrt(u*u + v*v)];
                    }}
                }};
            }}
            
            const windField = createWindField();
            
            // Create initial particles
            function initParticles() {{
                particles = [];
                for (let i = 0; i < maxParticles; i++) {{
                    particles.push(createParticle());
                }}
            }}
            
            function createParticle() {{
                const lon = Math.random() * 360 - 180;
                const lat = Math.random() * 180 - 90;
                const projected = projection([lon, lat]);
                
                return {{
                    lon: lon,
                    lat: lat,
                    x: projected ? projected[0] : -1000,
                    y: projected ? projected[1] : -1000,
                    age: Math.floor(Math.random() * maxAge),
                    color: getRandomColor()
                }};
            }}
            
            function getRandomColor() {{
                // Blue to purple gradient for particles
                const r = Math.floor(Math.random() * 100 + 50);
                const g = Math.floor(Math.random() * 100 + 50);
                const b = Math.floor(Math.random() * 150 + 105);
                return `rgba(${{r}},${{g}},${{b}},`;
            }}
            
            // Draw the globe and particles
            function draw() {{
                // Clear both canvases
                earthCtx.clearRect(0, 0, width, height);
                windCtx.clearRect(0, 0, width, height);
                
                // Draw Earth
                drawEarth();
                
                // Update and draw particles
                drawParticles();
                
                // Request next frame
                requestAnimationFrame(draw);
            }}
            
            function drawEarth() {{
                // Draw ocean (whole globe)
                earthCtx.beginPath();
                earthCtx.arc(center[0], center[1], scale, 0, 2 * Math.PI);
                earthCtx.fillStyle = oceanColor;
                earthCtx.fill();
                
                // Draw graticule (longitude/latitude lines)
                const graticule = d3.geoGraticule10();
                earthCtx.beginPath();
                path(graticule);
                earthCtx.strokeStyle = graticuleColor;
                earthCtx.lineWidth = 0.5;
                earthCtx.stroke();
                
                // Draw land areas
                fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/land-50m.json')
                    .then(response => response.json())
                    .then(world => {{
                        const land = topojson.feature(world, world.objects.land);
                        
                        earthCtx.beginPath();
                        path(land);
                        earthCtx.fillStyle = landColor;
                        earthCtx.fill();
                        
                        earthCtx.beginPath();
                        path(land);
                        earthCtx.strokeStyle = landStrokeColor;
                        earthCtx.lineWidth = 0.5;
                        earthCtx.stroke();
                    }})
                    .catch(error => {{
                        console.error("Error loading world data:", error);
                        // Draw a simple continent outline as fallback
                        drawFallbackContinents();
                    }});
            }}
            
            function drawFallbackContinents() {{
                // Draw simple continent shapes as fallback
                // Simplified continent outlines
                const continents = [
                    // Africa
                    [[-15, 35], [50, 35], [50, -35], [-15, -35]],
                    // Eurasia
                    [[-10, 80], [170, 80], [170, 0], [-10, 0]],
                    // North America
                    [[-170, 80], [-50, 80], [-50, 0], [-170, 0]],
                    // South America
                    [[-80, 10], [-30, 10], [-30, -55], [-80, -55]],
                    // Australia
                    [[110, -10], [155, -10], [155, -40], [110, -40]]
                ];
                
                continents.forEach(continent => {{
                    earthCtx.beginPath();
                    let first = true;
                    
                    for (const point of continent) {{
                        const projected = projection(point);
                        if (projected) {{
                            if (first) {{
                                earthCtx.moveTo(projected[0], projected[1]);
                                first = false;
                            }} else {{
                                earthCtx.lineTo(projected[0], projected[1]);
                            }}
                        }}
                    }}
                    
                    earthCtx.closePath();
                    earthCtx.fillStyle = landColor;
                    earthCtx.fill();
                    earthCtx.strokeStyle = landStrokeColor;
                    earthCtx.lineWidth = 0.5;
                    earthCtx.stroke();
                }});
            }}
            
            function drawParticles() {{
                // Move each particle along the wind field
                particles.forEach((p, i) => {{
                    // Advance particle age
                    p.age += 1;
                    
                    // Reset old particles
                    if (p.age > maxAge) {{
                        particles[i] = createParticle();
                        return;
                    }}
                    
                    // Calculate wind vector at this position
                    const wind = windField.getWind(p.lon, p.lat);
                    
                    // Update particle position based on wind
                    p.lon += wind[0] * particleBaseSpeed;
                    p.lat += wind[1] * particleBaseSpeed;
                    
                    // Wrap around the globe
                    if (p.lon > 180) p.lon -= 360;
                    if (p.lon < -180) p.lon += 360;
                    if (p.lat > 90) p.lat = 180 - p.lat;
                    if (p.lat < -90) p.lat = -180 - p.lat;
                    
                    // Project new position
                    const projected = projection([p.lon, p.lat]);
                    if (projected) {{
                        const newX = projected[0];
                        const newY = projected[1];
                        
                        // Determine if this particle is visible (on the front of the globe)
                        const r = scale;
                        const dx = newX - center[0];
                        const dy = newY - center[1];
                        const distSq = dx*dx + dy*dy;
                        
                        if (distSq <= r*r) {{
                            // Calculate opacity based on age
                            let alpha = 1.0;
                            if (p.age < fadeInDuration) {{
                                alpha = p.age / fadeInDuration;
                            }} else if (p.age > maxAge - fadeOutDuration) {{
                                alpha = (maxAge - p.age) / fadeOutDuration;
                            }}
                            
                            // Calculate line width based on wind speed
                            const lineWidth = Math.min(3, Math.max(0.5, wind[2] * 3));
                            
                            // Draw line from old position to new position
                            if (p.x > -1000 && p.y > -1000) {{
                                windCtx.beginPath();
                                windCtx.moveTo(p.x, p.y);
                                windCtx.lineTo(newX, newY);
                                windCtx.strokeStyle = p.color + alpha + ")";
                                windCtx.lineWidth = lineWidth;
                                windCtx.stroke();
                            }}
                            
                            // Update particle position
                            p.x = newX;
                            p.y = newY;
                        }} else {{
                            // Particle now on back side of globe, hide it
                            p.x = -1000;
                            p.y = -1000;
                        }}
                    }} else {{
                        // Projection failed, hide particle
                        p.x = -1000;
                        p.y = -1000;
                    }}
                }});
            }}
            
            // Interaction - rotating the globe on drag
            let dragging = false;
            let prevMouse = [0, 0];
            let rotation = [0, 0, 0];
            
            function startDrag(e) {{
                dragging = true;
                const x = e.touches ? e.touches[0].clientX : e.clientX;
                const y = e.touches ? e.touches[0].clientY : e.clientY;
                prevMouse = [x, y];
                
                // Get mouse position relative to container
                const rect = container.getBoundingClientRect();
                const mouseX = x - rect.left;
                const mouseY = y - rect.top;
                
                e.preventDefault();
            }}
            
            function drag(e) {{
                if (!dragging) return;
                
                const x = e.touches ? e.touches[0].clientX : e.clientX;
                const y = e.touches ? e.touches[0].clientY : e.clientY;
                
                // Calculate how much we've moved
                const dx = x - prevMouse[0];
                const dy = y - prevMouse[1];
                prevMouse = [x, y];
                
                // Update rotation
                rotation[0] += dx * 0.5;
                rotation[1] -= dy * 0.5;
                
                // Limit vertical rotation
                rotation[1] = Math.max(-90, Math.min(90, rotation[1]));
                
                // Update projection
                projection.rotate(rotation);
                
                // Reset all particles when dragging
                particles.forEach((p, i) => {{
                    const lon = Math.random() * 360 - 180;
                    const lat = Math.random() * 180 - 90;
                    const projected = projection([lon, lat]);
                    
                    p.lon = lon;
                    p.lat = lat;
                    p.x = projected ? projected[0] : -1000;
                    p.y = projected ? projected[1] : -1000;
                    p.age = Math.floor(Math.random() * maxAge);
                }});
                
                e.preventDefault();
            }}
            
            function endDrag() {{
                dragging = false;
            }}
            
            // Add event listeners for interaction
            container.addEventListener('mousedown', startDrag);
            container.addEventListener('mousemove', drag);
            container.addEventListener('mouseup', endDrag);
            container.addEventListener('mouseleave', endDrag);
            container.addEventListener('touchstart', startDrag);
            container.addEventListener('touchmove', drag);
            container.addEventListener('touchend', endDrag);
            
            // Load TopoJSON library
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/topojson@3/dist/topojson.min.js';
            document.head.appendChild(script);
            
            // Initialize and start animation
            script.onload = () => {{
                initParticles();
                draw();
            }};
            
            // Fallback if TopoJSON fails to load
            script.onerror = () => {{
                initParticles();
                draw();
            }};
        }})();
        </script>
    </body>
    </html>
    """
    
    # Return the HTML to be displayed in Streamlit
    return html

def display_nullschool_earth(width=800, height=600):
    """
    Display the Nullschool-style Earth visualization in Streamlit
    
    Args:
        width: Width of the visualization in pixels
        height: Height of the visualization in pixels
    """
    # Create container with styling
    st.markdown("""
    <div style="margin-top: 30px; margin-bottom: 30px; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); width: 100%;">
        <div style="background: linear-gradient(90deg, #1E90FF, #9370DB); height: 4px;"></div>
        <div id="nullschool-earth-container" style="width: 100%;"></div>
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
                    margin-top: 5px;">
            CeCe Global Climate Explorer (Nullschool Style)
        </div>
        """, unsafe_allow_html=True)
    
    # Display the visualization using streamlit components
    html = nullschool_earth(width=width, height=height)
    components.html(html, height=height+50, scrolling=False)
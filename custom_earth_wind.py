import streamlit as st
import streamlit.components.v1 as components
import random
import json
import math

def generate_sample_wind_data(resolution=5):
    """
    Generate sample wind data on a global grid
    
    Args:
        resolution: Grid resolution in degrees
        
    Returns:
        Dictionary with wind data
    """
    wind_data = []
    
    # Generate points across the globe with latitude (-90 to 90) and longitude (-180 to 180)
    for lat in range(-90, 91, resolution):
        for lon in range(-180, 181, resolution):
            # Create some realistic-looking patterns
            # Wind direction changes with latitude (simplified Coriolis effect)
            u = 5 * math.cos(math.radians(lat)) + random.uniform(-1, 1)
            v = 3 * math.sin(math.radians(lon/2)) + random.uniform(-1, 1)
            
            # Stronger winds near the equator
            magnitude = (4 + random.uniform(-1, 1)) * (1 - abs(lat/90)**2)
            
            wind_data.append({
                "lat": lat,
                "lon": lon,
                "u": u,  # east-west component
                "v": v,  # north-south component
                "magnitude": magnitude
            })
    
    return wind_data

def custom_earth_wind_visualization(height=600, background_color="#000"):
    """
    Create a custom Earth visualization with wind patterns, supporting
    zoom and rotation using mouse directly within Streamlit.
    
    Args:
        height: Height of the visualization in pixels
        background_color: Background color for the visualization
    """
    # Generate sample wind data
    try:
        wind_data = generate_sample_wind_data(5)
    except Exception as e:
        wind_data = []
        st.error(f"Error generating wind data: {str(e)}")
    
    # Convert data to JSON string for embedding in the HTML
    wind_data_json = json.dumps(wind_data)
    
    # Create a D3-based globe with wind visualization and interaction
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <script src="https://d3js.org/d3-geo.v3.min.js"></script>
        <script src="https://d3js.org/topojson.v3.min.js"></script>
        <style>
            body, html {{
                margin: 0;
                padding: 0;
                overflow: hidden;
                width: 100%;
                height: 100%;
                background-color: {background_color};
            }}
            #visualization {{
                width: 100%;
                height: {height}px;
                position: relative;
            }}
            .land {{
                fill: #222;
                stroke: #444;
                stroke-width: 0.5;
            }}
            .graticule {{
                fill: none;
                stroke: #333;
                stroke-width: 0.3;
                opacity: 0.5;
            }}
            .ocean {{
                fill: #10141f;
            }}
            .country {{
                fill: #1e2330;
                stroke: #333;
                stroke-width: 0.3;
            }}
            .country:hover {{
                fill: #2a3142;
            }}
            .wind-particle {{
                fill: rgba(30, 144, 255, 0.7);
                stroke: none;
            }}
            .wind-line {{
                stroke: rgba(30, 144, 255, 0.3);
                stroke-width: 1;
                fill: none;
            }}
            .controls {{
                position: absolute;
                bottom: 20px;
                right: 20px;
                background: rgba(0, 0, 0, 0.7);
                padding: 10px;
                border-radius: 5px;
                color: white;
                font-family: sans-serif;
                font-size: 14px;
                z-index: 1000;
            }}
            .controls button {{
                background: linear-gradient(90deg, #1E90FF, #9370DB);
                border: none;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                cursor: pointer;
                margin: 2px;
                font-weight: bold;
            }}
            .attribution {{
                position: absolute;
                bottom: 10px;
                left: 10px;
                color: #666;
                font-family: sans-serif;
                font-size: 12px;
                z-index: 1000;
            }}
            .attribution a {{
                color: #888;
                text-decoration: none;
            }}
            .attribution a:hover {{
                text-decoration: underline;
            }}
            .overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                background: radial-gradient(circle at center, 
                    rgba(0,0,0,0) 40%, 
                    rgba(0,0,0,0.8) 100%);
            }}
        </style>
    </head>
    <body>
        <div id="visualization"></div>
        <div class="controls">
            <button id="zoomIn">🔍+</button>
            <button id="zoomOut">🔍-</button>
            <button id="resetView">Reset</button>
        </div>
        <div class="attribution">
            CeCe Interactive Globe | Earth Visualization <br>
            Based on <a href="https://earth.nullschool.net" target="_blank">earth.nullschool.net</a>
        </div>
        <script>
            // Initialize globe visualization with D3
            const width = document.getElementById('visualization').clientWidth;
            const height = {height};
            const sensitivity = 75;
            
            // Wind data
            const windData = {wind_data_json};
            
            // Set up projection
            const projection = d3.geoOrthographic()
                .scale(height / 2.5)
                .translate([width / 2, height / 2])
                .clipAngle(90)
                .precision(0.3);
                
            // Create a path generator for map features
            const path = d3.geoPath().projection(projection);
            
            // Create SVG container
            const svg = d3.select("#visualization")
                .append("svg")
                .attr("width", width)
                .attr("height", height);
                
            // Add background circle (ocean)
            svg.append("circle")
                .attr("cx", width / 2)
                .attr("cy", height / 2)
                .attr("r", projection.scale())
                .attr("class", "ocean");
                
            // Create a group for all map elements
            const g = svg.append("g");
            
            // Add graticule
            const graticule = d3.geoGraticule().step([15, 15]);
            g.append("path")
                .datum(graticule)
                .attr("class", "graticule")
                .attr("d", path);
                
            // Create a group for wind particles
            const windLayer = svg.append("g")
                .attr("class", "wind-layer");
                
            // Initialize rotation
            let rotate = [0, 0, 0];
            let lastTime = Date.now();
            let autoRotate = true;
            
            // Animation particles for wind
            const particles = [];
            const numParticles = 1000;
            const maxAge = 100;
            
            function initParticles() {{
                for (let i = 0; i < numParticles; i++) {{
                    particles.push({{
                        x: Math.random() * width,
                        y: Math.random() * height,
                        age: Math.floor(Math.random() * maxAge),
                        isDead: false
                    }});
                }}
            }}
            
            function updateParticles() {{
                windLayer.selectAll("*").remove();
                
                particles.forEach((p, i) => {{
                    if (p.isDead) return;
                    
                    // Convert pixel coordinates back to lat/lon
                    const latLon = projection.invert([p.x, p.y]);
                    if (!latLon) {{
                        p.isDead = true;
                        return;
                    }}
                    
                    // Find nearest wind vector
                    let nearestWind = null;
                    let minDist = Infinity;
                    
                    windData.forEach(w => {{
                        const dist = Math.sqrt(
                            Math.pow(w.lat - latLon[1], 2) + 
                            Math.pow(w.lon - latLon[0], 2)
                        );
                        if (dist < minDist) {{
                            minDist = dist;
                            nearestWind = w;
                        }}
                    }});
                    
                    if (nearestWind) {{
                        // Move particle along wind vector
                        const speed = Math.min(5, nearestWind.magnitude);
                        const x2 = p.x + nearestWind.u * 0.2;
                        const y2 = p.y + nearestWind.v * 0.2;
                        
                        // Draw particle
                        windLayer.append("circle")
                            .attr("class", "wind-particle")
                            .attr("cx", p.x)
                            .attr("cy", p.y)
                            .attr("r", 1)
                            .attr("opacity", 1 - p.age / maxAge);
                            
                        // Draw line from old to new position for faster particles
                        if (speed > 2) {{
                            windLayer.append("line")
                                .attr("class", "wind-line")
                                .attr("x1", p.x)
                                .attr("y1", p.y)
                                .attr("x2", x2)
                                .attr("y2", y2)
                                .attr("opacity", (1 - p.age / maxAge) * 0.5);
                        }}
                        
                        // Update position
                        p.x = x2;
                        p.y = y2;
                        
                        // Check if the particle is still on the visible globe
                        const d = Math.sqrt(
                            Math.pow(p.x - width/2, 2) + 
                            Math.pow(p.y - height/2, 2)
                        );
                        
                        if (d > projection.scale()) {{
                            p.isDead = true;
                        }}
                    }}
                    
                    // Age particle
                    p.age++;
                    if (p.age > maxAge) {{
                        p.isDead = true;
                    }}
                }});
                
                // Replace dead particles
                for (let i = 0; i < particles.length; i++) {{
                    if (particles[i].isDead) {{
                        const lat = (Math.random() * 180) - 90;
                        const lon = (Math.random() * 360) - 180;
                        const pos = projection([lon, lat]);
                        
                        if (pos) {{
                            particles[i] = {{
                                x: pos[0],
                                y: pos[1],
                                age: 0,
                                isDead: false
                            }};
                        }}
                    }}
                }}
            }}
            
            // Load world data
            d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json")
                .then(function(world) {{
                    const countries = topojson.feature(world, world.objects.countries);
                    
                    // Add countries
                    g.selectAll("path.country")
                        .data(countries.features)
                        .enter()
                        .append("path")
                        .attr("class", "country")
                        .attr("d", path);
                    
                    // Initialize wind particles
                    initParticles();
                    
                    // Animation loop
                    function animate() {{
                        const now = Date.now();
                        const elapsed = now - lastTime;
                        lastTime = now;
                        
                        if (autoRotate) {{
                            rotate[0] += elapsed * 0.01;
                            projection.rotate(rotate);
                            
                            // Update all paths
                            svg.selectAll("path").attr("d", path);
                        }}
                        
                        // Update wind particles
                        updateParticles();
                        
                        requestAnimationFrame(animate);
                    }}
                    
                    animate();
                    
                    // Handle drag to rotate
                    const drag = d3.drag()
                        .on("start", function() {{
                            autoRotate = false;
                            const r = projection.rotate();
                            rotate = [r[0], r[1], r[2]];
                        }})
                        .on("drag", function(event) {{
                            const rotate = projection.rotate();
                            projection.rotate([
                                rotate[0] + event.dx / sensitivity,
                                rotate[1] - event.dy / sensitivity,
                                rotate[2]
                            ]);
                            svg.selectAll("path").attr("d", path);
                        }})
                        .on("end", function() {{
                            // Resume auto-rotation after a brief pause
                            setTimeout(() => {{ autoRotate = true; }}, 3000);
                        }});
                        
                    svg.call(drag);
                    
                    // Handle zoom with mouse wheel
                    svg.on("wheel", function(event) {{
                        event.preventDefault();
                        const scale = projection.scale();
                        const newScale = Math.max(
                            height / 5,
                            Math.min(height, scale + event.deltaY * -0.2)
                        );
                        
                        projection.scale(newScale);
                        
                        // Update ocean circle radius
                        svg.select(".ocean")
                            .attr("r", newScale);
                            
                        // Redraw all paths
                        svg.selectAll("path").attr("d", path);
                    }});
                    
                    // Add control button functionality
                    d3.select("#zoomIn").on("click", function() {{
                        const scale = projection.scale();
                        const newScale = Math.min(height, scale * 1.2);
                        projection.scale(newScale);
                        svg.select(".ocean").attr("r", newScale);
                        svg.selectAll("path").attr("d", path);
                    }});
                    
                    d3.select("#zoomOut").on("click", function() {{
                        const scale = projection.scale();
                        const newScale = Math.max(height / 5, scale * 0.8);
                        projection.scale(newScale);
                        svg.select(".ocean").attr("r", newScale);
                        svg.selectAll("path").attr("d", path);
                    }});
                    
                    d3.select("#resetView").on("click", function() {{
                        projection.scale(height / 2.5)
                            .rotate([0, 0, 0]);
                        svg.select(".ocean").attr("r", height / 2.5);
                        rotate = [0, 0, 0];
                        svg.selectAll("path").attr("d", path);
                        autoRotate = true;
                    }});
                })
                .catch(error => console.error("Error loading world data:", error));
        </script>
    </body>
    </html>
    """
    
    # Render the HTML content using Streamlit components
    components.html(html_content, height=height, scrolling=False)

if __name__ == "__main__":
    st.set_page_config(page_title="Interactive Earth Wind Visualization", layout="wide")
    st.title("Interactive Earth Wind Visualization")
    
    custom_earth_wind_visualization(height=700)
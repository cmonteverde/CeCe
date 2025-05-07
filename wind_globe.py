import streamlit as st
import streamlit.components.v1 as components
import json
import random
import math

def generate_wind_data(resolution=10):
    """
    Generate sample wind data on a global grid
    
    Args:
        resolution: Grid resolution in degrees
        
    Returns:
        List of wind data points
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

def interactive_wind_globe(height=600):
    """
    Create an interactive globe with wind visualizations
    using D3.js directly in Streamlit.
    
    Args:
        height: Height of the visualization in pixels
    """
    # Generate sample wind data
    try:
        wind_data = generate_wind_data(10)
    except Exception as e:
        wind_data = []
        st.error(f"Error generating wind data: {str(e)}")
    
    # Convert wind data to JSON
    wind_data_json = json.dumps(wind_data)
    
    # Create HTML for the visualization
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
                background-color: #000;
            }}
            #globe {{
                width: 100%;
                height: {height}px;
                position: relative;
            }}
            .ocean {{
                fill: #151b2d;
            }}
            .land {{
                fill: #283445;
                stroke: #374357;
                stroke-width: 0.5;
            }}
            .graticule {{
                fill: none;
                stroke: #444;
                stroke-width: 0.5px;
                opacity: 0.2;
            }}
            .particle {{
                fill: rgba(100, 180, 255, 0.6);
            }}
            .controls {{
                position: absolute;
                bottom: 20px;
                right: 20px;
                background: rgba(0,0,0,0.5);
                padding: 10px;
                border-radius: 5px;
                color: white;
                z-index: 100;
            }}
            .controls button {{
                background: linear-gradient(90deg, #1E90FF, #9370DB);
                color: white;
                border: none;
                padding: 5px 10px;
                margin: 2px;
                border-radius: 3px;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <div id="globe"></div>
        <div class="controls">
            <button id="zoomIn">Zoom +</button>
            <button id="zoomOut">Zoom -</button>
            <button id="reset">Reset</button>
        </div>
        
        <script>
            // Set up dimensions
            const width = document.getElementById('globe').clientWidth;
            const height = {height};
            
            // Create SVG container
            const svg = d3.select("#globe").append("svg")
                .attr("width", width)
                .attr("height", height);
                
            // Create projection
            const projection = d3.geoOrthographic()
                .scale(height / 2.5)
                .translate([width / 2, height / 2]);
                
            // Create path generator
            const path = d3.geoPath().projection(projection);
            
            // Add ocean background
            svg.append("circle")
                .attr("cx", width / 2)
                .attr("cy", height / 2)
                .attr("r", projection.scale())
                .attr("class", "ocean");
                
            // Add graticule
            const graticule = d3.geoGraticule();
            svg.append("path")
                .datum(graticule)
                .attr("class", "graticule")
                .attr("d", path);
            
            // Add group for particles
            const particleGroup = svg.append("g")
                .attr("class", "particles");
                
            // Wind data from Python
            const windData = {wind_data_json};
            
            // Load world TopoJSON
            d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json")
                .then(function(world) {{
                    // Draw land
                    svg.append("path")
                        .datum(topojson.feature(world, world.objects.land))
                        .attr("class", "land")
                        .attr("d", path);
                
                    // Draw country boundaries
                    svg.append("path")
                        .datum(topojson.mesh(world, world.objects.countries))
                        .attr("class", "boundary")
                        .attr("d", path);
                    
                    // Variables for rotation
                    let rotate = [0, 0];
                    let lastTime = Date.now();
                    let autoRotate = true;
                    
                    // Create particles for wind visualization
                    const particles = [];
                    const numParticles = 700;
                    const maxAge = 100;
                    
                    function initParticles() {{
                        for (let i = 0; i < numParticles; i++) {{
                            // Random position on the globe
                            const lon = Math.random() * 360 - 180;
                            const lat = Math.random() * 180 - 90;
                            const pos = projection([lon, lat]);
                            
                            if (pos) {{
                                particles.push({{
                                    lon: lon,
                                    lat: lat,
                                    x: pos[0],
                                    y: pos[1],
                                    age: Math.floor(Math.random() * maxAge),
                                    isDead: false
                                }});
                            }}
                        }}
                    }}
                    
                    function moveParticles() {{
                        particleGroup.selectAll("*").remove();
                        
                        particles.forEach((p, i) => {{
                            if (p.isDead) return;
                            
                            // Find nearest wind vector
                            let nearestWind = null;
                            let minDist = Infinity;
                            
                            windData.forEach(w => {{
                                const dist = Math.sqrt(
                                    Math.pow(w.lat - p.lat, 2) + 
                                    Math.pow(w.lon - p.lon, 2)
                                );
                                
                                if (dist < minDist) {{
                                    minDist = dist;
                                    nearestWind = w;
                                }}
                            }});
                            
                            if (nearestWind) {{
                                // Calculate new position based on wind
                                p.lon += nearestWind.u * 0.1;
                                p.lat += nearestWind.v * 0.1;
                                
                                // Keep within bounds
                                p.lon = ((p.lon + 180) % 360) - 180;
                                p.lat = Math.max(-90, Math.min(90, p.lat));
                                
                                // Project to screen coordinates
                                const pos = projection([p.lon, p.lat]);
                                
                                if (pos) {{
                                    p.x = pos[0];
                                    p.y = pos[1];
                                    
                                    // Draw particle
                                    particleGroup.append("circle")
                                        .attr("class", "particle")
                                        .attr("cx", p.x)
                                        .attr("cy", p.y)
                                        .attr("r", 1.2)
                                        .attr("opacity", 1 - p.age / maxAge);
                                        
                                    // Update age
                                    p.age++;
                                    if (p.age > maxAge) {{
                                        p.isDead = true;
                                    }}
                                }} else {{
                                    p.isDead = true;
                                }}
                            }}
                        }});
                        
                        // Replace dead particles
                        for (let i = 0; i < particles.length; i++) {{
                            if (particles[i].isDead) {{
                                const lon = Math.random() * 360 - 180;
                                const lat = Math.random() * 180 - 90;
                                const pos = projection([lon, lat]);
                                
                                if (pos) {{
                                    particles[i] = {{
                                        lon: lon,
                                        lat: lat,
                                        x: pos[0],
                                        y: pos[1],
                                        age: 0,
                                        isDead: false
                                    }};
                                }}
                            }}
                        }}
                    }}
                    
                    // Initialize particles
                    initParticles();
                    
                    // Animation function
                    function animate() {{
                        if (autoRotate) {{
                            const now = Date.now();
                            const elapsed = now - lastTime;
                            lastTime = now;
                            
                            rotate[0] += elapsed * 0.01;
                            projection.rotate(rotate);
                            
                            svg.selectAll("path").attr("d", path);
                        }}
                        
                        // Update particle positions
                        moveParticles();
                        
                        requestAnimationFrame(animate);
                    }}
                    
                    // Start animation
                    animate();
                    
                    // Drag to rotate
                    const drag = d3.drag()
                        .on("start", function() {{
                            autoRotate = false;
                            const r = projection.rotate();
                            rotate = [r[0], r[1]];
                        }})
                        .on("drag", function(event) {{
                            const r = projection.rotate();
                            projection.rotate([
                                rotate[0] + event.dx / 4,
                                rotate[1] - event.dy / 4
                            ]);
                            svg.selectAll("path").attr("d", path);
                        }})
                        .on("end", function() {{
                            setTimeout(() => {{ autoRotate = true; }}, 1500);
                        }});
                        
                    svg.call(drag);
                    
                    // Mouse wheel zooming
                    svg.on("wheel", function(event) {{
                        event.preventDefault();
                        
                        const scale = projection.scale();
                        const new_scale = Math.max(
                            height / 4,
                            Math.min(height, scale + event.deltaY * -0.1)
                        );
                        
                        projection.scale(new_scale);
                        
                        // Update ocean radius
                        svg.select(".ocean").attr("r", new_scale);
                        
                        // Redraw paths
                        svg.selectAll("path").attr("d", path);
                    }});
                    
                    // Controls
                    d3.select("#zoomIn").on("click", function() {{
                        const scale = projection.scale();
                        const new_scale = Math.min(height, scale * 1.2);
                        projection.scale(new_scale);
                        svg.select(".ocean").attr("r", new_scale);
                        svg.selectAll("path").attr("d", path);
                    }});
                    
                    d3.select("#zoomOut").on("click", function() {{
                        const scale = projection.scale();
                        const new_scale = Math.max(height / 4, scale * 0.8);
                        projection.scale(new_scale);
                        svg.select(".ocean").attr("r", new_scale);
                        svg.selectAll("path").attr("d", path);
                    }});
                    
                    d3.select("#reset").on("click", function() {{
                        projection.scale(height / 2.5).rotate([0, 0]);
                        svg.select(".ocean").attr("r", height / 2.5);
                        rotate = [0, 0];
                        svg.selectAll("path").attr("d", path);
                        autoRotate = true;
                    }});
                }});
        </script>
    </body>
    </html>
    """
    
    # Render the HTML with Streamlit components
    components.html(html_content, height=height)

if __name__ == "__main__":
    st.set_page_config(page_title="Interactive Wind Globe", layout="wide")
    st.title("Interactive Wind Globe")
    interactive_wind_globe(height=600)
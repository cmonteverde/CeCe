import streamlit as st
import streamlit.components.v1 as components

def custom_earth_visualization(height=600, mode="wind", background_color="#000"):
    """
    Create a custom Earth visualization with full zoom and rotation controls
    using D3.js directly in Streamlit.
    
    Args:
        height: Height of the visualization in pixels
        mode: Data visualization mode (wind, ocean, chem)
        background_color: Background color for the visualization
    """
    # Create a D3-based globe with zoom/rotation capabilities
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
                stroke: #555;
                stroke-width: 0.5;
            }}
            .graticule {{
                fill: none;
                stroke: #333;
                stroke-width: 0.3;
                opacity: 0.5;
            }}
            .ocean {{
                fill: #111;
            }}
            .country {{
                fill: #2a2a2a;
                stroke: #444;
                stroke-width: 0.3;
            }}
            .country:hover {{
                fill: #444;
            }}
            .point {{
                fill: rgba(30, 144, 255, 0.6);
                stroke: white;
                stroke-width: 0.5;
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
            Interactive Globe | Inspired by <a href="https://earth.nullschool.net" target="_blank">earth.nullschool.net</a>
        </div>
        <script>
            // Initialize globe visualization with D3
            const width = document.getElementById('visualization').clientWidth;
            const height = {height};
            const sensitivity = 75;
            
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
                .attr("class", "ocean")
                .attr("fill", "#001133");
                
            // Create a group for all map elements
            const g = svg.append("g");
            
            // Add graticule
            const graticule = d3.geoGraticule();
            g.append("path")
                .datum(graticule)
                .attr("class", "graticule")
                .attr("d", path);
                
            // Add overlay gradient
            svg.append("div")
                .attr("class", "overlay");
                
            // Initialize rotation
            let rotate = [0, 0, 0];
            let lastTime = 0;
            
            // Load world data
            d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json")
                .then(function(world) {
                    const countries = topojson.feature(world, world.objects.countries);
                    
                    // Add countries
                    g.selectAll("path.country")
                        .data(countries.features)
                        .enter()
                        .append("path")
                        .attr("class", "country")
                        .attr("d", path);
                    
                    // Initialize auto rotation
                    let autoRotate = true;
                    const globeRotate = () => {{
                        const now = Date.now();
                        const elapsed = now - lastTime;
                        lastTime = now;
                        
                        if (autoRotate) {{
                            rotate[0] += elapsed * 0.01;
                            projection.rotate(rotate);
                            svg.selectAll("path").attr("d", path);
                        }}
                        
                        requestAnimationFrame(globeRotate);
                    }};
                    
                    lastTime = Date.now();
                    globeRotate();
                    
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
                    
                    // Add some data visualization based on mode
                    if ("{mode}" === "wind") {{
                        // Simulate wind data with random points and lines
                        const points = [];
                        for (let i = 0; i < 300; i++) {{
                            points.push([
                                (Math.random() - 0.5) * 360,
                                (Math.random() - 0.5) * 180
                            ]);
                        }}
                        
                        g.selectAll("circle.point")
                            .data(points)
                            .enter()
                            .append("circle")
                            .attr("class", "point")
                            .attr("cx", d => projection(d)[0])
                            .attr("cy", d => projection(d)[1])
                            .attr("r", 1.5)
                            .attr("fill", "rgba(30, 144, 255, 0.6)");
                            
                        // Update points during rotation
                        const updatePoints = () => {{
                            g.selectAll("circle.point")
                                .attr("cx", d => {{
                                    const pos = projection(d);
                                    return pos ? pos[0] : 0;
                                }})
                                .attr("cy", d => {{
                                    const pos = projection(d);
                                    return pos ? pos[1] : 0;
                                }})
                                .attr("opacity", d => {{
                                    const pos = projection(d);
                                    return pos ? 1 : 0;
                                }});
                            requestAnimationFrame(updatePoints);
                        }};
                        updatePoints();
                    }}
                })
                .catch(error => console.error("Error loading world data:", error));
        </script>
    </body>
    </html>
    """
    
    # Render the HTML content using Streamlit components
    components.html(html_content, height=height, scrolling=False)

if __name__ == "__main__":
    st.set_page_config(page_title="Interactive Earth Visualization", layout="wide")
    st.title("Interactive Earth Visualization")
    
    custom_earth_visualization(height=700)
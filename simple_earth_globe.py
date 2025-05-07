import streamlit as st
import streamlit.components.v1 as components

def simple_earth_globe(height=600):
    """
    Create a simple D3.js-based interactive Earth globe
    with zoom and rotation capabilities.
    
    Args:
        height: Height of the visualization in pixels
    """
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
                background-color: black;
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
                    
                    // Auto-rotation function
                    function spin() {{
                        if (autoRotate) {{
                            const now = Date.now();
                            const elapsed = now - lastTime;
                            lastTime = now;
                            
                            rotate[0] += elapsed * 0.01;
                            projection.rotate(rotate);
                            
                            svg.selectAll("path").attr("d", path);
                        }}
                        requestAnimationFrame(spin);
                    }}
                    
                    // Start auto-rotation
                    spin();
                    
                    // Drag to rotate
                    const drag = d3.drag()
                        .on("start", function() {{
                            autoRotate = false;
                            r = projection.rotate();
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
    st.set_page_config(page_title="Simple Earth Globe", layout="wide")
    st.title("Simple Interactive Earth Globe")
    simple_earth_globe(height=600)
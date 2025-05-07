import streamlit as st
import components.v1 as components
import os

def display_nullschool_earth(url="https://earth.nullschool.net", height=600):
    """
    Uses Streamlit components.html to directly embed Earth Nullschool with full mouse interactivity.
    This approach bypasses Streamlit's iframe handling which can sometimes block mouse events.
    
    Args:
        url: The URL for Earth Nullschool including any view parameters
        height: Height of the component in pixels
    """
    # Create a custom HTML component with embedded nullschool
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            html, body {{ margin: 0; padding: 0; height: 100%; overflow: hidden; }}
            #nullschool-container {{
                width: 100%;
                height: {height}px;
                border-radius: 15px;
                overflow: hidden;
                position: relative;
            }}
            iframe {{
                border: none;
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                border-radius: 15px;
            }}
            .attribution {{
                position: absolute;
                bottom: 10px;
                right: 10px;
                background-color: rgba(0,0,0,0.5);
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 12px;
                color: white;
                z-index: 10;
            }}
            .attribution a {{
                color: #1E90FF;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div id="nullschool-container">
            <iframe src="{url}" allowfullscreen="true" allow="fullscreen"></iframe>
            <div class="attribution">
                Powered by <a href="https://earth.nullschool.net" target="_blank">earth.nullschool.net</a>
            </div>
        </div>
        <script>
            // Make sure the iframe gets focus for mouse events
            document.addEventListener('DOMContentLoaded', () => {{
                const iframe = document.querySelector('iframe');
                iframe.addEventListener('load', () => {{
                    iframe.focus();
                }});
                
                // Help ensure mouse events work
                iframe.style.pointerEvents = 'auto';
            }});
        </script>
    </body>
    </html>
    """
    
    # Use Streamlit's components.html to render the HTML content
    components.html(html_content, height=height+30, scrolling=False)

if __name__ == "__main__":
    st.set_page_config(page_title="Earth Nullschool Component", layout="wide")
    st.title("Earth Nullschool Visualization Component")
    
    # Sample URL with parameters
    url = "https://earth.nullschool.net/#current/wind/surface/level/orthographic=0,0,400"
    
    display_nullschool_earth(url=url, height=700)
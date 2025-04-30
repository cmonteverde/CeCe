"""
NASA Earth Explorer Elevation Module

This module provides functions to access elevation data from NASA Earth Explorer (USGS)
using authenticated requests. Requires a registered account with Earth Explorer.

Provides higher-quality global elevation data sets compared to other publicly available sources.
"""

import os
import io
import json
import time
import tempfile
import numpy as np
import requests
from requests.auth import HTTPBasicAuth
import matplotlib.pyplot as plt

# NASA Earth Explorer API endpoints
EE_LOGIN_URL = "https://ers.cr.usgs.gov/login"
EE_LOGOUT_URL = "https://ers.cr.usgs.gov/logout"
EE_SEARCH_URL = "https://earthexplorer.usgs.gov/inventory/json/v/1.4.1/search"
EE_DOWNLOAD_URL = "https://earthexplorer.usgs.gov/inventory/json/v/1.4.1/download"

# SRTM dataset identifiers in Earth Explorer
SRTM_1ARC_GLOBAL = "SRTM1"  # 1 arc-second (~30m) global coverage

class EarthExplorerAPI:
    """Client for NASA Earth Explorer API"""
    
    def __init__(self):
        """Initialize Earth Explorer API client"""
        self.session = requests.Session()
        self.api_key = None
        self.logged_in = False
    
    def login(self):
        """Login to Earth Explorer and get API key"""
        # Get credentials from environment variables
        username = os.environ.get("NASA_EE_USERNAME")
        password = os.environ.get("NASA_EE_PASSWORD")
        
        if not username or not password:
            print("NASA Earth Explorer credentials not found in environment variables")
            return False
        
        # First, get the login page to retrieve the CSRF token
        try:
            login_page = self.session.get(EE_LOGIN_URL)
            
            # Attempt login
            login_data = {
                "username": username,
                "password": password,
                "catalogId": "EE"
            }
            
            response = self.session.post(
                EE_LOGIN_URL, 
                data=login_data,
                headers={"Referer": EE_LOGIN_URL}
            )
            
            if response.status_code == 200:
                # If login successful, we should have cookies in the session
                if "EROS_SSO_cookie" in self.session.cookies:
                    print("Successfully logged into NASA Earth Explorer")
                    self.logged_in = True
                    
                    # Get API key
                    api_key_url = "https://earthexplorer.usgs.gov/inventory/json/v/1.4.1/api/api/login"
                    api_response = self.session.post(
                        api_key_url,
                        json={"username": username, "password": password}
                    )
                    
                    if api_response.status_code == 200:
                        data = api_response.json()
                        if "data" in data and "token" in data["data"]:
                            self.api_key = data["data"]["token"]
                            print("Successfully obtained API key")
                            return True
            
            print(f"Login failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"Error during login: {e}")
            return False
    
    def search_srtm(self, lat, lon, dataset=SRTM_1ARC_GLOBAL):
        """
        Search for SRTM data covering the specified coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            dataset: Earth Explorer dataset ID
            
        Returns:
            List of scene IDs
        """
        if not self.logged_in and not self.login():
            print("Not logged in, cannot search")
            return []
            
        # Create search parameters
        search_params = {
            "apiKey": self.api_key,
            "datasetName": dataset,
            "spatialFilter": {
                "filterType": "mbr",
                "lowerLeft": {
                    "latitude": lat - 0.1,
                    "longitude": lon - 0.1
                },
                "upperRight": {
                    "latitude": lat + 0.1,
                    "longitude": lon + 0.1
                }
            },
            "maxResults": 10
        }
        
        try:
            response = self.session.post(
                EE_SEARCH_URL,
                json=search_params,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "results" in data["data"]:
                    scene_ids = [result["entityId"] for result in data["data"]["results"]]
                    print(f"Found {len(scene_ids)} SRTM scenes")
                    return scene_ids
            
            print(f"Search failed: {response.status_code}")
            return []
            
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def download_scene(self, scene_id, dataset=SRTM_1ARC_GLOBAL):
        """
        Download an SRTM scene by ID
        
        Args:
            scene_id: Earth Explorer scene ID
            dataset: Earth Explorer dataset ID
            
        Returns:
            Path to downloaded file or None
        """
        if not self.logged_in and not self.login():
            print("Not logged in, cannot download")
            return None
            
        # Get download options
        download_params = {
            "apiKey": self.api_key,
            "datasetName": dataset,
            "entityIds": [scene_id]
        }
        
        try:
            # Get download URL
            download_options = self.session.post(
                EE_DOWNLOAD_URL,
                json=download_params,
                headers={"Content-Type": "application/json"}
            )
            
            if download_options.status_code == 200:
                data = download_options.json()
                if "data" in data and len(data["data"]) > 0:
                    download_url = data["data"][0]["url"]
                    
                    # Download the file
                    print(f"Downloading from: {download_url}")
                    file_response = self.session.get(download_url, stream=True)
                    
                    if file_response.status_code == 200:
                        # Save to temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as tmp_file:
                            for chunk in file_response.iter_content(chunk_size=8192):
                                tmp_file.write(chunk)
                            return tmp_file.name
            
            print(f"Download failed with status: {download_options.status_code}")
            return None
            
        except Exception as e:
            print(f"Error during download: {e}")
            return None
    
    def logout(self):
        """Logout from Earth Explorer"""
        if self.logged_in:
            try:
                response = self.session.get(EE_LOGOUT_URL)
                if response.status_code == 200:
                    print("Successfully logged out from NASA Earth Explorer")
                self.logged_in = False
                self.api_key = None
            except Exception as e:
                print(f"Error during logout: {e}")

def fetch_elevation_data(lat, lon, width=100, height=100, radius=0.05):
    """
    Fetch elevation data from NASA Earth Explorer for a region centered at lat, lon
    
    Args:
        lat: Center latitude
        lon: Center longitude
        width: Width of output array
        height: Height of output array
        radius: Radius around center point in degrees
        
    Returns:
        Tuple of (elevation_array, bounds)
    """
    print(f"Fetching NASA Earth Explorer elevation data for {lat}, {lon}")
    
    bounds = (lon - radius, lat - radius, lon + radius, lat + radius)
    
    # Create API client
    ee_client = EarthExplorerAPI()
    
    try:
        # Login
        if not ee_client.login():
            print("Failed to login to NASA Earth Explorer")
            return None, bounds
        
        # Search for scenes
        scene_ids = ee_client.search_srtm(lat, lon)
        if not scene_ids:
            print("No scenes found")
            return None, bounds
        
        # Download the first scene
        scene_file = ee_client.download_scene(scene_ids[0])
        if not scene_file:
            print("Failed to download scene")
            return None, bounds
        
        # Process the downloaded file
        try:
            # Read the GeoTIFF file
            import rasterio
            from rasterio.warp import calculate_default_transform, reproject, Resampling
            
            with rasterio.open(scene_file) as src:
                # Get the window for our bounds
                window = rasterio.windows.from_bounds(
                    bounds[0], bounds[1], bounds[2], bounds[3], 
                    src.transform
                )
                
                # Read the data within the window
                elevation_data = src.read(1, window=window)
                
                # Resample to desired dimensions if necessary
                if elevation_data.shape != (height, width):
                    from scipy.ndimage import zoom
                    
                    # Calculate zoom factors
                    zoom_y = height / elevation_data.shape[0]
                    zoom_x = width / elevation_data.shape[1]
                    
                    # Resample
                    elevation_data = zoom(elevation_data, (zoom_y, zoom_x), order=1)
                
                # Clean up the temporary file
                try:
                    os.unlink(scene_file)
                except:
                    pass
                
                print(f"Successfully fetched NASA EE elevation data, shape: {elevation_data.shape}")
                return elevation_data, bounds
                
        except Exception as e:
            print(f"Error processing elevation data: {e}")
            
            # Clean up the temporary file
            try:
                os.unlink(scene_file)
            except:
                pass
            
            return None, bounds
            
    except Exception as e:
        print(f"Error fetching NASA EE elevation data: {e}")
        return None, bounds
    finally:
        # Always logout to close the session
        ee_client.logout()

if __name__ == "__main__":
    # Test the functionality
    elevation_data, bounds = fetch_elevation_data(37.7749, -122.4194)  # San Francisco
    
    if elevation_data is not None:
        plt.figure(figsize=(10, 8))
        plt.imshow(elevation_data, cmap='terrain')
        plt.colorbar(label='Elevation (meters)')
        plt.title(f"NASA Earth Explorer Elevation Data")
        plt.show()
"""
GeoJSON Utilities for Drawing Maps

This module provides utility functions for accessing coastline 
and country border data in a format suitable for Plotly.
"""

import numpy as np

def get_coastlines():
    """
    Generate simplified world coastlines for plotting
    
    Returns:
        List of line segments, each containing ([longitudes], [latitudes])
    """
    # Simple approximation of major coastlines in format suitable for plotting
    # Each segment is a tuple of (lon_list, lat_list)
    coastlines = []
    
    # North America East Coast (simplified)
    coastlines.append((
        [-80, -75, -70, -65, -60, -65, -70, -75, -80],
        [25, 35, 40, 43, 45, 50, 55, 60, 65]
    ))
    
    # North America West Coast (simplified)
    coastlines.append((
        [-125, -120, -115, -110, -105, -110, -115, -120, -125, -130, -135],
        [30, 35, 40, 45, 50, 55, 60, 65, 60, 55, 50]
    ))
    
    # South America East Coast (simplified)
    coastlines.append((
        [-35, -40, -45, -50, -55, -60, -65, -70, -75, -80],
        [5, 0, -5, -10, -15, -20, -25, -30, -35, -40]
    ))
    
    # South America West Coast (simplified)
    coastlines.append((
        [-80, -75, -70, -75, -80, -85, -90],
        [-40, -30, -20, -10, 0, 5, 10]
    ))
    
    # Europe (simplified)
    coastlines.append((
        [-10, -5, 0, 5, 10, 15, 20, 25, 30],
        [35, 40, 45, 50, 55, 60, 55, 50, 45]
    ))
    
    # Africa (simplified)
    coastlines.append((
        [-15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50],
        [25, 20, 15, 10, 5, 0, -5, -10, -15, -20, -25, -30, -25, -20]
    ))
    
    # Asia (simplified)
    coastlines.append((
        [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150],
        [40, 45, 50, 55, 60, 55, 50, 45, 40, 35, 40, 45, 50]
    ))
    
    # Australia (simplified)
    coastlines.append((
        [115, 120, 125, 130, 135, 140, 145, 150, 145, 140, 135, 130, 125, 120, 115],
        [-35, -30, -25, -20, -15, -20, -25, -30, -35, -40, -35, -30, -25, -30, -35]
    ))
    
    # Antarctica (simplified)
    coastlines.append((
        [-180, -150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150, 180],
        [-65, -70, -75, -70, -65, -70, -75, -70, -65, -70, -75, -70, -65]
    ))
    
    return coastlines

def get_country_borders():
    """
    Generate simplified world country borders for plotting
    
    Returns:
        List of line segments, each containing ([longitudes], [latitudes])
    """
    # Simple approximation of major country borders in format suitable for plotting
    # Each segment is a tuple of (lon_list, lat_list)
    borders = []
    
    # US-Canada border (simplified)
    borders.append((
        [-125, -120, -115, -110, -105, -100, -95, -90, -85, -80, -75, -70],
        [49, 49, 49, 49, 49, 49, 49, 47, 45, 45, 45, 47]
    ))
    
    # US-Mexico border (simplified)
    borders.append((
        [-120, -115, -110, -105, -100, -95],
        [32, 32, 31.5, 31, 30, 26]
    ))
    
    # European borders (simplified collection)
    borders.append((
        [0, 5, 10, 15, 20, 25],
        [45, 47, 49, 50, 51, 52]
    ))
    
    # Russia-China border (simplified)
    borders.append((
        [80, 90, 100, 110, 120, 130],
        [50, 49, 48, 47, 46, 45]
    ))
    
    # India borders (simplified)
    borders.append((
        [70, 75, 80, 85, 90, 95],
        [35, 32, 29, 27, 26, 28]
    ))
    
    return borders
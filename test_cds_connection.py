"""
Test script to verify CDS API credentials are working correctly
"""

import os
import cdsapi
import time
import sys

def test_cds_connection():
    """Test the connection to the CDS API"""
    print("Testing CDS API connection...")
    
    # Check that we have the environment variables
    cds_url = os.environ.get("CDS_URL")
    cds_key = os.environ.get("CDS_KEY")
    
    if not cds_url or not cds_key:
        print("ERROR: CDS_URL or CDS_KEY environment variables are not set.")
        return False
    
    print(f"CDS_URL: {cds_url}")
    print(f"CDS_KEY: {'*' * (len(cds_key) - 8) + cds_key[-8:] if cds_key else 'Not set'}")
    
    try:
        # Try to initialize the CDS client
        client = cdsapi.Client()
        print("CDS client initialized successfully!")
        
        # Try a simple request (metadata only)
        print("Testing a small API request (retrieving product information)...")
        
        start_time = time.time()
        result = client.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': '2m_temperature',
                'year': '2023',
                'month': '01',
                'day': '01',
                'time': '12:00',
                'format': 'netcdf',
                'area': [50, -5, 49, -3],  # Small area (Northern France)
            },
            'test_data.nc'
        )
        
        # Wait for request to finish
        while not result.complete():
            print("Request in progress... waiting.")
            time.sleep(2)
        
        end_time = time.time()
        
        # If we got here, the request worked
        print(f"Request completed successfully in {end_time - start_time:.2f} seconds!")
        print("CDS API connection is working correctly.")
        
        # Clean up the file
        if os.path.exists('test_data.nc'):
            os.remove('test_data.nc')
            
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to connect to CDS API: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_cds_connection()
    sys.exit(0 if success else 1)
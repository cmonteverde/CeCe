"""
Test API connections for both CDS and NASA POWER APIs
"""
import os
import sys
import time
import json
import requests
import traceback

def test_nasa_power():
    """Test NASA POWER API connection"""
    print("\n--- Testing NASA POWER API Connection ---")
    
    try:
        # NASA POWER API doesn't require authentication
        base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        
        # Parameters for a small test request
        params = {
            'parameters': 'T2M',  # Temperature at 2 Meters
            'community': 'RE',
            'longitude': -75.0,
            'latitude': 40.0,
            'start': '20230101',
            'end': '20230102',
            'format': 'JSON'
        }
        
        print("Sending request to NASA POWER API...")
        start_time = time.time()
        response = requests.get(base_url, params=params)
        end_time = time.time()
        
        print(f"Request completed in {end_time - start_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Successfully retrieved data for coordinates: ({params['latitude']}, {params['longitude']})")
            
            # Check if the response has the expected structure
            if 'properties' in data and 'parameter' in data['properties']:
                param_data = data['properties']['parameter']
                if 'T2M' in param_data:
                    print("Data sample:")
                    for date, value in list(param_data['T2M'].items())[:3]:
                        print(f"  {date}: {value}°C")
                    return True
            
            print("Unexpected response format")
            print(json.dumps(data, indent=2)[:500] + "...")  # Print part of the response
            return False
        else:
            print(f"Error: {response.status_code}")
            print(response.text[:500])  # Print part of the error message
            return False
    
    except Exception as e:
        print(f"Error testing NASA POWER API: {str(e)}")
        traceback.print_exc()
        return False

def test_cds_api():
    """Test CDS API connection"""
    print("\n--- Testing CDS API Connection ---")
    
    print("Environment variables:")
    print(f"CDS_USER_ID: {'Set' if os.environ.get('CDS_USER_ID') else 'Not set'}")
    print(f"CDS_API_TOKEN: {'Set' if os.environ.get('CDS_API_TOKEN') else 'Not set'}")
    
    # Check if .cdsapirc exists
    home_dir = os.path.expanduser("~")
    cdsapirc_path = os.path.join(home_dir, ".cdsapirc")
    
    if os.path.exists(cdsapirc_path):
        print(f"\nFound .cdsapirc at {cdsapirc_path}")
        try:
            with open(cdsapirc_path, 'r') as f:
                content = f.read()
                # Don't print the actual key
                content_lines = content.strip().split('\n')
                url_line = next((line for line in content_lines if line.startswith('url:')), "url: Not found")
                key_line = next((line for line in content_lines if line.startswith('key:')), "key: Not found")
                key_parts = key_line.split(':')
                if len(key_parts) >= 2:
                    masked_key = f"{key_parts[1]}:{'*' * 8}"
                    key_line = f"key: {masked_key}"
                
                print(url_line)
                print(key_line)
        except Exception as e:
            print(f"Error reading .cdsapirc: {str(e)}")
    else:
        print(f"\n.cdsapirc not found at {cdsapirc_path}")
        print("Creating .cdsapirc file...")
        
        # Create .cdsapirc file
        try:
            user_id = os.environ.get('CDS_USER_ID', '')
            api_token = os.environ.get('CDS_API_TOKEN', '')
            
            if not user_id or not api_token:
                print("ERROR: CDS_USER_ID or CDS_API_TOKEN environment variables not set")
                return False
            
            with open(cdsapirc_path, 'w') as f:
                f.write(f"url: https://cds.climate.copernicus.eu/api/v2\nkey: {user_id}:{api_token}\n")
            
            print(f"Created .cdsapirc at {cdsapirc_path}")
        except Exception as e:
            print(f"Error creating .cdsapirc: {str(e)}")
            return False
    
    # Check if cdsapi is installed
    try:
        import cdsapi
        print("\ncdsapi module is installed")
    except ImportError:
        print("\nERROR: cdsapi module is not installed")
        return False
    
    # Test CDS API with a simple request
    try:
        print("\nInitializing CDS client...")
        client = cdsapi.Client()
        
        print("Testing connection with a small ERA5 request...")
        output_file = 'test_cds_data.nc'
        
        # Clean up any existing file
        if os.path.exists(output_file):
            os.remove(output_file)
        
        # Make a small request
        start_time = time.time()
        print("Submitting request for ERA5 data...")
        result = client.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'format': 'netcdf',
                'variable': 'surface_temperature',
                'year': '2020',
                'month': '01',
                'day': '01',
                'time': '12:00',
                'area': [50, -10, 40, 5],  # North, West, South, East
            },
            output_file
        )
        
        print("Request submitted. Waiting for data...")
        result.wait()
        
        end_time = time.time()
        print(f"Request completed in {end_time - start_time:.2f} seconds")
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / 1024  # Size in KB
            print(f"File downloaded: {output_file} ({file_size:.2f} KB)")
            os.remove(output_file)  # Clean up
            return True
        else:
            print(f"File not created: {output_file}")
            return False
    
    except Exception as e:
        print(f"\nError testing CDS API: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing API connections for climate data...")
    
    # Test NASA POWER API
    nasa_result = test_nasa_power()
    
    # Test CDS API
    cds_result = test_cds_api()
    
    # Summary
    print("\n--- Connection Test Results ---")
    print(f"NASA POWER API: {'SUCCESS' if nasa_result else 'FAILED'}")
    print(f"CDS API: {'SUCCESS' if cds_result else 'FAILED'}")
    
    if nasa_result and not cds_result:
        print("\nRecommendation: Use NASA POWER API for climate data")
    elif cds_result and not nasa_result:
        print("\nRecommendation: Use CDS API for ERA5 data")
    elif nasa_result and cds_result:
        print("\nRecommendation: Both APIs are available - ERA5 has higher resolution but NASA POWER is simpler to use")
    else:
        print("\nRecommendation: Troubleshoot API connections or consider using synthetic data for development")
    
    sys.exit(0 if nasa_result or cds_result else 1)
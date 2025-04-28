"""
Test script to verify we can fetch and process ERA5 data
"""

import os
import cdsapi
import time
import sys
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np

def test_era5_data_access():
    """Test that we can fetch and process ERA5 data"""
    print("Testing ERA5 data access...")
    
    # Verify the .cdsapirc file exists
    home_dir = os.path.expanduser("~")
    cdsapirc_path = os.path.join(home_dir, ".cdsapirc")
    
    if not os.path.exists(cdsapirc_path):
        print(f"ERROR: .cdsapirc file not found at {cdsapirc_path}")
        return False
    
    print(f"Found .cdsapirc file at {cdsapirc_path}")
    
    # Initialize CDS client
    try:
        client = cdsapi.Client()
        print("CDS client initialized successfully!")
        
        # Get a small amount of ERA5 data (small area, 1 day, 1 variable)
        output_file = 'test_era5_data.nc'
        
        if os.path.exists(output_file):
            os.remove(output_file)
        
        print("Requesting a small ERA5 dataset...")
        
        # Request data
        start_time = time.time()
        result = client.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'format': 'netcdf',
                'variable': '2m_temperature',
                'year': '2023',
                'month': '01',
                'day': '01',
                'time': [
                    '00:00', '12:00',
                ],
                'area': [50, -10, 35, 5],  # North, West, South, East (Western Europe)
            },
            output_file
        )
        
        print("Request submitted, waiting for data...")
        
        # Wait for the download to complete
        result.wait()
        
        end_time = time.time()
        print(f"Data retrieved in {end_time - start_time:.2f} seconds!")
        
        # Check if the file exists and has content
        if not os.path.exists(output_file):
            print(f"ERROR: Output file {output_file} was not created")
            return False
        
        file_size = os.path.getsize(output_file)
        print(f"Output file size: {file_size/1024:.2f} KB")
        
        if file_size == 0:
            print("ERROR: Output file is empty")
            return False
        
        # Try to open and process the data
        print("Opening the NetCDF file with xarray...")
        try:
            ds = xr.open_dataset(output_file)
            print("Successfully opened the dataset!")
            
            # Display basic dataset info
            print("\nDataset information:")
            print(f"Dimensions: {ds.dims}")
            print(f"Variables: {list(ds.variables)}")
            print(f"Attributes: {ds.attrs}")
            
            # Create a simple plot
            print("\nCreating a simple plot...")
            
            # Get temperature data, convert from Kelvin to Celsius
            if 't2m' in ds:
                temp_var = 't2m'
            elif '2m_temperature' in ds:
                temp_var = '2m_temperature'
            else:
                print(f"ERROR: Temperature variable not found in dataset. Variables: {list(ds.variables)}")
                return False
                
            temp_data = ds[temp_var][0] - 273.15  # First timestep, convert K to °C
            
            # Create plot
            plt.figure(figsize=(10, 6))
            temp_data.plot(cmap='RdBu_r', robust=True)
            plt.title('2m Temperature (°C) - ERA5 Data Test')
            plt.savefig('era5_test_plot.png')
            print("Plot saved to era5_test_plot.png")
            
            # Clean up
            ds.close()
            
            print("\nERA5 data access test completed successfully!")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to process the NetCDF file: {str(e)}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to fetch ERA5 data: {str(e)}")
        print("\nThis could be due to:")
        print("1. Invalid API credentials")
        print("2. Network connectivity issues")
        print("3. CDS API server issues")
        print("\nPlease check your CDS_URL and CDS_KEY values.")
        return False
    finally:
        # Clean up
        if os.path.exists(output_file):
            print(f"Cleaning up: Removing {output_file}")
            os.remove(output_file)

if __name__ == "__main__":
    success = test_era5_data_access()
    sys.exit(0 if success else 1)
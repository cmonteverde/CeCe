
import unittest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
import nasa_data

class TestNasaData(unittest.TestCase):
    def setUp(self):
        # Mock the API call
        self.original_fetch = nasa_data.fetch_nasa_power_data
        nasa_data.fetch_nasa_power_data = MagicMock(return_value=pd.DataFrame({'PRECTOTCORR': [10.0]}))

    def tearDown(self):
        nasa_data.fetch_nasa_power_data = self.original_fetch

    def test_fetch_precipitation_map_data_structure(self):
        # Test that the function returns a DataFrame with correct columns
        df = nasa_data.fetch_precipitation_map_data(
            lat=37.7749,
            lon=-122.4194,
            start_date="2023-01-01",
            end_date="2023-01-01",
            fast_mode=True
        )

        self.assertIsInstance(df, pd.DataFrame)
        self.assertListEqual(list(df.columns), ['latitude', 'longitude', 'precipitation'])
        self.assertEqual(len(df), 100)  # 10x10 grid

        # Check values are reasonable
        self.assertTrue((df['precipitation'] >= 0.01).all())
        # Check coordinates are within range
        self.assertTrue((df['latitude'] >= 37.7749 - 1.0).all())
        self.assertTrue((df['latitude'] <= 37.7749 + 1.0).all())

    def test_fetch_precipitation_map_data_slow_mode(self):
        # Trigger the interpolation path
        df = nasa_data.fetch_precipitation_map_data(
            lat=37.7749,
            lon=-122.4194,
            start_date="2023-01-01",
            end_date="2023-01-20", # > 14 days
            radius_degrees=1.0,    # > 0.5
            fast_mode=False
        )
        self.assertIsInstance(df, pd.DataFrame)
        self.assertListEqual(list(df.columns), ['latitude', 'longitude', 'precipitation'])
        self.assertEqual(len(df), 100) # 10x10 grid is hardcoded in function?
        # Check values
        self.assertTrue((df['precipitation'] >= 0.01).all())

if __name__ == '__main__':
    unittest.main()

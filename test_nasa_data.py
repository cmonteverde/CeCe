
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

    def test_heat_index_calculation(self):
        # Create a deterministic dataset
        n_points = 100
        t_values = np.linspace(20, 40, n_points)
        rh_values = np.linspace(20, 90, n_points)

        # Create sample DataFrame
        mock_df = pd.DataFrame({
            'Date': pd.date_range(start='2023-01-01', periods=n_points),
            'T2M_MAX': t_values,
            'RH2M': rh_values
        })

        # Update mock return value for this test
        nasa_data.fetch_nasa_power_data.return_value = mock_df.copy()

        # Clear cache
        nasa_data._get_extreme_heat_days_cached.cache_clear()

        # Call the function
        df, _, _ = nasa_data.get_extreme_heat_days(0, 0, 2023)

        # Original logic for verification
        def calculate_heat_index_original(t, rh):
            if t < 26:
                return t
            hi = -8.78469475556 + \
                    1.61139411 * t + \
                    2.33854883889 * rh + \
                    -0.14611605 * t * rh + \
                    -0.012308094 * t**2 + \
                    -0.0164248277778 * rh**2 + \
                    0.002211732 * t**2 * rh + \
                    0.00072546 * t * rh**2 + \
                    -0.000003582 * t**2 * rh**2
            return hi

        # Calculate expected values
        expected_values = [calculate_heat_index_original(t, rh) for t, rh in zip(t_values, rh_values)]

        # Compare
        pd.testing.assert_series_equal(
            df['Heat Index (°C)'],
            pd.Series(expected_values, name='Heat Index (°C)'),
            check_names=False,
            atol=1e-5
        )

if __name__ == '__main__':
    unittest.main()

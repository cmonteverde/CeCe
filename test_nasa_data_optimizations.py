
import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import datetime
import nasa_data

class TestNasaDataOptimizations(unittest.TestCase):

    @patch('nasa_data.requests.get')
    def test_fetch_nasa_power_data_parsing(self, mock_get):
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'properties': {
                'parameter': {
                    'T2M': {
                        '20230101': 20.0,
                        '20230102': 21.0
                    },
                    'T2M_MAX': {
                        '20230101': 25.0,
                        '20230102': 26.0
                    }
                }
            }
        }
        mock_get.return_value = mock_response

        # Call the function (using the public wrapper which calls cached function)
        # We need to bypass cache or use different args to ensure it runs
        df = nasa_data.fetch_nasa_power_data(
            lat=10.0, lon=10.0,
            start_date='2023-01-01', end_date='2023-01-02',
            parameters=['T2M', 'T2M_MAX']
        )

        # Verify DataFrame structure and content
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['Date']))
        self.assertEqual(df['T2M'].iloc[0], 20.0)
        self.assertEqual(df['T2M_MAX'].iloc[1], 26.0)
        self.assertEqual(df['Date'].iloc[0].strftime('%Y-%m-%d'), '2023-01-01')

    @patch('nasa_data.fetch_nasa_power_data')
    def test_get_extreme_heat_days_calculation(self, mock_fetch):
        # Create a mock DataFrame with known values
        mock_df = pd.DataFrame({
            'Date': [datetime(2023, 1, 1), datetime(2023, 1, 2)],
            'T2M_MAX': [25.0, 35.0],
            'RH2M': [50.0, 60.0]
        })
        mock_fetch.return_value = mock_df

        # Call function
        # Using a percentile that ensures 35C is extreme and 25C is not
        df, t_thresh, h_thresh = nasa_data.get_extreme_heat_days(
            lat=10.0, lon=10.0, year=2023, percentile=50
        )

        # Verify columns exist
        self.assertIn('Heat Index (°C)', df.columns)

        # Verify Heat Index values
        # For T=25 (<26), HI should be T
        self.assertAlmostEqual(df['Heat Index (°C)'].iloc[0], 25.0)

        # For T=35 (>26), HI should be calculated
        # Manual calc: -8.78 + 1.61*35 + 2.33*60 + ...
        # Just check it's not 35
        self.assertNotEqual(df['Heat Index (°C)'].iloc[1], 35.0)
        self.assertTrue(df['Heat Index (°C)'].iloc[1] > 35.0) # HI usually higher than T with humidity

if __name__ == '__main__':
    unittest.main()

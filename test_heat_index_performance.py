
import unittest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
import nasa_data
import era5_data

class TestHeatIndexLogic(unittest.TestCase):

    def test_nasa_heat_index_logic(self):
        # Create a mock DataFrame with known values
        # Case 1: Low temp (Heat Index = Temp)
        # Case 2: High temp, Low RH
        # Case 3: High temp, High RH

        # NASA data uses T2M_MAX (C) and RH2M (%)
        mock_df = pd.DataFrame({
            'Date': pd.date_range(start='2023-01-01', periods=3),
            'T2M_MAX': [20.0, 30.0, 35.0],
            'RH2M': [50.0, 40.0, 80.0],
            'T2M': [20.0, 30.0, 35.0], # Needed for other parts but not heat index
            'T2M_MIN': [15.0, 25.0, 30.0] # Needed for other parts but not heat index
        })

        # Mock fetch_nasa_power_data to return our mock_df
        with patch('nasa_data.fetch_nasa_power_data', return_value=mock_df):
            # We call the internal cached function directly or the wrapper.
            # The wrapper calls the cached function.
            # However, since the function is cached, we might hit the cache if not careful.
            # But in a fresh test run, cache is empty.

            # The function calculates heat index internally
            result_df, _, _ = nasa_data.get_extreme_heat_days(0, 0, 2023)

            # Verify calculations

            # Row 0: T=20 (<26), so HI should be 20
            self.assertAlmostEqual(result_df.loc[0, 'Heat Index (°C)'], 20.0)

            # Row 1: T=30, RH=40.
            # Formula check:
            # HI = -8.78469475556 + 1.61139411*30 + 2.33854883889*40 + ...
            # Let's verify against the known formula value.
            # I will use the old scalar implementation to verify the new vectorized one
            # matches the expected logic.

            t = 30.0
            rh = 40.0
            hi_expected_1 = -8.78469475556 + \
                 1.61139411 * t + \
                 2.33854883889 * rh + \
                 -0.14611605 * t * rh + \
                 -0.012308094 * t**2 + \
                 -0.0164248277778 * rh**2 + \
                 0.002211732 * t**2 * rh + \
                 0.00072546 * t * rh**2 + \
                 -0.000003582 * t**2 * rh**2

            self.assertAlmostEqual(result_df.loc[1, 'Heat Index (°C)'], hi_expected_1)

            # Row 2: T=35, RH=80
            t = 35.0
            rh = 80.0
            hi_expected_2 = -8.78469475556 + \
                 1.61139411 * t + \
                 2.33854883889 * rh + \
                 -0.14611605 * t * rh + \
                 -0.012308094 * t**2 + \
                 -0.0164248277778 * rh**2 + \
                 0.002211732 * t**2 * rh + \
                 0.00072546 * t * rh**2 + \
                 -0.000003582 * t**2 * rh**2

            self.assertAlmostEqual(result_df.loc[2, 'Heat Index (°C)'], hi_expected_2)

    def test_era5_heat_index_logic(self):
        # Mock ERA5 data
        # It expects '2m_temperature' (K) and '2m_dewpoint_temperature' (K)
        # or 'Temperature (°C)' and 'Dewpoint (°C)' if processed?
        # fetch_era5_data returns processed data.

        # Let's see what get_era5_extreme_heat does.
        # It calls fetch_era5_data, which returns a DF with 'Temperature (°C)' and 'Dewpoint (°C)' (if computed)
        # But wait, fetch_era5_data processes raw data.
        # So if we mock fetch_era5_data, we should return the processed format that get_era5_extreme_heat expects.

        # get_era5_extreme_heat calls:
        # df = fetch_era5_data(..., variables=['2m_temperature', '2m_dewpoint_temperature'])

        # And expects:
        # 'Temperature (°C)'
        # '2m_dewpoint_temperature' (raw?) or 'd2m'?

        # Let's check era5_data.py again.
        # inside get_era5_extreme_heat:
        # if '2m_dewpoint_temperature' in df.columns:
        #     df['Dewpoint (°C)'] = df['2m_dewpoint_temperature'] - 273.15

        # So fetch_era5_data returns whatever process_era5_data returns.
        # process_era5_data converts '2m_temperature' to 'Temperature (°C)'.
        # It does NOT seem to touch '2m_dewpoint_temperature' explicitly in the renames dict?
        # Renames: {'t2m': 'Temperature (K)', '2m_temperature': 'Temperature (K)', ...}
        # And then converts 'Temperature (K)' to 'Temperature (°C)'.

        # So '2m_dewpoint_temperature' likely remains as is in the dataframe returned by fetch_era5_data.

        # Let's verify correct mocking.

        # Create mock data with Temperature in C (already processed) and Dewpoint in K (raw)
        # T = 30°C
        # RH needs to be calculated to verify heat index.
        # RH = 100 * (EXP((17.625 * TD)/(243.04 + TD)) / EXP((17.625 * T)/(243.04 + T)))

        # Let's just mock 'Temperature (°C)' and '2m_dewpoint_temperature' (K)
        # Case 1: Low temp (20°C) -> 293.15 K
        # Case 2: High temp (35°C) -> 308.15 K

        # To get a specific RH, we need to set Dewpoint appropriately.
        # Approx T=35, RH=50% -> TD approx 23°C -> 296.15 K

        mock_df = pd.DataFrame({
            'time': pd.to_datetime(['2023-01-01 12:00:00', '2023-01-02 12:00:00']),
            'Temperature (°C)': [20.0, 35.0],
            '2m_dewpoint_temperature': [293.15 - 10, 296.15] # 283.15K (10°C), 296.15K (23°C)
        })

        with patch('era5_data.fetch_era5_data', return_value=mock_df):
            result_df, _, _ = era5_data.get_era5_extreme_heat(0, 0, 2023)

            # Verify results
            # Row 0: T=20C. F = 68F < 80F. Heat Index should be T.
            # Note: get_era5_extreme_heat groups by Date and takes MAX.
            # We have 2 dates, so 2 rows.

            row0 = result_df[result_df['Date'] == pd.to_datetime('2023-01-01').date()].iloc[0]
            self.assertAlmostEqual(row0['Heat Index (°C)'], 20.0)

            row1 = result_df[result_df['Date'] == pd.to_datetime('2023-01-02').date()].iloc[0]

            # Verify calculation for row 1
            # Re-calculate inputs locally
            t = 35.0
            td = 296.15 - 273.15 # 23.0

            # RH calculation used in code
            rh = 100 * (
                np.exp((17.625 * td) / (243.04 + td)) /
                np.exp((17.625 * t) / (243.04 + t))
            )

            # Heat Index calculation
            t_f = t * 9/5 + 32 # 95F

            # Full formula
            hi = -42.379 + 2.04901523 * t_f + 10.14333127 * rh
            hi = hi - 0.22475541 * t_f * rh - 0.00683783 * t_f**2
            hi = hi - 0.05481717 * rh**2 + 0.00122874 * t_f**2 * rh
            hi = hi + 0.00085282 * t_f * rh**2 - 0.00000199 * t_f**2 * rh**2

            hi_c = (hi - 32) * 5/9

            self.assertAlmostEqual(row1['Heat Index (°C)'], hi_c)

if __name__ == '__main__':
    unittest.main()

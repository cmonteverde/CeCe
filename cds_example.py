#!/usr/bin/env python
import cdsapi

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-pressure-levels',
    {
        'product_type': 'reanalysis',
        'format': 'netcdf',
        'variable': 'temperature',
        'pressure_level': '1000',
        'year': '2017',
        'month': '01',
        'day': '01',
        'time': '12:00',
    },
    'download.nc'
)
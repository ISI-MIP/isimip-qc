import math

import numpy as np

from ..config import settings


def check_dimension_variables(file):
    '''
    The first variables should be dimensions.
    '''
    for dimension_name, variable_name in zip(file.dataset.dimensions, file.dataset.variables):
        if dimension_name != variable_name:
            file.warn('%s should be %s.', variable_name, dimension_name)


def check_lon(file):
    '''
    The global grid ranges 89.75 to -89.75° latitude, and ‐179.75 to 179.75° longitude, i.e. 0.5° grid spacing,
    360 rows and 720 columns, or 259200 grid cells total.
    '''
    lon = file.dataset.variables.get('lon')
    if lon is None:
        file.error('lon is missing.')
    else:
        if lon.shape != (720, ):
            file.error('lat.shape=%s must be (720, ).', lon.shape)

        if np.min(lon) != -179.75:
            file.error('min(lon)=%s must be -179.75.', np.min(lon))

        if np.max(lon) != 179.75:
            file.error('max(lon)=%s must be 179.75.', np.max(lon))

        try:
            if lon.axis != 'X':
                file.warn('lon.axis="%s" should be "X".', lon.axis)
        except AttributeError:
            file.warn('lon.axis is missing.')

        try:
            if lon.standard_name != 'longitude':
                file.warn('lon.standard_name="%s" should be "longitude".', lon.standard_name)
        except AttributeError:
            file.warn('lon.standard_name is missing.')

        try:
            if lon.long_name not in ['longitude', 'Longitude']:
                file.warn('lon.long_name="%s" should be "longitude" or "Longitude".', lon.long_name)
        except AttributeError:
            file.warn('lon.long_name is missing.')

        try:
            if lon.units != 'degrees_east':
                file.warn('lon.units="%s" should be "degrees_east".', lon.units)
        except AttributeError:
            file.warn('lon.units is missing.')

        if lon.dtype != 'float64':
            file.warn('lon.dtype="%s" should be "float64".', lon.dtype)


def check_lat(file):
    '''
    The global grid ranges 89.75 to -89.75° latitude, and ‐179.75 to 179.75° longitude, i.e. 0.5° grid spacing,
    360 rows and 720 columns, or 259200 grid cells total.
    '''
    lat = file.dataset.variables.get('lat')
    if lat is None:
        file.error('Lat is missing.')
    else:
        if lat.shape != (360, ):
            file.error('lat.shape=%s must be (360, ).', lat.shape)

        if np.min(lat) != -89.75:
            file.error('min(lat)=%s must be -89.75.', np.min(lat))

        if np.max(lat) != 89.75:
            file.error('max(lat)=%s must be 89.75.', np.max(lat))

        try:
            if lat.axis != 'Y':
                file.warn('lon.axis="%s" should be "X".', lat.axis)
        except AttributeError:
            file.warn('lat.axis is missing.')

        try:
            if lat.standard_name != 'latitude':
                file.warn('lat.standard_name="%s" should be "latitude".', lat.standard_name)
        except AttributeError:
            file.warn('lat.standard_name is missing.')

        try:
            if lat.long_name not in ['latitude', 'Latitude']:
                file.warn('lat.long_name="%s" should be "latitude" or "Latitude".', lat.long_name)
        except AttributeError:
            file.warn('lat.long_name is missing.')

        try:
            if lat.units != 'degrees_north':
                file.warn('lat.units="%s" should be "degrees_north".', lat.units)
        except AttributeError:
            file.warn('lat.units is missing.')

        if lat.dtype != 'float64':
            file.warn('lat.dtype="%s" should be "float64".', lat.dtype)


def check_time(file):
    time = file.dataset.variables.get('time')

    if time is None:
        file.error('time is missing.')
    else:
        try:
            if time.axis != 'T':
                file.warn('lon.axis="%s" should be "T".', time.axis)
        except AttributeError:
            file.warn('time.axis is missing.')
            file.has_warnings = True

        try:
            if time.standard_name != 'time':
                file.warn('time.standard_name="%s" should be "time".', time.standard_name)
        except AttributeError:
            file.warn('time.standard_name is missing.')

        time_longname_valid = ['time', 'time axis', 'Time', 'Time axis']
        try:
            if time.long_name not in time_longname_valid:
                file.warn('time.long_name="%s" should one of %s', time.long_name, time_longname_valid)
        except AttributeError:
            file.warn('time.long_name is missing.')

        timestep = file.specifiers.get('timestep')
        unit_start = {
            'daily': 'days',
            'monthly': 'months',
            'annual': 'years',
            'decadal': 'decades',
            'seasonal': 'seasons'
        }.get(timestep)
        unit_enum = settings.SCHEMA['properties']['variables']['properties']['time']['properties']['units']['enum']
        try:
            if time.units not in unit_enum:
                file.warn('time.units="%s" should be one of %s.', time.units, unit_enum)

            if not time.units.startswith(unit_start):
                file.warn('time.units="%s" should be start with %s.', time.units, unit_start)

        except AttributeError:
            file.warn('time.units is missing.')

        calendars_valid = ['proleptic_gregorian', '365_day']
        try:
            if time.calendar not in calendars_valid:
                file.warn('time.calendar="%s" should be one of %s', time.calendar, calendars_valid)
        except AttributeError:
            file.warn('time.calendar is missing.')

        if time.dtype != 'float64':
            file.warn('time.dtype="%s" should be "float64".', time.dtype)


def check_variable(file):
    variable_name = list(file.dataset.variables)[-1]
    variable = file.dataset.variables.get(variable_name)

    if variable.dtype != 'float32':
        file.warn('%s.dtype="%s" should be "float32".', variable_name, variable.dtype)

    if variable.chunking() != [1, 360, 720]:
        file.warn('%s.chunking=%s should be [1, 360, 720].', variable_name, variable.chunking())

    dimensions = ('time', 'lat', 'lon')
    if variable.dimensions != dimensions:
        file.error('%s dimensions %s must be %s.', variable_name, variable.dimensions, dimensions)

    try:
        if not math.isclose(variable._FillValue, 1e+20, rel_tol=1e-6):
            file.warn('variable._FillValue="%s" should be 1e+20.', variable._FillValue)
    except AttributeError:
        file.warn('variable._FillValue is missing.')

    try:
        if not math.isclose(variable.missing_value, 1e+20, rel_tol=1e-6):
            file.warn('variable.missing_value="%s" should be 1e+20.', variable.missing_value)
    except AttributeError:
        file.warn('variable.missing_value is missing.')

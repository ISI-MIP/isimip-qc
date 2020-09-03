import math

import numpy as np

from ..config import settings


def check_lon_variable(file):
    lon = file.dataset.variables.get('lon')
    lon_definition = settings.DEFINITIONS['dimensions'].get('lon')

    if lon is None:
        file.error('Variable lon is missing.')
    elif not lon_definition:
        file.error('Definition for variable lon is missing.')
    else:
        # check dtype
        dtypes = ['float32', 'float64']
        if lon.dtype not in dtypes:
            file.warn('lon.dtype="%s" should be in %s.', lon.dtype, dtypes)

        # check shape
        size = lon_definition.get('size')
        if lon.shape != (size, ):
            file.error('lat.shape=%s must be (%s, ).', lon.shape, size)

        # check minimum
        minimum = lon_definition.get('minimum')
        if np.min(lon) != minimum:
            file.error('min(lon)=%s must be %s.', np.min(lon), minimum)

        # check maximum
        maximum = lon_definition.get('maximum')
        if np.max(lon) != maximum:
            file.error('max(lon)=%s must be %s.', np.max(lon), maximum)

        # check axis
        axis = lon_definition.get('axis')
        try:
            if lon.axis != axis:
                file.warn('Attribute lon.axis="%s" should be "%s".', lon.axis, axis)
        except AttributeError:
            file.warn('Attribute lon.axis is missing. Should be "%s".', axis)

        # check standard_name
        standard_name = lon_definition.get('standard_name')
        try:
            if lon.standard_name != standard_name:
                file.warn('Attribute lon.standard_name="%s" should be "%s".', lon.standard_name, standard_name)
        except AttributeError:
            file.warn('Attribute lon.standard_name is missing. Should be "%s".', standard_name)

        # check long_name
        long_names = lon_definition.get('long_names', [])
        try:
            if lon.long_name not in long_names:
                file.warn('Attribute lon.long_name="%s" should be in %s.', lon.long_name, long_names)
        except AttributeError:
            file.warn('Attribute lon.long_name is missing. Should be "%s".', long_names[0])

        # check units
        units = lon_definition.get('units')
        try:
            if lon.units != units:
                file.warn('Attribute lon.units="%s" should be "%s".', lon.units, units)
        except AttributeError:
            file.warn('Attribute lon.units is missing. Should be "%s".', units)


def check_lat_variable(file):
    lat = file.dataset.variables.get('lat')
    lat_definition = settings.DEFINITIONS['dimensions'].get('lat')

    if lat is None:
        file.error('Variable lat is missing.')
    elif not lat_definition:
        file.error('Definition for variable lat is missing.')
    else:
        # check dtype
        dtypes = ['float32', 'float64']
        if lat.dtype not in dtypes:
            file.warn('lat.dtype="%s" should be in %s.', lat.dtype, dtypes)

        # check shape
        size = lat_definition.get('size')
        if lat.shape != (size, ):
            file.error('lat.shape=%s must be (%s, ).', lat.shape, size)

        # check minimum
        minimum = lat_definition.get('minimum')
        if np.min(lat) != minimum:
            file.error('min(lat)=%s must be %s.', np.min(lat), minimum)

        # check maximum
        maximum = lat_definition.get('maximum')
        if np.max(lat) != maximum:
            file.error('max(lat)=%s must be %s.', np.max(lat), maximum)

        # check axis
        axis = lat_definition.get('axis')
        try:
            if lat.axis != axis:
                file.warn('Attribute lat.axis="%s" should be "%s".', lat.axis, axis)
        except AttributeError:
            file.warn('Attribute lat.axis is missing. Should be "%s".', axis)

        # check standard_name
        standard_name = lat_definition.get('standard_name')
        try:
            if lat.standard_name != standard_name:
                file.warn('Attribute lat.standard_name="%s" should be "%s".', lat.standard_name, standard_name)
        except AttributeError:
            file.warn('Attribute lat.standard_name is missing. Should be "%s".', standard_name)

        # check long_name
        long_names = lat_definition.get('long_names', [])
        try:
            if lat.long_name not in long_names:
                file.warn('Attribute lat.long_name="%s" should be in %s.', lat.long_name, long_names)
        except AttributeError:
            file.warn('Attribute lat.long_name is missing. Should be "%s".', long_names[0])

        # check units
        units = lat_definition.get('units')
        try:
            if lat.units != units:
                file.warn('Attribute lat.units="%s" should be "%s".', lat.units, units)
        except AttributeError:
            file.warn('Attribute lat.units is missing. Should be "%s".', units)

        lat_first = file.dataset.variables.get('lat')[0]
        lat_last  = file.dataset.variables.get('lat')[-1]
        if lat_first < lat_last:
            file.warn('latitudes in wrong order. Index should range from north to south. (found %s to %s)', lat_first, lat_last)
        else:
            file.info('Latidute index order looks good (N to S).')

def check_time_variable(file):
    import netCDF4
    import calendar

    time = file.dataset.variables.get('time')
    time_definition = settings.DEFINITIONS['dimensions'].get('time')

    if time is None:
        file.error('Variable time is missing.')
    elif not time_definition:
        file.error('Definition for variable time is missing.')
    else:
        # check dtype
        dtypes = ['float32', 'float64']
        if time.dtype not in dtypes:
            file.warn('time.dtype="%s" should be in %s.', time.dtype, dtypes)

        # check axis
        axis = time_definition.get('axis')
        try:
            if time.axis != axis:
                file.warn('Attribute time.axis="%s" should be "%s".', time.axis, axis)
        except AttributeError:
            file.warn('Attribute time.axis is missing. Should be "%s".', axis)

        # check standard_name
        standard_name = time_definition.get('standard_name')
        try:
            if time.standard_name != standard_name:
                file.warn('Attribute time.standard_name="%s" should be "%s".', time.standard_name, standard_name)
        except AttributeError:
            file.warn('Attribute time.standard_name is missing. Should be "%s".', standard_name)

        # check long_name
        long_names = time_definition.get('long_names', [])
        try:
            if time.long_name not in long_names:
                file.warn('Attribute time.long_name="%s" should be in %s.', time.long_name, long_names)
        except AttributeError:
            file.warn('Attribute time.long_name is missing. Should be "%s".', long_names[2])

        # check units
        minimum = settings.DEFINITIONS['time_span']['minimum']['value'][settings.SIMULATION_ROUND]
        units_templates = [
            "%s since %i-01-01",
            "%s since %i-01-01 00:00:00",
            "%s since %i-1-1",
            "%s since %i-1-1 00:00:00"
        ]
        units = []
        for specifier, definition in settings.DEFINITIONS['time_step'].items():
            units += [template % (definition['increment'], minimum) for template in units_templates]

        try:
            if time.units not in units:
                file.warn('Attribute time.units="%s" should be one of %s.', time.units, units)
            else:
                file.info('Valid time unit found (%s)', time.units)
        except AttributeError:
            file.warn('Attribute time.units is missing. Should be "%s".', units)

        # check calenders
        calenders = time_definition.get('calenders', [])
        try:
            if time.calendar not in calenders:
                file.warn('Attribute time.calendar="%s" should be one of %s', time.calendar, calenders)
            else:
                file.info('Valid calendar found (%s)', time.calendar)
        except AttributeError:
            file.warn('Attribute time.calendar is missing. Should be in "%s".', calenders)


        # first and last year from file name specifiers must match those from internal time axis
        # number of time steps must match those expected from the time axis

        time = file.dataset.variables.get('time')
        time_steps = len(time[:])
        time_units = time.units
        time_resolution = file.specifiers.get('time_step')

        if time_resolution == 'daily':
            try:
                time_calendar = time.calendar
            except AttributeError:
                file.warn('Can\'t check for number of time steps because of missing time.calendar attribute')
                return
        elif time_resolution == 'monthly':
            # for monthly resolution cftime.num2date only allows for '360_day' calendar
            time_calendar = '360_day'

        if time_resolution in ['daily','monthly']:
            firstdate_nc = netCDF4.num2date(time[0],time_units,time_calendar)
            lastdate_nc  = netCDF4.num2date(time[time_steps-1],time_units,time_calendar)
            startyear_nc = firstdate_nc.year
            endyear_nc   = lastdate_nc.year
        elif time_resolution == 'annual':
            ref_year     = int(time.units.split()[2].split("-")[0])
            startyear_nc = ref_year + int(time[0])
            endyear_nc   = ref_year + int(time[-1])

        startyear_file = int(file.specifiers.get('start_year'))
        endyear_file   = int(file.specifiers.get('end_year'))
        nyears_file    = endyear_file - startyear_file + 1

        if startyear_nc != startyear_file or endyear_nc != endyear_file:
            file.error('Start and/or end year of NetCDF time axis (%s-%s) doesn\'t match period defined in file name (%s-%s)', startyear_nc, endyear_nc, startyear_file, endyear_file)
        else:
            file.info('Time period covered by this file matches the internal time axis (%s-%s)', startyear_nc, endyear_nc)

        if time_resolution == 'daily':
            if time_calendar in ['proleptic_gregorian','standard']:
                time_days = 0
                for year in range(startyear_file,endyear_file+1):
                    if calendar.isleap(year):
                        time_days += 366
                    else:
                        time_days += 365
            elif time_calendar == '366_day':
                time_days = nyears_file * 366
            elif time_calendar == '365_day':
                time_days = nyears_file * 365
            elif time_calendar == '360_day':
                time_days = nyears_file * 360

            if time_days != time_steps:
                file.error('Number of internal time steps (%s) does not match the expected number from the file name specifiers (%s). (\'%s\' calendar found)', time_steps, time_days, time_calendar)
            else:
                file.info('Correct number of time steps (%s) given the defined calendar (%s)', time_steps, time_calendar)
        elif time_resolution == 'monthly':
            time_months = nyears_file * 12
            if time_months != time_steps:
                file.error('Number of internal time steps (%s) does not match the expected number from the file name specifiers (%s).', time_steps, time_months)
            else:
                file.info('Correct number of time steps (%s).', time_steps)
        elif time_resolution == 'annual':
            if nyears_file != time_steps:
                file.error('Number of internal time steps (%s) does not match the expected number from the file name specifiers (%s).', time_steps, nyears_file)
            else:
                file.info('Correct number of time steps (%s).', time_steps)


def check_variable(file):
    variable_name = file.specifiers.get('variable')
    variable = file.dataset.variables.get(variable_name)
    definition = settings.DEFINITIONS.get('variable', {}).get(variable_name)

    if not variable:
        file.error('Variable %s is missing.', variable_name)
    elif not definition:
        file.error('Definition for variable %s is missing.', variable_name)
    else:
        # check dtype
        if variable.dtype != 'float32':
            file.warn('%s.dtype="%s" should be "float32".', variable_name, variable.dtype)

        # check chunking
        chunking = variable.chunking()
        if chunking[0] != 1 or chunking[-2] != 360 or chunking[-1] != 720:
            file.warn('%s.chunking=%s should be [1, ... , 360, 720].', variable_name, chunking)
        else:
            file.info('Variable chunking looks good (%s)', chunking)

        # check dimensions
        definition_dimensions = tuple(definition.get('dimensions', []))
        default_dimensions = ('time', 'lat', 'lon')
        if definition_dimensions:
            if variable.dimensions not in [definition_dimensions, default_dimensions]:
                file.error('%s dimension %s must be %s or %s.', variable_name, variable.dimensions, definition_dimensions, default_dimensions)
        else:
            if variable.dimensions != default_dimensions:
                file.error('%s dimension %s must be %s.', variable_name, variable.dimensions, default_dimensions)

        # check variable units
        units = definition.get('units')
        if units is not None:
            try:
                if variable.units != units:
                    file.error('%s.units=%s should be %s.', variable_name, variable.units, units)
                else:
                    file.info('Variable unit matches protocol definition (%s)', variable.units)
            except AttributeError:
                file.error('%s.units is missing. Should be "%s".', variable_name, units)
        else:
            file.warn('No units information on %s in definition.', variable_name)

        # check dimension order
        dim_len = len(variable.dimensions)
        if dim_len == 3:
            if variable.dimensions[0] != 'time' or variable.dimensions[1] != 'lat' or variable.dimensions[2] != 'lon':
                file.warn('%s dimension order %s should be ["time", "lat", "lon"].', variable_name, variable.dimensions)
            else:
                file.info('Dimensions for variable "%s" look good: %s', variable_name, variable.dimensions)
        elif dim_len == 4:
            if variable.dimensions[0] != 'time' or variable.dimensions[1] not in ['depth'] or variable.dimensions[2] != 'lat' or variable.dimensions[2] != 'lon':
                file.warn('%s dimension order %s should be ["time", "depth" , "lat", "lon"].', variable_name, variable.dimensions)
            else:
                file.info('Dimensions for variable "%s" look good', variable_name)
        else:
            file.error('Variable "%s" neither holds 2d or 3d data. (dim=%s)', dim_len)

        # check _FillValue and missing_value
        for name in ['_FillValue', 'missing_value']:
            try:
                attr = variable.getncattr(name)
                if not math.isclose(attr, 1e+20, rel_tol=1e-6):
                    file.warn('variable.%s="%s" should be 1e+20.', name, attr)
                else:
                    file.info('%s is properly set.', name)
            except AttributeError:
                file.warn('variable.%s is missing. Should be 1e+20.', name)

        # check valid range
        if settings.MINMAX:
            valid_min = definition.get('valid_min')
            valid_max = definition.get('valid_max')
            if (valid_min is not None) and (valid_min is not None):
                var_min = variable[:].min()
                var_max = variable[:].max()
                if (var_min < float(valid_min)) or (var_max > float(valid_max)):
                    file.error('Min/Max values (%.2E/%.2E) of %s are outside the valid range (%.2E to %.2E).', var_min, var_max, variable_name, valid_min, valid_max)
                else:
                    file.info('Min/Max values within valid range (%.2E to %.2E).', valid_min, valid_max)
            else:
                file.info('No min and/or max definition found for variable "%s".', variable_name)

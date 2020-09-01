import math

import numpy as np

from ..config import settings


def check_lon_variable(file):
    lon = file.dataset.variables.get('lon')
    lon_definition = settings.DEFINITIONS['dimensions'].get('lon')

    if lon is None:
        file.error('variable lon is missing.')
    elif not lon_definition:
        file.error('definition for variable lon is missing.')
    else:
        # check dtype
        if lon.dtype != 'float64':
            file.warn('lon.dtype="%s" should be "float64".', lon.dtype)

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
        try:
            axis = lon_definition.get('axis')
            if lon.axis != axis:
                file.warn('lon.axis="%s" should be "%s".', lon.axis, axis)
        except AttributeError:
            file.warn('lon.axis is missing.')

        # check standard_name
        try:
            standard_name = lon_definition.get('standard_name')
            if lon.standard_name != standard_name:
                file.warn('lon.standard_name="%s" should be "%s".', lon.standard_name, standard_name)
        except AttributeError:
            file.warn('lon.standard_name is missing.')

        # check long_name
        try:
            long_names = lon_definition.get('long_names', [])
            if lon.long_name not in long_names:
                file.warn('lon.long_name="%s" should be in %s.', lon.long_name, long_names)
        except AttributeError:
            file.warn('lon.long_name is missing.')

        # check units
        try:
            units = lon_definition.get('units')
            if lon.units != units:
                file.warn('lon.units="%s" should be "%s".', lon.units, units)
        except AttributeError:
            file.warn('lon.units is missing.')


def check_lat_variable(file):
    lat = file.dataset.variables.get('lat')
    lat_definition = settings.DEFINITIONS['dimensions'].get('lat')

    if lat is None:
        file.error('variable lat is missing.')
    elif not lat_definition:
        file.error('definition for variable lat is missing.')
    else:
        # check dtype
        if lat.dtype != 'float64':
            file.warn('lat.dtype="%s" should be "float64".', lat.dtype)

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
        try:
            axis = lat_definition.get('axis')
            if lat.axis != axis:
                file.warn('lat.axis="%s" should be "%s".', lat.axis, axis)
        except AttributeError:
            file.warn('lat.axis is missing.')

        # check standard_name
        try:
            standard_name = lat_definition.get('standard_name')
            if lat.standard_name != standard_name:
                file.warn('lat.standard_name="%s" should be "%s".', lat.standard_name, standard_name)
        except AttributeError:
            file.warn('lat.standard_name is missing.')

        # check long_name
        try:
            long_names = lat_definition.get('long_names', [])
            if lat.long_name not in long_names:
                file.warn('lat.long_name="%s" should be in %s.', lat.long_name, long_names)
        except AttributeError:
            file.warn('lat.long_name is missing.')

        # check units
        try:
            units = lat_definition.get('units')
            if lat.units != units:
                file.warn('lat.units="%s" should be "%s".', lat.units, units)
        except AttributeError:
            file.warn('lat.units is missing.')

        lat_first = file.dataset.variables.get('lat')[0]
        lat_last  = file.dataset.variables.get('lat')[-1]
        if lat_first < lat_last:
            # fix with 'cdo invertlat IFILE OFILE'
            file.warn('latitudes in wrong order. Index should range from north to south. (found %s to %s)', lat_first, lat_last)

def check_time_variable(file):
    import netCDF4
    import calendar

    time = file.dataset.variables.get('time')
    time_definition = settings.DEFINITIONS['dimensions'].get('time')

    if time is None:
        file.error('variable time is missing.')
    elif not time_definition:
        file.error('definition for variable time is missing.')
    else:
        # check dtype
        if time.dtype != 'float64':
            file.warn('time.dtype="%s" should be "float64".', time.dtype)

        # check axis
        try:
            axis = time_definition.get('axis')
            if time.axis != axis:
                file.warn('time.axis="%s" should be "%s".', time.axis, axis)
        except AttributeError:
            file.warn('time.axis is missing.')

        # check standard_name
        try:
            standard_name = time_definition.get('standard_name')
            if time.standard_name != standard_name:
                file.warn('time.standard_name="%s" should be "%s".', time.standard_name, standard_name)
        except AttributeError:
            file.warn('time.standard_name is missing.')

        # check long_name
        try:
            long_names = time_definition.get('long_names', [])
            if time.long_name not in long_names:
                file.warn('time.long_name="%s" should be in %s.', time.long_name, long_names)
        except AttributeError:
            file.warn('time.long_name is missing.')

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
                file.warn('time.units="%s" should be one of %s.', time.units, units)
        except AttributeError:
            file.warn('time.units is missing.')

        # check calenders
        try:
            calenders = time_definition.get('calenders', [])
            if time.calendar not in calenders:
                file.warn('time.calendar="%s" should be one of %s', time.calendar, calenders)
        except AttributeError:
            file.warn('time.calendar is missing.')


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

        if startyear_nc != startyear_file:
            file.error('Start year of time axis (%s) doesn\'t match start year in file name (%s)', startyear_nc, startyear_file)

        if endyear_nc != endyear_file:
            file.error('End year of time axis (%s) does not match end year in file name (%s)', endyear_nc, endyear_file)

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
                file.error('number of internal time steps (%s) does not match the expected number from the file name specifiers (%s). (\'%s\' calendar found)', time_steps, time_days, time_calendar)
        elif time_resolution == 'monthly':
            time_months = nyears_file * 12
            if time_months != time_steps:
                file.error('number of internal time steps (%s) does not match the expected number from the file name specifiers (%s).', time_steps, time_months)
        elif time_resolution == 'annual':
            if nyears_file != time_steps:
                file.error('number of internal time steps (%s) does not match the expected number from the file name specifiers (%s).', time_steps, nyears_file)


def check_variable(file):
    variable_name = file.specifiers.get('variable')
    variable = file.dataset.variables.get(variable_name)
    definition = settings.DEFINITIONS.get('variable', {}).get(variable_name)

    if not variable:
        file.error('variable %s is missing.', variable_name)
    elif not definition:
        file.error('definition for variable %s is missing.', variable_name)
    else:
        # check dtype
        if variable.dtype != 'float32':
            file.warn('%s.dtype="%s" should be "float32".', variable_name, variable.dtype)

        # check chunking
        chunking = variable.chunking()
        if chunking[0] != 1 or chunking[-2] != 360 or chunking[-1] != 720:
            file.warn('%s.chunking=%s should be [1, ... , 360, 720].', variable_name, chunking)

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
            except AttributeError:
                file.error('%s.units is missing.', variable_name)
        else:
            file.warn('No units information on %s in definition.', variable_name)

        # check dimension order
        if variable.dimensions[0] != 'time' or variable.dimensions[-2] != 'lat' or variable.dimensions[-1] != 'lon':
            file.warn('%s dimension order %s should be ["time", ... , "lat", "lon"].', variable_name, variable.dimensions)

        # check _FillValue and missing_value
        for name in ['_FillValue', 'missing_value']:
            try:
                attr = variable.getncattr(name)
                if not math.isclose(attr, 1e+20, rel_tol=1e-6):
                    file.warn('variable.%s="%s" should be 1e+20.', name, attr)
            except AttributeError:
                file.warn('variable.%s is missing.', name)

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
                    file.info('No min and/or max information on %s in definition.', variable_name)

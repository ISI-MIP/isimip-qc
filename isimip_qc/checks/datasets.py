import numpy as np


def check_data_model(file, dataset):
    '''
    File must use the NetCDF4 classic data model
    '''
    if dataset.data_model != 'NETCDF4_CLASSIC':
        file.warn('Data model is %s (not NETCDF4_CLASSIC).', dataset.data_model)


def check_zip(file, dataset):
    '''
    Variables must be compressed with at least compression level 4
    '''
    for variable_name, variable in dataset.variables.items():
        zlib = variable.filters().get('zlib')
        if zlib:
            complevel = variable.filters().get('complevel')
            if complevel < 4:
                file.warn('Variable %s _DeflateLevel=%s (< 4).', variable_name, complevel)
        else:
            file.warn('Variable %s is not compressed.', variable_name)


def check_dimensions(file, dataset):
    '''
    The order of dimensions should be (lon, lat, time)
    '''
    dimensions = ('lon', 'lat', 'time')
    if tuple(dataset.dimensions) != dimensions:
        file.warn('Dimensions should be %s, but are %s.', dimensions, tuple(dataset.dimensions))


def check_dimension_variables(file, dataset):
    '''
    The first variables should be dimensions.
    '''
    for dimension_name, variable_name in zip(dataset.dimensions, dataset.variables):
        if dimension_name != variable_name:
            file.warn('Variable %s should be %s.', variable_name, dimension_name)


def check_lon(file, dataset):
    '''
    The global grid ranges 89.75 to -89.75° latitude, and ‐179.75 to 179.75° longitude, i.e. 0.5° grid spacing, 360 rows and 720 columns, or 259200 grid cells total.
    '''
    lon = dataset.variables.get('lon')
    if lon is None:
        file.error('lon is missing.')
    else:
        if lon.shape != (720, ):
            file.error('lon shape is not (720, ), but %s.', lon.shape)

        if np.min(lon) != -179.75:
            file.error('lon min is not -179.75, but %s.', np.min(lon))

        if np.max(lon) != 179.75:
            file.error('lon max is not 179.75, but %s.', np.max(lon))

        try:
            if lon.axis != 'X':
                file.warn('lon.axis must be "X", but is "%s".', lon.axis)
        except AttributeError:
            file.warn('lon.axis is missing.')

        try:
            if lon.standard_name != 'lon':
                file.warn('lon.standard_name must be "lon", but is "%s".', lon.standard_name)
        except AttributeError:
            file.warn('lon.standard_name is missing.')

        try:
            if lon.long_name != 'longitude':
                file.warn('lon.long_name must be "longitude", but is "%s".', lon.long_name)
        except AttributeError:
            file.warn('lon.long_name is missing.')

        try:
            if lon.units != 'degrees_east':
                file.warn('lon.units must be "degrees_east", but is "%s".', lon.units)
        except AttributeError:
            file.warn('lon.units is missing.')

        if lon.dtype != 'float64':
            file.warn('lon precision should be float64 but is %s.', lon.dtype)


def check_lat(file, dataset):
    '''
    The global grid ranges 89.75 to -89.75° latitude, and ‐179.75 to 179.75° longitude, i.e. 0.5° grid spacing, 360 rows and 720 columns, or 259200 grid cells total.
    '''
    lat = dataset.variables.get('lat')
    if lat is None:
        file.error('Lat is missing.')
    else:
        if lat.shape != (360, ):
            file.error('Lat shape is not (360, ), but %s.', lat.shape)

        if np.min(lat) != -89.75:
            file.error('Lat min is not -89.75, but %s.', np.min(lat))

        if np.max(lat) != 89.75:
            file.error('Lat max is not 89.75, but %s.', np.max(lat))

        try:
            if lat.axis != 'Y':
                file.warn('lon.axis must be "X", but is "%s".', lat.axis)
        except AttributeError:
            file.warn('lat.axis is missing.')

        try:
            if lat.standard_name != 'lat':
                file.warn('lat.standard_name must be "lat", but is "%s".', lat.standard_name)
        except AttributeError:
            file.warn('lat.standard_name is missing.')

        try:
            if lat.long_name != 'latitude':
                file.warn('lat.long_name must be "latitude", but is "%s".', lat.long_name)
        except AttributeError:
            file.warn('lat.long_name is missing.')

        try:
            if lat.units != 'degrees_north':
                file.warn('lat.units must be "degrees_east", but is "%s".', lat.units)
        except AttributeError:
            file.warn('lat.units is missing.')

        if lat.dtype != 'float64':
            file.warn('lat precision should be float64 but is %s.', lat.dtype)


def check_time(file, dataset):
    time = dataset.variables.get('time')
    if time is None:
        file.error('time is missing.')
    else:
        try:
            if time.axis != 'Time':
                file.warn('lon.axis must be "Time", but is "%s".', time.axis)
        except AttributeError:
            file.warn('time.axis is missing.')

        try:
            if time.standard_name != 'time':
                file.warn('time.standard_name must be "time", but is "%s".', time.standard_name)
        except AttributeError:
            file.warn('time.standard_name is missing.')

        try:
            file.warn('time.long_name is "%s", but should not be set.', time.long_name)
        except AttributeError:
            pass

        units = 'days since 1661-01-01 00:00:00'
        try:
            if time.units != units:
                file.warn('time.units must be "%s", but is "%s".', units, time.units)
        except AttributeError:
            file.warn('time.units is missing.')

        if time.dtype != 'float64':
            file.warn('time precision should be float64 but is %s.', time.dtype)


def check_variable(file, dataset):
    variable_name = list(dataset.variables)[-1]
    variable = dataset.variables.get(variable_name)

    if variable.dtype != 'float32':
        file.warn('Variable %s precision should be float32 but is %s.', variable_name, variable.dtype)

    dimensions = ('time', 'lat', 'lon')
    if variable.dimensions != dimensions:
        file.warn('Variable %s dimensions should be %s but are %s.', variable_name, dimensions, variable.dimensions)

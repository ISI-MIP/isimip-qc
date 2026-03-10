from ..config import settings


def check_lon_dimension(file):
    model = file.specifiers.get('model')
    climate_forcing = file.specifiers.get('climate_forcing')
    sens_scenario = file.specifiers.get('sens_scenario')

    if settings.SECTOR in ('marine-fishery_regional', 'water_regional', 'lakes_local', 'forestry'):
        return

    ds = file.dataset
    dims = ds.dimensions
    lon_dim = dims.get('lon')
    if lon_dim is None:
        file.error('Longitude dimension "lon" is missing.')
        return

    if model == 'dbem':
        lon_size = 720
    else:
        lon_size = settings.DEFINITIONS['dimensions'].get('lon')['size']

    # pick longitude size if available from data set definition
    cf_def = settings.DEFINITIONS['climate_forcing'].get(climate_forcing, {})
    grid_info = cf_def.get('grid', {})
    if 'lon_size' in grid_info:
        lon_size = (
            grid_info.get('lon_size', {})
                     .get(sens_scenario, grid_info.get('lon_size', {}).get('default', lon_size))
        )

    actual = lon_dim.size
    if lon_size != actual:
        file.warning('Unexpected number of longitudes found (%s). Should be %s', actual, lon_size)
    else:
        file.info('%s longitudes defined.', lon_size)


def check_lat_dimension(file):
    model = file.specifiers.get('model')
    climate_forcing = file.specifiers.get('climate_forcing')
    sens_scenario = file.specifiers.get('sens_scenario')

    if settings.SECTOR in ('marine-fishery_regional', 'water_regional', 'lakes_local', 'forestry'):
        return

    ds = file.dataset
    dims = ds.dimensions
    lat_dim = dims.get('lat')
    if lat_dim is None:
        file.error('Latitude dimension "lat" is missing.')
        return

    if model == 'dbem':
        lat_size = 360
    else:
        lat_size = settings.DEFINITIONS['dimensions'].get('lat')['size']

    cf_def = settings.DEFINITIONS['climate_forcing'].get(climate_forcing, {})
    grid_info = cf_def.get('grid', {})
    if 'lat_size' in grid_info:
        lat_size = (
            grid_info.get('lat_size', {})
                     .get(sens_scenario, grid_info.get('lat_size', {}).get('default', lat_size))
        )

    actual = lat_dim.size
    if lat_size != actual:
        file.warning('Unexpected number of latitudes found (%s). Should be %s', actual, lat_size)
    else:
        file.info('%s latitudes defined.', lat_size)


def check_time_dimension(file):
    if not file.is_time_fixed:
        if file.dataset.dimensions.get('time') is None:
            file.error('Dimension "time" is missing.')


def check_depth_dimension(file):
    if file.is_3d:
        if file.dataset.dimensions.get(file.dim_vertical) is None:
            file.error('Valid 4th dimension is missing. Should be of of [depth, bins]. Found "%s" instead.',
                       file.dim_vertical)


def check_dimensions(file):
    # check dimension order
    variable = file.dataset.variables.get(file.variable_name)
    dims = variable.dimensions

    if file.is_time_fixed:
        expected = ('lat', 'lon')
    elif file.is_2d:
        expected = ('time', 'lat', 'lon')
    elif file.is_3d:
        expected = ('time', file.dim_vertical, 'lat', 'lon')
    else:
        file.error('Variable "%s" neither holds 2d or 3d data. (dim=%s)', file.variable_name, file.dim_len)
        return

    if dims != expected:
        file.error('Dimension order for variable "%s" is %s. Should be %s.', file.variable_name, dims, expected)
    else:
        file.info('Dimensions for variable "%s" look good: %s.', file.variable_name, dims)

    for dimension_name, dimension in file.dataset.dimensions.items():
        dimension_definition = settings.DEFINITIONS['dimensions'].get(dimension_name)

        if not dimension_definition:
            file.error('"%s" is not a valid dimension name as per protocol.', dimension_name)
            continue

        # size of lat and lon are checked above
        if dimension_definition.get('specifier') in ('lat', 'lon'):
            continue

        size = dimension_definition.get('size')
        if size and dimension.size != size:
            file.error('Size of "%s" dimension is %s. Must be %s.', dimension_name, dimension.size, size)

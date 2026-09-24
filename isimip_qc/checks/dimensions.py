import re

from ..config import settings
from ..utils.grid import update_grid_value


def check_lon_dimension(file):
    # get dimension from the dataset
    # skip check for plot-based forestry variables
    variable = file.dataset.variables.get(file.variable_name)
    if variable is not None and len(variable.dimensions) > 1 and variable.dimensions[1] == 'plot':
        return

    lon_dim = file.dataset.dimensions.get('lon')
    if lon_dim is None:
        file.error('Longitude dimension "lon" is missing.')
        return

    # get size from the protocol
    lon_size = settings.DEFINITIONS['dimensions']['lon']['size']

    # overwrite for special cases defined in the protocol
    lon_size = update_grid_value(file, 'lon', 'size', lon_size)

    actual = lon_dim.size
    if lon_size != actual:
        file.warning('Unexpected number of longitudes found (%s). Should be %s', actual, lon_size)
    else:
        file.info('%s longitudes defined.', lon_size)


def check_lat_dimension(file):
    # get dimension from the dataset
    # skip check for plot-based forestry variables
    variable = file.dataset.variables.get(file.variable_name)
    if variable is not None and len(variable.dimensions) > 1 and variable.dimensions[1] == 'plot':
        return

    lat_dim = file.dataset.dimensions.get('lat')
    if lat_dim is None:
        file.error('Latitude dimension "lat" is missing.')
        return

    # get size from the protocol
    lat_size = settings.DEFINITIONS['dimensions']['lat']['size']

    # overwrite for special cases defined in the protocol
    lat_size = update_grid_value(file, 'lat', 'size', lat_size)

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
        if variable.dimensions[1] == 'plot':
            expected = ('time', 'plot')
            if variable.dimensions[0] != 'time' or variable.dimensions[1] != 'plot':
                file.error('Dimension order for variable "%s" is %s. Should be ["time", "plot"].',
                           file.variable_name, variable.dimensions)
                expected = ('time', 'plot', 'layer')
        elif variable.dimensions[0] != 'time' or variable.dimensions[1] != 'lat' or variable.dimensions[2] != 'lon':
            expected = ('time', 'lat', 'lon')
            file.error('Dimension order for variable "%s" is %s. Should be ["time", "lat", "lon"].',
                       file.variable_name, variable.dimensions)
        else:
            expected = ('time', 'lat', 'lon')
            file.info('Dimensions for variable "%s" look good: %s.',
                      file.variable_name, variable.dimensions)
    elif file.is_3d:
        if variable.dimensions[1] == 'plot':
            expected = ('time', 'plot', 'layer')
            if variable.dimensions[0] != 'time' or variable.dimensions[1] != 'plot' or variable.dimensions[2] != 'layer':
                file.error('Dimension order for variable "%s" is %s. Should be ["time", "plot", "layer"].',
                           file.variable_name, variable.dimensions)
        else:
            expected = ('time', file.dim_vertical, 'lat', 'lon')
    else:
        file.error('Variable "%s" neither holds 2d or 3d data. (dim=%s)', file.variable_name, file.dim_len)
        return

    if dims != expected:
        file.error('Dimension order for variable "%s" is %s. Should be %s.', file.variable_name, dims, expected)
    else:
        file.info('Dimensions for variable "%s" look good: %s.', file.variable_name, dims)

    for dimension_name, dimension in file.dataset.dimensions.items():
        if dimension_name in ['nchar']:
            continue

        dimension_definition = settings.DEFINITIONS['dimensions'].get(dimension_name)

        # check string length dimensions
        match = re.match(r'string(\d+)', dimension_name)
        if match:
            if int(match.group(1)) != dimension.size:
                file.error('String dimension "%s" is not correctly named (size=%s).', dimension_name, dimension.size)
            continue

        if not dimension_definition:
            file.error('"%s" is not a valid dimension name as per protocol.', dimension_name)
            continue

        # size of lat and lon are checked above
        if dimension_definition.get('specifier') in ('lat', 'lon'):
            continue

        size = dimension_definition.get('size')
        if size and dimension.size != size:
            file.error('Size of "%s" dimension is %s. Must be %s.', dimension_name, dimension.size, size)

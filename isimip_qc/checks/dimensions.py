from ..config import settings


def check_lon_dimension(file):
    lon_definition = settings.DEFINITIONS['dimensions'].get('lon')
    lon_size = lon_definition['size']

    if file.dataset.dimensions.get('lon') is None:
        file.error('Longitude dimension "lon" is missing.')
    else:
        if lon_size != file.dataset.dimensions.get('lon').size:
            file.warn('Unexpected number of longitudes found (%s). Should be %s', file.dataset.dimensions.get('lon').size, lon_size)
        else:
            file.info('%s longitudes defined.', lon_size)


def check_lat_dimension(file):
    lat_definition = settings.DEFINITIONS['dimensions'].get('lat')
    lat_size = lat_definition['size']

    if file.dataset.dimensions.get('lat') is None:
        file.error('Latitude dimension "lat" is missing.')
    else:
        if lat_size != file.dataset.dimensions.get('lat').size:
            file.warn('Unexpected number of latitudes found (%s). Should be %s', file.dataset.dimensions.get('lat').size, lat_size)
        else:
            file.info('%s latitudes defined.', lat_size)


def check_time_dimension(file):
    if file.dataset.dimensions.get('time') is None:
        file.error('Dimension "time" is missing.')


def check_depth_dimension(file):
    if file.is_3d:
        if file.dataset.dimensions.get(file.dim_vertical) is None:
            file.error('Valid 4th dimension is missing. Should be of of [depth, bins]. Found "%s" instead.', file.dim_vertical)


def check_dimensions(file):
    # check dimension order
    variable = file.dataset.variables.get(file.variable_name)

    dim_len = len(variable.dimensions)
    if file.is_2d:
        if variable.dimensions[0] != 'time' or variable.dimensions[1] != 'lat' or variable.dimensions[2] != 'lon':
            file.error('Dimension order for variable "%s" is %s. Should be ["time", "lat", "lon"].', file.variable_name, variable.dimensions)
        else:
            file.info('Dimensions for variable "%s" look good: %s.', file.variable_name, variable.dimensions)
    elif file.is_3d:
        if variable.dimensions[0] != 'time' or variable.dimensions[2] != 'lat' or variable.dimensions[3] != 'lon':
            file.error('Dimension order for variable "%s" is %s. Should be ["time", "%s" , "lat", "lon"].', file.variable_name, variable.dimensions, file.dim_vertical)
        else:
            file.info('Dimensions for variable "%s" look good.', file.variable_name)
    else:
        file.error('Variable "%s" neither holds 2d or 3d data. (dim=%s)', dim_len)

    for dimension_name, dimension in file.dataset.dimensions.items():
        dimension_definition = settings.DEFINITIONS['dimensions'].get(dimension_name)

        if dimension_definition:
            # size of lat and lon are checked above 
            if dimension_definition.get('specifier') not in ['lat', 'lon']:
                size = dimension_definition.get('size')
                if size and dimension.size != size:
                    file.error('Size of "%s" dimension is %s. Must be %s.', dimension_name, dimension.size, size)
        else:
            file.error('"%s" is not a valid dimension name as per protocol.', dimension_name)

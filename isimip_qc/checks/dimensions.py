from ..config import settings

def check_1_dimensions(file):
    variable_name = file.specifiers.get('variable')
    variable = file.dataset.variables.get(variable_name)
    dim_len = len(variable.dimensions)

    # detect 2d or 3d data
    if dim_len == 3:
        file.is_2d = True
    elif dim_len == 4:
        file.is_3d = True


def check_lon_dimension(file):
    if file.dataset.dimensions.get('lon') is None:
        file.error('Dimension \'lon\' is missing.')


def check_lat_dimension(file):
    if file.dataset.dimensions.get('lat') is None:
        file.error('Dimension \'lat\' is missing.')


def check_time_dimension(file):
    if file.dataset.dimensions.get('time') is None:
        file.error('Dimension \'time\' is missing.')


def check_depth_dimension(file):
    if file.is_3d:
        if file.dataset.dimensions.get('depth') is None:
            file.error('Dimension \'depth\' is missing.')


def check_2_dimensions(file):
    # check dimension order
    variable_name = file.specifiers.get('variable')
    variable = file.dataset.variables.get(variable_name)

    dim_len = len(variable.dimensions)
    if file.is_2d:
        if variable.dimensions[0] != 'time' or variable.dimensions[1] != 'lat' or variable.dimensions[2] != 'lon':
            file.warn('%s dimension order %s should be ["time", "lat", "lon"].', variable_name, variable.dimensions)
        else:
            file.info('Dimensions for variable "%s" look good: %s', variable_name, variable.dimensions)
    elif file.is_3d:
        if variable.dimensions[0] != 'time' or variable.dimensions[1] not in ['depth'] or variable.dimensions[2] != 'lat' or variable.dimensions[2] != 'lon':
            file.warn('%s dimension order %s should be ["time", "depth" , "lat", "lon"].', variable_name, variable.dimensions)
        else:
            file.info('Dimensions for variable "%s" look good', variable_name)
    else:
        file.error('Variable "%s" neither holds 2d or 3d data. (dim=%s)', dim_len)

    for dimension_name, dimension in file.dataset.dimensions.items():
        dimension_definition = settings.DEFINITIONS['dimensions'].get(dimension_name)

        if dimension_definition:
            size = dimension_definition.get('size')
            if size and dimension.size != size:
                file.error('%s.size=%s must be %s.', dimension_name, dimension.size, size)
        else:
            file.warn('No definition for dimension %s.', dimension_name)

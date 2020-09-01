from ..config import settings


def check_lon_dimension(file):
    if file.dataset.dimensions.get('lon') is None:
        file.error('Dimension \'lon\' is missing.')


def check_lat_dimension(file):
    if file.dataset.dimensions.get('lat') is None:
        file.error('Dimension \'lat\' is missing.')


def check_time_dimension(file):
    if file.dataset.dimensions.get('time') is None:
        file.error('Dimension \'time\' is missing.')


def check_dimensions(file):
    for dimension_name, dimension in file.dataset.dimensions.items():
        dimension_definition = settings.DEFINITIONS['dimensions'].get(dimension_name)

        if dimension_definition:
            size = dimension_definition.get('size')
            if size and dimension.size != size:
                file.error('%s.size=%s must be %s.', dimension_name, dimension.size, size)
        else:
            file.warn('No definition for dimension %s.', dimension_name)

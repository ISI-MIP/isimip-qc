from ..config import settings


def check_lon_dimension(file):
    lon = file.dataset.dimensions.get('lon')
    if lon is None:
        file.error('dimension lon is missing.')
    else:
        if lon.size != 720:
            file.error('lon.size=%s must be 720.', lon.size)


def check_lat_dimension(file):
    lat = file.dataset.dimensions.get('lat')
    if lat is None:
        file.error('dimension lat is missing.')
    else:
        if lat.size != 360:
            file.error('lat.size=%s must be 360.', lat.size)


def check_time_dimension(file):
    time = file.dataset.dimensions.get('time')
    if time is None:
        file.error('dimension time is missing.')
    else:
        if time.size == 0:
            file.error('time.size=%s must be > 0.')


def check_level_dimensions(file):
    for dimension_name, dimension in file.dataset.dimensions.items():
        if dimension_name not in ['lon', 'lat', 'time']:
            schema_dimension = settings.SCHEMA['properties']['dimensions']['properties'].get(dimension_name)
            if schema_dimension is None:
                file.error('dimension %s not in schema.', dimension_name)
            if dimension.size == 0:
                file.error('%s.size=%s must be > 0.', dimension.size)

import numpy as np
from isimip_qc.config import settings
from isimip_qc.fixes import fix_set_variable_attr


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

        # check minimum
        minimum = lat_definition.get('minimum')[file.sector]
        if np.min(lat) != minimum:
            file.error('min(lat)=%s must be %s.', np.min(lat), minimum)

        # check maximum
        maximum = lat_definition.get('maximum')[file.sector]
        if np.max(lat) != maximum:
            file.error('max(lat)=%s must be %s.', np.max(lat), maximum)

        # check axis
        axis = lat_definition.get('axis')
        try:
            if lat.axis != axis:
                file.warn('Attribute lat.axis="%s" should be "%s".', lat.axis, axis, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'lat', 'axis', axis)
                })
        except AttributeError:
            file.warn('Attribute lat.axis is missing. Should be "%s".', axis, fix={
                'func': fix_set_variable_attr,
                'args': (file, 'lat', 'axis', axis)
            })

        # check standard_name
        standard_name = lat_definition.get('standard_name')
        try:
            if lat.standard_name != standard_name:
                file.warn('Attribute lat.standard_name="%s" should be "%s".', lat.standard_name, standard_name, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'lat', 'standard_name', standard_name)
                })
        except AttributeError:
            file.warn('Attribute lat.standard_name is missing. Should be "%s".', standard_name)

        # check long_name
        long_names = lat_definition.get('long_names', [])
        try:
            if lat.long_name not in long_names:
                file.warn('Attribute lat.long_name="%s" should be in %s.', lat.long_name, long_names, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'lat', 'long_name', long_names[0])
                })
        except AttributeError:
            file.warn('Attribute lat.long_name is missing. Should be "%s".', long_names[0])

        # check units
        units = lat_definition.get('units')
        try:
            if lat.units != units:
                file.warn('Attribute lat.units="%s" should be "%s".', lat.units, units, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'lat', 'units', units)
                })
        except AttributeError:
            file.warn('Attribute lat.units is missing. Should be "%s".', units, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'lat', 'units', units)
                })

        lat_first = file.dataset.variables.get('lat')[0]
        lat_last = file.dataset.variables.get('lat')[-1]
        if lat_first < lat_last:
            file.warn('latitudes in wrong order. Index should range from north to south. (found %s to %s)', lat_first, lat_last)
        else:
            file.info('Latitude index order looks good (N to S).')

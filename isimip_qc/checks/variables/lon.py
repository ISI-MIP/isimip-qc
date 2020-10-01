import numpy as np
from isimip_qc.config import settings
from isimip_qc.fixes import fix_set_variable_attr


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
            file.warn('Data type of "lon" is "%s". Should be float or double (one of %s).', lon.dtype, dtypes)

        # check minimum
        minimum = lon_definition.get('minimum')
        if np.min(lon) != minimum:
            file.error('First longitude is %s. Must be %s.', np.min(lon), minimum)

        # check maximum
        maximum = lon_definition.get('maximum')
        if np.max(lon) != maximum:
            file.error('Last longitude is %s. Must be %s.', np.min(lon), maximum)

        # check axis
        axis = lon_definition.get('axis')
        try:
            if lon.axis != axis:
                file.warn('"axis" attribute of "lon" is %s. Should be "%s".', lon.axis, axis, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'lon', 'axis', axis)
                })
        except AttributeError:
            file.warn('"axis" attribute of "lon" is missing. Should be "%s".', axis, fix={
                'func': fix_set_variable_attr,
                'args': (file, 'lon', 'axis', axis)
            })

        # check standard_name
        standard_name = lon_definition.get('standard_name')
        try:
            if lon.standard_name != standard_name:
                file.warn('"standard_name" attribute of "lon" is "%s". Should be "%s".', lon.standard_name, standard_name, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'lon', 'standard_name', standard_name)
                })
        except AttributeError:
            file.warn('"standard_name" attribute of "lon" is missing. Should be "%s".', standard_name)

        # check long_name
        long_names = lon_definition.get('long_names', [])
        try:
            if lon.long_name not in long_names:
                file.warn('"long_name" attribute of "lon" is %s". Should be in %s.', lon.long_name, long_names, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'lon', 'long_name', long_names[0])
                })
        except AttributeError:
            file.warn('"long_name" attribute of "lon" is missing. Should be "%s".', long_names[0])

        # check units
        units = lon_definition.get('units')
        try:
            if lon.units != units:
                file.warn('"units" attribute for "lon" is "%s". Should be "%s".', lon.units, units, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'lon', 'units', units)
                })
        except AttributeError:
            file.warn('"units" attribute for "lon" is missing. Should be "%s".', units, fix={
                'func': fix_set_variable_attr,
                'args': (file, 'lon', 'units', units)
            })

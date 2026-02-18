import numpy as np

from isimip_qc.config import settings
from isimip_qc.fixes import fix_set_variable_attr


def check_latlon_variable(file):
    model = file.specifiers.get('model')
    climate_forcing = file.specifiers.get('climate_forcing')
    sens_scenario = file.specifiers.get('sens_scenario')

    ds = file.dataset
    variables = ds.variables

    for variable in ('lat', 'lon'):
        var = variables.get(variable)
        var_definition = settings.DEFINITIONS['dimensions'].get(variable)

        if var is None:
            file.error('Variable "%s" is missing.', variable)
            continue
        if not var_definition:
            file.error('Definition for variable "%s" is missing.', variable)
            continue

        # check dtype
        if var.dtype not in (np.dtype('float32'), np.dtype('float64')):
            file.warn('Data type of "%s" is "%s". Should be float or double (one of %s).',
                      variable, var.dtype, ('float32', 'float64'))

        # check axis
        axis = var_definition.get('axis')
        cur_axis = getattr(var, 'axis', None)
        if cur_axis != axis:
            file.warn('"axis" attribute of "%s" is %s. Should be "%s".', variable, cur_axis, axis, fix={
                'func': fix_set_variable_attr,
                'args': (file, variable, 'axis', axis)
            })

        # check standard_name
        standard_name = var_definition.get('standard_name')
        cur_std = getattr(var, 'standard_name', None)
        if cur_std != standard_name:
            file.warn('"standard_name" attribute of "%s" is "%s". Should be "%s".',
                      variable, cur_std, standard_name, fix={
                          'func': fix_set_variable_attr,
                          'args': (file, variable, 'standard_name', standard_name)
                      })

        # check long_name
        long_names = var_definition.get('long_names', [])
        if long_names:
            cur_long = getattr(var, 'long_name', None)
            default_long = long_names[0]
            if cur_long not in long_names:
                file.warn('"long_name" attribute of "%s" is %s. Should be in %s.',
                          variable, cur_long, long_names, fix={
                              'func': fix_set_variable_attr,
                              'args': (file, variable, 'long_name', default_long)
                          })

        # check units
        units = var_definition.get('units')
        cur_units = getattr(var, 'units', None)
        if cur_units != units:
            file.warn('"units" attribute for "%s" is "%s". Should be "%s".',
                      variable, cur_units, units, fix={
                          'func': fix_set_variable_attr,
                          'args': (file, variable, 'units', units)
                      })

        if settings.SECTOR in ('marine-fishery_regional', 'water_regional', 'lakes_local', 'forestry'):
            continue

        # pick lat/lon ranges if available from dimensions definition
        minimum = var_definition.get('minimum')
        maximum = var_definition.get('maximum')

        # overwrite lat/lon ranges if available from climate forcing definition
        cf_def = settings.DEFINITIONS['climate_forcing'].get(climate_forcing, {})
        grid_info = cf_def.get('grid', {})
        if grid_info:
            if variable == 'lat':
                minimum = grid_info.get('lat_min', {}).get(sens_scenario, grid_info.get('lat_min', {}).get('default', minimum))
                maximum = grid_info.get('lat_max', {}).get(sens_scenario, grid_info.get('lat_max', {}).get('default', maximum))
            else:
                minimum = grid_info.get('lon_min', {}).get(sens_scenario, grid_info.get('lon_min', {}).get('default', minimum))
                maximum = grid_info.get('lon_max', {}).get(sens_scenario, grid_info.get('lon_max', {}).get('default', maximum))

        # overwrite for special cases not defined in the protocol
        if model == 'dbem':
            if variable == 'lat':
                minimum = -89.75
                maximum = 89.75
            elif variable == 'lon':
                minimum = -179.75
                maximum = 179.75

        # use first and last element which is sufficient for monotonic lat/lon
        try:
            first_val = var[0].item()
            last_val = var[-1].item()
        except Exception:
            # fallback to full-array min/max if needed
            arr = np.asarray(var[:])
            first_val = float(np.min(arr))
            last_val = float(np.max(arr))

        # For latitude we expect values to decrease (north -> south),
        # so the first element should match the protocol's "maximum" and
        # the last element the "minimum". For longitude we expect
        # increasing values (west -> east): first == minimum, last == maximum.
        if variable == 'lat':
            expected_first = maximum
            expected_last = minimum
        else:  # lon
            expected_first = minimum
            expected_last = maximum

        if expected_first is not None and round(first_val, 7) != expected_first:
            file.error('First value of variable "%s" is %s. Must be %s.', variable, first_val, expected_first)

        if expected_last is not None and round(last_val, 7) != expected_last:
            file.error('Last value of variable "%s" is %s. Must be %s.', variable, last_val, expected_last)

        # check ordering direction and report helpful messages
        if variable == 'lat':
            if not (first_val > last_val):
                file.warn('Latitudes in wrong order. Index should range from north to south. (found %s to %s)',
                          first_val, last_val)
            else:
                file.info('Latitude index order looks good (N to S).')
        else:  # lon
            if not (first_val < last_val):
                file.warn('Longitudes in wrong order. Index should range from west to east. (found %s to %s)',
                          first_val, last_val)
            else:
                file.info('Longitude index order looks good (W to E).')

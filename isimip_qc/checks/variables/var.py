import math

import netCDF4
import numpy as np

from isimip_qc.config import settings
from isimip_qc.fixes import fix_set_variable_attr


def check_variable(file):
    variable = file.dataset.variables.get(file.variable_name)
    definition = settings.DEFINITIONS.get('variable', {}).get(file.specifiers.get('variable'))
    model = file.specifiers.get('model')
    climate_forcing = file.specifiers.get('climate_forcing')
    sens_scenario = file.specifiers.get('sens_scenario')

    if not variable:
        file.error('Variable %s is missing.', file.variable_name)
    elif not definition:
        file.error('Definition for variable %s is missing.', file.variable_name)
    else:
        # check file name and NetCDF variable to match each other
        if variable.name != file.variable_name:
            file.error('File name variable (%s) does not match internal variable name (%s).',
                       file.variable_name, variable.name)

        # check dtype
        if variable.dtype != 'float32':
            file.warn('%s data type is "%s" should be "float32".',
                      file.variable_name, variable.dtype, fix_datamodel=True)

        # check chunking
        chunking = variable.chunking()
        if chunking:
            # pick lat/lon sizes from dimensions definition
            if settings.SECTOR in ['marine-fishery_regional', 'water_regional', 'lakes_local', 'forestry']:
                lat_size = file.dataset.variables.get('lat').shape[0]
                lon_size = file.dataset.variables.get('lon').shape[0]
            else:
                lat_size = settings.DEFINITIONS['dimensions'].get('lat')['size']
                lon_size = settings.DEFINITIONS['dimensions'].get('lon')['size']

            # overwrite lat/lon ranges if available from climate forcing definition
            if 'grid' in settings.DEFINITIONS['climate_forcing'].get(climate_forcing):
                grid_info = settings.DEFINITIONS['climate_forcing'].get(climate_forcing)['grid']
                try:
                    lat_size = grid_info['lat_size'][sens_scenario]
                    lon_size = grid_info['lon_size'][sens_scenario]
                except KeyError:
                    lat_size = grid_info['lat_size']['default']
                    lon_size = grid_info['lon_size']['default']

            # overwrite for special cases not defined in the protocol
            if model == 'dbem':
                lat_size = 360
                lon_size = 720

            if file.is_2d:
                if chunking[0] != 1 or chunking[1] != lat_size or chunking[2] != lon_size:
                    file.warn('%s.chunking=%s should be [1, %s, %s] (with proper depencency order).',
                              file.variable_name, chunking, lat_size, lon_size, fix_datamodel=True)
                else:
                    file.info('Variable properly chunked [1, %s, %s].', lat_size, lon_size)
            if file.is_3d:
                var3d_size = file.dataset.dimensions.get(file.dim_vertical).size
                if (chunking[0] != 1
                    or (chunking[1] != 1 and chunking[1] != var3d_size)
                    or chunking[2] != lat_size
                    or chunking[3] != lon_size):
                    file.warn('%s.chunking=%s. Should be [1, %s, %s, %s] or [1, 1, %s, %s]'
                              ' (with proper depencency order).',
                              file.variable_name, chunking, var3d_size, lat_size, lon_size,
                              lat_size, lon_size, fix_datamodel=True)
                else:
                    file.info('Variable properly chunked [1, %s, %s, %s].', var3d_size, lat_size, lon_size)
        else:
            file.info('Variable chunking not supported by data model found.')

        # check dimensions
        definition_dimensions = tuple(definition.get('dimensions', []))

        if file.is_time_fixed:
            default_dimensions = ('lat', 'lon')
        if file.is_2d:
            default_dimensions = ('time', 'lat', 'lon')
        elif file.is_3d:
            default_dimensions = ('time', file.dim_vertical, 'lat', 'lon')

        if definition_dimensions:
            if variable.dimensions not in [definition_dimensions, default_dimensions]:
                file.error('Found %s dimensions for "%s". Must be %s.',
                           variable.dimensions, file.variable_name, default_dimensions)
        else:
            if variable.dimensions != default_dimensions:
                file.error('Found %s dimensions for "%s". Must be %s.',
                           variable.dimensions, file.variable_name, default_dimensions)

        # check standard_name
        standard_name = definition.get('standard_name')
        if standard_name:
            try:
                if variable.standard_name != standard_name:
                    file.warn(
                        'Attribute standard_name="%s" for variable "%s". Should be "%s".',
                        variable.standard_name, file.variable_name, standard_name, fix={
                            'func': fix_set_variable_attr,
                            'args': (file, file.variable_name, 'standard_name', standard_name)
                        }
                    )
            except AttributeError:
                file.warn(
                    'Attribute standard_name is missing for variable "%s". Should be "%s".',
                    file.variable_name, standard_name, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, file.variable_name, 'standard_name', standard_name)
                    }
                )

        # check long_name
        long_name = definition.get('long_name')
        if long_name:
            try:
                if variable.long_name != long_name:
                    file.warn(
                        'Attribute long_name="%s" for variable "%s". Should be "%s".',
                        variable.long_name, file.variable_name, long_name, fix={
                            'func': fix_set_variable_attr,
                            'args': (file, file.variable_name, 'long_name', long_name)
                        }
                    )
            except AttributeError:
                file.warn(
                    'Attribute long_name is missing for variable "%s". Should be "%s".',
                    file.variable_name, long_name, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, file.variable_name, 'long_name', long_name)
                    }
                )

        # check variable units
        units = definition.get('units')
        if units is not None:
            try:
                if variable.units != units:
                    file.error('%s.units="%s" should be "%s". Check if values are matching the unit given.',
                               file.variable_name, variable.units, units)
                else:
                    file.info('Variable unit matches protocol definition (%s).', variable.units)
            except AttributeError:
                file.warn(
                    'Variable "%s" units attribute is missing. Should be "%s".',
                    file.variable_name, units, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, file.variable_name, 'units', units)
                    }
                )
        else:
            file.warn('No units information for variable "%s" in definition.', file.variable_name)

        # check _FillValue and missing_value
        for name in ['_FillValue', 'missing_value']:
            try:
                attr = variable.getncattr(name)
                if attr.dtype != variable.dtype:
                    file.error('%s data type (%s) differs from %s data type (%s).',
                               name, attr.dtype, file.variable_name, variable.dtype)
                else:
                    if not math.isclose(attr, 1e+20, rel_tol=1e-6):
                        file.error('Missing values for variable "%s": %s=%s but should be 1e+20.',
                                   file.variable_name, name, attr)
                    else:
                        file.info('Missing value attribute "%s" is properly set.', name)
            except AttributeError:
                if name == 'missing_value':
                    file.warn(
                        '"%s" attribute for variable "%s" is missing. Should be set to 1e+20f.',
                        name, file.variable_name, fix={
                            'func': fix_set_variable_attr,
                            'args': (file, file.variable_name, 'missing_value', 1e+20)
                        }
                    )
                else:
                    file.error('"%s" attribute for variable "%s" is missing. Should be set to 1e+20f and must be set'
                               ' when variable is created.', name, file.variable_name)

        # check valid range
        if settings.SECTOR == 'agriculture':
            return

        if settings.MINMAX:
            if file.is_time_fixed:
                file.warn('Valid range test for fixed data not yet implemented')
                return

            valid_min = definition.get('valid_min')
            valid_max = definition.get('valid_max')
            if (valid_min is not None) and (valid_max is not None):
                file.info('Checking values for valid minimum and maximum range defined in'
                          ' the protocol. This could take some time...')
                lat = file.dataset.variables.get('lat')
                lon = file.dataset.variables.get('lon')
                time = file.dataset.variables.get('time')

                too_low = np.argwhere(variable[:] < valid_min)
                too_high = np.argwhere(variable[:] > valid_max)

                time = file.dataset.variables.get('time')
                file.specifiers.get('time_step')

                try:
                    time_units = time.units
                except AttributeError:
                    file.warn('Can\'t check for valid ranges because of missing units attribute in time variable')
                    return

                try:
                    time_calendar = time.calendar
                except AttributeError:
                    file.warn('Can\'t check for valid ranges because of missing calendar attribute in time variable')
                    return

                if too_low.size:
                    file.warn('%i values are lower than the valid minimum (%.2E %s).',
                              too_low.shape[0], valid_min, units)
                    if settings.LOG_LEVEL == 'VRDETAIL':
                        file.warn('%i lowest values are :', min(settings.MINMAX, too_low.shape[0]))

                        too_low_list = []
                        for index in too_low[0:too_low.shape[0]]:
                            too_low_list.append([tuple(index), variable[tuple(index)].data.tolist()])

                        too_low_sorted = sorted(too_low_list, key=lambda value: value[1], reverse=False)
                        for i in range(0, min(settings.MINMAX, too_low.shape[0])):
                            if file.is_2d:
                                file.warn('date: %s, lat/lon: %4.2f/%4.2f, value: %E %s',
                                          netCDF4.num2date(time[too_low_sorted[i][0][0]], time_units, time_calendar),
                                          lat[too_low_sorted[i][0][-2]],
                                          lon[too_low_sorted[i][0][-1]],
                                          too_low_sorted[i][1], units)
                            elif file.is_3d:
                                file.warn('date: %s, lat/lon: %4.2f/%4.2f, level: %s, value: %E %s',
                                          netCDF4.num2date(time[too_low_sorted[i][0][0]], time_units, time_calendar),
                                          lat[too_low_sorted[i][0][-2]],
                                          lon[too_low_sorted[i][0][-1]],
                                          too_low_sorted[i][0][-3] + 1,
                                          too_low_sorted[i][1], units)

                if too_high.size:
                    file.warn('%i values are higher than the valid maximum (%.2E %s).',
                              too_high.shape[0], valid_max, units)
                    if settings.LOG_LEVEL == 'VRDETAIL':
                        file.warn('%i highest values are :', min(settings.MINMAX, too_high.shape[0]))

                        too_high_list = []
                        for index in too_high[0:too_high.shape[0]]:
                            too_high_list.append([tuple(index), variable[tuple(index)].data.tolist()])

                        too_high_sorted = sorted(too_high_list, key=lambda value: value[1], reverse=True)
                        for i in range(0, min(settings.MINMAX, too_high.shape[0])):
                            if file.is_2d:
                                file.warn('date: %s, lat/lon: %4.2f/%4.2f, value: %E %s',
                                          netCDF4.num2date(time[too_high_sorted[i][0][0]], time_units, time_calendar),
                                          lat[too_high_sorted[i][0][-2]],
                                          lon[too_high_sorted[i][0][-1]],
                                          too_high_sorted[i][1], units)
                            elif file.is_3d:
                                file.warn('date: %s, lat/lon: %4.2f/%4.2f, level: %s, value: %E %s',
                                          netCDF4.num2date(time[too_high_sorted[i][0][0]], time_units, time_calendar),
                                          lat[too_high_sorted[i][0][-2]],
                                          lon[too_high_sorted[i][0][-1]],
                                          too_high_sorted[i][0][-3] + 1,
                                          too_high_sorted[i][1], units)

                if not too_low.shape and not too_high.shape:
                    file.info('Values are within valid range (%.2E to %.2E).', valid_min, valid_max)

            else:
                file.warn('No min and/or max definition found for variable "%s" in protocol. Skipping test.',
                          file.variable_name)

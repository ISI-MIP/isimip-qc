import heapq
import math

import netCDF4
import numpy as np

from isimip_qc.config import settings
from isimip_qc.fixes import fix_set_variable_attr
from isimip_qc.utils.grid import update_grid_value


def check_variable(file):
    ds = file.dataset
    variables = ds.variables
    variable = variables.get(file.variable_name)
    definition = settings.DEFINITIONS.get('variable', {}).get(file.specifiers.get('variable'))

    # bool(Variable) is false for variables with an empty first dimension and an empty
    # definition dict is falsy as well, so compare against None explicitly
    if variable is None:
        file.error('Variable %s is missing.', file.variable_name)
    elif definition is None:
        file.error('Definition for variable %s is missing.', file.variable_name)
    else:
        # check file name and NetCDF variable to match each other
        if variable.name != file.variable_name:
            file.error('File name variable (%s) does not match internal variable name (%s).',
                       file.variable_name, variable.name)

        # check dtype (compare with NumPy dtype object)
        if variable.dtype != np.dtype('float32'):
            file.warning('%s data type is "%s" should be "float32".',
                         file.variable_name, variable.dtype, fix_datamodel=True)

        # check chunking (netCDF4 reports contiguous storage as the truthy
        # string 'contiguous' rather than as a list of chunk sizes)
        chunking = variable.chunking()

        if chunking == 'contiguous':
            file.info('Variable is stored contiguously (no chunking).')

        elif chunking:
            # get sizes from the protocol
            lat_size = settings.DEFINITIONS['dimensions']['lat']['size']
            lon_size = settings.DEFINITIONS['dimensions']['lon']['size']

            # overwrite for special cases defined in the protocol
            lat_size = update_grid_value(file, 'lat', 'size', lat_size)
            lon_size = update_grid_value(file, 'lon', 'size', lon_size)

            if file.is_2d:
                if chunking[0] != 1 or chunking[1] != lat_size or chunking[2] != lon_size:
                    file.warning('%s.chunking=%s should be [1, %s, %s] (with proper dependency order).',
                                 file.variable_name, chunking, lat_size, lon_size, fix_datamodel=True)
                else:
                    file.info('Variable properly chunked [1, %s, %s].', lat_size, lon_size)

            if file.is_3d:
                vertical_dim = ds.dimensions.get(file.dim_vertical)
                if vertical_dim is None:
                    file.warning('Can\'t check chunking: vertical dimension "%s" not found in file.',
                                 file.dim_vertical)
                else:
                    var3d_size = vertical_dim.size
                    if (chunking[0] != 1
                        or (chunking[1] != 1 and chunking[1] != var3d_size)
                        or chunking[2] != lat_size
                        or chunking[3] != lon_size):
                        file.warning('%s.chunking=%s. Should be [1, %s, %s, %s] or [1, 1, %s, %s]'
                                     ' (with proper dependency order).',
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
        elif file.is_2d:
            default_dimensions = ('time', 'lat', 'lon')
        elif file.is_3d:
            default_dimensions = ('time', file.dim_vertical, 'lat', 'lon')
        else:
            # neither 2d nor 3d data: reported by check_3d already (if it ran)
            default_dimensions = None

        if default_dimensions is None:
            file.warning('Can\'t check the dimensions of variable "%s": it is neither 2d nor 3d data.',
                         file.variable_name)
        elif definition_dimensions:
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
            cur = getattr(variable, 'standard_name', None)
            if cur != standard_name:
                file.warning(
                    'Attribute standard_name="%s" for variable "%s". Should be "%s".',
                    cur, file.variable_name, standard_name, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, file.variable_name, 'standard_name', standard_name)
                    }
                )

        # check long_name
        long_name = definition.get('long_name')
        if long_name:
            cur = getattr(variable, 'long_name', None)
            if cur != long_name:
                file.warning(
                    'Attribute long_name="%s" for variable "%s". Should be "%s".',
                    cur, file.variable_name, long_name, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, file.variable_name, 'long_name', long_name)
                    }
                )

        # check variable units
        units = definition.get('units')
        if units is not None:
            cur = getattr(variable, 'units', None)
            if cur is None:
                file.warning(
                    'Variable "%s" units attribute is missing. Should be "%s".',
                    file.variable_name, units, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, file.variable_name, 'units', units)
                    }
                )
            elif cur != str(units):
                file.error('%s.units="%s" should be "%s". Check if values are matching the unit given.',
                           file.variable_name, cur, units)
            else:
                file.info('Variable unit matches protocol definition (%s).', cur)
        else:
            file.warning('No units information for variable "%s" in definition.', file.variable_name)

        # check _FillValue and missing_value using ncattrs to avoid exceptions
        ncattrs = []
        try:
            ncattrs = variable.ncattrs()
        except AttributeError:
            ncattrs = list(variable.__dict__.keys())

        for name in ['_FillValue', 'missing_value']:
            if name in ncattrs:
                attr = variable.getncattr(name)
                try:
                    attr_dtype = np.asarray(attr).dtype
                except AttributeError:
                    attr_dtype = None

                if attr_dtype is not None and attr_dtype != variable.dtype:
                    file.error('%s data type (%s) differs from %s data type (%s).',
                               name, attr_dtype, file.variable_name, variable.dtype)
                else:
                    try:
                        val = float(attr)
                        if not math.isclose(val, 1e+20, rel_tol=1e-6):
                            file.error('Missing values for variable "%s": %s=%s but should be 1e+20.',
                                       file.variable_name, name, attr)
                        else:
                            file.info('Missing value attribute "%s" is properly set.', name)
                    except AttributeError:
                        file.error('Could not interpret %s attribute for variable "%s" as numeric.',
                                   name, file.variable_name)
            else:
                if name == 'missing_value':
                    file.warning(
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
        if isinstance(settings.MINMAX, (int, float)) and not isinstance(settings.MINMAX, bool) and settings.MINMAX >= 0:
            if file.is_time_fixed:
                file.warning('Valid range test for fixed data not yet implemented.')
                return

            # skip valid range check for special sectors
            if (
                settings.DEFINITIONS['sector'].get(settings.SECTOR, {}).get('valid_min') is False or
                settings.DEFINITIONS['sector'].get(settings.SECTOR, {}).get('valid_max') is False
            ):
                file.warning('Skip valid range test for "%s" sector.', settings.SECTOR)
                return

            valid_min = definition.get('valid_min')
            valid_max = definition.get('valid_max')
            if (valid_min is not None) and (valid_max is not None):
                file.info('Checking values for valid minimum and maximum range defined in'
                          ' the protocol. This could take some time...')
                time_var = file.dataset.variables.get('time')

                try:
                    time_units = time_var.units
                except AttributeError:
                    file.warning('Can\'t check for valid ranges because of missing units attribute in time variable')
                    return

                try:
                    time_calendar = time_var.calendar
                except AttributeError:
                    file.warning('Can\'t check for valid ranges because of missing calendar attribute in time variable')
                    return

                file.info('Scanning in streaming mode to limit memory usage...')

                lat_var = file.dataset.variables.get('lat')
                lon_var = file.dataset.variables.get('lon')
                # preload lat/lon arrays to avoid repeated I/O; missing coordinate
                # variables are reported by the coordinate checks, here we just cope
                # without them
                lat_vals = lat_var[:] if lat_var is not None else None
                lon_vals = lon_var[:] if lon_var is not None else None

                nt = time_var.size
                if nt == 0:
                    file.warning('Can\'t check for valid ranges because the time axis is empty.')
                    return

                # Heaps to keep top N extremes while scanning
                n_keep = int(settings.MINMAX)
                low_heap = []  # max-heap via storing (-value, index_tuple)
                high_heap = []  # min-heap storing (value, index_tuple)
                count_low = 0
                count_high = 0

                # iterate over time slices to limit memory usage
                for t in range(nt):
                    try:
                        slice_arr = variable[t]
                    except AttributeError:
                        # If time is not first dim, attempt generic slicing
                        slice_arr = variable[(t, ...)]

                    ma = np.ma.asarray(slice_arr)
                    data = ma.data
                    mask = np.ma.getmaskarray(ma)
                    valid_mask = ~mask

                    if file.is_2d:
                        # data shape: (lat, lon)
                        cond_low = (data < valid_min) & valid_mask
                        cond_high = (data > valid_max) & valid_mask
                        low_idx = np.argwhere(cond_low)
                        high_idx = np.argwhere(cond_high)
                        for idx in low_idx:
                            count_low += 1
                            full_idx = (t, idx[0], idx[1])
                            val = float(data[idx[0], idx[1]])
                            heapq.heappush(low_heap, (-val, full_idx))
                            if len(low_heap) > n_keep:
                                heapq.heappop(low_heap)
                        for idx in high_idx:
                            count_high += 1
                            full_idx = (t, idx[0], idx[1])
                            val = float(data[idx[0], idx[1]])
                            heapq.heappush(high_heap, (val, full_idx))
                            if len(high_heap) > n_keep:
                                heapq.heappop(high_heap)

                    elif file.is_3d:
                        # data shape: (level, lat, lon)
                        cond_low = (data < valid_min) & valid_mask
                        cond_high = (data > valid_max) & valid_mask
                        low_idx = np.argwhere(cond_low)
                        high_idx = np.argwhere(cond_high)
                        for idx in low_idx:
                            count_low += 1
                            full_idx = (t, idx[0], idx[1], idx[2])
                            val = float(data[idx[0], idx[1], idx[2]])
                            heapq.heappush(low_heap, (-val, full_idx))
                            if len(low_heap) > n_keep:
                                heapq.heappop(low_heap)
                        for idx in high_idx:
                            count_high += 1
                            full_idx = (t, idx[0], idx[1], idx[2])
                            val = float(data[idx[0], idx[1], idx[2]])
                            heapq.heappush(high_heap, (val, full_idx))
                            if len(high_heap) > n_keep:
                                heapq.heappop(high_heap)

                # reporting
                if count_low:
                    file.warning('%i values are lower than the valid minimum (%.2E %s).',
                                 count_low, valid_min, units)
                if count_high:
                    file.warning('%i values are higher than the valid maximum (%.2E %s).',
                                 count_high, valid_max, units)

                def describe(v, idx):
                    date = netCDF4.num2date(time_var[idx[0]], time_units, time_calendar)
                    parts = ['date: %s' % date]
                    if (lat_vals is not None and lon_vals is not None
                            and idx[-2] < len(lat_vals) and idx[-1] < len(lon_vals)):
                        parts.append('lat/lon: %4.2f/%4.2f' % (lat_vals[idx[-2]], lon_vals[idx[-1]]))
                    else:
                        parts.append('lat/lon: n/a')
                    if not file.is_2d:
                        parts.append('level: %s' % (idx[-3] + 1))
                    parts.append('value: %E %s' % (v, units))
                    return ', '.join(parts)

                if count_low:
                    file.warning('%i lowest values are :', min(n_keep, count_low))
                    # low_heap stores negated values; sorting them descending yields
                    # the original values in ascending order (lowest first)
                    for v, idx in sorted(low_heap, key=lambda x: x[0], reverse=True)[:n_keep]:
                        try:
                            file.warning('%s', describe(-v, idx))
                        except (AttributeError, OverflowError, TypeError, ValueError):
                            file.warning('index: %s, value: %E %s (date/coordinates unavailable)',
                                         idx, -v, units)

                if count_high:
                    file.warning('%i highest values are :', min(n_keep, count_high))
                    for v, idx in sorted(high_heap, key=lambda x: x[0], reverse=True)[:n_keep]:
                        try:
                            file.warning('%s', describe(v, idx))
                        except (AttributeError, OverflowError, TypeError, ValueError):
                            file.warning('index: %s, value: %E %s (date/coordinates unavailable)',
                                         idx, v, units)

                if not count_low and not count_high:
                    file.info('Values are within valid range (%.2E to %.2E).', valid_min, valid_max)

            else:
                file.warning('No min and/or max definition found for variable "%s" in protocol. Skipping test.',
                             file.variable_name)

import numpy as np
from isimip_qc.config import settings
from isimip_qc.fixes import fix_set_variable_attr


def check_depth_variable(file):
    if file.is_3d:
        depth = file.dataset.variables.get(file.dim_vertical)
        depth_definition = settings.DEFINITIONS['dimensions'].get('depth')

        # check if vertical dimension ha a variable associated
        if depth is None and file.dim_vertical:
            file.error('Found a vertical dimension (%s) but no variable linked to it. Introduce "depth" as variable also.', file.dim_vertical)
            depth = file.dataset.variables.get(file.dim_vertical)

        # check for definition in protocol for "depth" variable
        if not depth_definition:
            file.error('No definition for variable "depth" in protocol.')

        # do checks of definition and vertical variable were found
        if depth and depth_definition:
            # check dtype
            dtypes = ['float32', 'float64']
            if depth.dtype not in dtypes:
                file.warn('depth.dtype="%s" should be in %s.', depth.dtype, dtypes)

            # check axis
            axis = depth_definition.get('axis')
            try:
                if depth.axis != axis:
                    file.warn('Attribute depth.axis="%s" should be "%s".', depth.axis, axis, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, file.dim_vertical, 'axis', axis)
                    })
            except AttributeError:
                file.warn('Attribute depth.axis is missing. Should be "%s".', axis, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, file.dim_vertical, 'axis', axis)
                })

            # check standard_name
            standard_name = depth_definition.get('standard_name')
            try:
                if depth.standard_name != standard_name:
                    file.warn('Attribute depth.standard_name="%s" should be "%s".', depth.standard_name, standard_name, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, file.dim_vertical, 'standard_name', standard_name)
                    })
            except AttributeError:
                file.warn('Attribute depth.standard_name is missing. Should be "%s".', standard_name, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, file.dim_vertical, 'standard_name', standard_name)
                })

            # check long_name
            long_name = depth_definition.get('long_name')
            try:
                if depth.long_name != long_name:
                    file.warn('Attribute depth.long_name="%s". Should be "%s".', depth.long_name, long_name, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, file.dim_vertical, 'long_name', long_name)
                    })
            except AttributeError:
                file.warn('Attribute depth.long_name is missing. Should be "%s".', long_name, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, file.dim_vertical, 'long_name', long_name)
                })

            # check units
            units = depth_definition.get('units')
            try:
                if depth.units != units:
                    file.warn('Depth units="%s" should be "%s".', depth.units, units)
            except AttributeError:
                file.warn('Depth units are missing. Should be "%s".', units)

            # check direction of depth dimension
            depth_first = file.dataset.variables.get(file.dim_vertical)[0]
            depth_last = file.dataset.variables.get(file.dim_vertical)[-1]

            if depth_first > depth_last:
                file.warn('Depths in wrong order. Should increase with depth . (found %s to %s)', depth_first, depth_last)
            else:
                file.info('Depths order looks good (positive down).')

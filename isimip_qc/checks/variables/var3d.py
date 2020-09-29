import numpy as np
from isimip_qc.config import settings
from isimip_qc.fixes import fix_set_variable_attr


def check_3d_variable(file):
    if file.is_3d:
        var3d = file.dataset.variables.get(file.dim_vertical)
        var3d_definition = settings.DEFINITIONS['dimensions'].get(file.dim_vertical)

        # check if vertical dimension ha a variable associated
        if var3d is None and file.dim_vertical:
            file.error('Found dimension (%s) but no variable linked to it. Introduce "%s" as variable also.', file.dim_vertical, file.dim_vertical)

        # check for definition in protocol for 3d variable
        if not var3d_definition:
            file.error('No definition for variable "%s" in protocol.', file.dim_vertical)

        # do checks of definition and vertical variable were found
        if var3d and var3d_definition:
            # check dtype
            dtypes = ['float32', 'float64']
            if var3d.dtype not in dtypes:
                file.warn('%s.datatype="%s" should be in %s.', file.dim_vertical, var3d.dtype, dtypes)

            # check axis
            axis = var3d_definition.get('axis')
            try:
                if var3d.axis != axis:
                    file.warn('Attribute %s.axis="%s" should be "%s".', file.dim_vertical, var3d.axis, axis, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, file.dim_vertical, 'axis', axis)
                    })
            except AttributeError:
                file.warn('Attribute %s.axis is missing. Should be "%s".', file.dim_vertical, axis, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, file.dim_vertical, 'axis', axis)
                })

            # check standard_name
            standard_name = var3d_definition.get('standard_name')
            try:
                if var3d.standard_name != standard_name:
                    file.warn('Attribute %s.standard_name="%s" should be "%s".', file.dim_vertical, var3d.standard_name, standard_name, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, file.dim_vertical, 'standard_name', standard_name)
                    })
            except AttributeError:
                file.warn('Attribute %s.standard_name is missing. Should be "%s".', file.dim_vertical, standard_name, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, file.dim_vertical, 'standard_name', standard_name)
                })

            # check long_name
            long_name = var3d_definition.get('long_name')
            try:
                if var3d.long_name != long_name:
                    file.warn('Attribute %s.long_name="%s". Should be "%s".', file.dim_vertical, var3d.long_name, long_name, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, file.dim_vertical, 'long_name', long_name)
                    })
            except AttributeError:
                file.warn('Attribute %s.long_name is missing. Should be "%s".', file.dim_vertical, long_name, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, file.dim_vertical, 'long_name', long_name)
                })

            # check units
            units = var3d_definition.get('units')
            try:
                if var3d.units != units:
                    file.warn('%s.units="%s" should be "%s".', file.dim_vertical, var3d.units, units)
            except AttributeError:
                file.warn('"%s" units are missing. Should be "%s".', file.dim_vertical, units)

            if file.dim_vertical == 'depth':
                # check direction of depth dimension
                depth_first = file.dataset.variables.get(file.dim_vertical)[0]
                depth_last = file.dataset.variables.get(file.dim_vertical)[-1]

                if depth_first > depth_last:
                    file.warn('Depths in wrong order. Should increase with depth . (found %s to %s)', depth_first, depth_last)
                else:
                    file.info('Depths order looks good (positive down).')

import numpy as np
from isimip_qc.config import settings
from isimip_qc.fixes import fix_set_variable_attr


def check_depth_variable(file):
    if file.is_3d:
        depth = file.dataset.variables.get('depth')
        depth_definition = settings.DEFINITIONS['dimensions'].get('depth')

        if depth is None:
            file.error('Variable depth is missing.')
        elif not depth_definition:
            file.error('Definition for variable depth is missing.')
        else:
            # check dtype
            dtypes = ['float32', 'float64']
            if depth.dtype not in dtypes:
                file.warn('depth.dtype="%s" should be in %s.', depth.dtype, dtypes)

            # check shape
            size = depth_definition.get('size')
            if depth.shape != (size, ):
                file.error('depth.shape=%s must be (%s, ).', depth.shape, size)

            # check axis
            axis = depth_definition.get('axis')
            try:
                if depth.axis != axis:
                    file.warn('Attribute depth.axis="%s" should be "%s".', depth.axis, axis, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, 'depth', 'axis', axis)
                    })
            except AttributeError:
                file.warn('Attribute depth.axis is missing. Should be "%s".', axis, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'depth', 'axis', axis)
                })

            # check standard_name
            standard_name = depth_definition.get('standard_name')
            try:
                if depth.standard_name != standard_name:
                    file.warn('Attribute depth.standard_name="%s" should be "%s".', depth.standard_name, standard_name)
            except AttributeError:
                file.warn('Attribute depth.standard_name is missing. Should be "%s".', standard_name)

            # check long_name
            long_names = depth_definition.get('long_names', [])
            try:
                if depth.long_name not in long_names:
                    file.warn('Attribute depth.long_name="%s" should be in %s.', depth.long_name, long_names)
            except AttributeError:
                file.warn('Attribute depth.long_name is missing. Should be "%s".', long_names[0])

            # check units
            units = depth_definition.get('units')
            try:
                if depth.units != units:
                    file.warn('Attribute depth.units="%s" should be "%s".', depth.units, units)
            except AttributeError:
                file.warn('Attribute depth.units is missing. Should be "%s".', units)

            depth_first = file.dataset.variables.get('depth')[0]
            depth_last = file.dataset.variables.get('depth')[-1]
            if depth_first > depth_last:
                file.warn('Depths in wrong order. Should increase with depth . (found %s to %s)', depth_first, depth_last)
            else:
                file.info('Depths order looks good (positive down).')

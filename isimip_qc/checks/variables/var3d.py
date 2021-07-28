import numpy as np
from isimip_qc.config import settings
from isimip_qc.fixes import fix_set_variable_attr


def check_3d_variable(file):

    def check_attribute(var3d, attr_type, attribute):
        try:
            var3d_attr = getattr(var3d, attr_type)
            if var3d_attr != attribute:
                file.warn('Attribute %s.%s="%s". Should be "%s".', var3d.name, attr_type, var3d_attr, attribute, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, var3d.name, attr_type, attribute)
                })
        except AttributeError:
            file.warn('Attribute %s.%s is missing. Should be "%s".', var3d.name, attr_type, attribute, fix={
                'func': fix_set_variable_attr,
                'args': (file, var3d.name, attr_type, attribute)
            })

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

            # check attributes
            for attribute in ['axis', 'standard_name', 'long_name', 'units']:
                if settings.SIMULATION_ROUND in ['ISIMIP2a', 'ISIMIP2b'] and var3d.name == 'levlak':
                    continue
                attr_definition = var3d_definition.get(attribute)
                check_attribute(var3d, attribute, attr_definition)

            if file.dim_vertical == 'depth':
                # check direction of depth dimension
                depth_first = file.dataset.variables.get(file.dim_vertical)[0]
                depth_last = file.dataset.variables.get(file.dim_vertical)[-1]

                if depth_first > depth_last:
                    file.warn('Depths in wrong order. Should increase with depth . (found %s to %s)', depth_first, depth_last)
                else:
                    file.info('Depths order looks good (positive down).')

            # for lakes sector
            if file.dim_vertical == 'levlak':
                if len(file.dataset.variables.get(file.dim_vertical).shape) == 1:
                    levlak_first = file.dataset.variables.get(file.dim_vertical)[0]
                    levlak_last = file.dataset.variables.get(file.dim_vertical)[-1]

                    if levlak_first > levlak_last:
                        file.warn('"levlak" in wrong order. Should increase with depth . (found %s to %s)', levlak_first, levlak_last)
                    else:
                        file.info('"levlak" order looks good (positive down).')

                if settings.SIMULATION_ROUND not in ['ISIMIP2a', 'ISIMIP2b']:

                    depth_file = file.dataset.variables.get('depth')

                    if depth_file is None:
                        file.warn('Variable "depth" not found. Introduce layer vertical center depths in [m] as depth(levlak,lat,lon) or depth(time,levlak,lat,lon)')
                    else:
                        if len(depth_file.dimensions) == 4:
                            if depth_file.dimensions[1] != 'levlak':
                                file.error('Time varying "depth" variable has no dependency for "levlak" level index. Expecting: depth(time,levlak,lat,lon)')
                        elif len(depth_file.dimensions) == 3:
                            if depth_file.dimensions[0] != 'levlak':
                                file.error('Fixed-time "depth" variable has no dependency for "levlak" level index. Expecting: depth(levlak,lat,lon)')
                        elif len(depth_file.dimensions) == 1:
                            if depth_file.dimensions[0] != 'levlak':
                                file.error('Globally fixed "depth" variable has no dependency for "levlak" level index. Expecting: depth(levlak)')
                        else:
                            file.error('No proper "levlak" dependency found in "depth" variable.')

                        depth_definition = settings.DEFINITIONS['dimensions'].get('depth')

                        if depth_definition is None:
                            file.warn('Dimension "depth" is not yet defined in protocol. Skipping attribute checks for "depth".')
                        else:
                            for attribute in ['axis', 'standard_name', 'long_name', 'units']:
                                attr_definition = depth_definition.get(attribute)
                                check_attribute(depth_file, attribute, attr_definition)

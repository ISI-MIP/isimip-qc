from isimip_qc.config import settings
from isimip_qc.fixes import fix_set_variable_attr

from ...exceptions import FileWarning


def check_3d_variable(file):
    def check_attribute(var3d, attr_type, attribute):
        try:
            var3d_attr = getattr(var3d, attr_type)
        except AttributeError:
            file.warn('Attribute %s.%s is missing. Should be "%s".', var3d.name, attr_type, attribute, fix={
                'func': fix_set_variable_attr,
                'args': (file, var3d.name, attr_type, attribute)
            })
            return

        if var3d_attr != attribute:
            file.warn('Attribute %s.%s="%s". Should be "%s".', var3d.name, attr_type, var3d_attr, attribute, fix={
                'func': fix_set_variable_attr,
                'args': (file, var3d.name, attr_type, attribute)
            })

    if file.is_3d:

        var3d = file.dataset.variables.get(file.dim_vertical)
        var3d_definition = settings.DEFINITIONS['dimensions'].get(file.dim_vertical)

        # check if vertical dimension ha a variable associated
        if var3d is None and file.dim_vertical:
            file.error('Found dimension (%s) but no variable linked to it. Introduce "%s" as variable also.',
                       file.dim_vertical, file.dim_vertical)

        # check for definition in protocol for 3d variable
        if not var3d_definition:
            file.error('No definition for variable "%s" in protocol.', file.dim_vertical)

        # do checks of definition and vertical variable were found
        if var3d and var3d_definition:
            # check dtype
            dtypes = ['float32', 'float64']
            if var3d.name == 'bins':
                # bins should be integer types in addition to numeric floats
                allowed = dtypes + ['int16', 'int32']
            else:
                allowed = dtypes

            if var3d.dtype not in allowed:
                file.warn('%s.datatype="%s" should be in %s.', file.dim_vertical, var3d.dtype, allowed)

            # check attributes
            sim_round = settings.SIMULATION_ROUND
            for attribute in ('axis', 'standard_name', 'long_name', 'units'):
                if sim_round in ('ISIMIP2a', 'ISIMIP2b') and var3d.name == 'levlak':
                    continue
                attr_definition = var3d_definition.get(attribute)
                # only check attributes that are defined in the protocol
                if attr_definition is None:
                    continue
                check_attribute(var3d, attribute, attr_definition)

            # check direction of depth dimension
            # check direction of depth dimension (read only first and last value)
            try:
                depth_first = var3d[0].item()
                depth_last = var3d[-1].item()
            except Exception:
                # fallback to reading full array if slicing fails
                vals = var3d[:]
                depth_first = vals[0]
                depth_last = vals[-1]

            if var3d.shape[0] > 1 and depth_first > depth_last:
                file.warn('"%s" in wrong order. Should increase with depth. (found %s to %s)',
                          file.dim_vertical, depth_first, depth_last)
            else:
                file.info('Depths or layers order looks good (positive down).')

            if file.dim_vertical == 'levlak' and settings.SIMULATION_ROUND not in ['ISIMIP2a', 'ISIMIP2b']:

                depth_file = file.dataset.variables.get('depth')

                if depth_file is None:
                    file.warn(
                        'Variable "depth" not found. Introduce layer vertical center'
                        ' depths in [m] as depth(levlak,lat,lon) or depth(time,levlak,lat,lon)'
                    )
                else:
                    ndims = len(depth_file.dimensions)
                    if ndims == 4:
                        if depth_file.dimensions[1] != 'levlak':
                            file.error('Time varying "depth" variable has no dependency for "levlak"'
                                       ' level index. Expecting: depth(time,levlak,lat,lon)')
                    elif ndims == 3:
                        if depth_file.dimensions[0] != 'levlak':
                            file.error('Fixed-time "depth" variable has no dependency for "levlak"'
                                       ' level index. Expecting: depth(levlak,lat,lon)')
                    elif ndims == 1:
                        if depth_file.dimensions[0] != 'levlak':
                            file.error('Globally fixed "depth" variable has no dependency for "levlak"'
                                       ' level index. Expecting: depth(levlak)')
                    else:
                        file.error('No proper "levlak" dependency found in "depth" variable.')

                    depth_definition = settings.DEFINITIONS['dimensions'].get('depth')

                    if depth_definition is None:
                        file.warn('Dimension "depth" is not yet defined in protocol. Skipping'
                                  ' attribute checks for "depth".')
                    else:
                        for attribute in ('axis', 'standard_name', 'long_name', 'units'):
                            attr_definition = depth_definition.get(attribute)
                            if attr_definition is None:
                                continue
                            check_attribute(depth_file, attribute, attr_definition)

            # check if vertical bounds were defined
            if file.dim_vertical in ['depth', 'levlak']:
                try:
                    var3d_bnds = file.dataset.variables.get('depth').bounds
                    file.info('Vertical bounds "%s" found for "depth" variable', var3d_bnds)
                except AttributeError:
                    raise FileWarning(file,
                                      'No vertical boundaries defined for "depth" variable.'
                                      ' Consider adding depth_bnds(%s, bnds). '
                                      ' See examples at https://bit.ly/ncdf-bounds', file.dim_vertical
                                      ) from None

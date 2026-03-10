from isimip_qc.config import settings

from ..exceptions import FileCritical


def check_3d(file):
    """Validate a 3D variable inside a file and set metadata flags on the
    file object.

    This function builds the variable name from `file.specifiers`, verifies
    the variable exists in the NetCDF dataset, reads its dimensionality and
    checks it against the definition in settings.DEFINITIONS.
    """

    # Build canonical variable name from specifiers in a predictable order.
    base_var = file.specifiers.get('variable')
    if not base_var:
        raise FileCritical(file, 'No base variable specified in file specifiers.')

    suffix_keys = ('crop', 'irrigation', 'species', 'pt', 'pool', 'pft')
    parts = [base_var] + [file.specifiers.get(k) for k in suffix_keys if file.specifiers.get(k)]
    file.variable_name = '-'.join(parts)

    # Defensively retrieve the variable and its dimensions.
    variable = file.dataset.variables.get(file.variable_name)
    if variable is None:
        raise FileCritical(
            file,
            'Variable "%s" from file name not found inside the file! Check NetCDF header. Stopping tool!',
            file.variable_name,
        )

    file.dim_len = len(variable.dimensions)

    # Lookup variable definition (use base name without suffixes).
    definition = settings.DEFINITIONS.get('variable', {}).get(base_var)
    if definition is None:
        raise FileCritical(
            file,
            'Variable %s not defined for sector %s. Skipping...',
            file.variable_name,
            settings.SECTOR,
        )

    # Number of expected dimensions
    if 'dimensions' in definition:
        definition_dim_len = len(definition['dimensions'])
        dims_expected = str(definition['dimensions']).replace("'", '')
    else:
        definition_dim_len = 3
        dims_expected = '[time, lat, lon]'

    # detect 2d or 3d data: here we treat [time, lat, lon] as 3 dims (2D data),
    # and an extra vertical dimension yields 4 dims (3D data).
    if file.specifiers.get('time_step') == 'fixed':
        file.is_time_fixed = True
        if file.dim_len > 2:
            raise FileCritical(
                file,
                'File has fixed data but more than 2 dimensions. Remove "time" dimension if present.',
            )
        return
    elif file.dim_len == 3:
        file.is_2d = True
    elif file.dim_len == 4:
        file.is_3d = True
        # Expect ordering [time, vertical, lat, lon]. If the second dimension is
        # one of time/lat/lon, find the first non-spatial/time dimension and
        # report an error about ordering.
        if variable.dimensions[1] in ('time', 'lat', 'lon'):
            pos = next((i for i, d in enumerate(variable.dimensions) if d not in ('time', 'lat', 'lon')), None)
            if pos is None:
                raise FileCritical(
                    file,
                    'Unable to determine vertical dimension for %s.',
                    file.variable_name,
                )
            file.dim_vertical = variable.dimensions[pos]
            raise FileCritical(
                file,
                'Variable "%s" has time/lat/lon as second dependency. Dependency order must be [time, %s, lat, lon]. '
                ' "time" is always first.',
                file.variable_name,
                variable.dimensions[pos],
            )
        else:
            file.dim_vertical = variable.dimensions[1]

    if file.dim_len != definition_dim_len and file.specifiers.get('time_step') != 'fixed':
        raise FileCritical(
            file,
            'Dimension missing (%s found, %s expected). Declare variable as %s%s.',
            file.dim_len,
            definition_dim_len,
            file.variable_name,
            dims_expected,
        )

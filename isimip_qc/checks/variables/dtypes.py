import numpy as np

from isimip_qc.config import settings

# the protocol names a few types differently than numpy does
dtype_aliases = {
    'char': 'S1',
    'string': 'O',
}


def check_dimension_variable_dtypes(file):
    # coordinate variables (named after their dimension) must be stored as one
    # of the data types the protocol lists under "dtypes"; protocol versions
    # predating the dtypes integration carry no such list, so their dimension
    # variables stay unchecked instead of crashing the run
    for name, definition in settings.DEFINITIONS.get('dimensions', {}).items():
        variable = file.dataset.variables.get(name)
        if variable is None:
            continue

        dtypes = (definition or {}).get('dtypes')
        if not dtypes:
            file.debug('Protocol defines no "dtypes" for "%s". Skipping data type check.', name)
            continue

        allowed = []
        for dtype in dtypes:
            try:
                allowed.append(np.dtype(dtype_aliases.get(dtype, dtype)))
            except TypeError:
                # a data type we don't know can't match; keep the others
                file.debug('Unknown data type "%s" defined for "%s".', dtype, name)

        # netCDF4 reports string variables as the plain str type instead of a
        # numpy dtype; they are read back as object arrays
        var_dtype = np.dtype('O') if variable.dtype is str else variable.dtype

        if var_dtype not in allowed:
            file.warning('Data type of "%s" is "%s". Should be one of %s.',
                         name, var_dtype, dtypes)
        else:
            file.info('Data type of "%s" looks good (%s).', name, var_dtype)

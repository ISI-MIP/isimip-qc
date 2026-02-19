from ..fixes import fix_remove_variable_attr, fix_rename_dimension, fix_rename_variable, fix_rename_variable_attr

# Attributes allowed by the protocol (kept as a set for fast membership tests)
_ALLOWED_VARIABLE_ATTRS = {
    'axis', 'standard_name', 'long_name', 'calendar', 'missing_value',
    'units', 'comment', 'enteric_infection', 'description', 'unit_conversion_info',
    'positive', 'bounds', 'classes', 'pft', 'fuelclass'
}

# Attributes that should be ignored from removal checks
_ATTR_EXCEPTIONS = {'_FillValue'}


def check_data_model(file):
    '''
    File must use the NetCDF4 classic data model
    '''
    if file.dataset.data_model != 'NETCDF4_CLASSIC':
        file.warn('Data model is %s (not NETCDF4_CLASSIC).', file.dataset.data_model, fix_datamodel=True)
    else:
        file.info('Data model looks good (%s).', file.dataset.data_model)


def check_zip(file):
    '''
    Data variables must be compressed with at least compression level 4. Skip check for dimension variables.
    '''

    variable = file.dataset.variables.get(file.variable_name)
    if variable is None:
        file.warn('Variable "%s" not found for compression check.', file.variable_name)
        return

    try:
        filters = variable.filters()
    except AttributeError:
        filters = None

    if not filters:
        file.warn('Variable "%s" is not compressed.', file.variable_name, fix_datamodel=True)
        return

    zlib = filters.get('zlib')
    complevel = filters.get('complevel')
    if zlib:
        if complevel < 4:
            file.warn('Variable "%s" compression level is "%s". Should be >= 5.',
                      file.variable_name, complevel, fix_datamodel=True)
        else:
            file.info('Variable "%s" compression level looks good (%s)', file.variable_name, complevel)
    else:
        file.warn('Variable "%s" is not compressed.', file.variable_name, fix_datamodel=True)


def check_lower_case(file):
    '''
    Internal names of dimensions and variables are lowercase.
    '''

    for dimension_name in file.dataset.dimensions:
        if not dimension_name.islower():
            file.warn('Dimension "%s" is not lower case.', dimension_name, fix={
                'func': fix_rename_dimension,
                'args': (file, dimension_name)
            })

    for variable_name, variable in file.dataset.variables.items():
        if not variable_name.islower():
            file.warn('Variable "%s" is not lower case.', variable_name, fix={
                'func': fix_rename_variable,
                'args': (file, variable_name)
            })

        # Use NetCDF4's ncattrs() to get user-defined attribute names reliably
        try:
            attrs = variable.ncattrs()
        except AttributeError:
            # Fallback to __dict__ if ncattrs isn't available
            attrs = list(variable.__dict__.keys())

        for attr in attrs:
            if attr in _ATTR_EXCEPTIONS:
                continue

            if attr not in _ALLOWED_VARIABLE_ATTRS:
                file.warn('Attribute "%s" for variable "%s" is not needed.', attr, variable_name, fix={
                    'func': fix_remove_variable_attr,
                    'args': (file, variable_name, attr)
                })
            else:
                if not attr.islower():
                    file.warn('Attribute "%s" for variable "%s" is not lower case.', attr, variable_name, fix={
                        'func': fix_rename_variable_attr,
                        'args': (file, variable_name, attr)
                    })

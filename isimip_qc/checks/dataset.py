def check_data_model(file):
    '''
    File must use the NetCDF4 classic data model
    '''
    if file.dataset.data_model != 'NETCDF4_CLASSIC':
        file.warn('Data model is %s (not NETCDF4_CLASSIC).', file.dataset.data_model)


def check_zip(file):
    '''
    Data variables must be compressed with at least compression level 4. Skip check for dimension variables.
    '''
    for variable_name, variable in file.dataset.variables.items():
        if variable_name not in ['time', 'lat', 'lon']:
            zlib = variable.filters().get('zlib')
            if zlib:
                complevel = variable.filters().get('complevel')
                if complevel < 1:
                    file.warn('%s._DeflateLevel=%s should be > 4.', variable_name, complevel)
            else:
                file.warn('%s is not compressed.', variable_name)


def check_lower_case(file):
    '''
    Internal names of dimensions and variables are lowercase.
    '''

    for dimension_name in file.dataset.dimensions:
        if not dimension_name.islower():
            file.warn('Dimension "%s" is not lower case.', dimension_name)

    for variable_name, variable in file.dataset.variables.items():
        if not variable_name.islower():
            file.warn('Variable "%s" is not lower case.', variable_name)

        for attr in variable.__dict__:
            if attr not in ['_FillValue']:
                if not attr.islower():
                    file.warn('Attribute "%s.%s" is not lower case.', variable_name, attr, fix={
                        'func': fix_variable_attr,
                        'args': (file, variable_name, attr)
                    })
                if attr not in ['axis', 'standard_name', 'long_name', 'calendar', 'missing_value', 'units']:
                    file.warn('Attribute "%s.%s" is not needed. Consider removing it.', variable_name, attr)


def fix_variable_attr(file, variable_name, attr_name):
    file.info('Renaming "%s.%s" -> "%s.%s".', variable_name, attr_name, variable_name, attr_name.lower())
    file.dataset.variables[variable_name].renameAttribute(attr_name, attr_name.lower())

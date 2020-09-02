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
                    file.warn('Variable %s._DeflateLevel=%s should be > 4.', variable_name, complevel)
                else:
                    file.info('Compression level for variable "%s" looks good (%s)', variable_name, complevel)
            else:
                file.warn('Variable "%s" is not compressed.', variable_name)


def check_lower_case(file):
    '''
    Internal names of dimensions and variables are lowercase.
    '''

    for dimension_name in file.dataset.dimensions:
        if not dimension_name.islower():
            file.warn('Dimension "%s" is not lower case.', dimension_name, fix={
                        'func': fix_rename_dim,
                        'args': (file, dimension_name)
                    })

    for variable_name, variable in file.dataset.variables.items():
        if not variable_name.islower():
            file.warn('Variable "%s" is not lower case.', variable_name, fix={
                        'func': fix_rename_var,
                        'args': (file, variable_name)
                    })

        for attr in variable.__dict__:
            if attr not in ['_FillValue']:
                if not attr.islower():
                    file.warn('Attribute "%s.%s" is not lower case.', variable_name, attr, fix={
                        'func': fix_rename_attr,
                        'args': (file, variable_name, attr)
                    })
                if attr not in ['axis', 'standard_name', 'long_name', 'calendar', 'missing_value', 'units']:
                    file.warn('Attribute "%s.%s" is not needed.', variable_name, attr, fix={
                        'func': fix_remove_attr,
                        'args': (file, variable_name, attr)
                    })


def fix_rename_dim(file, dimension_name):
    file.info('Renaming dimension "%s" -> "%s".', dimension_name, dimension_name.lower())
    file.dataset.dimensions[dimension_name].renameDimension(dimension_name, dimension_name.lower())

def fix_rename_var(file, variable_name):
    file.info('Renaming variable "%s" -> "%s".', variable_name, variable_name.lower())
    file.dataset.variables[variable_name].renameVariable(variable_name, variable_name.lower())

def fix_rename_attr(file, variable_name, attr_name):
    file.info('Renaming "%s.%s" -> "%s.%s".', variable_name, attr_name, variable_name, attr_name.lower())
    file.dataset.variables[variable_name].renameAttribute(attr_name, attr_name.lower())

def fix_remove_attr(file, variable_name, attr_name):
    file.info('Removing attribute "%s.%s"', variable_name, attr_name)
    file.dataset.variables[variable_name].delncattr(attr_name)

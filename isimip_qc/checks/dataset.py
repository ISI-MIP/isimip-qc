from ..fixes import (fix_remove_variable_attr, fix_rename_dimension,
                     fix_rename_variable, fix_rename_variable_attr)


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
                        'func': fix_rename_dimension,
                        'args': (file, dimension_name)
                    })

    for variable_name, variable in file.dataset.variables.items():
        if not variable_name.islower():
            file.warn('Variable "%s" is not lower case.', variable_name, fix={
                        'func': fix_rename_variable,
                        'args': (file, variable_name)
                    })

        for attr in variable.__dict__:
            if attr not in ['_FillValue']:
                if attr not in ['axis', 'standard_name', 'long_name', 'calendar', 'missing_value', 'units']:
                    file.warn('Attribute "%s.%s" is not needed.', variable_name, attr, fix={
                        'func': fix_remove_variable_attr,
                        'args': (file, variable_name, attr)
                    })
                elif not attr.islower():
                    file.warn('Attribute "%s.%s" is not lower case.', variable_name, attr, fix={
                        'func': fix_rename_variable_attr,
                        'args': (file, variable_name, attr)
                    })

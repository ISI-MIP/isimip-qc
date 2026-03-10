def fix_rename_dimension(file, dimension_name, new_dimension_name):
    file.info('Renaming dimension "%s" -> "%s".', dimension_name, new_dimension_name)
    if dimension_name in file.dataset.dimensions:
        file.dataset.renameDimension(dimension_name, new_dimension_name)
    else:
        file.error('Cannot apply fix: dimension "%s" not found.', dimension_name)


def fix_rename_variable(file, variable_name, new_variable_name):
    file.info('Renaming variable "%s" -> "%s".', variable_name, new_variable_name)
    if variable_name in file.dataset.variables:
        file.dataset.renameVariable(variable_name, new_variable_name)
    else:
        file.error('Cannot apply fix: variable "%s" not found.', variable_name)


def fix_set_variable_attr(file, variable_name, attr_name, value):
    file.info('Setting attribute "%s.%s=%s"', variable_name, attr_name, value)
    if variable_name in file.dataset.variables:
        file.dataset.variables[variable_name].setncattr(attr_name, value)
    else:
        file.error('Cannot apply fix: variable "%s" not found.', variable_name)


def fix_rename_variable_attr(file, variable_name, attr_name, new_attr_name):
    file.info('Renaming attribute "%s.%s" -> "%s.%s".', variable_name, attr_name, variable_name, new_attr_name)
    if variable_name in file.dataset.variables:
        file.dataset.variables[variable_name].renameAttribute(attr_name, new_attr_name)
    else:
        file.error('Cannot apply fix: variable "%s" not found.', variable_name)


def fix_remove_variable_attr(file, variable_name, attr_name):
    file.info('Removing attribute "%s.%s"', variable_name, attr_name)
    if variable_name in file.dataset.variables:
        file.dataset.variables[variable_name].delncattr(attr_name)
    else:
        file.error('Cannot apply fix: variable "%s" not found.', variable_name)


def fix_set_global_attr(file, attr_name, value):
    file.info('Setting global attribute "%s=%s"', attr_name, value)
    file.dataset.setncattr(attr_name, value)


def fix_rename_global_attr(file, attr_name, new_attr_name):
    file.info('Renaming global attribute "%s" -> "%s".', attr_name, new_attr_name)
    if attr_name in file.dataset.ncattrs():
        file.dataset.renameAttribute(attr_name, new_attr_name)
    else:
        file.error('Cannot apply fix: global attribute "%s" not found.', attr_name)


def fix_remove_global_attr(file, attr_name):
    file.info('Removing global attribute "%s"', attr_name)
    if attr_name in file.dataset.ncattrs():
        file.dataset.delncattr(attr_name)
    else:
        file.error('Cannot apply fix: global attribute "%s" not found.', attr_name)

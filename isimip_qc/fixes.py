def fix_rename_dimension(file, dimension_name, new_dimension_name):
    file.info('Renaming dimension "%s" -> "%s".', dimension_name, new_dimension_name)
    file.dataset.dimensions[dimension_name].renameDimension(dimension_name, new_dimension_name)


def fix_rename_variable(file, variable_name, new_variable_name):
    file.info('Renaming variable "%s" -> "%s".', variable_name, new_variable_name)
    file.dataset.variables[variable_name].renameVariable(variable_name, new_variable_name)


def fix_set_variable_attr(file, variable_name, attr_name, value):
    file.info('Setting attribute "%s.%s=%s"', variable_name, attr_name, value)
    file.dataset.variables[variable_name].setncattr(attr_name, value)


def fix_rename_variable_attr(file, variable_name, attr_name, new_attr_name):
    file.info('Renaming attribute "%s.%s" -> "%s.%s".', variable_name, attr_name, variable_name, new_attr_name)
    file.dataset.variables[variable_name].renameAttribute(attr_name, new_attr_name)


def fix_remove_variable_attr(file, variable_name, attr_name):
    file.info('Removing attribute "%s.%s"', variable_name, attr_name)
    file.dataset.variables[variable_name].delncattr(attr_name)


def fix_set_global_attr(file, attr_name, value):
    file.info('Setting global attribute "%s=%s"', attr_name, value)
    file.dataset.setncattr(attr_name, value)


def fix_rename_global_attr(file, attr_name, new_attr_name):
    file.info('Renaming global attribute "%s" -> "%s".', attr_name, new_attr_name)
    file.dataset.renameAttribute(attr_name, new_attr_name)


def fix_remove_global_attr(file, attr_name):
    file.info('Removing global attribute "%s"', attr_name)
    file.dataset.delncattr(attr_name)

def _ds(file):
    return file.dataset


def _get_var(ds, file, variable_name):
    v = ds.variables.get(variable_name)
    if v is None:
        file.error('Cannot apply fix: variable "%s" not found.', variable_name)
    return v


def _get_dim(ds, file, dimension_name):
    d = ds.dimensions.get(dimension_name)
    if d is None:
        file.error('Cannot apply fix: dimension "%s" not found.', dimension_name)
    return d


def fix_rename_dimension(file, dimension_name, new_dimension_name):
    file.info('Renaming dimension "%s" -> "%s".', dimension_name, new_dimension_name)
    ds = _ds(file)
    d = _get_dim(ds, file, dimension_name)
    if d is None:
        return
    # netCDF4 dimensions expose a renameDimension method on the Dataset
    ds.renameDimension(dimension_name, new_dimension_name)


def fix_rename_variable(file, variable_name, new_variable_name):
    file.info('Renaming variable "%s" -> "%s".', variable_name, new_variable_name)
    ds = _ds(file)
    v = _get_var(ds, file, variable_name)
    if v is None:
        return
    # use the dataset-level helper if available
    try:
        ds.renameVariable(variable_name, new_variable_name)
    except Exception:
        # fallback to variable-level if dataset helper missing
        v.renameVariable(variable_name, new_variable_name)


def fix_set_variable_attr(file, variable_name, attr_name, value):
    file.info('Setting attribute "%s.%s=%s"', variable_name, attr_name, value)
    ds = _ds(file)
    v = _get_var(ds, file, variable_name)
    if v is None:
        return
    v.setncattr(attr_name, value)


def fix_rename_variable_attr(file, variable_name, attr_name, new_attr_name):
    file.info('Renaming attribute "%s.%s" -> "%s.%s".', variable_name, attr_name, variable_name, new_attr_name)
    ds = _ds(file)
    v = _get_var(ds, file, variable_name)
    if v is None:
        return
    try:
        v.renameAttribute(attr_name, new_attr_name)
    except Exception:
        # emulate rename by copying and deleting
        if hasattr(v, 'getncattr'):
            try:
                val = v.getncattr(attr_name)
                v.setncattr(new_attr_name, val)
                v.delncattr(attr_name)
            except Exception:
                file.error('Failed to rename attribute %s on %s', attr_name, variable_name)


def fix_remove_variable_attr(file, variable_name, attr_name):
    file.info('Removing attribute "%s.%s"', variable_name, attr_name)
    ds = _ds(file)
    v = _get_var(ds, file, variable_name)
    if v is None:
        return
    try:
        v.delncattr(attr_name)
    except Exception:
        file.error('Failed to remove attribute %s on %s', attr_name, variable_name)


def fix_set_global_attr(file, attr_name, value):
    file.info('Setting global attribute "%s=%s"', attr_name, value)
    ds = _ds(file)
    ds.setncattr(attr_name, value)


def fix_rename_global_attr(file, attr_name, new_attr_name):
    file.info('Renaming global attribute "%s" -> "%s".', attr_name, new_attr_name)
    ds = _ds(file)
    try:
        ds.renameAttribute(attr_name, new_attr_name)
    except Exception:
        # emulate via get/set/del
        try:
            val = ds.getncattr(attr_name)
            ds.setncattr(new_attr_name, val)
            ds.delncattr(attr_name)
        except Exception:
            file.error('Failed to rename global attribute %s', attr_name)


def fix_remove_global_attr(file, attr_name):
    file.info('Removing global attribute "%s"', attr_name)
    ds = _ds(file)
    try:
        ds.delncattr(attr_name)
    except Exception:
        file.error('Failed to remove global attribute %s', attr_name)

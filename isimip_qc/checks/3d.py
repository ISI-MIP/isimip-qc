def check_3d(file):
    crop = file.specifiers.get('crop')
    irrigation = file.specifiers.get('irrigation')
    pft = file.specifiers.get('pft')
    species = file.specifiers.get('species')

    file.variable_name = file.specifiers.get('variable')

    if crop:
        file.variable_name = file.variable_name + '-' + file.specifiers.get('crop')
    if irrigation:
        file.variable_name = file.variable_name + '-' + file.specifiers.get('irrigation')
    if pft:
        file.variable_name = file.variable_name + '-' + file.specifiers.get('pft')
    if species:
        file.variable_name = file.variable_name + '-' + file.specifiers.get('species')

    try:
        variable = file.dataset.variables.get(file.variable_name)
        if variable is None:
            file.critical('Variable "%s" from file name not found inside the file! Check NetCDF header.', file.variable_name)
    except AttributeError:
        file.critical('Variable "%s" from file name not found inside the file! Check NetCDF header.', file.variable_name)
        # abort further tests

    dim_len = len(variable.dimensions)

    # detect 2d or 3d data
    if dim_len == 3:
        file.is_2d = True
    elif dim_len == 4:
        file.is_3d = True
        if variable.dimensions[1] in ['time', 'lat', 'lon']:
            for pos in range(0, dim_len):
                if variable.dimensions[pos] not in ['time', 'lat', 'lon']:
                    break
            file.critical('Variable "%s" has "time", "lat" or "lon" as second dependeny. Depencency order must be [time, %s, lat, lon]. "time" is first always.', file.variable_name, variable.dimensions[pos])
            file.dim_vertical = variable.dimensions[pos]
        else:
            file.dim_vertical = variable.dimensions[1]

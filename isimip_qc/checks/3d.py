def check_3d(file):
    variable_name = file.specifiers.get('variable')
    variable = file.dataset.variables.get(variable_name)
    dim_len = len(variable.dimensions)

    # detect 2d or 3d data
    if dim_len == 3:
        file.is_2d = True
    elif dim_len == 4:
        file.is_3d = True
        file.dim_vertical = variable.dimensions[1]


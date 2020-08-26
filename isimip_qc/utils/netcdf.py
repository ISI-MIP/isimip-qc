from netCDF4 import Dataset


def open_dataset_read(file_path):
    return Dataset(file_path, 'r')


def open_dataset_write(file_path):
    return Dataset(file_path, 'r+')


def get_data_model(dataset):
    return dataset.data_model


def get_dimensions(dataset):
    dimensions = {}
    for dimension_name, dimension in dataset.dimensions.items():
        dimensions[dimension_name] = dimension.size

    return dimensions


def get_variables(dataset):
    variables = {}
    for variable_name, variable in dataset.variables.items():
        variables[variable_name] = variable.__dict__
        variables[variable_name]['dimensions'] = list(variable.dimensions)

    return variables


def get_global_attributes(dataset):
    return dataset.__dict__

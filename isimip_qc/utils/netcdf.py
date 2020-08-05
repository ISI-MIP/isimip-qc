from netCDF4 import Dataset


def open_dataset(file_path):
    return Dataset(file_path, 'r')

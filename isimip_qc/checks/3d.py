from isimip_qc.config import settings

from ..exceptions import FileCritical, FileWarning


def check_3d(file):
    crop = file.specifiers.get('crop')
    irrigation = file.specifiers.get('irrigation')
    pft = file.specifiers.get('pft')
    species = file.specifiers.get('species')
    pool = file.specifiers.get('pool')
    pt = file.specifiers.get('pt')

    file.variable_name = file.specifiers.get('variable')

    if crop:
        file.variable_name = file.variable_name + '-' + file.specifiers.get('crop')
    if irrigation:
        file.variable_name = file.variable_name + '-' + file.specifiers.get('irrigation')
    if species:
        file.variable_name = file.variable_name + '-' + file.specifiers.get('species')
    if pt:
        file.variable_name = file.variable_name + '-' + file.specifiers.get('pt')
    if pool:
        file.variable_name = file.variable_name + '-' + file.specifiers.get('pool')
    if pft:
        file.variable_name = file.variable_name + '-' + file.specifiers.get('pft')

    try:
        variable = file.dataset.variables.get(file.variable_name)
        if variable is None:
            file.critical('Variable "%s" from file name not found inside the file! Check NetCDF header. Stopping tool!',
                          file.variable_name)
            raise SystemExit(1)
    except AttributeError as e:
        file.critical('Variable "%s" from file name not found inside the file! Check NetCDF header. Stopping tool!',
                      file.variable_name)
        raise SystemExit(1) from e

    definition = settings.DEFINITIONS.get('variable', {}).get(file.specifiers.get('variable'))
    if definition is None:
        raise FileCritical(file, 'Variable %s not defined for sector %s. skipping...',
                           file.variable_name, settings.SECTOR)

    # check for number of variable dependencies

    file_dim_len = len(variable.dimensions)

    if 'dimensions' in definition:
        settings_dim_len = len(definition['dimensions'])
        dims_expected = str(definition['dimensions']).replace('\'', '')
    else:
        settings_dim_len = 3
        dims_expected = '[time, lat, lon]'

    if file_dim_len != settings_dim_len:
        raise FileCritical(file,
                           'Dimension missing (%s found, %s expected). Declare variable as %s%s.',
                           file_dim_len, settings_dim_len, file.variable_name, dims_expected
        )

    # detect 2d or 3d data
    file.is_time_fixed = False

    if file.specifiers.get('time_step') == 'fixed':
        file.is_time_fixed = True
        if file_dim_len > 2:
            file.critical('File has fixed data but more than 2 dimensions. Remove "time" dimension if present.')
            return
    elif file_dim_len == 3:
        file.is_2d = True
    elif file_dim_len == 4:
        file.is_3d = True
        if variable.dimensions[1] in ['time', 'lat', 'lon']:
            for pos in range(0, file_dim_len):
                if variable.dimensions[pos] not in ['time', 'lat', 'lon']:
                    break
            file.critical('Variable "%s" has "time", "lat" or "lon" as second dependeny.'
                          ' Depencency order must be [time, %s, lat, lon]. "time" is first always.',
                          file.variable_name, variable.dimensions[pos])
            file.dim_vertical = variable.dimensions[pos]
        else:
            file.dim_vertical = variable.dimensions[1]

    # check if vertical bounds were defined
    if file.is_3d:
        if variable.dimensions[1] in ['depth', 'levlak']:
            if definition.get('bounds') is None:
                raise FileWarning(file,
                                  'No vertical boundaries defined for %s dimension. ' +
                                  'Consider adding depth_bnds(depth, bnds). ' +
                                  'See examples at https://bit.ly/ncdf-bounds', variable.dimensions[1])

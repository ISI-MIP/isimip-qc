from ..config import settings
from ..fixes import fix_remove_variable_attr, fix_rename_dimension, fix_rename_variable, fix_rename_variable_attr

# Attributes allowed by the protocol (kept as a set for fast membership tests)
_ALLOWED_VARIABLE_ATTRS = {
    'axis',
    'bounds',
    'calendar',
    'classes',
    'comment',
    'description',
    'enteric_infection',
    'fuelclass',
    'long_name',
    'missing_value',
    'pft',
    'positive',
    'standard_name',
    'unit_conversion_info',
    'units',
}

# Attributes that should be ignored from removal checks
_IGNORED_VARIABLE_ATTRS = {
    '_FillValue'
}


def check_data_model(file):
    '''
    File must use the NetCDF4 classic data model
    '''
    if file.dataset.data_model != 'NETCDF4_CLASSIC':
        file.warning('Data model is %s (not NETCDF4_CLASSIC).', file.dataset.data_model, fix_datamodel=True)
    else:
        file.info('Data model looks good (%s).', file.dataset.data_model)


def check_zip(file):
    '''
    Data variables must be compressed with at least compression level 4. Skip check for dimension variables.
    '''

    variable = file.dataset.variables.get(file.variable_name)
    if variable is None:
        file.warning('Variable "%s" not found for compression check.', file.variable_name)
        return

    try:
        filters = variable.filters()
    except AttributeError:
        filters = None

    if not filters or not filters.get('zlib'):
        file.warning('Variable "%s" is not compressed.', file.variable_name, fix_datamodel=True)
        return

    complevel = filters.get('complevel')
    if complevel < 5:
        file.warning('Variable "%s" compression level is "%s". Should be >= 5.',
                  file.variable_name, complevel, fix_datamodel=True)
    else:
        file.info('Variable "%s" compression level looks good (%s)', file.variable_name, complevel)


def check_lower_case(file):
    '''
    Internal names of dimensions and variables are lowercase.
    '''

    for dimension_name in file.dataset.dimensions:
        if not dimension_name.islower():
            file.warning('Dimension "%s" is not lower case.', dimension_name, fix={
                'func': fix_rename_dimension,
                'args': (file, dimension_name, dimension_name.lower())
            })

    for variable_name, variable in file.dataset.variables.items():
        if not variable_name.islower():
            file.warning('Variable "%s" is not lower case.', variable_name, fix={
                'func': fix_rename_variable,
                'args': (file, variable_name, variable_name.lower())
            })

        # Use NetCDF4's ncattrs() to get user-defined attribute names reliably
        try:
            attrs = variable.ncattrs()
        except AttributeError:
            # Fallback to __dict__ if ncattrs isn't available
            attrs = list(variable.__dict__.keys())

        for attr in attrs:
            if attr in _IGNORED_VARIABLE_ATTRS:
                continue

            if attr not in _ALLOWED_VARIABLE_ATTRS:
                file.warning('Attribute "%s" for variable "%s" is not needed.', attr, variable_name, fix={
                    'func': fix_remove_variable_attr,
                    'args': (file, variable_name, attr)
                })
            else:
                if not attr.islower():
                    file.warning('Attribute "%s" for variable "%s" is not lower case.', attr, variable_name, fix={
                        'func': fix_rename_variable_attr,
                        'args': (file, variable_name, attr)
                    })


def _split_classes(value):
    '''
    Parse a "classes" attribute into a list of class names. Accepts a comma-separated
    string as well as a sequence of (byte-)strings.
    '''
    if isinstance(value, (str, bytes)):
        candidates = [value]
    else:
        candidates = list(value)

    classes = []
    for candidate in candidates:
        if isinstance(candidate, bytes):
            candidate = candidate.decode()
        for part in str(candidate).split(','):
            part = part.strip().strip('\x00').strip()
            if part:
                classes.append(part)

    return classes


def check_fuelclass(file):
    '''
    The "fuelclass" variable must carry the mandatory "classes" attribute listing the
    model-specific fuel classes. Which attributes are mandatory is read from the protocol
    (definitions/dimensions.yaml, key "required_attributes") where available. The class
    names themselves are model-specific and can not be fixed by the tool.
    '''
    variable = file.dataset.variables.get('fuelclass')
    if variable is None:
        return

    definition = settings.DEFINITIONS['dimensions'].get('fuelclass', {})
    required_attributes = definition.get('required_attributes')
    if required_attributes is None:
        # protocol versions without "required_attributes" yet: "classes" is mandatory as per fire.yaml
        required_attributes = ['classes']

    for attribute in required_attributes:
        value = getattr(variable, attribute, None)
        if value is None:
            file.warning('Attribute "%s" for variable "fuelclass" is missing. It is mandatory, list the '
                         'model-specific fuel class names.', attribute)
            continue

        classes = _split_classes(value)
        if not classes:
            file.warning('Attribute "%s" for variable "fuelclass" is empty. List the model-specific '
                         'fuel class names.', attribute)
            continue

        file.info('Attribute "%s" for variable "fuelclass" found with %s class(es): %s.',
                  attribute, len(classes), ', '.join(classes))

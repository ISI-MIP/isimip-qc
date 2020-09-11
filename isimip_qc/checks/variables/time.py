import calendar

import netCDF4
from isimip_qc.config import settings
from isimip_qc.fixes import fix_set_variable_attr


def check_time_variable(file):
    time = file.dataset.variables.get('time')
    time_definition = settings.DEFINITIONS['dimensions'].get('time')

    if time is None:
        file.error('Variable time is missing.')
    elif not time_definition:
        file.error('Definition for variable time is missing.')
    else:
        # check dtype
        dtypes = ['float32', 'float64']
        if time.dtype not in dtypes:
            file.warn('time.dtype="%s" should be in %s.', time.dtype, dtypes)

        # check axis
        axis = time_definition.get('axis')
        try:
            if time.axis != axis:
                file.warn('Attribute time.axis="%s" should be "%s".', time.axis, axis, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'time', 'axis', axis)
                })
        except AttributeError:
            file.warn('Attribute time.axis is missing. Should be "%s".', axis, fix={
                'func': fix_set_variable_attr,
                'args': (file, 'time', 'axis', axis)
            })

        # check standard_name
        standard_name = time_definition.get('standard_name')
        try:
            if time.standard_name != standard_name:
                file.warn('Attribute time.standard_name="%s" should be "%s".', time.standard_name, standard_name)
        except AttributeError:
            file.warn('Attribute time.standard_name is missing. Should be "%s".', standard_name)

        # check long_name
        long_names = time_definition.get('long_names', [])
        try:
            if time.long_name not in long_names:
                file.warn('Attribute time.long_name="%s" should be in %s.', time.long_name, long_names)
        except AttributeError:
            file.warn('Attribute time.long_name is missing. Should be "%s".', long_names[2])

        # check units
        time_step = file.specifiers.get('time_step')
        increment = settings.DEFINITIONS['time_step'][time_step]['increment']
        minimum = settings.DEFINITIONS['time_span']['minimum']['value'][settings.SIMULATION_ROUND]
        units_templates = [
            "%s since %i-01-01",
            "%s since %i-01-01 00:00:00",
            "%s since %i-1-1",
            "%s since %i-1-1 00:00:00"
        ]
        units = [template % (increment, minimum) for template in units_templates]

        try:
            if time.units not in units:
                file.error('Attribute time.units="%s" should be one of %s.', time.units, units)
            else:
                file.info('Valid time unit found (%s)', time.units)
        except AttributeError:
            file.error('Attribute time.units is missing. Should be "%s".', units)

        # check calenders
        calenders = time_definition.get('calenders', [])
        try:
            if time.calendar not in calenders:
                file.warn('Attribute time.calendar="%s" should be one of %s', time.calendar, calenders)
            else:
                file.info('Valid calendar found (%s)', time.calendar)
        except AttributeError:
            file.warn('Attribute time.calendar is missing. Should be in "%s".', calenders)

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
            file.warn('Data type of "time" is "%s". Should be float or double (one of %s).', time.dtype, dtypes)

        # check axis
        axis = time_definition.get('axis')
        try:
            if time.axis != axis:
                file.warn('"axis" attribute of "time" is %s. Should be "%s".', time.axis, axis, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'time', 'axis', axis)
                })
        except AttributeError:
            file.warn('"axis" attribute of "time" is missing. Should be "%s".', axis, fix={
                'func': fix_set_variable_attr,
                'args': (file, 'time', 'axis', axis)
            })

        # check standard_name
        standard_name = time_definition.get('standard_name')
        try:
            if time.standard_name != standard_name:
                file.warn('"standard_name" attribute of "time" is "%s". Should be "%s".', time.standard_name, standard_name, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'time', 'standard_name', standard_name)
                })
        except AttributeError:
            file.warn('"standard_name" attribute of "time" is missing. Should be "%s".', standard_name, fix={
                'func': fix_set_variable_attr,
                'args': (file, 'time', 'standard_name', standard_name)
            })

        # check long_name
        long_names = time_definition.get('long_names', [])
        try:
            if time.long_name not in long_names:
                file.warn('"long_name" attribute of "time" is %s". Should be in %s.', time.long_name, long_names, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'time', 'long_name', long_names[2])
                })
        except AttributeError:
            file.warn('"long_name" attribute of "time" is missing. Should be "%s".', long_names[2], fix={
                'func': fix_set_variable_attr,
                'args': (file, 'time', 'long_name', long_names[2])
            })

        # check units
        time_step = file.specifiers.get('time_step')
        increment = settings.DEFINITIONS['time_step'][time_step]['increment']
        minimum = settings.DEFINITIONS['time_span']['minimum']['value']
        units_templates = [
            "%s since %i-01-01",
            "%s since %i-01-01 00:00:00",
            "%s since %i-1-1",
            "%s since %i-1-1 00:00:00"
        ]
        units = [template % (increment, minimum) for template in units_templates]

        try:
            if time.units not in units:
                file.error('"units" attribute for "time" is "%s". Should be "%s".', time.units, units)
            else:
                file.info('Valid time unit found (%s)', time.units)
        except AttributeError:
            file.error('Attribute time.units is missing. Should be "%s".', units)

        # check calenders
        if time_step == 'daily':
            try:
                calenders_daily = time_definition.get('calenders_daily', [])
                if time.calendar not in calenders_daily:
                    file.error('"calendar" attribute for "time" is "%s". Should be "%s".', time.calendar, calenders_daily)
                else:
                    file.info('Valid calendar found (%s)', time.calendar)
            except AttributeError:
                file.warn('"calendar" attribute for "time" is missing. Should be in "%s".', calenders_daily)
        else:
            try:
                calenders_other = time_definition.get('calenders_other', [])
                if time.calendar not in calenders_other:
                    file.warn('"calendar" attribute for "time" is "%s". Should be one of %s', time.calendar, calenders_other, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, 'time', 'calendar', '360_day')
                    })
                else:
                    file.info('Valid calendar found (%s)', time.calendar)
            except AttributeError:
                file.warn('"calendar" attribute for "time" is missing. Should be in "%s".', calenders_other, fix={
                    'func': fix_set_variable_attr,
                    'args': (file, 'time', 'calendar', '360_day')
                })

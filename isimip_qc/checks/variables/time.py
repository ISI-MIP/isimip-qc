
from isimip_qc.config import settings
from isimip_qc.fixes import fix_set_variable_attr


def check_time_variable(file):
    if file.is_time_fixed:
        return
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
                file.warn(
                    '"standard_name" attribute of "time" is "%s". Should be "%s".',
                    time.standard_name, standard_name, fix={
                        'func': fix_set_variable_attr,
                        'args': (file, 'time', 'standard_name', standard_name)
                    }
                )
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

        # check calendars
        try:
            calendars = time_definition.get('calenders_daily', [])
            if time.calendar not in calendars:
                file.error('"calendar" attribute for "time" is "%s". Must be one of "%s".', time.calendar, calendars)
            else:
                file.info('Valid calendar found (%s)', time.calendar)
        except AttributeError:
            file.warn('"calendar" attribute for "time" is missing. Should be in "%s".', calendars)

def check_time_span_periods(file):

    if settings.TIME_SPAN:
        file.info('skipping test of covered simulation period per option')
        return

    climate_forcing = file.specifiers.get('climate_forcing')

    if 'pre-industrial' in str(file.abs_path):
        definition_startyear = settings.DEFINITIONS['time_span'].get('start_pre-ind')['value']
        definition_endyear = settings.DEFINITIONS['time_span'].get('end_pre-ind')['value']
    elif 'historical' in str(file.abs_path):
        if settings.SIMULATION_ROUND in ['ISIMIP2a', 'ISIMIP3a']:
            definition_startyear = settings.DEFINITIONS['time_span'].get('start_hist')['value'][climate_forcing]
            definition_endyear = settings.DEFINITIONS['time_span'].get('end_hist')['value'][climate_forcing]
        elif settings.SIMULATION_ROUND in ['ISIMIP2b', 'ISIMIP3b']:
            definition_startyear = settings.DEFINITIONS['time_span'].get('start_hist')['value']
            definition_endyear = settings.DEFINITIONS['time_span'].get('end_hist')['value']
    elif 'future' in str(file.abs_path):
        definition_startyear = settings.DEFINITIONS['time_span'].get('start_fut')['value']
        definition_endyear = settings.DEFINITIONS['time_span'].get('end_fut')['value']
    else:
        file.warn('Skipping check for simulation period as the period itself could not be'
                  ' determined from the file path (pre-industrial, historical or future).')
        return

    file_startyear = file.specifiers.get('start_year')
    file_endyear = file.specifiers.get('end_year')

    time_resolution = file.specifiers.get('time_step')

    if time_resolution not in ['daily', 'fixed']:
        if definition_startyear != file_startyear or definition_endyear != file_endyear:
            file.warn('time period covered by file (%s-%s) does not match input data time span (%s-%s).'
                      ' Ensure to prepare the full period for all variables using the latest input data set.',
                      file_startyear, file_endyear, definition_startyear, definition_endyear)
        else:
            file.info('File is covering the full simulation period (by file name)')
    else:
        if 'historical' in str(file.abs_path):
            if settings.SIMULATION_ROUND == 'ISIMIP3a' and climate_forcing == '20crv3-era5':
                last_file_startyear = 2021
            else:
                last_file_startyear = 2011

            if file_startyear == last_file_startyear:
                if definition_endyear != file_endyear:
                    file.warn('Last year of time period covered by file (%s) does not match end of input'
                              ' data time span (%s). Ensure to prepare the full period for all variables'
                              ' using the latest input data set.',
                              file_endyear, definition_endyear)

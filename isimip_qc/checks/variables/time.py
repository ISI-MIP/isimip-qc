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
        minimum = settings.DEFINITIONS['time_span']['minimum']['value'][settings.SIMULATION_ROUND]
        units_templates = [
            "%s since %i-01-01",
            "%s since %i-01-01 00:00:00",
            "%s since %i-1-1",
            "%s since %i-1-1 00:00:00"
        ]
        units = []
        for specifier, definition in settings.DEFINITIONS['time_step'].items():
            units += [template % (definition['increment'], minimum) for template in units_templates]

        try:
            if time.units not in units:
                file.warn('Attribute time.units="%s" should be one of %s.', time.units, units)
            else:
                file.info('Valid time unit found (%s)', time.units)
        except AttributeError:
            file.warn('Attribute time.units is missing. Should be "%s".', units)

        # check calenders
        calenders = time_definition.get('calenders', [])
        try:
            if time.calendar not in calenders:
                file.warn('Attribute time.calendar="%s" should be one of %s', time.calendar, calenders)
            else:
                file.info('Valid calendar found (%s)', time.calendar)
        except AttributeError:
            file.warn('Attribute time.calendar is missing. Should be in "%s".', calenders)

        # first and last year from file name specifiers must match those from internal time axis
        # number of time steps must match those expected from the time axis
        time = file.dataset.variables.get('time')
        time_steps = len(time[:])
        time_units = time.units
        time_resolution = file.specifiers.get('time_step')

        if time_resolution == 'daily':
            try:
                time_calendar = time.calendar
            except AttributeError:
                file.warn('Can\'t check for number of time steps because of missing time.calendar attribute')
                return
        elif time_resolution == 'monthly':
            # for monthly resolution cftime.num2date only allows for '360_day' calendar
            time_calendar = '360_day'

        if time_resolution in ['daily', 'monthly']:
            firstdate_nc = netCDF4.num2date(time[0], time_units, time_calendar)
            lastdate_nc = netCDF4.num2date(time[time_steps-1], time_units, time_calendar)
            startyear_nc = firstdate_nc.year
            endyear_nc = lastdate_nc.year
        elif time_resolution == 'annual':
            ref_year = int(time.units.split()[2].split("-")[0])
            startyear_nc = ref_year + int(time[0])
            endyear_nc = ref_year + int(time[-1])

        startyear_file = int(file.specifiers.get('start_year'))
        endyear_file = int(file.specifiers.get('end_year'))
        nyears_file = endyear_file - startyear_file + 1

        if startyear_nc != startyear_file or endyear_nc != endyear_file:
            file.error('Start and/or end year of NetCDF time axis (%s-%s) doesn\'t match period defined in file name (%s-%s)', startyear_nc, endyear_nc, startyear_file, endyear_file)
        else:
            file.info('Time period covered by this file matches the internal time axis (%s-%s)', startyear_nc, endyear_nc)

        if time_resolution == 'daily':
            if time_calendar in ['proleptic_gregorian', 'standard']:
                time_days = 0
                for year in range(startyear_file, endyear_file+1):
                    if calendar.isleap(year):
                        time_days += 366
                    else:
                        time_days += 365
            elif time_calendar == '366_day':
                time_days = nyears_file * 366
            elif time_calendar == '365_day':
                time_days = nyears_file * 365
            elif time_calendar == '360_day':
                time_days = nyears_file * 360

            if time_days != time_steps:
                file.error('Number of internal time steps (%s) does not match the expected number from the file name specifiers (%s). (\'%s\' calendar found)', time_steps, time_days, time_calendar)
            else:
                file.info('Correct number of time steps (%s) given the defined calendar (%s)', time_steps, time_calendar)
        elif time_resolution == 'monthly':
            time_months = nyears_file * 12
            if time_months != time_steps:
                file.error('Number of internal time steps (%s) does not match the expected number from the file name specifiers (%s).', time_steps, time_months)
            else:
                file.info('Correct number of time steps (%s).', time_steps)
        elif time_resolution == 'annual':
            if nyears_file != time_steps:
                file.error('Number of internal time steps (%s) does not match the expected number from the file name specifiers (%s).', time_steps, nyears_file)
            else:
                file.info('Correct number of time steps (%s).', time_steps)

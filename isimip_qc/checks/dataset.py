def check_data_model(file):
    '''
    File must use the NetCDF4 classic data model
    '''
    if file.dataset.data_model != 'NETCDF4_CLASSIC':
        file.warn('Data model is %s (not NETCDF4_CLASSIC).', file.dataset.data_model)


def check_zip(file):
    '''
    Data variables must be compressed with at least compression level 4. Skip check for dimension variables.
    '''
    for variable_name, variable in file.dataset.variables.items():
        if variable_name not in ['time', 'lat', 'lon']:
            zlib = variable.filters().get('zlib')
            if zlib:
                complevel = variable.filters().get('complevel')
                if complevel < 4:
                    file.info('%s._DeflateLevel=%s should be > 4.', variable_name, complevel)
            else:
                file.warn('%s is not compressed.', variable_name)


def check_lower_case(file):
    '''
    Internal names of dimensions and variables are lowercase.
    '''

    for dimension_name in file.dataset.dimensions:
        if not dimension_name.islower():
            file.warn('Dimension "%s" is not lower case.', dimension_name)

    for variable_name, variable in file.dataset.variables.items():
        if not variable_name.islower():
            file.warn('Variable "%s" is not lower case.', variable_name)

        for attr in variable.__dict__:
            if attr not in ['_FillValue']:
                if not attr.islower():
                    file.warn('Attribute "%s.%s" is not lower case.', variable_name, attr)
                if attr not in ['axis', 'standard_name', 'long_name', 'calendar', 'missing_value', 'units']:
                    file.warn('Attribute "%s.%s" is not needed. Consider removing it.', variable_name, attr)

def check_period(file):
    '''
    first and last year from file name specifiers must match those from internal time axis
    number of time steps must match those expected from the time axis
    '''

    import netCDF4
    import calendar

    time_var = file.dataset.variables.get('time')
    time_steps = len(time_var[:])
    time_units = time_var.units
    time_resolution = file.specifiers.get('time_step')

    if time_resolution == 'daily':
        time_calendar = time_var.calendar
    elif time_resolution == 'monthly':
        # for monthly resolution cftime only allows for 360_day calendar
        time_calendar = '360_day'

    if time_resolution in ['daily','monthly']:
        firstdate_nc = netCDF4.num2date(time_var[0],time_units,time_calendar)
        lastdate_nc  = netCDF4.num2date(time_var[time_steps-1],time_units,time_calendar)
        startyear_nc = firstdate_nc.year
        endyear_nc   = lastdate_nc.year
    elif time_resolution == 'annual':
        ref_year = int(time_var.units.split()[2].split("-")[0])
        startyear_nc = ref_year + int(time_var[0])
        endyear_nc   = ref_year + int(time_var[-1])

    startyear_file = int(file.specifiers.get('start_year'))
    endyear_file   = int(file.specifiers.get('end_year'))
    nyears_file    = endyear_file - startyear_file + 1

    if startyear_nc != startyear_file:
        file.error('Start year of time axis (%s) doesn\'t match start year in file name (%s)', startyear_nc, startyear_file)

    if endyear_nc != endyear_file:
        file.error('End year of time axis (%s) does not match end year in file name (%s)', endyear_nc, endyear_file)

    if time_resolution == 'daily':
        if time_calendar in ['proleptic_gregorian','standard']:
            for year in range(startyear_file,endyear_file):
                if calendar.isleap(year):
                    time_days = time_days + 366
                else:
                    time_days = time_days + 365
        elif time_calendar == '366_day':
            time_days = nyears_file * 366
        elif time_calendar == '365_day':
            time_days = nyears_file * 365
        elif time_calendar == '360_day':
            time_days = nyears_file * 360

        if time_days != time_steps:
            file.error('number of internal time steps (%s) does not match the expected number from the file name specifiers (%s)', time_steps, time_days)
    elif time_resolution == 'monthly':
        time_months = nyears_file * 12
        if time_months != time_steps:
            file.error('number of internal time steps (%s) does not match the expected number from the file name specifiers', time_steps, time_months)
    elif time_resolution == 'annual':
        if nyears_file != time_steps:
            file.error('number of internal time steps (%s) does not match the expected number from the file name specifiers', time_steps, nyears_file)

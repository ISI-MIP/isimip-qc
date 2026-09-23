from isimip_qc.config import settings


def update_grid_value(file, variable, key, value):
    model = file.specifiers.get('model')
    climate_forcing = file.specifiers.get('climate_forcing')
    sens_scenario = file.specifiers.get('sens_scenario')

    # overwrite for special climate forcings defined in the protocol
    climate_forcing_grid = settings.DEFINITIONS['climate_forcing'].get(climate_forcing, {}).get('grid')
    if climate_forcing_grid:
        climate_forcing_value = climate_forcing_grid.get(variable, {}).get(key, {})
        if isinstance(climate_forcing_value, dict):
            climate_forcing_default = climate_forcing_value.get('default', value)
            value = climate_forcing_value.get(sens_scenario, climate_forcing_default)
        else:
            value = climate_forcing_value

    # overwrite for special sectors defined in the protocol
    sector_grid = settings.DEFINITIONS['sector'].get(settings.SECTOR, {}).get('grid')
    if sector_grid:
        sector_value = sector_grid.get(variable, {}).get(key, {})
        if isinstance(sector_value, dict):
            sector_default = sector_value.get('default', value)
            value = sector_value.get(sens_scenario, sector_default)
        else:
            value = sector_value

    # overwrite for special models defined in the protocol
    model_grid = settings.DEFINITIONS['model'].get(model, {}).get('grid')
    if model_grid:
        model_value = model_grid.get(variable, {}).get(key, {})
        if isinstance(model_value, dict):
            model_default = model_value.get('default', value)
            value = model_value.get(sens_scenario, model_default)
        else:
            value = model_value

    return value

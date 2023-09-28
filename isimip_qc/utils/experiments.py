from ..config import settings


def get_experiment(specifiers):
    climate_scenario = specifiers.get('climate_scenario')
    soc_scenario = specifiers.get('soc_scenario')
    sens_scenario = specifiers.get('sens_scenario')

    for experiment_specifier, experiment_values in settings.DEFINITIONS.get('experiments').items():
        for period_specifier, period_values in settings.DEFINITIONS.get('period', []).items():
            if (period_values.get('start_year') <= specifiers.get('start_year') and
                period_values.get('end_year') >= specifiers.get('end_year')):

                experiment_period = experiment_values.get(period_specifier, {})

                if (isinstance(experiment_period, dict) and
                    experiment_period.get('climate') == climate_scenario and
                    experiment_period.get('soc') == soc_scenario and
                    (sens_scenario == 'default' or
                     experiment_period.get('climate_sens') == sens_scenario or
                     experiment_period.get('soc_sens') == sens_scenario)):
                    return experiment_specifier

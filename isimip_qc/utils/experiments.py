from ..config import settings


def get_experiment(specifiers):
    climate_scenario = specifiers.get('climate_scenario')
    soc_scenario = specifiers.get('soc_scenario')
    sens_scenario = specifiers.get('sens_scenario')

    for specifier, experiment in settings.DEFINITIONS.get('experiments').items():
        for period in settings.DEFINITIONS.get('period', []):
            experiment_period = experiment.get(period, {})

            if experiment_period.get('climate') == climate_scenario and \
                    experiment_period.get('soc') == soc_scenario:
                if sens_scenario == 'default' or \
                        experiment_period.get('climate_sens') == sens_scenario or \
                        experiment_period.get('soc_sens') == sens_scenario:
                    return specifier

from ..utils.experiments import get_experiment


def check_experiment(file):
    experiment = get_experiment(file.specifiers)
    if experiment is None:
        file.critical('No valid experiment found for {climate_scenario}, {soc_scenario} and {sens_scenario}'.format(**file.specifiers))
    else:
        file.info('Experiment looks good (%s).', experiment)

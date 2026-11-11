from ..config import settings


def match_climate_scenario(experiment_climate, file_climate):
    # ISIMIP4b experiments list the climate_scenario specifier ('h'), but file names
    # may carry one of its specifier_alias values (CMIP7 vocabulary like 'scen7-h'
    # or 'esm-scen7-h'); accept any alias, not just the bare specifier
    scenario = settings.DEFINITIONS.get('climate_scenario', {}).get(experiment_climate)
    if scenario is not None and file_climate in scenario.get('specifier_alias', []):
        return True
    return experiment_climate == file_climate


def get_period(path):
    # the simulation period is encoded in the folder structure below UNCHECKED_PATH
    # (pre-industrial/historical/future), see also check_time_span_periods
    path_str = str(path)
    for period in ('pre-industrial', 'historical', 'future'):
        if period in path_str:
            return period
    return None


def get_experiment(specifiers, period=None):
    climate_scenario = specifiers.get('climate_scenario')
    soc_scenario = specifiers.get('soc_scenario')
    sens_scenario = specifiers.get('sens_scenario')

    experiments = settings.DEFINITIONS.get('experiments')
    if experiments is None:
        # no experiments information is available
        return False

    all_periods = settings.DEFINITIONS.get('period', {})
    # anchor the search to the period from the subfolder when the protocol defines it,
    # so a file is only tested against its subfolder's period; fall back to inferring
    # the period from the covered years when the folder structure does not name one
    period_candidates = [period] if period in all_periods else list(all_periods)

    for experiment_specifier, experiment_values in experiments.items():
        for period_specifier in period_candidates:
            period_values = all_periods[period_specifier]
            if period_values.get('start_year') <= specifiers.get('start_year') and period_values.get(
                'end_year'
            ) >= specifiers.get('end_year'):
                experiment_period = experiment_values.get(period_specifier, {})

                if (
                    isinstance(experiment_period, dict)
                    and match_climate_scenario(experiment_period.get('climate'), climate_scenario)
                    and experiment_period.get('soc') == soc_scenario
                    and (
                        sens_scenario == 'default'
                        or experiment_period.get('climate_sens') == sens_scenario
                        or experiment_period.get('soc_sens') == sens_scenario
                    )
                ):
                    return experiment_specifier

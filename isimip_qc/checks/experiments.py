from isimip_qc.config import settings

from ..exceptions import FileCritical
from ..utils.experiments import get_experiment, get_period


def check_experiment(file):
    if settings.SKIP_EXP:
        return

    if file.specifiers.get("time_step") == "fixed":
        return

    specifiers = file.specifiers
    start_year = specifiers.get('start_year')
    end_year = specifiers.get('end_year')
    period = get_period(file.path)

    # the file must stay within the simulation period defined for the subfolder
    # it sits in (sample files are allowed, but must not straddle or leave the period)
    period_definition = settings.DEFINITIONS.get('period', {}).get(period) or {}
    definition_startyear = period_definition.get('start_year')
    definition_endyear = period_definition.get('end_year')
    if (definition_startyear is not None and definition_endyear is not None and
            start_year is not None and end_year is not None and
            not (definition_startyear <= start_year and end_year <= definition_endyear)):
        raise FileCritical(
            file,
            f"Period covered by the file ({start_year}-{end_year}) is not within the "
            f"{period} simulation period defined in the protocol "
            f"({definition_startyear}-{definition_endyear}). Skipping...",
        )

    experiment = get_experiment(specifiers, period)

    if experiment is False:
        file.warning("No experiment information found in the protocol. Skipping...")
        return

    if experiment is None:
        # use safe lookups to avoid KeyError if spec misses entries
        msg = (
            "No valid experiment found for this sector in the {period} period and "
            "{climate_scenario}, {soc_scenario}, {sens_scenario} between "
            "{start_year} and {end_year}. Skipping..."
        ).format(
            period=period or 'unknown',
            climate_scenario=specifiers.get('climate_scenario', '<unknown>'),
            soc_scenario=specifiers.get('soc_scenario', '<unknown>'),
            sens_scenario=specifiers.get('sens_scenario', '<unknown>'),
            start_year=start_year if start_year is not None else '<unknown>',
            end_year=end_year if end_year is not None else '<unknown>',
        )
        raise FileCritical(file, msg)

    file.info("Experiment looks good (%s).", experiment)

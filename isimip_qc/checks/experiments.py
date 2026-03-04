from isimip_qc.config import settings

from ..exceptions import FileCritical
from ..utils.experiments import get_experiment


def check_experiment(file):
    if settings.SKIP_EXP:
        return

    if file.specifiers.get("time_step") == "fixed":
        return
    spec = file.specifiers
    experiment = get_experiment(spec)
    if experiment is False:
        file.warning("No experiment information found in the protocol. Skipping...")
        return

    if experiment is None:
        # use safe lookups to avoid KeyError if spec misses entries
        msg = (
            "No valid experiment found for this sector and {climate_scenario}, "
            "{soc_scenario}, {sens_scenario} between {start_year} and {end_year}. Skipping..."
        ).format(
            climate_scenario=spec.get('climate_forcing', '<unknown>'),
            soc_scenario=spec.get('soc_scenario', '<unknown>'),
            sens_scenario=spec.get('sens_scenario', '<unknown>'),
            start_year=spec.get('start_year', '<unknown>'),
            end_year=spec.get('end_year', '<unknown>'),
        )
        raise FileCritical(file, msg)

    file.info("Experiment looks good (%s).", experiment)

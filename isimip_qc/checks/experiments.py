from isimip_qc.config import settings

from ..exceptions import FileCritical
from ..utils.experiments import get_experiment


def check_experiment(file):
    if settings.SKIP_EXP:
        return

    if file.specifiers.get("time_step") == "fixed":
        return

    experiment = get_experiment(file.specifiers)
    if experiment is None:
        raise FileCritical(file, "No valid experiment found for this sector and {climate_scenario}, "\
                           "{soc_scenario}, {sens_scenario} between {start_year} and {end_year}. skipping..."\
                           .format(**file.specifiers)
                           )

    else:
        file.info("Experiment looks good (%s).", experiment)

from ..utils.experiments import get_experiment
from ..exceptions import FileCritical

def check_experiment(file):
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

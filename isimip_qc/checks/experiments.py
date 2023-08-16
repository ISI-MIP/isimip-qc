from ..utils.experiments import get_experiment


def check_experiment(file):
    if file.specifiers.get("time_step") == "fixed":
        return

    experiment = get_experiment(file.specifiers)
    if experiment is None:
        file.critical(
            "No valid experiment found for {climate_scenario}, {soc_scenario}, {sens_scenario} between {start_year} and {end_year}.".format(
                **file.specifiers
            )
        )
    else:
        file.info("Experiment looks good (%s).", experiment)

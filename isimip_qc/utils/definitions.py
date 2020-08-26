def filter_definitions(definition, simulation_round, product, sector=None):
    for row in definition.values():
        if 'simulation_rounds' not in row or simulation_round in row['simulation_rounds']:
            if 'products' not in row or product in row['products']:
                if sector is not None:
                    if 'sectors' not in row or sector in row['sectors']:
                        yield row
                else:
                    yield row

import importlib
import inspect
from pathlib import Path

# gather functions from the python files in this directory
functions = []
for file_path in Path(__file__).parent.iterdir():
    if file_path.stem[0] not in ['_', '.']:
        module_name = 'isimip_qc.checks.{}'.format(file_path.stem)
        module = importlib.import_module(module_name)
        functions += [function for function in inspect.getmembers(module, inspect.isfunction)]

# find checks
checks = [function[1] for function in functions if function[0].startswith('check_')]

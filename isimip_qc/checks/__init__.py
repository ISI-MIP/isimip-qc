import importlib
import inspect
import os
from pathlib import Path

checks_dir = Path(__file__).parent

# gather functions from the python files in this directory
functions = []

for root, dirs, files in os.walk(checks_dir):
    for file_name in sorted(files):
        file_path = checks_dir / root / file_name
        if file_path.suffix == '.py' and file_path.name != '__init__.py':
            parts = file_path.relative_to(checks_dir).with_suffix('').parts
            module_name = 'isimip_qc.checks.{}'.format('.'.join(parts))
            module = importlib.import_module(module_name)
            functions += [function for function in inspect.getmembers(module, inspect.isfunction)]

# find checks
checks = [function[1] for function in functions if function[0].startswith('check_')]

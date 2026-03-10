import importlib
import inspect
from pathlib import Path

checks_dir = Path(__file__).parent

# gather functions from the python files in this directory
checks = []

# gather all check functions from all python filesin this directory
for path in sorted(checks_dir.rglob('*.py')):
    if path.name == '__init__.py':
        continue
    parts = path.relative_to(checks_dir).with_suffix('').parts
    module_name = 'isimip_qc.checks.{}'.format('.'.join(parts))
    module = importlib.import_module(module_name)
    checks += [
        func
        for _, func in inspect.getmembers(module, inspect.isfunction)
        if func.__name__.startswith('check_')
    ]

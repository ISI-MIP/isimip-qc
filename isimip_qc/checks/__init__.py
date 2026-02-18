import importlib
import inspect
import os
from pathlib import Path

checks_dir = Path(__file__).parent

# gather functions from the python files in this directory
functions = []

from collections import deque

# Walk directory using os.scandir to avoid building large lists like os.walk does.
queue = deque([checks_dir])
while queue:
    current = queue.popleft()
    try:
        with os.scandir(current) as it:
            entries = sorted(it, key=lambda e: e.name)
            for entry in entries:
                p = Path(entry.path)
                if entry.is_dir():
                    queue.append(p)
                elif entry.is_file() and p.suffix == '.py' and p.name != '__init__.py':
                    parts = p.relative_to(checks_dir).with_suffix('').parts
                    module_name = 'isimip_qc.checks.{}'.format('.'.join(parts))
                    module = importlib.import_module(module_name)
                    functions += list(inspect.getmembers(module, inspect.isfunction))
    except PermissionError:
        # skip directories we cannot access
        continue

# find checks
checks = [function[1] for function in functions if function[0].startswith('check_')]

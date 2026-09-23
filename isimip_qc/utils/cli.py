import argparse
import re
from pathlib import Path


def parse_schema_path(path):
    if not re.match(r'^[A-Za-z0-9/_-]+$', path):
        raise argparse.ArgumentTypeError('must only contain letters, numbers, underscores, hyphens and slashes.')

    path = Path(path)
    if path.is_absolute():
        raise argparse.ArgumentTypeError('must not be an absolute path.')
    return path

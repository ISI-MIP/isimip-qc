import argparse
import importlib.metadata
import logging
import re
from pathlib import Path
from urllib.parse import urlparse

import requests
from packaging.version import Version

logger = logging.getLogger(__name__)


def parse_schema_path(path):
    if not re.match(r'^[A-Za-z0-9/_-]+$', path):
        raise argparse.ArgumentTypeError('must only contain letters, numbers, underscores, hyphens and slashes.')

    path = Path(path)
    if path.is_absolute():
        raise argparse.ArgumentTypeError('must not be an absolute path.')
    return path


def check_version():
    current = Version(importlib.metadata.version('isimip-qc'))
    try:
        response = requests.get('https://pypi.org/pypi/isimip-qc/json')
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        return

    latest = Version(response.json()['info']['version'])
    if current < latest:
        logging.warning(
            f'There is a newer version of isimip-qc available: {latest}.'
            + ' Please upgrade using "pip install --upgrade isimip-qc".'
        )


def check_connection(protocol_locations):
    for protocol_location in protocol_locations:
        if not isinstance(protocol_location, Path) and urlparse(protocol_location).scheme:
            requests.head(f'{protocol_location}/glossary.json')

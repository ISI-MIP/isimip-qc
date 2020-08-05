import json
import logging
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


def fetch_pattern(pattern_bases, pattern_path):
    pattern_json = fetch_json(pattern_bases, pattern_path)
    if pattern_json:
        assert isinstance(pattern_json['path'], str)
        assert isinstance(pattern_json['file'], str)
        assert isinstance(pattern_json['dataset'], str)
        assert isinstance(pattern_json['suffix'], list)

        return {
            'path': re.compile(pattern_json['path']),
            'file': re.compile(pattern_json['file']),
            'dataset': re.compile(pattern_json['dataset']),
            'suffix': pattern_json['suffix']
        }


def fetch_schema(schema_bases, schema_path):
    return fetch_json(schema_bases, schema_path)


def fetch_json(bases, path):
    for base in bases:
        if urlparse(base).scheme:
            location = base + path.as_posix() + '.json'
            logger.debug('json_url=%s', location)
            response = requests.get(location)

            if response.status_code == 200:
                return response.json()

        else:
            location = Path(base).joinpath(path).with_suffix('.json')
            logger.debug('json_path=%s', location)

            if location.exists():
                return json.loads(open(location).read())

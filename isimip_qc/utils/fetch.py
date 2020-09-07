import json
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

import colorlog

logger = colorlog.getLogger(__name__)


def fetch_definitions(bases, path):
    definition_path = Path('definitions').joinpath(path).with_suffix('.json')
    definition_json = fetch_json(bases, definition_path)
    if definition_json:
        definitions = {}
        for definition_name, definition in definition_json.items():
            if isinstance(definition, str):
                definitions[definition_name] = definition
            else:
                definitions[definition_name] = {
                    row['specifier']: row for row in definition
                }

        return definitions


def fetch_pattern(bases, path):
    pattern_path = Path('pattern').joinpath(path).with_suffix('.json')
    pattern_json = fetch_json(bases, pattern_path)
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


def fetch_schema(bases, path):
    schema_path = Path('schema').joinpath(path).with_suffix('.json')
    schema_json = fetch_json(bases, schema_path)
    return schema_json


def fetch_json(bases, path):
    for base in bases:
        if urlparse(base).scheme:
            location = base.rstrip('/') + '/' + path.as_posix()
            logger.debug('json_url=%s', location)
            response = requests.get(location)

            if response.status_code == 200:
                return response.json()

        else:
            location = Path(base).expanduser().joinpath(path)
            logger.debug('json_path=%s', location)
            if location.exists():
                return json.loads(open(location).read())

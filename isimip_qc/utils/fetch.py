import json
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

import colorlog

logger = colorlog.getLogger(__name__)


def fetch_definitions(base):
    index_path = Path('definitions') / 'index.json'
    index_json = fetch_json(base, index_path)

    definitions = {}
    for file_name in index_json:
        definition_name = Path(file_name).stem
        definition_path = Path('definitions') / file_name
        definition_json = fetch_json(base, definition_path)
        definitions[definition_name] = {definition['specifier']: definition for definition in definition_json}

    return definitions


def fetch_pattern(base, path):
    pattern_path = Path('pattern').joinpath(path).with_suffix('.json')
    pattern_json = fetch_json(base, pattern_path)
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


def fetch_schema(base, path):
    schema_path = Path('schema').joinpath(path).with_suffix('.json')
    schema_json = fetch_json(base, schema_path)
    return schema_json


def fetch_json(base, path):
    if urlparse(base).scheme:
        location = base + path.as_posix() + '.json'
        logger.debug('json_url=%s', location)
        response = requests.get(location)

        if response.status_code == 200:
            return response.json()

    else:
        location = Path(base).expanduser().joinpath(path).with_suffix('.json')
        logger.debug('json_path=%s', location)

        if location.exists():
            return json.loads(open(location).read())

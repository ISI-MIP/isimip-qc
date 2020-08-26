import json
import re
from pathlib import Path
from urllib.parse import urlparse

import colorlog
import requests

logger = colorlog.getLogger(__name__)


def fetch_definitions(bases, path):
    index_path = Path('definitions') / path / 'index.json'
    index_json = fetch_json(bases, index_path)

    definitions = {}
    for file_name in index_json:
        definition_name = Path(file_name).stem
        definition_path = Path('definitions') / path / file_name
        definition_json = fetch_json(bases, definition_path)
        definitions[definition_name] = {definition['specifier']: definition for definition in definition_json}

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
            location = base.rstrip('/') + path.as_posix() + '.json'
            logger.debug('json_url=%s', location)
            response = requests.get(location)

            if response.status_code == 200:
                return response.json()

        else:
            location = Path(base).expanduser().joinpath(path).with_suffix('.json')
            logger.debug('json_path=%s', location)

            if location.exists():
                return json.loads(open(location).read())

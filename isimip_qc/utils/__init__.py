import json
import logging
import os
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

import requests
from netCDF4 import Dataset

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


def walk_files(path):
    for root, dirs, file_names in os.walk(path):
        for file_name in file_names:
            file_path = Path(root) / file_name
            yield file_path


def open_file(file_path):
    return Dataset(file_path, 'r')


def move_file(source_path, target_path):
    logger.debug('source_path=%s target_path=%s', source_path, target_path)

    # create directories
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # move the file
    shutil.move(source_path, target_path)

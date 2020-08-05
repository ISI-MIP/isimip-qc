import logging
import os
import shutil
from pathlib import Path

from netCDF4 import Dataset

logger = logging.getLogger(__name__)


def walk_files(path):
    for root, dirs, file_names in os.walk(path):
        for file_name in file_names:
            file_path = Path(root) / file_name
            yield file_path


def open_file(file_path):
    return Dataset(file_path, 'r')


def move_file(source_path, target_path):
    logger.debug('source_path=%s target_path=%s', source_path, target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(source_path, target_path)


def copy_file(source_path, target_path):
    logger.debug('source_path=%s target_path=%s', source_path, target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(source_path, target_path)

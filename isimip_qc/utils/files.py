import os
import shutil
from pathlib import Path

import colorlog

logger = colorlog.getLogger(__name__)


def walk_files(path):
    for root, dirs, file_names in sorted(os.walk(path)):
        for file_name in sorted(file_names):
            file_path = Path(root) / file_name
            yield file_path


def move_file(source_path, target_path):
    logger.debug('source_path=%s target_path=%s', source_path, target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(source_path, target_path)


def copy_file(source_path, target_path):
    logger.debug('source_path=%s target_path=%s', source_path, target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(source_path, target_path)

import os
import shutil
from pathlib import Path

import colorlog

from ..config import settings

logger = colorlog.getLogger(__name__)


def walk_files(path):
    for root, dirs, file_names in sorted(os.walk(path)):
        for file_name in sorted(file_names):
            file_path = Path(root) / file_name
            yield file_path


def move_file(source_path, target_path, overwrite=False):
    if settings.OVERWRITE is True:
        overwrite = True

    logger.debug('source_path=%s target_path=%s', source_path, target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if not target_path.is_file() or overwrite:
        logger.info('Copy file')
        shutil.move(source_path, target_path)
    else:
        logger.warn('Skip moving because target file is present and overwriting not allowed.'
                    ' Use -O to allow overwriting.')


def copy_file(source_path, target_path):
    logger.debug('source_path=%s target_path=%s', source_path, target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if not target_path.is_file() or settings.OVERWRITE:
        logger.info('Copy file')
        shutil.copy(source_path, target_path)
    else:
        logger.warn('Skip copying because target file is present and overwriting not allowed.'
                    ' Use -O to allow overwriting.')

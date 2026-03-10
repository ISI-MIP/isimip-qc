import logging
import os
import shutil
from pathlib import Path

from ..config import settings

logger = logging.getLogger(__name__)


def walk_files(path):
    # Use os.scandir recursively to avoid creating large lists returned by os.walk
    stack = [Path(path)]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                entries = sorted(it, key=lambda e: e.name)
                for entry in entries:
                    # skip symlinks to avoid repeated or unexpected traversal
                    if entry.is_symlink():
                        continue
                    # prefer non-following-symlink checks
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(Path(entry.path))
                    elif entry.is_file(follow_symlinks=False):
                        yield Path(entry.path)
        except PermissionError:
            # skip directories we cannot access
            continue


def move_file(source_path, target_path, overwrite=False):
    if settings.OVERWRITE is True:
        overwrite = True

    logger.debug('source_path=%s target_path=%s', source_path, target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if not target_path.is_file() or overwrite:
        logger.info('Move file')
        shutil.move(source_path, target_path)
    else:
        logger.warning('Skip moving because target file is present and overwriting not allowed.'
                    ' Use -O to allow overwriting.')


def copy_file(source_path, target_path):
    logger.debug('source_path=%s target_path=%s', source_path, target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if not target_path.is_file() or settings.OVERWRITE:
        logger.info('Copy file')
        shutil.copy(source_path, target_path)
    else:
        logger.warning('Skip copying because target file is present and overwriting not allowed.'
                    ' Use -O to allow overwriting.')

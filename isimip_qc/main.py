import argparse
import logging

from .checks import checks
from .config import settings
from .models import File
from .utils.files import copy_file, move_file, walk_files

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    # mandatory
    parser.add_argument('schema_path', help='ISIMIP schema_path, e.g. ISIMIP3a/OutputData/water_global')
    # optional
    parser.add_argument('--copy', dest='move', action='store_true', default=None,
                        help='Copy checked files to the CHECKED_PATH')
    parser.add_argument('--move', dest='move', action='store_true', default=None,
                        help='Move checked files to the CHECKED_PATH')
    parser.add_argument('--config-file', dest='config_file', default=None,
                        help='File path to the config file')
    parser.add_argument('--unchecked-path', dest='unchecked_path', default=None,
                        help='base path of the unchecked files')
    parser.add_argument('--checked-path', dest='checked_path', default=None,
                        help='base path for the checked files')
    parser.add_argument('--pattern-location', dest='pattern_locations', default=None,
                        help='URL or file path to the pattern json')
    parser.add_argument('--schema-location', dest='schema_locations', default=None,
                        help='URL or file path to the json schema')
    parser.add_argument('--log-level', dest='log_level', default=None,
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-path', dest='log_path', default=None,
                        help='base path for the log files for individual files')
    parser.add_argument('--first-file', dest='first_file', action='store_true', default=False,
                        help='only process first file found in UNCHECKED_PATH')

    # setup
    args = parser.parse_args()
    settings.setup(args)

    if settings.PATTERN is None:
        parser.error('no pattern could be found.')
    if settings.SCHEMA is None:
        parser.error('no schema could be found.')

    # walk over unchecked files
    for file_path in walk_files(settings.UNCHECKED_PATH):
        if file_path.suffix in settings.PATTERN['suffix']:
            file = File(file_path)
            file.open()
            file.match()
            for check in checks:
                check(file)
            file.validate()
            file.close()

            if settings.MOVE and settings.CHECKED_PATH and file.clean:
                if settings.MOVE:
                    move_file(settings.UNCHECKED_PATH / file.path, settings.CHECKED_PATH / file.path)
                elif settings.COPY:
                    copy_file(settings.UNCHECKED_PATH / file.path, settings.CHECKED_PATH / file.path)
        else:
            logger.error('%s has wrong suffix. Use "%s" for this simulation round', file_path, settings.PATTERN['suffix'][0])

        if settings.FIRST_FILE:
            break

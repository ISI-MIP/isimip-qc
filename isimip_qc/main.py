import argparse

import colorlog

from .checks import checks
from .config import settings
from .models import File
from .utils.files import walk_files

logger = colorlog.getLogger(__name__)


def get_parser():
    parser = argparse.ArgumentParser(description='Check ISIMIP files for matching protocol definitions')
    # mandatory
    parser.add_argument('schema_path', help='ISIMIP schema_path, e.g. ISIMIP3a/OutputData/water_global')
    # optional
    parser.add_argument('--config-file', dest='config_file',
                        help='File path of the config file')

    parser.add_argument('-c', '--copy', dest='copy', action='store_true',
                        help='Copy checked files to CHECKED_PATH')
    parser.add_argument('-m', '--move', dest='move', action='store_true',
                        help='Move checked files to CHECKED_PATH')

    parser.add_argument('--unchecked-path', dest='unchecked_path',
                        help='base path of the unchecked files')
    parser.add_argument('--checked-path', dest='checked_path',
                        help='base path for the checked files')
    parser.add_argument('--protocol-location', dest='protocol_locations',
                        help='URL or file path to the protocol')
    parser.add_argument('--log-level', dest='log_level',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-path', dest='log_path',
                        help='base path for the log files for individual files')
    parser.add_argument('-f', '--first-file', dest='first_file', action='store_true', default=False,
                        help='only process first file found in UNCHECKED_PATH')
    parser.add_argument('-w', '--stop-on-warnings', dest='stop_warn', action='store_true', default=False,
                        help='stop execution on warnings')
    parser.add_argument('-e', '--stop-on-errors', dest='stop_err', action='store_true', default=False,
                        help='stop execution on errors')
    parser.add_argument('--fix', dest='fix', action='store_true', default=False,
                        help='try to fix warnings detected')
    parser.add_argument('--check', dest='check',
                        help='perform only one particular check')
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    settings.setup(args)

    if settings.DEFINITIONS is None:
        parser.error('no definitions could be found.')
    if settings.PATTERN is None:
        parser.error('no pattern could be found.')
    if settings.SCHEMA is None:
        parser.error('no schema could be found.')

    # walk over unchecked files
    for file_path in walk_files(settings.UNCHECKED_PATH):
        print('Checking: %s' % file_path)
        if file_path.suffix in settings.PATTERN['suffix']:
            file = File(file_path)
            file.open_log()
            file.open_dataset()
            file.match()
            for check in checks:
                if not settings.CHECK or check.__name__ == settings.CHECK:
                    check(file)
            file.validate()
            file.close_dataset()

            if file.is_clean:
                logger.info('File has successfully passed all checks')
            else:
                logger.critical('File did not pass all checks')

            if file.has_warnings and settings.STOP_WARN:
                break
            if file.has_errors and settings.STOP_ERR:
                break

            if file.has_warnings and settings.FIX:
                print('Fix warnings: %s' % file_path)
                file.open_dataset(write=True)
                file.fix_warnings()
                file.close_dataset()

            if file.is_clean:
                if settings.MOVE:
                    file.move()
                elif settings.COPY:
                    file.copy()

        else:
            logger.error('%s has wrong suffix. Use "%s" for this simulation round', file_path, settings.PATTERN['suffix'][0])

        if settings.FIRST_FILE:
            break

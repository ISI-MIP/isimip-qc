import argparse
import logging

from .checks import checks
from .config import settings
from .models import File
from .utils.files import copy_file, move_file, open_file, walk_files

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    # mandatory
    parser.add_argument('simulation_round', help='ISIMIP simulation_round, e.g. ISIMIP3a')
    parser.add_argument('sector', help='ISIMIP sector, e.g. water_global')
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
    parser.add_argument('--pattern-location', dest='pattern_location', default=None,
                        help='URL or file path to the pattern json')
    parser.add_argument('--schema-location', dest='schema_location', default=None,
                        help='URL or file path to the json schema')
    parser.add_argument('--log-level', dest='log_level', default=None,
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-path', dest='log_path', default=None,
                        help='base path for the log files for individual files')

    # setup
    args = parser.parse_args()
    settings.setup(args)

    # walk over unchecked files
    for file_path in walk_files(settings.UNCHECKED_PATH):
        if file_path.suffix in settings.PATTERN['suffix']:
            file = File(file_path)
            file.match_identifiers()

            with open_file(file_path) as dataset:
                for check in checks:
                    check(file, dataset)

            if settings.MOVE and settings.CHECKED_PATH and file.clean:
                if settings.MOVE:
                    move_file(settings.UNCHECKED_PATH / file.path, settings.CHECKED_PATH / file.path)
                elif settings.COPY:
                    copy_file(settings.UNCHECKED_PATH / file.path, settings.CHECKED_PATH / file.path)

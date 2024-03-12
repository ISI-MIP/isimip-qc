import sys
from os import path

import colorlog

from isimip_utils.parser import ArgumentParser

from . import VERSION
from .checks import checks
from .config import settings
from .exceptions import FileCritical, FileError, FileWarning
from .models import File, Summary
from .utils.files import walk_files
from .utils.logging import CHECKING

logger = colorlog.getLogger(__name__)


def get_parser():
    parser = ArgumentParser(prog='isimip-qc', description='Check ISIMIP files for matching protocol definitions')

    # mandatory
    parser.add_argument('schema_path', help='ISIMIP schema_path, e.g. ISIMIP3a/OutputData/water_global')

    # optional
    parser.add_argument('-c', '--copy', dest='copy', action='store_true',
                        help='copy checked files to CHECKED_PATH if no warnings or errors were found')
    parser.add_argument('-m', '--move', dest='move', action='store_true',
                        help='move checked files to CHECKED_PATH if no warnings or errors were found')
    parser.add_argument('-O', '--overwrite', dest='overwrite', action='store_true',
                        help='overwrite files in CHECKED_PATH if present. Default is False.')
    parser.add_argument('--unchecked-path', dest='unchecked_path',
                        help='base path of the unchecked files')
    parser.add_argument('--checked-path', dest='checked_path',
                        help='base path for the checked files')
    parser.add_argument('--protocol-location', dest='protocol_locations',
                        default='https://protocol.isimip.org https://protocol2.isimip.org',
                        help='URL or file path to the protocol when different from official repository')
    parser.add_argument('--log-level', dest='log_level', default='CHECKING',
                        help='log level (CRITICAL, ERROR, WARN, VRDETAIL, CHECKING, SUMMARY,'
                        ' INFO, or DEBUG) [default: CHECKING]')
    parser.add_argument('--log-path', dest='log_path',
                        help='base path for the individual log files')
    parser.add_argument('--log-path-level', dest='log_path_level', default='WARN',
                        help='log level for the individual log files [default: WARN]')
    parser.add_argument('--include', dest='include_list',
                        help='patterns of files to include. Exclude those that don\'t match any.')
    parser.add_argument('--exclude', dest='exclude_list',
                        help='patterns of files to exclude. Include only those that don\'t match any.')
    parser.add_argument('-f', '--first-file', dest='first_file', action='store_true', default=False,
                        help='only process first file found in UNCHECKED_PATH')
    parser.add_argument('-w', '--stop-on-warnings', dest='stop_warn', action='store_true', default=False,
                        help='stop execution on warnings')
    parser.add_argument('-e', '--stop-on-errors', dest='stop_err', action='store_true', default=False,
                        help='stop execution on errors')
    parser.add_argument('--ignore-critical', dest='ignore_crit', action='store_true', default=False,
                        help='allow fixing and copy/move files with critical issues found')
    parser.add_argument('--skip-exp', dest='skip_exp', action='store_true', default=False,
                        help='skip test for valid experiment combination')
    parser.add_argument('-r', '--minmax', dest='minmax', action='store', nargs='?', const=10, type=int,
                        help='test values for valid range (slow, argument MINMAX defaults to show the top 10 values)')
    parser.add_argument('-nt', '--skip-time-span-check', dest='time_span', action='store_true', default=False,
                        help='skip check for simulated time period')
    parser.add_argument('--fix', dest='fix', action='store_true', default=False,
                        help='try to fix warnings detected on the original files')
    parser.add_argument('--fix-datamodel', dest='fix_datamodel', action='store', nargs='?', const='nccopy', type=str,
                        help='also fix warnings on data model found using NCCOPY or CDO (slow).'
                        ' Choose preferred tool per lower case argument.')
    parser.add_argument('--check', dest='check',
                        help='perform only one particular check')
    parser.add_argument('--force-copy-move', dest='force_copy_move', action='store_true', default=False,
                        help='Copy or move files despite errors')
    parser.add_argument('-V', '--version', action='version',
                        version=VERSION)
    return parser


def init_settings(**kwargs):
    parser = get_parser()
    args = parser.get_defaults()
    args.update(kwargs)
    settings.setup(args)
    return settings


def main():
    parser = get_parser()
    args = vars(parser.parse_args())
    settings.setup(args)
    summary = Summary()

    if settings.DEFINITIONS is None:
        parser.error('no definitions could be found. Check schema_path argument.')
    if settings.PATTERN is None:
        parser.error('no pattern could be found. Check schema_path argument.')
    if settings.SCHEMA is None:
        parser.error('no schema could be found. Check schema_path argument.')

    if settings.UNCHECKED_PATH:
        if not path.exists(settings.UNCHECKED_PATH):
            logger.error('UNCHECKED_PATH does not exist:', settings.UNCHECKED_PATH)
            quit()

    if settings.CHECKED_PATH:
        if not path.exists(settings.CHECKED_PATH):
            logger.error('CHECKED_PATH does not exist:', settings.CHECKED_PATH)
            quit()

    # walk over unchecked files
    for file_path in walk_files(settings.UNCHECKED_PATH):
        if path.islink(file_path):
            continue

        logger.log(CHECKING, file_path)

        if settings.INCLUDE_LIST:
            if not any(string in str(file_path) for string in settings.INCLUDE_LIST.split(',')):
                logger.log(CHECKING, ' skipped by include option.')
                continue

        if settings.EXCLUDE_LIST:
            if any(string in str(file_path) for string in settings.EXCLUDE_LIST.split(',')):
                logger.log(CHECKING, ' skipped by exclude option.')
                continue

        if file_path.suffix in settings.PATTERN['suffix']:

            file = File(file_path)
            file.open_log()

            file.match()

            # skip opening non-NetCDF files
            if file_path.suffix not in ['.nc', '.nc4']:
                continue

            # 1st pass: perform checks
            try:
                file.open_dataset()
            except OSError:
                logger.critical('Could not open file, maybe it is corrupted, or not a NetCDF file.')
                continue

            if file.matched:

                for check in checks:
                    skip = False
                    if not settings.CHECK or check.__name__ == settings.CHECK:
                        try:
                            check(file)
                        except FileWarning:
                            pass
                        except FileError:
                            pass
                        except FileCritical:
                            skip = True
                            if not settings.IGNORE_CRIT:
                                logger.info('Skip further checks.'
                                            ' Try to repair the file first before checking it again.')
                                break

                if skip:
                    file.close_dataset()
                    file.close_log()
                    continue
                else:
                    file.validate()
                    file.close_dataset()

                # log result of checks, stop if flags are set
                if file.is_clean:
                    logger.info('File has successfully passed all checks.')
                elif file.has_warnings and not file.has_errors:
                    logger.info('File passed all checks without unfixable issues.')
                elif file.has_errors:
                    logger.critical('File did not pass all checks. Unfixable issues detected.')

                if file.has_warnings and settings.STOP_WARN:
                    logger.warn('Warnings found. Exiting per -w option.')
                    sys.exit(1)

                if file.has_errors and settings.STOP_ERR:
                    logger.error('Errors found. Exiting per -e option.')
                    sys.exit(1)

                # 2nd pass: fix warnings and fixable infos
                if settings.FIX:
                    file.open_dataset(write=True)
                    if file.has_infos_fixable:
                        logger.info('Fix INFOs...')
                        file.fix_infos()
                    if file.has_warnings:
                        logger.info('Fix WARNINGs...')
                        file.fix_warnings()

                    file.close_dataset()

                # 2nd pass: fix warnings
                if file.has_warnings and settings.FIX_DATAMODEL:
                    logger.info('Fix data model...')
                    file.fix_datamodel()

                # copy/move files to checked_path
                if settings.MOVE or settings.COPY:
                    if file.is_clean or settings.FORCE_COPY_MOVE:
                        if settings.MOVE:
                            file.move()
                        elif settings.COPY:
                            file.copy()
                    else:
                        logger.warn('File has not been moved or copied due to warnings or erros found.')

                # collect stats about the file
                summary.update_specifiers(file.specifiers)
                summary.update_variables(file.specifiers)
                summary.update_experiments(file.specifiers)

            else:
                file.close_dataset()

            # close the log for this file
            file.close_log()
        else:
            logger.error('File has wrong suffix. Use "%s" for this simulation round.', settings.PATTERN['suffix'][0])

        # stop if flag is set
        if settings.FIRST_FILE:
            break

    summary.log()

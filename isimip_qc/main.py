import logging
import sys
from pathlib import Path

from isimip_utils.cli import ArgumentParser, parse_list, parse_locations, parse_path, setup_logs
from isimip_utils.exceptions import NotFound
from isimip_utils.utils import exclude_path, include_path

from . import VERSION
from .checks import checks
from .config import settings
from .exceptions import FileCritical, FileError, FileWarning
from .models import File, Summary
from .utils.files import walk_files
from .utils.logging import CHECKING

logger = logging.getLogger(__name__)


def main():
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
    parser.add_argument('--unchecked-path', dest='unchecked_path', type=parse_path, default=Path().cwd(),
                        help='base path of the unchecked files')
    parser.add_argument('--checked-path', dest='checked_path', type=parse_path, default=Path().cwd(),
                        help='base path for the checked files')
    parser.add_argument('--protocol-location', dest='protocol_locations', type=parse_locations,
                        default='https://protocol.isimip.org https://protocol2.isimip.org',
                        help='URL or file path to the protocol when different from official repository')
    parser.add_argument('--log-level', dest='log_level', default='CHECKING', type=lambda s: s.upper(),
                        help='log level (CRITICAL, ERROR, WARN, CHECKING, INFO, or DEBUG) [default: CHECKING]')
    parser.add_argument('--show-time', dest='show_time', action='store_true', default=False,
                        help='show time in console logs')
    parser.add_argument('--show-path', dest='show_path', action='store_true', default=False,
                        help='show path in console logs')
    parser.add_argument('--log-path', dest='log_path', type=parse_path,
                        help='base path for the individual log files')
    parser.add_argument('--log-path-level', dest='log_path_level', default='WARN',
                        help='log level for the individual log files [default: WARN]')
    parser.add_argument('--include', dest='include', type=parse_list,
                        help='patterns of files to include. Exclude those that don\'t match any.')
    parser.add_argument('--exclude', dest='exclude', type=parse_list,
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
    parser.add_argument('--match-only', dest='match_only', action='store_true', default=False,
                        help='only match the file name and skip all other checks')
    parser.add_argument('-r', '--minmax', dest='minmax', action='store_true', default=False,
                        help='test values for valid range (slow)')
    parser.add_argument('--minmax-values', dest='minmax_values', type=int, default=0,
                        help='number of values displayed when checking for valid range')
    parser.add_argument('-nt', '--skip-time-span-check', dest='time_span', action='store_true', default=False,
                        help='skip check for simulated time period')
    parser.add_argument('--summary', dest='summary', action='store_true', default=False,
                        help='append a summary with statistics about experiments and specifiers to the output')
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

    args = parser.parse_args()

    setup_logs(log_level=args.log_level, show_time=args.show_time, show_path=args.show_path)

    settings.from_dict(vars(args))

    summary = Summary()

    try:
        settings.DEFINITIONS, settings.PATTERN, settings.SCHEMA
    except NotFound as e:
        parser.error(f'{e} Check schema_path argument.')

    if settings.UNCHECKED_PATH:
        if not settings.UNCHECKED_PATH.exists():
            parser.error(f'UNCHECKED_PATH does not exist: {settings.UNCHECKED_PATH}')

    if settings.CHECKED_PATH:
        if not settings.CHECKED_PATH.exists():
            parser.error(f'CHECKED_PATH does not exist: {settings.CHECKED_PATH}')

    # determine checks to run and walk over unchecked files
    if settings.CHECK:
        checks_to_run = [c for c in checks if c.__name__ == settings.CHECK]
    else:
        checks_to_run = list(checks)

    # walk over unchecked files
    for file_path in walk_files(settings.UNCHECKED_PATH):
        if not check_file_path(file_path):
            continue

        logger.log(CHECKING, file_path)

        file = File(file_path)
        file.open_log()

        try:
            check_single_file(file, checks_to_run, summary)
        finally:
            # ensure that dataset and log are closed
            file.close_dataset()
            file.close_log()

        # stop if flag is set
        if settings.FIRST_FILE:
            break

    if settings.SUMMARY:
        summary.print()


def check_file_path(file_path):
    if file_path.is_symlink():
        return False

    if settings.INCLUDE:
        if not include_path(settings.INCLUDE, file_path):
            return False

    if settings.EXCLUDE:
        if exclude_path(settings.EXCLUDE, file_path):
            return False

    if file_path.suffix not in settings.PATTERN.get('suffix', []):
        logger.error('File has wrong suffix. Use "%s" for this simulation round.', settings.PATTERN['suffix'][0])
        return False

    return True


def check_single_file(file, checks_to_run, summary):
    file.match()

    if not file.matched:
        return

    file.validate()

    if settings.SUMMARY:
        summary.update_specifiers(file.specifiers)
        summary.update_variables(file.specifiers)
        summary.update_experiments(file.specifiers)

    if settings.MATCH_ONLY:
        return

    # skip opening non-NetCDF files
    if file.path.suffix not in ['.nc', '.nc4']:
        return

    # 1st pass: perform checks
    try:
        file.open_dataset()
    except OSError:
        logger.critical('Could not open file, maybe it is corrupted, or not a NetCDF file.')
        return

    skip = False
    for check in checks_to_run:
        try:
            check(file)
        except FileWarning:
            pass
        except FileError:
            pass
        except FileCritical:
            skip = True
            if not settings.IGNORE_CRIT:
                logger.info('Skip further checks. Try to repair the file first before checking it again.')
                break

    # close the dataset
    file.close_dataset()

    # skip further checks for files with critical errors
    if skip:
        return

    # log result of checks, stop if flags are set
    if file.is_clean:
        logger.info('File has successfully passed all checks.')
    elif file.has_warnings and not file.has_errors:
        logger.info('File passed all checks without unfixable issues.')
    elif file.has_errors:
        logger.critical('File did not pass all checks. Unfixable issues detected.')

    if file.has_warnings and settings.STOP_WARN:
        logger.warning('Warnings found. Exiting per -w option.')
        sys.exit(1)

    if file.has_errors and settings.STOP_ERR:
        logger.error('Errors found. Exiting per -e option.')
        sys.exit(1)

    # 2nd pass: fix warnings and fixable infos
    if settings.FIX:
        try:
            file.open_dataset(write=True)
        except OSError:
            logger.critical('Could not reopen file for writing to apply fixes.')
        else:
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
            logger.warning('File has not been moved or copied due to warnings or errors found.')

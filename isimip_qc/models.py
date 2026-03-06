import logging
import shutil
from collections import Counter
from pathlib import Path

import jsonschema
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from isimip_utils.exceptions import DidNotMatch
from isimip_utils.netcdf import (
    get_dimensions,
    get_global_attributes,
    get_variables,
    open_dataset_read,
    open_dataset_write,
)
from isimip_utils.patterns import match_file

from .config import settings
from .utils.datamodel import call_cdo, call_nccopy
from .utils.experiments import get_experiment
from .utils.files import copy_file, move_file

logger = logging.getLogger(__name__)

console = Console()

class File:

    def __init__(self, file_path):
        file_path = Path(file_path).expanduser()
        self.path = file_path.relative_to(settings.UNCHECKED_PATH)
        self.abs_path = file_path

        self.infos = []
        self.warnings = []
        self.errors = []
        self.criticals = []

        self.logger = None
        self.handler = None
        self.file_handler = None

        self.dataset = None
        self.specifiers = {}

        self.is_2d = False
        self.is_3d = False
        self.is_time_fixed = False

    @property
    def json(self):
        if self.dataset is None:
            return {
                'specifiers': self.specifiers
            }
        else:
            return {
                'dimensions': get_dimensions(self.dataset),
                'variables': get_variables(self.dataset),
                'global_attributes': get_global_attributes(self.dataset),
                'specifiers': self.specifiers
            }

    def open_log(self):
        self.logger = self.get_logger()

    def close_log(self):
        if self.handler:
            self.handler.close()

    def open_dataset(self, write=False):
        if write:
            self.dataset = open_dataset_write(self.abs_path)
        else:
            self.dataset = open_dataset_read(self.abs_path)

    def close_dataset(self):
        self.dataset.close()

    def debug(self, message, *args):
        if self.logger is not None:
            self.logger.debug(message, *args)

    def info(self, message, *args, fix=None):
        if self.logger is not None:
            self.logger.info(message, *args)

        self.infos.append((message % args, fix))

    def warning(self, message, *args, fix=None, fix_datamodel=None):
        if self.logger is not None:
            self.logger.warning(message, *args)

        self.warnings.append((message % args, fix, fix_datamodel))

    def error(self, message, *args):
        if self.logger is not None:
            self.logger.error(message, *args)

        self.errors.append(message % args)

    def critical(self, message, *args):
        if self.logger is not None:
            self.logger.critical(message, *args)

        self.criticals.append(message % args)

    def fix_infos(self):
        for info in self.infos[:]:
            _, fix = info
            if fix:
                fix['func'](*fix['args'])
                self.infos.remove(info)

    def fix_warnings(self):
        for warning in self.warnings[:]:
            _, fix, _ = warning
            if fix:
                fix['func'](*fix['args'])
                self.warnings.remove(warning)

    def fix_datamodel(self):
        # check if we need to fix using cdu
        if any(fix_datamodel for _, _, fix_datamodel in self.warnings):
            # fix using tmpfile
            tmp_abs_path = self.abs_path.parent / ('.' + self.abs_path.name + '-fix')
            if settings.FIX_DATAMODEL == 'cdo':
                if shutil.which('cdo'):
                    self.info('Rewriting file with fixed data model using "cdo"')
                    call_cdo(['--history', '-s', '-z', 'zip_5', '-f', 'nc4c', '-b', 'F32', '-k', 'grid', '-copy'],
                             self.abs_path, tmp_abs_path)
                else:
                    self.error('"cdo" is not available for execution. Please install before.')
            elif settings.FIX_DATAMODEL == 'nccopy':
                if shutil.which('nccopy'):
                    self.info('Rewriting file with fixed data model using "nccopy"')
                    call_nccopy(['-k4', '-d5'], self.abs_path, tmp_abs_path)
                else:
                    self.error('"nccopy" is not available for execution. Please install before.')
            else:
                self.error(f'"{settings.FIX_DATAMODEL}" is not a valid argument for --fix-datamodel option.'
                           ' Chose "nccopy" or "cdo"')

            if settings.FIX_DATAMODEL in ['nccopy', 'cdo']:
                # move tmp file to original file
                move_file(tmp_abs_path, self.abs_path, overwrite=True)

                # remove warnings after fix
                for warning in self.warnings[:]:
                    _, _, fix_datamodel = warning
                    if fix_datamodel:
                        self.warnings.remove(warning)

    @property
    def has_infos_fixable(self):
        for info in self.infos[:]:
            _, fix = info
            if fix:
                return bool(self.infos)

    @property
    def has_warnings(self):
        return bool(self.warnings)

    @property
    def has_errors(self):
        return bool(self.errors)

    @property
    def has_criticals(self):
        return bool(self.criticals)

    @property
    def is_clean(self):
        return not (self.has_warnings or self.has_errors or self.has_criticals)

    def get_logger(self):
        # setup a log handler for the command line and one for the file
        logger_name = str(self.path)

        logger = logging.getLogger(logger_name)
        logger.setLevel(settings.LOG_LEVEL)

        # do not propagate messages to the root logger,
        # which is configured in main()
        logger.propagate = False

        # add rich handler
        logger.addHandler(RichHandler(show_time=settings.SHOW_TIME, show_path=settings.SHOW_PATH))

        # add file handler
        if settings.LOG_PATH:
            self.handler = self.get_file_handler()
            logger.addHandler(self.handler)

        return logger

    def get_file_handler(self):
        log_name = self.path.name.split('.')[0] + '_' + settings.NOW
        log_path = (settings.LOG_PATH / self.path.parent / log_name).with_suffix('.log')
        log_path.parent.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter(' %(levelname)-9s: %(message)s')

        handler = logging.FileHandler(log_path, 'w')
        handler.setLevel(settings.LOG_PATH_LEVEL)
        handler.setFormatter(formatter)

        return handler

    def match(self):
        try:
            _, self.specifiers = match_file(settings.PATTERN, self.path)
            self.info('File matched naming scheme: %s.', self.specifiers)
            self.matched = True
        except DidNotMatch as e:
            self.error(str(e))
            self.matched = False

    def validate(self):
        try:
            jsonschema.validate(schema=settings.SCHEMA, instance=self.json)
        except jsonschema.exceptions.ValidationError as e:
            self.error('Failed to validate with JSON schema: %s\n%s', self.json, e)

    def copy(self):
        copy_file(self.abs_path, settings.CHECKED_PATH / self.path)

    def move(self):
        move_file(self.abs_path, settings.CHECKED_PATH / self.path)


class Summary:

    def __init__(self):
        self.specifiers = {}
        self.variables = {}
        self.experiments = Counter()

    def update_specifiers(self, specifiers):
        for identifier, specifier in specifiers.items():
            if identifier not in self.specifiers:
                self.specifiers[identifier] = Counter()

            self.specifiers[identifier][specifier] += 1

    def update_variables(self, specifiers):
        variable = specifiers.get('variable')
        if variable is not None:
            if variable not in self.variables:
                definition = settings.DEFINITIONS['variable'].get(variable)
                self.variables[variable] = {
                    'specifier': variable,
                    'sectors': definition.get('sectors'),
                    'count': 1
                }
            else:
                self.variables[variable]['count'] += 1

    def update_experiments(self, specifiers):
        experiment = get_experiment(specifiers)
        if experiment:
            self.experiments[experiment] += 1

    def print_specifiers(self):
        table = Table()
        table.add_column('Identifier')
        table.add_column('Specifier', style='magenta')
        table.add_column('Count', justify='right', style='cyan')

        for identifier, counter in self.specifiers.items():
            for i, (specifier, count) in enumerate(sorted(counter.items(), key=lambda x: x[1], reverse=True)):
                table.add_row(identifier if i == 0 else '', str(specifier), str(count))

        console.print(table)

    def print_variables(self):
        table = Table()
        table.add_column('Specifier', style='magenta')
        table.add_column('Sectors', style='green')
        table.add_column('Count', justify='right', style='cyan')

        for specifier, variable in sorted(self.variables.items(), key=lambda x: x[1].get('count'), reverse=True):
            table.add_row(specifier, ', '.join(variable.get('sectors')), str(variable.get('count')))

        console.print(table)

    def print_experiments(self):
        table = Table()
        table.add_column('Experiment')
        table.add_column('Count', justify='right', style='cyan')

        for experiment, count in sorted(self.experiments.items(), key=lambda x: x[1], reverse=True):
            table.add_row(experiment, str(count))

        console.print(table)

    def print(self):
        self.print_specifiers()
        self.print_variables()
        self.print_experiments()

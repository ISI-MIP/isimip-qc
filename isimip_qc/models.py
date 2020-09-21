import logging

import colorlog
import jsonschema

from .config import settings
from .utils.cdo import call_cdo
from .utils.files import copy_file, move_file
from .utils.netcdf import (get_dimensions, get_global_attributes,
                           get_variables, open_dataset_read,
                           open_dataset_write)


class File(object):

    def __init__(self, file_path):
        self.path = file_path.relative_to(settings.UNCHECKED_PATH)
        self.abs_path = file_path

        self.infos = []
        self.warnings = []
        self.errors = []

        self.logger = None
        self.handler = None
        self.file_handler = None

        self.dataset = None
        self.specifiers = {}

        self.is_2d = False
        self.is_3d = False

    @property
    def json(self):
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
        self.logger.debug(message, *args)

    def info(self, message, *args, fix=None):
        self.logger.info(message, *args)
        self.infos.append((message % args, fix))

    def warn(self, message, *args, fix=None, fix_datamodel=None):
        self.logger.warn(message, *args)
        self.warnings.append((message % args, fix, fix_datamodel))

    def error(self, message, *args, fix=None):
        self.logger.error(message, *args)
        self.errors.append((message % args, fix))

    def critical(self, message, *args):
        self.logger.critical(message, *args)

    def fix_warnings(self):
        for warning in self.warnings[:]:
            message, fix, _ = warning
            if fix:
                fix['func'](*fix['args'])
                self.warnings.remove(warning)

    def fix_datamodel(self):
        # check if we need to fix using cdu
        if any([fix_datamodel for _, _, fix_datamodel in self.warnings]):
            # fix using tmpfile
            tmp_abs_path = self.abs_path.parent / ('.' + self.abs_path.name + '-fix')
            call_cdo(['-s', '-z', 'zip_4', '-f', 'nc4c', '-b', 'F32', '-copy'], self.abs_path, tmp_abs_path)

            # move tmp file to original file
            move_file(tmp_abs_path, self.abs_path)

            # remove warnings after fix
            for warning in self.warnings[:]:
                message, _, fix_datamodel = warning
                if fix_datamodel:
                    self.warnings.remove(warning)

    @property
    def has_warnings(self):
        return bool(self.warnings)

    @property
    def has_errors(self):
        return bool(self.errors)

    @property
    def is_clean(self):
        return not (self.has_warnings or self.has_errors)

    def get_logger(self):
        # setup a log handler for the command line and one for the file
        logger_name = str(self.path)
        logger = colorlog.getLogger(logger_name)

        # do not propagate messages to the root logger,
        # which is configured in settings.setup()
        logger.propagate = False

        # add handlers
        logger.addHandler(self.get_stream_handler())
        if settings.LOG_PATH:
            self.handler = self.get_file_handler()
            logger.addHandler(self.handler)

        return logger

    def get_stream_handler(self):
        formatter = colorlog.ColoredFormatter(' %(log_color)s%(levelname)-9s: %(message)s%(reset)s')

        handler = colorlog.StreamHandler()
        handler.setLevel(settings.LOG_LEVEL)
        handler.setFormatter(formatter)

        return handler

    def get_file_handler(self):
        log_path = settings.LOG_PATH / self.path.with_suffix('.log')
        log_path.parent.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter(' %(levelname)-9s: %(message)s')

        handler = logging.FileHandler(log_path, 'w')
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)

        return handler

    def match(self):
        match = settings.PATTERN['file'].match(self.path.name)
        if match:
            for key, value in match.groupdict().items():
                if value is not None:
                    if value.isdigit():
                        self.specifiers[key] = int(value)
                    else:
                        self.specifiers[key] = value

            self.info('File matched: %s.', self.specifiers)
        else:
            self.error('File did not match.')

    def validate(self):
        try:
            jsonschema.validate(schema=settings.SCHEMA, instance=self.json)
        except jsonschema.exceptions.ValidationError as e:
            self.error('Failed to validate with JSON schema: %s\n%s', self.json, e)

    def copy(self):
        copy_file(self.abs_path, settings.CHECKED_PATH / self.path)

    def move(self):
        move_file(self.abs_path, settings.CHECKED_PATH / self.path)

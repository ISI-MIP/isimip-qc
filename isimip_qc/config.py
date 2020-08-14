import configparser
import logging
import os
from pathlib import Path

from .utils.fetch import fetch_pattern, fetch_schema

DEFAULT_PATTERN_LOCATIONS = ['https://protocol.isimip.org/pattern/']
DEFAULT_SCHEMA_LOCATIONS = ['https://protocol.isimip.org/schema/']

logger = logging.getLogger(__name__)


class Settings(object):

    _shared_state = {}

    CONFIG_FILES = [
        'isimip.conf',
        '~/.isimip.conf',
        '/etc/isimip.conf'
    ]

    ATTRS = [
        'MOVE',
        'COPY',
        'UNCHECKED_PATH',
        'CHECKED_PATH',
        'PATTERN_LOCATIONS',
        'SCHEMA_LOCATIONS',
        'LOG_LEVEL',
        'LOG_PATH',
        'FIRST_FILE'
    ]

    def __init__(self):
        self.__dict__ = self._shared_state

    def __str__(self):
        return str(vars(self))

    def setup(self, args):
        # read config file
        config = self.read_config(args.config_file)

        # combine settings from args, os.environ, and config
        self.combine_settings(args, os.environ, config)

        # set create pathes and set default values
        if self.UNCHECKED_PATH is not None:
            self.UNCHECKED_PATH = Path(self.UNCHECKED_PATH).expanduser()
        else:
            self.UNCHECKED_PATH = Path().cwd()

        if self.CHECKED_PATH is not None:
            self.CHECKED_PATH = Path(self.CHECKED_PATH).expanduser()

        if self.PATTERN_LOCATIONS is not None:
            self.PATTERN_LOCATIONS = self.PATTERN_LOCATIONS.split()
        else:
            self.PATTERN_LOCATIONS = DEFAULT_PATTERN_LOCATIONS

        if self.SCHEMA_LOCATIONS is not None:
            self.SCHEMA_LOCATIONS = self.SCHEMA_LOCATIONS.split()
        else:
            self.SCHEMA_LOCATIONS = DEFAULT_SCHEMA_LOCATIONS

        if self.LOG_LEVEL is not None:
            self.LOG_LEVEL = self.LOG_LEVEL.upper()
        else:
            self.LOG_LEVEL = 'WARN'

        if self.LOG_PATH is not None:
            self.LOG_PATH = Path(self.LOG_PATH).expanduser()

        # setup logs
        logging.basicConfig(level=self.LOG_LEVEL,
                            format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')

        # set the path
        self.SCHEMA_PATH = Path(args.schema_path)

        # fetch pattern and schema
        self.PATTERN = fetch_pattern(self.PATTERN_LOCATIONS, self.SCHEMA_PATH)
        self.SCHEMA = fetch_schema(self.SCHEMA_LOCATIONS, self.SCHEMA_PATH)

        # log settings
        logger.debug(self)

    def read_config(self, config_file_arg):
        if config_file_arg:
            config = configparser.ConfigParser()
            config.read(config_file_arg)
            if 'isimip-qc' in config:
                return config['isimip-qc']
        else:
            for config_file in self.CONFIG_FILES:
                config_path = Path(config_file).expanduser()
                if config_path.is_file():
                    config = configparser.ConfigParser()
                    config.read(config_path)
                    if 'isimip-qc' in config:
                        return config['isimip-qc']

    def combine_settings(self, args, environ, config):
        for attr in self.ATTRS:
            if hasattr(args, attr.lower()) and getattr(args, attr.lower()) is not None:
                setattr(self, attr, getattr(args, attr.lower()))
            elif attr in environ:
                setattr(self, attr, environ[attr])
            elif config is not None and attr.lower() in config:
                setattr(self, attr, config[attr.lower()])
            else:
                setattr(self, attr, None)


settings = Settings()

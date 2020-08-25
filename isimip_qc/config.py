import configparser
import os
from pathlib import Path

import colorlog
from dotenv import load_dotenv

from .utils.fetch import fetch_pattern, fetch_schema

logger = colorlog.getLogger(__name__)


class Settings(object):

    _shared_state = {}

    CONFIG_FILES = [
        'isimip.conf',
        '~/.isimip.conf',
        '/etc/isimip.conf'
    ]

    DEFAULTS = {
        'LOG_LEVEL': 'WARN',
        'PATTERN_LOCATIONS': 'https://protocol.isimip.org/pattern/',
        'SCHEMA_LOCATIONS': 'https://protocol.isimip.org/pattern/'
    }

    def __init__(self):
        self.__dict__ = self._shared_state

    def __str__(self):
        return str(vars(self))

    def setup(self, args):
        # setup env from .env file
        load_dotenv(Path().cwd() / '.env')

        # read config file
        config = self.read_config(args.config_file)

        # combine settings from args, os.environ, and config
        self.build_settings(args, os.environ, config)

        # set create pathes and set default values
        if self.UNCHECKED_PATH is not None:
            self.UNCHECKED_PATH = Path(self.UNCHECKED_PATH).expanduser()
        else:
            self.UNCHECKED_PATH = Path().cwd()

        if self.CHECKED_PATH is not None:
            self.CHECKED_PATH = Path(self.CHECKED_PATH).expanduser()

        self.LOG_LEVEL = self.LOG_LEVEL.upper()
        if self.LOG_PATH is not None:
            self.LOG_PATH = Path(self.LOG_PATH).expanduser()

        # setup logs
        colorlog.basicConfig(level=self.LOG_LEVEL,
                             format=' %(log_color)s%(levelname)-8s : %(message)s%(reset)s')

        # set the path
        self.SCHEMA_PATH = Path(args.schema_path)

        # fetch pattern and schema
        self.PATTERN = fetch_pattern(self.PATTERN_LOCATIONS.split(), self.SCHEMA_PATH)
        self.SCHEMA = fetch_schema(self.SCHEMA_LOCATIONS.split(), self.SCHEMA_PATH)

        # log settings
        colorlog.debug(self)

    def read_config(self, config_file_arg):
        config_files = [config_file_arg] + self.CONFIG_FILES
        for config_file in config_files:
            if config_file:
                config = configparser.ConfigParser()
                config.read(config_file)
                if 'isimip-qc' in config:
                    return config['isimip-qc']

    def build_settings(self, args, environ, config):
        args_dict = vars(args)
        for key, value in args_dict.items():
            if key not in ['config_file']:
                attr = key.upper()
                if value is not None:
                    attr_value = value
                elif environ.get(attr):
                    attr_value = environ.get(attr)
                elif config and config.get(key):
                    attr_value = config.get(key)
                else:
                    attr_value = self.DEFAULTS.get(attr)

                setattr(self, attr, attr_value)


settings = Settings()

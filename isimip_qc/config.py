from pathlib import Path

import colorlog

from isimip_utils.config import ISIMIPSettings
from isimip_utils.decorators import cached_property
from isimip_utils.fetch import fetch_definitions, fetch_pattern, fetch_schema

from datetime import datetime

logger = colorlog.getLogger(__name__)


class Settings(ISIMIPSettings):

    def setup(self, parser):
        super().setup(parser)

        self.NOW = datetime.utcnow().strftime("%Y%m%dT%H%MZ")

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

        # set the simulation_round, product and sector
        self.SIMULATION_ROUND, self.PRODUCT, self.SECTOR = Path(self.SCHEMA_PATH).parts[0:3]

        # log settings
        colorlog.debug(self)

    @cached_property
    def DEFINITIONS(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_definitions(self.PROTOCOL_LOCATIONS.split(), self.SCHEMA_PATH)

    @cached_property
    def PATTERN(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_pattern(self.PROTOCOL_LOCATIONS.split(), self.SCHEMA_PATH)

    @cached_property
    def SCHEMA(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_schema(self.PROTOCOL_LOCATIONS.split(), self.SCHEMA_PATH)


settings = Settings()

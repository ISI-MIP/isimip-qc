from datetime import datetime
from pathlib import Path

from isimip_utils.config import Settings as BaseSettings
from isimip_utils.fetch import fetch_definitions, fetch_pattern, fetch_schema
from isimip_utils.utils import cached_property


class Settings(BaseSettings):

    @cached_property
    def NOW(self):
        return datetime.utcnow().strftime("%Y%m%dT%H%MZ")

    @cached_property
    def SIMULATION_ROUND(self):
        return Path(self.SCHEMA_PATH).parts[0]

    @cached_property
    def PRODUCT(self):
        return Path(self.SCHEMA_PATH).parts[1]

    @cached_property
    def SECTOR(self):
        return Path(self.SCHEMA_PATH).parts[2]

    @cached_property
    def DEFINITIONS(self):
        if self.PROTOCOL_LOCATIONS is None:
            raise RuntimeError('PROTOCOL_LOCATIONS is not set')
        return fetch_definitions(self.SCHEMA_PATH, self.PROTOCOL_LOCATIONS.split())

    @cached_property
    def PATTERN(self):
        if self.PROTOCOL_LOCATIONS is None:
            raise RuntimeError('PROTOCOL_LOCATIONS is not set')
        return fetch_pattern(self.SCHEMA_PATH, self.PROTOCOL_LOCATIONS.split())

    @cached_property
    def SCHEMA(self):
        if self.PROTOCOL_LOCATIONS is None:
            raise RuntimeError('PROTOCOL_LOCATIONS is not set')
        return fetch_schema(self.SCHEMA_PATH, self.PROTOCOL_LOCATIONS.split())


settings = Settings()

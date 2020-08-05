import logging
from datetime import date

from .config import settings


class File(object):

    def __init__(self, file_path):
        self.path = file_path.relative_to(settings.UNCHECKED_PATH)
        self.abs_path = file_path
        self.identifiers = {}
        self.clean = True
        self.logger_name = str(self.path)
        self.setup_logger()

        self.info('File %s found.', self.abs_path)

    def info(self, *args, **kwargs):
        logging.getLogger(self.logger_name).info(*args, **kwargs)

    def warn(self, *args, **kwargs):
        logging.getLogger(self.logger_name).warn(*args, **kwargs)

    def error(self, *args, **kwargs):
        logging.getLogger(self.logger_name).error(*args, **kwargs)
        self.clean = False  # this file should not be moved!

    def setup_logger(self):
        # setup a log handler for the command line and one for the file
        logger = logging.getLogger(self.logger_name)

        # do not propagate messages to the root logger,
        # which is configured in settings.setup()
        logger.propagate = False

        # set the log level to INFO, so that it is not influeced by settings.LOG_LEVEL
        logger.setLevel(logging.INFO)

        # add handlers
        logger.addHandler(self.get_stream_handler())
        if settings.LOG_PATH:
            logger.addHandler(self.get_file_handler())

    def get_stream_handler(self):
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')

        handler = logging.StreamHandler()
        handler.setLevel(settings.LOG_LEVEL)
        handler.setFormatter(formatter)

        return handler

    def get_file_handler(self):
        log_path = settings.LOG_PATH / date.today().strftime("%Y%m%d") / self.path.with_suffix('.log')
        log_path.parent.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

        handler = logging.FileHandler(log_path)
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)

        return handler

    def match_identifiers(self):
        match = settings.PATTERN['file'].match(self.path.name)
        if match:
            for key, value in match.groupdict().items():
                if value is not None:
                    if value.isdigit():
                        self.identifiers[key] = int(value)
                    else:
                        self.identifiers[key] = value

            self.info('File matched: %s.', self.identifiers)
        else:
            self.error('File did not match.')

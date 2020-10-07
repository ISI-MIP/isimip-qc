class FileWarning(Exception):

    def __init__(self, file, message, *args, **kwargs):
        file.warn(message, *args, **kwargs)
        super().__init__(message % args)


class FileError(Exception):

    def __init__(self, file, message, *args, **kwargs):
        file.error(message, *args, **kwargs)
        super().__init__(message % args)


class FileCritical(Exception):

    def __init__(self, file, message, *args, **kwargs):
        file.critical(message, *args, **kwargs)
        super().__init__(message % args)

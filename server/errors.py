import logging
from functools import wraps
from typing import Callable

from server.settings import settings
from tornado.web import HTTPError

APP_NOT_FOUND_MESSAGE = 'Application not found'
UNEXPECTED_PARAM_MESSAGE = 'Unexpected param'


class AppStorageException(Exception):
    reason: str
    status_code = 400

    def __init__(self, *args, **kwargs):
        super().__init__(self.reason)


class RequiredFileNotFoundError(AppStorageException):
    reason = 'Missing one or more required files'


class InvalidPackageSizeError(AppStorageException):
    reason = f'Package size should be less than {settings.MAX_PACKAGE_SIZE_MB} MB'


class EmptyRequiredFileError(AppStorageException):
    reason = 'One of required files is empty'


class ApplicationInitError(AppStorageException):
    reason = 'Exceeded tries count for app creation: lack of unique ids'


def handle_internal_error(func) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        handler = args[0]

        try:
            await func(*args, **kwargs)
        except Exception as error:
            if isinstance(error, (HTTPError, AppStorageException)):
                message = error.reason
                handler.handle_client_error(status=error.status_code, error=message)
            else:
                message = str(error)
                handler.handle_internal_error(error=message)

            logging.error(message)

    return wrapper

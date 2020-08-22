from server.settings import settings


class AppStorageException(Exception):
    reason: str

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

from server.settings import settings


class RequiredFileNotFoundError(Exception):
    reason = "Missing one of more required files"


class InvalidPackageSizeError(Exception):
    reason = f"Package size should be less than {settings.MAX_PACKAGE_SIZE_MB} MB"


class EmptyRequiredFileError(Exception):
    reason = "One of required files is empty"


class ApplicationInitError(Exception):
    reason = "Exceeded tries count for app creation: lack of unique ids"

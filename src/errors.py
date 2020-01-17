from src.consts import MAX_PACKAGE_SIZE_MB


class RequiredFileNotFoundError(Exception):
    reason = 'Missing one of more required files'


class InvalidPackageSizeError(Exception):
    reason = f'Package size should be less than {MAX_PACKAGE_SIZE_MB} MB'


class EmptyRequiredFileError(Exception):
    reason = 'One of required files is empty'

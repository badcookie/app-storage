from functools import reduce
from typing import TYPE_CHECKING, List

from server import errors
from server.settings import settings

if TYPE_CHECKING:
    from zipfile import ZipFile


ENTRYPOINT_PATH_VARIABLE_NAME = 'ENTRYPOINT'
APP_NAME_VARIABLE_NAME = 'APP_NAME'
APP_DESCRIPTION_VARIABLE_NAME = 'APP_DESCRIPTION'

ENV_FILE_NAME = 'env'
REQUIREMENTS_FILE_NAME = 'requirements.txt'

REQUIRED_FILES = [REQUIREMENTS_FILE_NAME, ENV_FILE_NAME]


def mb_to_bytes(mb: int) -> int:
    return mb * 1024 * 1024


def get_package_size_bytes(package: 'ZipFile') -> int:
    files = package.filelist
    return reduce(lambda acc, file: acc + file.file_size, files, 0)


def required_files_included(package: 'ZipFile') -> bool:
    package_filenames = package.namelist()
    return set(REQUIRED_FILES).issubset(package_filenames)


def package_size_valid(package: 'ZipFile') -> bool:
    package_size_bytes = get_package_size_bytes(package)
    max_valid_size_bytes = mb_to_bytes(settings.MAX_PACKAGE_SIZE_MB)
    return package_size_bytes < max_valid_size_bytes


def required_files_not_empty(package: 'ZipFile') -> bool:
    empty_files = [
        filename
        for filename in REQUIRED_FILES
        if package.getinfo(filename).file_size == 0
    ]
    return len(empty_files) == 0


def required_configuration_included(package: 'ZipFile') -> bool:
    env_data = package.read(ENV_FILE_NAME)
    decoded_data = env_data.decode()

    lines = [line for line in decoded_data.split('\n') if line]
    for line in lines:
        key, value = line.split('=')
        if key == ENTRYPOINT_PATH_VARIABLE_NAME:
            return True

    return False


def database_configuration_included(package: 'ZipFile') -> bool:
    env_data = package.read(ENV_FILE_NAME)
    decoded_data = env_data.decode()

    lines = [line for line in decoded_data.split('\n') if line]

    expected_params = {'DB_PORT': None, 'DB_PASSWORD': None, 'DB_USER': None}

    for line in lines:
        key, value = line.split('=')
        if key in expected_params:
            expected_params[key] = value

    expected_params_values = list(expected_params.values())
    return all(param is not None for param in expected_params_values)


VALIDATION_RULES = [
    {
        'constraint': required_files_included,
        'exception': errors.RequiredFileNotFoundError,
    },
    {'constraint': package_size_valid, 'exception': errors.InvalidPackageSizeError},
    {
        'constraint': required_files_not_empty,
        'exception': errors.EmptyRequiredFileError,
    },
    {
        'constraint': required_configuration_included,
        'exception': errors.InvalidConfiguration,
    },
]


DB_VALIDATION_RULES = [
    *VALIDATION_RULES,
    {
        'constraint': database_configuration_included,
        'exception': errors.DBConfigurationError,
    },
]


def get_validation_rules(create_db_instance: bool) -> List[dict]:
    return DB_VALIDATION_RULES if create_db_instance else VALIDATION_RULES

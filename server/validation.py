from functools import reduce
from typing import TYPE_CHECKING

from server.exceptions import (
    EmptyRequiredFileError,
    InvalidPackageSizeError,
    RequiredFileNotFoundError,
)
from server.settings import settings

if TYPE_CHECKING:
    from zipfile import ZipFile


required_files = ['requirements.txt', 'application.py']


def mb_to_bytes(mb: int) -> int:
    return mb * 1024 * 1024


def get_package_size_bytes(package: 'ZipFile') -> int:
    files = package.filelist
    return reduce(lambda acc, file: acc + file.file_size, files, 0)


def required_files_included(package: 'ZipFile') -> bool:
    package_filenames = package.namelist()
    return set(required_files).issubset(package_filenames)


def package_size_valid(package: 'ZipFile') -> bool:
    package_size_bytes = get_package_size_bytes(package)
    max_valid_size_bytes = mb_to_bytes(settings.MAX_PACKAGE_SIZE_MB)
    return package_size_bytes < max_valid_size_bytes


def required_files_not_empty(package: 'ZipFile') -> bool:
    empty_files = [
        *filter(
            lambda filename: package.getinfo(filename).file_size == 0, required_files
        )
    ]
    return len(empty_files) == 0


VALIDATION_RULES = [
    {'constraint': required_files_included, 'exception': RequiredFileNotFoundError},
    {'constraint': package_size_valid, 'exception': InvalidPackageSizeError},
    {'constraint': required_files_not_empty, 'exception': EmptyRequiredFileError},
]

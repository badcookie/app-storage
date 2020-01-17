import pytest
from os.path import join
from zipfile import ZipFile

from src import errors
from src.consts import MAX_PACKAGE_SIZE_MB
from src.utils import get_package_size_bytes, mb_to_bytes
from src.environment import validate_package, create_application_environment


required_files = ['application.py', 'requirements.txt']


def required_files_included(package: 'ZipFile') -> bool:
    package_filenames = package.namelist()
    return set(required_files).issubset(package_filenames)


def package_size_valid(package: 'ZipFile') -> bool:
    package_size_bytes = get_package_size_bytes(package)
    max_valid_size_bytes = mb_to_bytes(MAX_PACKAGE_SIZE_MB)
    return package_size_bytes < max_valid_size_bytes


def required_files_not_empty(package: 'ZipFile') -> bool:
    empty_files = [
        *filter(
            lambda filename: package.getinfo(filename).file_size == 0,
            required_files
        )
    ]
    return len(empty_files) == 0


validation_rules = [
    {
        'constraint': required_files_included,
        'exception': errors.RequiredFileNotFoundError,
    },
    {
        'constraint': package_size_valid,
        'exception': errors.InvalidPackageSizeError,
    },
    {
        'constraint': required_files_not_empty,
        'exception': errors.EmptyRequiredFileError,
    },
]


def build_package_path(package_name: str) -> str:
    fixtures_dir = 'fixtures'
    filename = f'{package_name}.zip'
    return join(fixtures_dir, filename)


def get_package(package_name: str) -> 'ZipFile':
    package_path = build_package_path(package_name)
    return ZipFile(package_path)


def test_valid_package():
    package = get_package('valid-package')
    validate_package(package, validation_rules)
    assert True


def test_package_validation_with__missing_required_file():
    package = get_package('package-with-missing-file')
    with pytest.raises(errors.RequiredFileNotFoundError):
        validate_package(package, validation_rules)


def test_package_validation_with_empty_required_file():
    package = get_package('package-with-empty-required-file')
    with pytest.raises(errors.EmptyRequiredFileError):
        validate_package(package, validation_rules)


def test_package_with_invalid_size():
    package = get_package('heavy-package')
    with pytest.raises(errors.InvalidPackageSizeError):
        validate_package(package, validation_rules)

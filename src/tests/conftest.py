import pytest
from shutil import rmtree
from os import path, mkdir
from zipfile import ZipFile

from src.utils import get_package_size_bytes, mb_to_bytes
from src.consts import MAX_PACKAGE_SIZE_MB, DEFAULT_APPS_BASE_DIR
from src.errors import (
    RequiredFileNotFoundError,
    InvalidPackageSizeError,
    EmptyRequiredFileError,
)


required_files = ['application.py', 'requirements.txt']


def build_package_path(package_name: str) -> str:
    fixtures_dir = 'fixtures'
    filename = f'{package_name}.zip'
    return path.join(fixtures_dir, filename)


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


@pytest.fixture
def validation_rules():
    return [
        {
            'constraint': required_files_included,
            'exception': RequiredFileNotFoundError,
        },
        {
            'constraint': package_size_valid,
            'exception': InvalidPackageSizeError,
        },
        {
            'constraint': required_files_not_empty,
            'exception': EmptyRequiredFileError,
        },
    ]


@pytest.fixture
def get_package():
    cache = []

    def getter(package_name: str) -> 'ZipFile':
        package_path = build_package_path(package_name)
        package = ZipFile(package_path)
        cache.append(package)
        return package

    yield getter

    cached_package, = cache
    cached_package.close()


@pytest.fixture(scope='session', autouse=True)
def create_apps_directory():
    mkdir(DEFAULT_APPS_BASE_DIR)
    yield
    rmtree(DEFAULT_APPS_BASE_DIR)

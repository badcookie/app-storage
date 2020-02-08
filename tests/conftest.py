import os
import shutil
import pytest
from zipfile import ZipFile

from src.errors import (
    RequiredFileNotFoundError,
    InvalidPackageSizeError,
    EmptyRequiredFileError,
)
from src.consts import MAX_PACKAGE_SIZE_MB, APPS_DIR
from src.utils import get_package_size_bytes, mb_to_bytes


required_files = ['requirements.txt']


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
    cache = {}

    def getter(package_name: str) -> 'ZipFile':
        fixture_path = os.path.join(
            os.path.dirname(__file__), 'fixtures', package_name
        )
        package_path = shutil.make_archive(
            fixture_path, 'zip', fixture_path
        )
        package = ZipFile(package_path)
        cache[package_path] = package
        return package

    yield getter

    package_dir, = cache
    cache[package_dir].close()
    os.remove(package_dir)


@pytest.fixture(scope='session', autouse=True)
def create_apps_directory():
    yield os.mkdir(APPS_DIR)
    shutil.rmtree(APPS_DIR)


@pytest.fixture
def get_items_generator():
    def getter(collection):
        for item in collection:
            yield item

    return getter

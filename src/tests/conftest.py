import pytest
from os.path import join
from zipfile import ZipFile


def build_package_path(package_name: str) -> str:
    fixtures_dir = 'fixtures'
    filename = f'{package_name}.zip'
    return join(fixtures_dir, filename)


@pytest.yield_fixture
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

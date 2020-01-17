from os.path import join
from zipfile import ZipFile


def build_package_path(package_name: str) -> str:
    fixtures_dir = 'fixtures'
    filename = f'{package_name}.zip'
    return join(fixtures_dir, filename)


def get_package(package_name: str) -> 'ZipFile':
    package_path = build_package_path(package_name)
    return ZipFile(package_path)

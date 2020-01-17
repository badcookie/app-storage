from zipfile import ZipFile
from typing import List, Optional


max_package_size_mb = 5

required_files = ['application.py', 'requirements.txt']


def required_files_included(package: 'ZipFile') -> bool:
    package_filenames = package.namelist()
    return set(required_files).issubset(package_filenames)


def package_size_valid(package: 'ZipFile') -> bool:
    pass


validation_rules = [
    {
        'constraint': required_files_included,
        'at_fail': {
            'exception': None,
            'message': 'Missing required files'
        },
    },
    {
        'constraint': package_size_valid,
        'at_fail': {
            'exception': None,
            'message': f'Package size should be less than {max_package_size_mb} MB'
        }
    }
]


def validate_package(package: 'ZipFile', rules: List[bool]) -> Optional[list]:
    pass


def create_application_environment():
    pass

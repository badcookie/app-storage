from typing import List
from zipfile import ZipFile


def validate_package(package: 'ZipFile', rules: List[dict]) -> None:
    for rule in rules:
        constraint_is_fulfilled = rule['constraint']
        if not constraint_is_fulfilled(package):
            exception = rule['exception']
            raise exception


def create_application_environment():
    pass

import pytest

from src import errors
from src.environment import validate_package, create_application_environment


def test_valid_package(get_package, validation_rules):
    package = get_package('valid-package')
    validate_package(package, validation_rules)
    assert True


def test_package_validation_with__missing_required_file(get_package, validation_rules):
    package = get_package('package-with-missing-file')
    with pytest.raises(errors.RequiredFileNotFoundError):
        validate_package(package, validation_rules)


def test_package_validation_with_empty_required_file(get_package, validation_rules):
    package = get_package('package-with-empty-required-file')
    with pytest.raises(errors.EmptyRequiredFileError):
        validate_package(package, validation_rules)


def test_package_with_invalid_size(get_package, validation_rules):
    package = get_package('heavy-package')
    with pytest.raises(errors.InvalidPackageSizeError):
        validate_package(package, validation_rules)


def test_environment_creation(get_package, validation_rules):
    package = get_package('valid-package')
    validate_package(package, validation_rules)

    create_application_environment(package)

import pytest
from os import path, listdir

from src import errors
from src.consts import DEFAULT_APPS_BASE_DIR
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

    app_id = create_application_environment(package)
    app_dirpath = path.join(DEFAULT_APPS_BASE_DIR, app_id)
    assert path.exists(app_dirpath)

    extracted_files = listdir(app_dirpath)
    assert len(extracted_files) != 0

    venv_path = path.join(app_dirpath, 'venv')
    assert path.exists(venv_path)

    installed_packages = listdir(venv_path)
    assert len(installed_packages) != 0


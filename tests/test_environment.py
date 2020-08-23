import os
from unittest.mock import patch

import pytest
from server import errors
from server.services import (
    create_app_directory,
    create_application_environment,
    generate_app_uid,
    validate_package,
)
from server.settings import settings


def test_valid_package(get_package, validation_rules):
    package = get_package('valid_app')
    validate_package(package, validation_rules)
    assert True


def test_package_validation_with_missing_required_file(get_package, validation_rules):
    package = get_package('app_with_missing_file')
    with pytest.raises(errors.RequiredFileNotFoundError):
        validate_package(package, validation_rules)


def test_package_validation_with_empty_required_file(get_package, validation_rules):
    package = get_package('app_with_empty_file')
    with pytest.raises(errors.EmptyRequiredFileError):
        validate_package(package, validation_rules)


def test_package_with_invalid_size(get_package, validation_rules):
    package = get_package('heavy_app')
    with pytest.raises(errors.InvalidPackageSizeError):
        validate_package(package, validation_rules)


def test_successful_app_init_from_first_try():
    app_dir = create_app_directory()
    assert os.path.exists(app_dir)


@patch('server.services.generate_app_uid')
def test_successful_app_init_from_nth_try(app_id_generator_mock, get_items_generator):
    app_ids = [generate_app_uid() for _ in range(settings.APP_ID_CREATION_TRIES_COUNT)]

    for uid in app_ids[:-1]:
        os.mkdir(os.path.join(settings.apps_path, uid))

    items_generator = get_items_generator(app_ids)

    app_id_generator_mock.side_effect = lambda: next(items_generator)
    app_dir = create_app_directory()
    assert os.path.exists(app_dir)


@patch('server.services.generate_app_uid')
def test_failed_app_init(app_id_generator_mock, get_items_generator):
    app_ids = [generate_app_uid() for _ in range(settings.APP_ID_CREATION_TRIES_COUNT)]

    for uid in app_ids:
        os.mkdir(os.path.join(settings.apps_path, uid))

    items_generator = get_items_generator(app_ids)

    app_id_generator_mock.side_effect = lambda: next(items_generator)
    with pytest.raises(errors.ApplicationInitError):
        create_app_directory()


def test_environment_creation(get_package, validation_rules):
    package = get_package('valid_app')
    validate_package(package, validation_rules)

    app_id = create_application_environment(package)
    app_dirpath = os.path.join(settings.apps_path, app_id)
    assert os.path.exists(app_dirpath)

    extracted_files = os.listdir(app_dirpath)
    assert len(extracted_files) != 0

    venv_path = os.path.join(app_dirpath, 'venv')
    assert os.path.exists(venv_path)

    bin_path = os.path.join(venv_path, 'bin')
    assert 'flask' in os.listdir(bin_path)

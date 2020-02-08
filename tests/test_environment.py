import os
import pytest
from unittest.mock import patch

from src import errors
from src.lib.environment import (
    init_app,
    generate_app_id,
    validate_package,
    create_application_environment,
)
from src.consts import APPS_DIR, APP_ID_CREATION_TRIES_COUNT


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
    app_dir = init_app()
    assert os.path.exists(app_dir)


@patch('src.lib.environment.generate_app_id')
def test_successful_app_init_from_nth_try(app_id_generator_mock, get_items_generator):
    app_ids = [
        generate_app_id()
        for _ in range(APP_ID_CREATION_TRIES_COUNT)
    ]

    for uid in app_ids[:-1]:
        os.mkdir(os.path.join(APPS_DIR, uid))

    items_generator = get_items_generator(app_ids)

    app_id_generator_mock.side_effect = lambda: next(items_generator)
    app_dir = init_app()
    assert os.path.exists(app_dir)


@patch('src.lib.environment.generate_app_id')
def test_failed_app_init(app_id_generator_mock, get_items_generator):
    app_ids = [
        generate_app_id()
        for _ in range(APP_ID_CREATION_TRIES_COUNT)
    ]

    for uid in app_ids:
        os.mkdir(os.path.join(APPS_DIR, uid))

    items_generator = get_items_generator(app_ids)

    app_id_generator_mock.side_effect = lambda: next(items_generator)
    with pytest.raises(errors.ApplicationInitError):
        init_app()


def test_environment_creation(get_package, validation_rules):
    package = get_package('valid_app')
    validate_package(package, validation_rules)

    app_id = create_application_environment(package)
    app_dirpath = os.path.join(APPS_DIR, app_id)
    assert os.path.exists(app_dirpath)

    extracted_files = os.listdir(app_dirpath)
    assert len(extracted_files) != 0

    venv_path = os.path.join(app_dirpath, 'venv')
    assert os.path.exists(venv_path)

    bin_path = os.path.join(venv_path, 'bin')
    assert 'flask' in os.listdir(bin_path)

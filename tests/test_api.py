import json
from os import path

import pytest
from requests import Request
from server.settings import settings
from server.validation import APP_DESCRIPTION_VARIABLE_NAME, APP_NAME_VARIABLE_NAME

TESTS_DIR = path.dirname(__file__)
FIXTURES_DIR = path.join(TESTS_DIR, 'fixtures')


@pytest.fixture(autouse=True)
async def teardown_unit(app):
    yield
    configurator = app.settings['configurator']
    await configurator.reset_configuration()


@pytest.fixture
def routes(base_url):
    return {
        'app_list': lambda: f'{base_url}/applications/',
        'app_detail': lambda app_id: f'{base_url}/applications/{app_id}/',
    }


@pytest.fixture
def prepare_send_file_request(get_package, routes):
    def _(filename: str) -> dict:
        get_package(filename)

        filename_with_ext = f'{filename}.zip'
        filepath = path.join(FIXTURES_DIR, filename_with_ext)
        absolute_filepath = path.abspath(filepath)

        zipfile = open(absolute_filepath, 'rb')
        files = {'zipfile': zipfile}

        url = routes['app_list']()
        request = Request(url=url, files=files)
        prepared_request = request.prepare()
        content_type = prepared_request.headers.get('Content-Type')
        headers = {'Content-Type': content_type}

        return {
            'body': prepared_request.body,
            'headers': headers,
        }

    return _


@pytest.mark.gen_test(timeout=90)
async def test_successful_app_lifecycle(
    prepare_send_file_request, http_client, routes, app,
):
    repo = app.settings['repository']
    configurator = app.settings['configurator']

    request_data = prepare_send_file_request('valid_app')
    assert request_data

    list_url = routes['app_list']()
    response = await http_client.fetch(
        list_url, method='POST', **request_data, raise_error=False, request_timeout=90,
    )
    assert response.code == 201

    response_body = response.body.decode()
    app_data = json.loads(response_body)

    app_port = app_data['port']
    app_id = app_data['id']
    app_uid = app_data['uid']

    app_url = f'http://localhost:{app_port}/'
    app_response = await http_client.fetch(app_url, method='GET', raise_error=False)
    response_data = app_response.body.decode()
    assert response_data == 'It works'

    stored_environment_vars = await configurator.get_app_environment_data(app_uid)
    old_modification_ts = stored_environment_vars.pop(configurator.MODIFIED_AT_ENV_NAME)

    expected_environment_vars = {'ENTRYPOINT': 'application', 'ABC': '5'}
    assert stored_environment_vars == expected_environment_vars

    app_path = path.join(settings.apps_path, app_uid)

    saved_app = await repo.get(id=app_id)
    assert saved_app and saved_app.uid == app_uid

    assert path.exists(app_path)

    detail_url = routes['app_detail'](app_id)

    update_request_data = prepare_send_file_request('another_valid_app')
    assert update_request_data

    response = await http_client.fetch(
        detail_url,
        method='PUT',
        **update_request_data,
        raise_error=False,
        request_timeout=90,
    )
    assert response.code == 200
    assert path.exists(app_path)

    updated_data = json.loads(response.body.decode())
    updated_app = await repo.get(id=app_id)

    assert updated_app.name == updated_data['name']
    assert updated_app.description == updated_data['description']

    stored_environment_vars = await configurator.get_app_environment_data(app_uid)
    expected_environment_vars = {
        'TEST_ENV': '2',
        f'{APP_NAME_VARIABLE_NAME}': updated_app.name,
        f'{APP_DESCRIPTION_VARIABLE_NAME}': updated_app.description,
        'ENTRYPOINT': 'application',
    }
    new_modification_ts = stored_environment_vars.pop(configurator.MODIFIED_AT_ENV_NAME)

    assert stored_environment_vars == expected_environment_vars
    assert new_modification_ts != old_modification_ts

    app_url = f'http://localhost:{app_port}/'
    app_response = await http_client.fetch(app_url, method='GET', raise_error=False)
    response_data = app_response.body.decode()
    assert response_data == expected_environment_vars['TEST_ENV']

    book_id = 5
    app_detail_url = f'http://localhost:{app_port}/books/{book_id}/'
    app_response = await http_client.fetch(
        app_detail_url, method='DELETE', raise_error=False
    )
    response_data = app_response.body.decode()
    assert response_data == str(book_id)

    response = await http_client.fetch(detail_url, method='DELETE', raise_error=False)
    assert response.code == 204

    deleted_app = await repo.get(id=app_id)
    assert deleted_app is None

    assert not path.exists(app_path)

    with pytest.raises(ConnectionRefusedError):
        await http_client.fetch(app_url, method='GET', raise_error=False)


@pytest.mark.gen_test(timeout=90)
async def test_failed_app_cases(prepare_send_file_request, http_client, routes):
    url = routes['app_list']()

    request_data = prepare_send_file_request('app_with_empty_file')
    response = await http_client.fetch(
        url, method='POST', raise_error=False, **request_data,
    )
    assert response.code == 400

    some_uid = 'abc'
    invalid_post_url = f'{url}{some_uid}'
    response = await http_client.fetch(
        invalid_post_url, method='POST', raise_error=False, **request_data
    )
    assert response.code == 400

    invalid_delete_url = routes['app_detail'](some_uid)
    response = await http_client.fetch(
        invalid_delete_url, method='DELETE', raise_error=False, request_timeout=90
    )
    assert response.code == 404

    request_data = prepare_send_file_request('app_with_missing_entrypoint')
    response = await http_client.fetch(
        url, method='POST', raise_error=False, **request_data,
    )
    assert response.code == 400

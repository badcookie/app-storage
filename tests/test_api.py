import json
from os import path

import pytest
from requests import Request
from server.settings import settings

TESTS_DIR = path.dirname(__file__)
FIXTURES_DIR = path.join(TESTS_DIR, 'fixtures')


@pytest.fixture
def routes(base_url):
    return {
        'index': lambda: f'{base_url}',
        'app_list': lambda: f'{base_url}/applications/',
        'app_detail': lambda app_id: f'{base_url}/applications/{app_id}',
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
    request_data = prepare_send_file_request('valid_app')
    assert request_data

    create_url = routes['app_list']()
    response = await http_client.fetch(
        create_url,
        method='POST',
        **request_data,
        raise_error=False,
        request_timeout=90,
    )
    assert response.code == 201

    response_body = response.body.decode()
    app_data = json.loads(response_body)

    app_port = app_data['port']
    app_url = f'http://localhost:{app_port}/'
    app_response = await http_client.fetch(app_url, method='GET', raise_error=False)
    response_data = app_response.body.decode()
    assert response_data == 'It works'

    app_id = app_data['id']
    app_uid = app_data['uid']

    app_path = path.join(settings.APPS_DIR, app_uid)

    repo = app.settings['repository']
    saved_app = await repo.get(id=app_id)
    assert saved_app and saved_app.port == app_port and saved_app.uid == app_uid

    assert path.exists(app_path)

    delete_url = routes['app_detail'](app_id)
    response = await http_client.fetch(delete_url, method='DELETE', raise_error=False)
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
    assert response.code == 500

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

import json
from os import path

import pytest
from requests import Request

TESTS_DIR = path.dirname(__file__)
FIXTURES_DIR = path.join(TESTS_DIR, 'fixtures')


@pytest.fixture
def routes(base_url):
    return {
        'app_create': lambda: f'{base_url}/application/',
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

        url = routes['app_create']()
        request = Request(url=url, files=files)
        prepared_request = request.prepare()
        content_type = prepared_request.headers.get('Content-Type')
        headers = {'Content-Type': content_type}

        return {
            'body': prepared_request.body,
            'headers': headers,
        }

    return _


@pytest.mark.usefixtures('unit_service', 'db_service')
@pytest.mark.gen_test(timeout=90)
async def test_successful_app_validation(
    prepare_send_file_request, http_client, routes, app,
):
    request_data = prepare_send_file_request('valid_app')
    assert request_data

    url = routes['app_create']()
    response = await http_client.fetch(
        url, method='POST', **request_data, raise_error=False, request_timeout=90,
    )
    assert response.code == 200

    response_body = response.body.decode()
    app_data = json.loads(response_body)

    app_port = app_data['port']
    app_url = f'http://localhost:{app_port}/'
    app_response = await http_client.fetch(app_url, method='GET', raise_error=False)
    response_data = app_response.body.decode()
    assert response_data == 'It works'

    repo = app.settings['app_repository']
    saved_app = await repo.get(id=app_data['id'])
    assert saved_app and saved_app.port == app_port and saved_app.uid == app_data['uid']


@pytest.mark.gen_test
async def test_failed_app_validation(prepare_send_file_request, http_client, routes):
    url = routes['app_create']()
    request_data = prepare_send_file_request('app_with_empty_file')
    response = await http_client.fetch(
        url, method='POST', raise_error=False, **request_data,
    )
    assert response.code == 500

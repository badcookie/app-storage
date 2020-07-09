import json
from os import path

import pytest
from requests import Request
from server.settings import settings

TESTS_DIR = path.dirname(__file__)
FIXTURES_DIR = path.join(TESTS_DIR, 'fixtures')


@pytest.fixture()
def unit_service(docker_client):
    image = docker_client.images.pull(settings.UNIT_IMAGE)
    volume = {settings.APPS_DIR: {'bind': '/apps/', 'mode': 'rw'}}
    command = f'unitd --no-daemon --control 127.0.0.1:{settings.UNIT_PORT}'

    container = docker_client.containers.create(
        image=image,
        network='host',
        command=command,
        volumes=volume,
        name='test_unit_service',
        auto_remove=True,
    )
    container.start()
    yield container
    container.stop()


@pytest.fixture
def routes(base_url):
    return {
        'app_create': lambda: f'{base_url}/create/',
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


@pytest.mark.usefixtures('unit_service')
@pytest.mark.gen_test(timeout=90)
async def test_successful_app_validation(
    prepare_send_file_request, http_client, routes,
):
    apps_count = 2
    request_data = prepare_send_file_request('valid_app')
    assert request_data

    url = routes['app_create']()
    for _ in range(apps_count):
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


@pytest.mark.gen_test
async def test_failed_app_validation(prepare_send_file_request, http_client, routes):
    url = routes['app_create']()
    request_data = prepare_send_file_request('app_with_empty_file')
    response = await http_client.fetch(
        url, method='POST', raise_error=False, **request_data,
    )
    assert response.code == 500

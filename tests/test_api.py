import json
import os

import docker
import pytest
from requests import Request
from src.consts import APPS_DIR
from src.validation import required_files

TESTS_DIR = os.path.dirname(__file__)
FIXTURES_DIR = os.path.join(TESTS_DIR, "fixtures")

# @pytest.fixture(scope='module')
# def docker_client():
#     return docker.from_env()
#
#
# @pytest.fixture(scope='module', autouse=True)
# def nginx_unit(docker_client):
#     containers = docker_client.containers.list()
#     runner_container = [
#         *filter(lambda item: 'runner' in item.name, containers)
#     ]
#     network = (
#         'host' if not runner_container
#         else f'container:/{runner_container[0].name}'
#     )
#
#     image = docker_client.images.pull('nginx/unit:1.15.0-python3.7')
#     container = docker_client.containers.create(
#         image=image, network=network, auto_remove=True
#     )
#     container.start()
#     yield container
#     container.stop()


@pytest.fixture
def app_creation_url(base_url):
    return f'{base_url}/create/'


@pytest.fixture
def prepare_send_file_request(get_package, app_creation_url):
    def _(filename: str):
        get_package(filename)

        filename_with_ext = f'{filename}.zip'
        filepath = os.path.join(FIXTURES_DIR, filename_with_ext)
        absolute_filepath = os.path.abspath(filepath)

        zipfile = open(absolute_filepath, 'rb')
        files = {'zipfile': zipfile}

        request = Request(url=app_creation_url, files=files)
        prepared_request = request.prepare()
        content_type = prepared_request.headers.get('Content-Type')
        headers = {"Content-Type": content_type}
        return {
            'body': prepared_request.body,
            'headers': headers,
        }

    return _


@pytest.mark.gen_test
async def test_simple_get_request(http_client, base_url):
    response = await http_client.fetch(f"{base_url}")
    assert response.code == 200
    data = response.body.decode()
    assert json.loads(data) == {"it": "works"}


@pytest.mark.gen_test
async def test_successful_app_validation(
        prepare_send_file_request,
        http_client,
        app_creation_url
):
    request_data = prepare_send_file_request('valid_app')
    response = await http_client.fetch(
        app_creation_url, method='POST', **request_data
    )
    assert response.code == 200

    app_id = response.body.decode()
    app_dir = os.path.join(APPS_DIR, app_id)
    assert os.path.exists(app_dir)

    files = os.listdir(app_dir)
    assert 'venv' in files
    files.remove('venv')
    assert files == required_files


@pytest.mark.gen_test
async def test_failed_app_validation(
        prepare_send_file_request,
        http_client,
        app_creation_url
):
    request_data = prepare_send_file_request('app_with_empty_file')
    response = await http_client.fetch(
        app_creation_url,
        method='POST',
        raise_error=False,
        **request_data
    )
    assert response.code == 500

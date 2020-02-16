import json

import docker
import pytest
from requests import Request

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


@pytest.mark.gen_test
async def test_simple_get_request(http_client, base_url):
    response = await http_client.fetch(f"{base_url}")
    assert response.code == 200
    data = response.body.decode()
    assert json.loads(data) == {"it": "works"}


@pytest.mark.gen_test
async def test_app_creation(get_package, http_client, base_url):
    url = f'{base_url}/create/'

    get_package('valid_app')
    zipfile = open('fixtures/valid_app.zip', 'rb')
    files = {'zipfile': zipfile}
    data = {}

    request = Request(url=url, files=files, data=data)
    prepare = request.prepare()
    content_type = prepare.headers.get('Content-Type')
    body = prepare.body
    headers = {
        "Content-Type": content_type,
    }

    response = await http_client.fetch(url, method='POST', body=body, headers=headers)
    assert response.code == 200
    assert response.body.decode() == 'OK'

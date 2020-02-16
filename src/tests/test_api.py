import json

import docker
import pytest
import requests

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
async def test_something(http_client, base_url):
    response = await http_client.fetch(f"{base_url}")
    assert response.code == 200
    data = response.body.decode()
    assert json.loads(data) == {"it": "works"}


# @pytest.mark.asyncio
# async def test_zip_request(get_package, client):
#     package = get_package('valid_app')
#
#     with open('fixtures/valid_app.zip', 'rb') as zipfile:
#         bytes_data = zipfile.read()
#
#     files = {'upload_file': bytes_data}
#     response = requests.post('http://localhost:8000/create/', files=files)
#     assert response.status_code == 200
#     assert 'OK' in response.text

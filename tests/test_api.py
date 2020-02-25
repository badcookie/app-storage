import json
from os import path

import docker
import pytest
from requests import Request
from src.consts import APPS_DIR, UNIT_IMAGE, UNIT_PORT

TESTS_DIR = path.dirname(__file__)
FIXTURES_DIR = path.join(TESTS_DIR, "fixtures")


@pytest.fixture(scope="module")
def docker_client():
    return docker.from_env()


@pytest.fixture()
def unit_service(docker_client):
    containers = docker_client.containers.list()
    runner_container = [*filter(lambda item: "runner" in item.name, containers)]
    network = (
        "host" if not runner_container else f"container:/{runner_container[0].name}"
    )
    image = docker_client.images.pull(UNIT_IMAGE)
    volume = {APPS_DIR: {"bind": "/apps/", "mode": "rw"}}
    command = f"unitd --no-daemon --control 127.0.0.1:{UNIT_PORT}"
    container = docker_client.containers.create(
        image=image,
        network=None,
        command=command,
        volumes=volume,
        name="test_unit_service",
        auto_remove=True,
    )
    container.start()
    yield container
    container.stop()


@pytest.fixture
def app_creation_url(base_url):
    return f"{base_url}/create/"


@pytest.fixture
def prepare_send_file_request(get_package, app_creation_url):
    def _(filename: str) -> dict:
        get_package(filename)

        filename_with_ext = f"{filename}.zip"
        filepath = path.join(FIXTURES_DIR, filename_with_ext)
        absolute_filepath = path.abspath(filepath)

        zipfile = open(absolute_filepath, "rb")
        files = {"zipfile": zipfile}

        request = Request(url=app_creation_url, files=files)
        prepared_request = request.prepare()
        content_type = prepared_request.headers.get("Content-Type")
        headers = {"Content-Type": content_type}
        return {
            "body": prepared_request.body,
            "headers": headers,
        }

    return _


@pytest.mark.gen_test
async def test_simple_get_request(http_client, base_url):
    response = await http_client.fetch(f"{base_url}")
    assert response.code == 200
    data = response.body.decode()
    assert json.loads(data) == {"it": "works"}


@pytest.mark.gen_test(timeout=30)
async def test_successful_app_validation(
    unit_service, prepare_send_file_request, http_client, app_creation_url,
):
    apps_count = 3
    request_data = prepare_send_file_request("valid_app")
    assert request_data

    for _ in range(apps_count):
        response = await http_client.fetch(
            app_creation_url, method="POST", **request_data, raise_error=False
        )
        print(unit_service.logs())
        assert response.code == 200

        response_body = response.body.decode()
        app_data = json.loads(response_body)

        app_port = app_data["port"]
        app_url = f"http://localhost:{app_port}/"
        app_response = await http_client.fetch(app_url, method="GET", raise_error=False)
        response_data = app_response.body.decode()
        assert response_data == "It works"


@pytest.mark.gen_test
async def test_failed_app_validation(
    prepare_send_file_request, http_client, app_creation_url
):
    request_data = prepare_send_file_request("app_with_empty_file")
    response = await http_client.fetch(
        app_creation_url, method="POST", raise_error=False, **request_data
    )
    assert response.code == 500

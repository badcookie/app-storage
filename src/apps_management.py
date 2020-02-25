import json
import os
from socket import AF_INET, SOCK_STREAM, socket

from src.consts import UNIT_PORT
from tornado.httpclient import AsyncHTTPClient

BASE_URL = f"http://localhost:{UNIT_PORT}/config"


client = AsyncHTTPClient()


def get_unused_port() -> int:
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


async def add_listener(app_id: str) -> int:
    """
    Делает запрос n/unit на добавление адреса, по
    которому будет доступно приложение.

    :param app_id: id приложения.
    :return: порт, который приложение будет слушать.
    """

    app_port = get_unused_port()
    url = f"{BASE_URL}/listeners/127.0.0.1:{app_port}/"
    listener_data = {"pass": f"applications/{app_id}"}
    request_body = json.dumps(listener_data)
    response = await client.fetch(
        url, body=request_body, method="PUT", raise_error=False
    )
    print(response.body.decode())
    return app_port


async def add_application(app_id: str) -> None:
    """
    Делает запрос n/unit на добавление приложения в конфигурацию.

    :param app_id: id приложения.
    """

    apps_dir = "/apps/"
    app_dir = os.path.join(apps_dir, app_id)
    venv_dir = os.path.join(app_dir, "venv")

    app_data = {
        "type": "python 3",
        "path": app_dir,
        "module": "application",
        "home": venv_dir,
    }
    request_body = json.dumps(app_data)
    url = f"{BASE_URL}/applications/{app_id}/"
    response = await client.fetch(
        url, body=request_body, method="PUT", raise_error=False
    )
    print(response.body.decode())


async def register_app(app_id: str) -> int:
    """
    Делает запрос n/unit на обновление конфигурации.

    :param app_id: id приложения.
    :return: порт, который приложение будет слушать.
    """

    await add_application(app_id)
    app_port = await add_listener(app_id)
    return app_port

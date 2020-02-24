import json
import os
from socket import AF_INET, SOCK_STREAM, socket

from src.consts import APPS_DIR, UNIT_PORT
from tornado.httpclient import AsyncHTTPClient

BASE_URL = f"http://localhost:{UNIT_PORT}/config"


client = AsyncHTTPClient()


def get_unused_port() -> int:
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


async def add_listener(app_id: str) -> int:
    app_port = get_unused_port()
    url = f"{BASE_URL}/listeners/127.0.0.1:{app_port}/pass"
    listener_pass = f"applications/{app_id}"
    await client.fetch(url, body=listener_pass, method="PUT", raise_error=False)
    return app_port


async def add_application(app_id: str) -> None:
    app_data = {
        "type": "python 3",
        "path": os.path.join(APPS_DIR, app_id),
        "module": "application",
    }
    request_body = json.dumps(app_data)
    url = f"{BASE_URL}/applications/{app_id}"
    response = await client.fetch(
        url, body=request_body, method="PUT", raise_error=False
    )
    print(response.body)


async def register_app(app_id: str) -> int:
    await add_application(app_id)
    app_port = await add_listener(app_id)
    return app_port


# curl -X PUT --data-binary @config.json --unix-socket
# /path/to/control.unit.sock http://localhost/config/listeners/127.0.0.1:8300

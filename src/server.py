import os
from io import BytesIO
from zipfile import ZipFile

from more_itertools import one
from src.environment import validate_package
from src.validation import VALIDATION_RULES
from tornado.httputil import HTTPServerRequest
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

APP_PORT = os.environ.get("APP_PORT", 8000)


def get_request_file(request: "HTTPServerRequest") -> "ZipFile":
    files = request.files
    file_data = one(files.get("zipfile"))
    file_body = file_data["body"]
    return ZipFile(BytesIO(file_body), "r")


class BaseHandler(RequestHandler):
    async def get(self):
        await self.finish({"it": "works"})


class ApplicationsHandler(RequestHandler):
    async def post(self):
        file = get_request_file(self.request)
        validate_package(file, VALIDATION_RULES)
        # files = file.namelist()
        self.write("OK")


def make_app():
    return Application([(r"/", BaseHandler), (r"/create/", ApplicationsHandler),])


if __name__ == "__main__":
    app = make_app()
    app.listen(APP_PORT)
    IOLoop.current().start()

import os

from lib.environment import create_application_environment, validate_package
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

APP_PORT = os.environ.get("APP_PORT", 8000)


def get_package_from_request(request):
    pass


class BaseHandler(RequestHandler):
    async def get(self):
        await self.finish({"it": "works"})


class ApplicationsHandler(RequestHandler):
    async def post(self):
        files = self.request.files
        await self.finish(files)


def make_app():
    return Application([(r"/", BaseHandler), (r"/create/", ApplicationsHandler),])


if __name__ == "__main__":
    app = make_app()
    app.listen(APP_PORT)
    IOLoop.current().start()

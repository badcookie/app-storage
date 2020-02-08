import os
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler


APP_PORT = os.environ.get('APP_PORT', 8000)


class MainHandler(RequestHandler):
    def get(self):
        self.write("Hello, world")


def make_app():
    return Application([
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(APP_PORT)
    IOLoop.current().start()

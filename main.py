from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from motor.motor_tornado import MotorClient


class MainHandler(RequestHandler):
    async def get(self):
        db = self.settings['db']
        apps = db.apps
        document = {'key': 'value'}
        result = await apps.insert_one(document)
        print('result %s' % repr(result.inserted_id))
        self.write("Hello, world")


def make_app():
    db_client = MotorClient('localhost', 27017)
    db = db_client.apps

    return Application([
        (r"/", MainHandler),
    ], db=db)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    loop = IOLoop.current()
    loop.start()

import logging.config

from server.app import make_app
from server.settings import settings
from tornado.ioloop import IOLoop

logging.config.dictConfig(settings.logging)
logger = logging.getLogger('app')


if __name__ == '__main__':
    app = make_app()

    try:
        app.listen(settings.APP_PORT)
        logger.info('Server started on port %s', settings.APP_PORT)
        IOLoop.current().start()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Server graceful shutdown')

import os

from flask import Flask

application = Flask(__name__)


@application.route('/', methods=['GET'])
def hello_world():
    test_env = os.getenv('TEST_ENV', 1)
    return str(test_env)


@application.route('/books/<int:book_id>/', methods=['GET', 'DELETE'])
def some_handler(book_id):
    return str(book_id)

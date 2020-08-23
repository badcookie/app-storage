from flask import Flask

application = Flask(__name__)


@application.route('/', methods=['GET'])
def hello_world():
    return 'It works too'

@application.route('/books/<int:book_id>/', methods=['GET', 'DELETE'])
def some_handler(book_id)
   return book_id

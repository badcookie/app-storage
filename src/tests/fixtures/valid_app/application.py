from flask import Flask

application = Flask(__name__)


@application.route("/some_path", methods=["GET"])
def hello_world():
    return "It works"

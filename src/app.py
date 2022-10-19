from dotenv import load_dotenv
from flask import Flask, jsonify, make_response
from flask_cors import CORS

from src.controllers import blp_aws_exam
from src.controllers.comments_controller import blp_comments
from src.controllers.questions_controller import blp_questions
from src.controllers.users_controller import blp_users

load_dotenv()

app = Flask(__name__)
cors = CORS(app)


app.register_blueprint(blp_aws_exam, url_prefix="/aws")
app.register_blueprint(blp_comments, url_prefix="/aws")
app.register_blueprint(blp_questions, url_prefix="/aws")
app.register_blueprint(blp_users, url_prefix="/aws")


@app.route("/")
def hello():
    return jsonify(message='Hello!')


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)


def internal_server_error(e):
    print(e)
    return 'error', 500


app.register_error_handler(500, internal_server_error)

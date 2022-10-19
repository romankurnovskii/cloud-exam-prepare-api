from flask import Blueprint, request,  jsonify

from src.common.configs import ResponseStatus
from src.common.verify_token import token_required
from src.db.mongo import db_aws_questions
from src.services.users_service import get_user_info, get_progress_data, update_user_data

users_collection = db_aws_questions.users
questions_collection = db_aws_questions.questions

from . import blp_aws_exam


blp_users = Blueprint('users', __name__)


@blp_users.route("/getProgressData", methods=["POST"])
@token_required
def get_progress_data_handler(token_data):
    return get_progress_data(token_data)


@blp_users.route("/getUserInfo", methods=["POST"])
@token_required
def get_user_info_handler(token_data):
    user = get_user_info(token_data)
    if user:
        return jsonify({
            "data": user,
            "status": ResponseStatus.SUCCESS.name
        }), 200
    return jsonify({
          "error": "User not found",
            "status": ResponseStatus.ERROR.name
        }), 400


@blp_users.route("/updateUserData", methods=["POST"])
@token_required
def update_user_data_handler(token_data):
    return update_user_data(token_data)

from flask import Blueprint,  request, jsonify

from src.common.configs import ResponseStatus
from src.services.exams_service import add_exam, get_exams_list

from . import blp_aws_exam
from src.common.verify_token import if_authorized, token_required
from src.services.questions_service import add_user_answer, get_question, get_random_question, put_question, sync_questions_with_local_db


blp_exams = Blueprint('exams', __name__)


@blp_exams.route("/getExams", methods=["GET"])
@if_authorized
def get_exams_handler(token_data):
    ''' Get list of exams '''
    exams = get_exams_list()
    return jsonify({"status": ResponseStatus.SUCCESS.name, 'data': exams})

@blp_exams.route("/addExam", methods=["POST"])
@token_required
def add_exam_handler(token_data):
    payload = request.get_json()
    can_add_questions = token_data["data"].get("canAddQuestions")
    if not can_add_questions:
        return {
            "error": "Account dos not have permissions to add questions",
            "status": ResponseStatus.ERROR.name,
            "a":token_data
        }, 400
    code = payload.get("code")
    name = payload.get("name")
    free = payload.get("free", False)
    if not code or not name:
        return {
            "error": "Missing required fields",
            "status": ResponseStatus.ERROR.name
        }, 400
    return add_exam(code, name, free)

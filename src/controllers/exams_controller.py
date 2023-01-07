from flask import Blueprint,  request, jsonify

from src.common.configs import ResponseStatus
from src.services.exams_service import add_exam, get_exams_list

from src.common.verify_token import token_required


blp_exams = Blueprint('exams', __name__)


@blp_exams.route("/getExams", methods=["GET"])
def get_exams_handler():
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

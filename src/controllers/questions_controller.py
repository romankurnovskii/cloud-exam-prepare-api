from flask import Blueprint,  request, jsonify

from src.common.configs import ResponseStatus

from src.common.verify_token import if_authorized, token_required
from src.services.questions_service import add_user_answer, get_question, get_random_question, put_question, sync_questions_with_local_db


blp_questions = Blueprint('questions', __name__)


@blp_questions.route("/getQuestion", methods=["POST"])
@if_authorized
def get_question_handler(token_data):
    payload = request.get_json() or {}
    question_id = payload.get('question_id')
    if not question_id:
        return {}  # TODO
    q = get_question(question_id)
    return jsonify({"status": ResponseStatus.SUCCESS.name, 'data': q})


@blp_questions.route("/getRandomQuestion", methods=["POST"])
@if_authorized
def get_randon_question_handler(token_data):
    '''
        return example:
            {
            "data": {
                "_id": "631039603414ee7d8a9c33b8",
                "answers": [
                    {
                        "id": 2,
                        "text": "214234"
                    }
                ],
                "correct_answers": [
                    1,
                    2
                ],
                "correct_answers_count": 2,
                "explanation": "str",
                "publish_date": "Thu, 01 Sep 2022 07:47:28 GMT",
                "exam_code": "AWS-DVS-C02",
                "question_text": "str"
            },
            "questionsCount": 3
            }
    '''
    exam_code = token_data['payload'].get('exam_code')
    return get_random_question(token_data, exam_code)


@blp_questions.route("/addNewQuestion", methods=["POST"])
@token_required
def put_question_handler(token_data):
    payload = request.get_json()
    return put_question(token_data, payload)


@blp_questions.route("/addAnswer", methods=["POST"])
@if_authorized
def add_user_answer_handler(token_data):
    payload = request.get_json()
    return add_user_answer(token_data, payload)


@blp_questions.route("/syncQuestions", methods=["POST"])
@token_required
def sync_questions_with_local_db_handler(token_data):
    return sync_questions_with_local_db(token_data)

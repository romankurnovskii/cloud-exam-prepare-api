from bson.objectid import ObjectId
from datetime import datetime as dt
from flask import request, jsonify
from pymongo.collection import Collection

from src.common.configs import ResponseStatus
from src.db.aws_exam_schema import AwsExamValidator
from src.db.mongo import db_aws_questions
from src.services.questions_service import get_question, update_question
from src.services.users_service import get_user_info

users_collection = db_aws_questions.users
questions_collection: Collection[AwsExamValidator] = db_aws_questions.questions


def add_comment(verify_data, payload):
    user_info = get_user_info(verify_data)
    if user_info.get('status') == ResponseStatus.ERROR.name:
        return {
            "error": user_info.get('error', "User not found"),
            "status": ResponseStatus.ERROR.name,
        }, 401

    question_id = payload['question_id']
    comment = {
        'user_id': user_info['_id'],
        'comment': payload['comment'],
        'publish_date': dt.now()
    }
    questions_collection.find_one_and_update({'_id': ObjectId(question_id)}, {'$push': {'comments': comment}})
    return {"status": "success"}

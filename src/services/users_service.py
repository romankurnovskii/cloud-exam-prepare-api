
from bson.objectid import ObjectId
from flask import request, jsonify
from pymongo.collection import Collection

from src.common.configs import ResponseStatus
from src.db.aws_exam_schema import AwsExamValidator
from src.db.mongo import db_aws_questions

users_collection = db_aws_questions.users
questions_collection = db_aws_questions.questions


def get_user_info(token_data):
    is_valid = token_data.get("is_valid")
    if not is_valid:
        return {"error": "Invalid token", "status": ResponseStatus.ERROR.name}
    # TODO refactor to separate func / added to token _reqeured
    user_sub = token_data["data"].get("sub")
    try:
        user = users_collection.find_one({"sub": user_sub})
        if user is None:
            user = users_collection.insert_one({
                "sub":
                user_sub,
                "name":
                token_data["data"].get("name"),
                "email":
                token_data["data"].get("email"),
                "progress": {
                    "questions_answered": 0,
                    "questions_correct": 0,
                    "questions_wrong": 0,
                    "questions": {},
                },
            })
            user = users_collection.find_one({"sub": user_sub})
            if user is None:
                return None
        data = {
            '_id': str(user.get('_id')),
            "name": user.get("name"),
            "email": user.get("email"),
            "progress": user.get("progress"),
        }
        if user.get("canAddQuestions"):
            data["canAddQuestions"] = True
        
        return data
    except Exception:
        return None


def update_user_data(verify_data):
    ''' update username '''
    is_valid = verify_data.get("is_valid")
    if not is_valid:
        return {"error": "Invalid token", "status": ResponseStatus.ERROR.name}

    user_sub = verify_data["data"].get("sub")
    payload = request.get_json()
    name = payload["name"]
    if name:
        result = users_collection.update_one(
            {
                "sub": user_sub,
                "name": {
                    "$ne": name
                }
            }, {"$set": {
                "name": name
            }})
        return jsonify({"status": ResponseStatus.SUCCESS.name}), 201


def get_progress_data(token_data):
    is_valid = token_data.get("is_valid")
    if not is_valid:
        return {"error": "Invalid token", "status": ResponseStatus.ERROR.name}
    user_sub = token_data["data"].get("sub")

    try:
        user = users_collection.find_one({"sub": user_sub})
        if user is None:
            return {
                "error": "User not found",
                "status": ResponseStatus.ERROR.name
            }, 401
        return jsonify({"data": user.get("progress")})
    except Exception:
        return {"error": "User not found"}, 401


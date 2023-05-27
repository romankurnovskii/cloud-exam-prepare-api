from pymongo.collection import Collection

from src.common.configs import ResponseStatus
from src.db.aws_exam_schema import QuestionDataType, MetaDataType, MetaDataValidator
from src.db.mongo import db_aws_questions


users_collection = db_aws_questions.users
questions_collection: Collection[QuestionDataType] = db_aws_questions.questions
meta_data_collection: Collection[MetaDataValidator] = db_aws_questions.meta


# -------- EXAM


def get_exams_list():
    meta_data = meta_data_collection.find_one({"type": MetaDataType.EXAMS.value})
    exams = meta_data.get("exams", [])
    return exams


def get_exam_metadata(exam_code):
    exams = get_exams_list()
    exam = list(filter(lambda x: (x["code"] == exam_code), exams))

    if not exam:
        return False, ResponseStatus.EXAM_NOT_FOUND
    return True, exam[0]


def add_exam(code, name, free=False):
    result = meta_data_collection.find_one_and_update(
        {"type": MetaDataType.EXAMS.value},
        {"$push": {"exams": {"code": code, "name": name, "free": free}}},
    )
    return {"status": "success", "id": str(result)}

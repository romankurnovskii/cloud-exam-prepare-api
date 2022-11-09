from bson.objectid import ObjectId
from datetime import datetime as dt
from flask import jsonify
from pymongo.collection import Collection

from src.common.configs import ExamSubscriptions, ResponseStatus
from src.common.validator import is_view_exam_alowed
from src.db.aws_exam_schema import QuestionDataType, MetaDataType, MetaDataValidator
from src.db.mongo import db_aws_questions

users_collection = db_aws_questions.users
questions_collection: Collection[QuestionDataType] = db_aws_questions.questions
meta_data_collection: Collection[MetaDataValidator] = db_aws_questions.meta


# TODO add specific to exam code metadata
def _get_meta_data():
    return meta_data_collection.find_one({"type": MetaDataType.QUESTIONS.name})


def update_meta_data():
    ''' update last update date '''
    meta_data_collection.find_one_and_update(
        {"type": MetaDataType.QUESTIONS.name},
        {'$set': {
            'last_updated': dt.now()
        }},
        upsert=True)


def get_exam_code_metadata(exam_code):
    exams = get_exams_list()
    exam = list(filter(lambda x: (x['code'] == exam_code),exams))

    if not exam:
        return False, ResponseStatus.EXAM_NOT_FOUND
    return True, exam[0]


def get_exams_list():
    meta_data = meta_data_collection.find_one(
        {"type": MetaDataType.EXAMS.value})
    exams = meta_data.get('exams', [])
    return exams


def get_question(question_id):
    q = questions_collection.find_one({"_id": ObjectId(question_id)})
    if q:
        q['_id'] = str(q['_id'])
    return q


def get_random_question(token_data=None, exam_code=None) -> QuestionDataType:
    """
    return:
    {
        data: {
            question... },
        questionsCount: number
    }
    """
    if not exam_code:
        #TODO
        exam_code = ExamSubscriptions.AWS_DVA_C02.value
        # response = jsonify({
        #             "error": True,
        #             "message": "Exam code is not provided"
        #         })
        #         return response, 400
    else:
        found, exam_data = get_exam_code_metadata(exam_code)
        if not found:
            response = jsonify({
                "error": True,
                "message": "Exam code not found"
            })
            return response, 400
        if not exam_data['free']:
            # TODO
            alowed = is_view_exam_alowed(token_data, exam_code)
            if not alowed:
                response = jsonify({
                    "error": True,
                    "message": "Exam is not free"
                })
                return response, 400
    

    
    questions = list(questions_collection.aggregate([
        {"$match": {"exam_code": {"$eq": exam_code}}},
        {"$sample": {"size": 1}}
    ]))


    question = None
    if questions:
        question = questions[0]
    else:
        response = jsonify({
            "error": True,
            "message": "No questions found"
        })
        return response, 400

    count = questions_collection.count_documents({
        "exam_code": {"$eq": exam_code}
    })

    question_response = {}
    if question:
        question_response["_id"] = str(question["_id"])
        question_response['exam_code'] = question.get('exam_code')
        question_response['question_text'] = question.get('question_text')
        question_response['correct_answers_count'] = question.get(
            'correct_answers_count')
        question_response['answers'] = question.get('answers')
        question_response['comments'] = question.get('comments', [])

    meta_data = _get_meta_data()
    if meta_data:
        last_updated = meta_data.get('last_updated', '2022')
    response = jsonify({
        "data": question_response,
        "questions_count": count,
        'last_updated': last_updated
    })
    return response


def put_question(token_data, payload):
    ''' Create new question '''
    can_add_questions = token_data["data"].get("canAddQuestions")
    if not can_add_questions:
        return {
            "error": "Account dos not have permissions to add questions",
            "status": ResponseStatus.ERROR.name,
        }, 401

    question_data = {}
    for k in QuestionDataType.__annotations__.keys():
        try:
            question_data[k] = payload[k]
        except Exception as e:
            print('no key', e)

    question_data['publish_date'] = dt.now()
    result = questions_collection.insert_one(question_data)
    update_meta_data()
    return {"status": "success", 'id': str(result.inserted_id)}


def update_question(question):
    question_id = question['_id']
    res = questions_collection.find_one_and_update(
        {'_id': ObjectId(question_id)}, question)
    if res:
        update_meta_data()
    return res


def add_user_answer(verify_data, payload):
    user = None
    question_id = payload.get("question_id")
    answers_id = payload.get("answers_id")
    if not all([question_id, answers_id]):
        return jsonify({
            "status": ResponseStatus.ERROR.name,
            "message": "wrong data"
        })

    question = questions_collection.find_one({"_id": ObjectId(question_id)})
    if not question:
        return jsonify({
            "status": ResponseStatus.ERROR.name,
            "message": "wrong data (maybe question not found)"
        })

    is_valid = verify_data.get("is_valid")
    if is_valid:
        user_sub = verify_data["data"].get("sub")
        user = users_collection.find_one({"sub": user_sub})

    correct_answers = question["correct_answers"]
    is_correct = set(answers_id) == set(correct_answers)
    explanation = {}

    if user and is_valid:
        explanation = question.get("explanation", {})  # only for registered

        # update user's progress data
        progress = user.get("progress")
        question = progress["questions"].get(question_id)
        # if already answered
        questions_correct = progress["questions_correct"]
        questions_wrong = progress["questions_wrong"]
        if question is None:
            progress["questions_answered"] += 1
            if is_correct:
                questions_correct += 1
            else:
                questions_wrong += 1
        else:
            # prev result answer: boolean
            if question:  # was answered correct
                if not is_correct:
                    questions_correct -= 1
                    questions_wrong += 1
            else:  # was incorrect before
                if is_correct:
                    questions_correct += 1
                    questions_wrong -= 1

        progress["questions"][question_id] = is_correct
        progress["questions_correct"] = questions_correct
        progress["questions_wrong"] = questions_wrong

        users_collection.update_one(
            {"sub": user_sub},
            {"$set": {
                "progress": progress
            }},
        )

    return jsonify({
        "status": ResponseStatus.SUCCESS.name,
        'is_answer_correct': is_correct,
        "correct_answers": correct_answers,
        'explanation': explanation
    })


def _convert_udemy_to_question_data(question):

    id = question['id']
    udemy_answers = question['prompt']['answers']
    udemy_explanation = question['prompt']['explanation']
    udemy_question_text = question['prompt']['question']
    udemy_correct_answers = question['correct_response']

    meta = {
        'source': 'udemy',
        'id': id,
    }
    answers = []
    for i, ans in enumerate(udemy_answers):
        answer = {'id': i + 1, 'text': ans}
        answers.append(answer)
    explanation = {'id': 1, 'description': udemy_explanation}
    correct_answers = []
    for a in udemy_correct_answers:
        if a == 'a':
            correct_answers.append(1)
        elif a == 'b':
            correct_answers.append(2)
        elif a == 'c':
            correct_answers.append(3)
        elif a == 'd':
            correct_answers.append(4)
        elif a == 'e':
            correct_answers.append(5)
        elif a == 'f':
            correct_answers.append(6)
        else:
            raise Exception('Unknown answer:', question)

    question_data = {
        'question_text': udemy_question_text,
        'answers': answers,
        'explanation': explanation,
        'correct_answers_count': len(correct_answers),
        'correct_answers': correct_answers,
        'meta': meta
    }

    return question_data


def _convert_old_to_question_data(q):
    for a in q['answers']:
        a['text'] = a.pop('description')

    question_data = {
        'question_text': q['description'],
        'answers': q['answers'],
        'explanation': q['explanation'],
        'correct_answers_count': q['correct_answers_count'],
        'correct_answers': q['correct_answers']
    }


def sync_questions_with_local_db(token_data):
    # define source
    can_add_questions = token_data["data"].get("canAddQuestions")

    # if not can_add_questions:
    #     return {
    #         "error": "Account dos not have permissions to add questions",
    #         "status": ResponseStatus.ERROR.name,
    #     }, 401

    def insert_to_db(question_data):
        questions_collection.insert_one(question_data)

    import json
    file_name = 'src/services/q.json'
    with open(file_name, 'r') as f:
        z = json.load(f)

        data = z['data']
        for q in data:
            # _convert_old_to_question_data(q)
            question_data = _convert_udemy_to_question_data(q)
            question_data['publish_date'] = dt.now()

            # insert_to_db(question_data)
        update_meta_data()
        return z

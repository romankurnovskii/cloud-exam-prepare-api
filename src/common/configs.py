from enum import Enum


class ResponseStatus(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    EXAM_NOT_FOUND = "EXAM_NOT_FOUND"


class ExamCodes(Enum):
    # not used currently
    # mongo_collection not in use. All questions within question collection
    AWS_CLOUD_PRACTITIONER = {
        "exam_code": "AWS_CLF_C01",
        "title": "AWS Certified Cloud Practitioner",
        "mongo_collection": 'questions-aws-clf-c01'
    }
    AWS_DEVELOPER_ASSOCIATE = {
        "exam_code": "AWS_DVA_C02",
        "title": "AWS Certified Developer - Associate",
        "mongo_collection": 'questions'
    }
    AWS_SOLUTIONS_ARCHITECT_ASSOCIATE = {
        "exam_code": "AWS_SAA_C03",
        "title": "AWS Certified Solutions Architect - Associate",
        "mongo_collection": 'questions-aws-saa-co3'
    }
    AWS_SOLUTIONS_ARCHITECT_PROFESSIONAL = {
        "exam_code": "AWS_SAP_C02",
        "title": "AWS Certified Solutions Architect - Professional",
        "mongo_collection": 'questions-aws-sap-co2'
    }

class ExamSubscriptions(Enum):
    ALL = "ALL"
    AWS_CLF_C01 = "AWS_CLF_C01"
    AWS_DVA_C02 = "AWS_DVA_C02"
    AWS_SAA_C03 = "AWS_SAA_C03"
    AWS_SAP_C02 = "AWS_SAP_C02"


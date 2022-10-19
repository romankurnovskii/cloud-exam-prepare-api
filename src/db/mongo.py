import os

from pymongo import MongoClient

MONGO_CONNECTION_STRING = os.environ.get(
    "MONGO_CONNECTION_STRING", default="mongodb://localhost:27017/"
)
MONGO_COLLECTION_AWS_QUESTIONS = os.environ.get(
    "MONGO_COLLECTION_AWSQUESTIONS", default="test-awsquestions"
)


db_client_aws_questions = MongoClient(MONGO_CONNECTION_STRING)
db_aws_questions = db_client_aws_questions[MONGO_COLLECTION_AWS_QUESTIONS]

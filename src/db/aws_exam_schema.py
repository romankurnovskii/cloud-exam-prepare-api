from datetime import datetime as dt
import enum
from typing import TypedDict


class AnswerType(TypedDict):
    id: int
    text: str


class CommentType(TypedDict):
    date: dt
    text: str
    # link: NotRequired[str]


class QuestionExplanationType(TypedDict):
    id: int
    description: str
    author: str


class AwsExamValidator(TypedDict):
    """
    more info:
        - https://peps.python.org/pep-0589/
        - https://pymongo.readthedocs.io/en/stable/examples/type_hints.html#typed-collection
    """
    question_text: str
    correct_answers_count: int
    correct_answers: list[int]
    answers: list[AnswerType]
    explanation: QuestionExplanationType
    publish_date: dt
    comments: list[CommentType]


class MetaDataType(enum.Enum):
    QUESTIONS = 'QUESTIONS'


class MetaDataValidator(TypedDict):
    type: MetaDataType
    last_updated: dt
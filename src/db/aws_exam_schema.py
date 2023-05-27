from datetime import datetime as dt
import enum
from typing import List, Optional, TypedDict

from src.common.configs import ExamSubscriptions


class MetaDataType(enum.Enum):
    QUESTIONS = "QUESTIONS"
    EXAMS = "EXAMS"


class MetaDataExamType(TypedDict):
    code: ExamSubscriptions  ## TODO remove 'ALL' from list
    name: str
    free: bool


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


class QuestionDataType(TypedDict):
    """
    more info:
        - https://peps.python.org/pep-0589/
        - https://pymongo.readthedocs.io/en/stable/examples/type_hints.html#typed-collection
    """

    exam_code: str
    question_text: str
    correct_answers_count: int
    correct_answers: list[int]
    answers: list[AnswerType]
    explanation: QuestionExplanationType
    publish_date: dt
    comments: list[CommentType]


class ExamProgressType(TypedDict):
    exam_code: str
    questions_answered: int
    questions_correct: int
    questions_wrong: int


class UserProgressType(TypedDict):
    questions_answered: int
    questions_correct: int
    questions_wrong: int
    questions: int
    by_exam: List[ExamProgressType]


class UserType(TypedDict):
    sub: str
    name: str
    email: str
    progress: UserProgressType
    canAddQuestions: Optional[bool]
    subscriptions: Optional[List[str]]  # ExamSubscriptions


class MetaDataValidator(TypedDict):
    type: MetaDataType
    last_updated: dt

from typing import TypedDict
from bson import ObjectId

from app.shared.constants import AnswerOptionKeys

__all__ = ['Questions', 'Topics', 'Answers']


class Options(TypedDict):
    _id: ObjectId
    title: str
    key: AnswerOptionKeys


class Questions(TypedDict):
    _id: ObjectId
    title: str
    options: Options[str]
    tags: str
    is_active: bool
    topic_id: str
    answer: str


class Topics(TypedDict):
    _id: ObjectId
    name: str


class Answers(TypedDict):
    _id: ObjectId
    question_id: str
    correct_option: AnswerOptionKeys

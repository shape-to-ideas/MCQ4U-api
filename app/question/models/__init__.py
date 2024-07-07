from typing import TypedDict

from app.shared.constants import AnswerOptionKeys

__all__ = ['Questions', 'Topics', 'Answers']


class Options(TypedDict):
    title: str
    key: AnswerOptionKeys


class Questions(TypedDict):
    title: str
    options: Options[str]
    tags: str
    is_active: bool
    topic_id: str
    answer: str


class Topics(TypedDict):
    name: str


class Answers(TypedDict):
    question_id: str
    correct_option: AnswerOptionKeys

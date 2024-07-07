from typing import TypedDict
from bson import ObjectId

from app.shared.constants import AnswerOptionKeys

__all__ = ['Users']


class AttemptedQuestions(TypedDict):
    question_id: ObjectId
    selected_option: AnswerOptionKeys


class Users(TypedDict):
    _id: ObjectId
    email: str
    phone: str
    first_name: str
    password: str
    last_name: str
    is_admin: bool
    attempted_questions: AttemptedQuestions

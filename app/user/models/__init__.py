from typing import TypedDict
from bson import ObjectId

from app.shared.constants import AnswerOptionKeys

__all__ = ['Users', 'AttemptedQuestions']


class AttemptedQuestions(TypedDict):
    _id: ObjectId
    question_id: ObjectId
    selected_option: AnswerOptionKeys
    user_id: ObjectId


class Users(TypedDict):
    _id: ObjectId
    email: str
    phone: str
    first_name: str
    password: str
    last_name: str
    is_admin: bool
    attempted_questions: AttemptedQuestions

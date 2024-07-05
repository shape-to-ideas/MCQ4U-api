from pydantic import BaseModel, UUID4, Field

from app.shared.constants import AnswerOptionKeys

__all__ = ['Users']


class AttemptedQuestions:
    question_id: UUID4
    selected_option: AnswerOptionKeys


class Users(BaseModel):
    _id: UUID4
    email: str
    phone: str
    first_name: str
    password: str
    last_name: str
    is_admin: bool = Field(default=False)
    attempted_questions: AttemptedQuestions

from pydantic import BaseModel, UUID4, Field
from typing import TypedDict

from app.shared.constants import AnswerOptionKeys

__all__ = ['Questions', 'Topics', 'Answers']


# class Questions(BaseModel):
#     title: str
#     options: [str]
#     tags: str
#     is_active: bool = Field(default=True)
#     topic_id: UUID4


class Topics(TypedDict):
    name: str

# class Answers(BaseModel):
#     question_id: UUID4
#     correct_option: AnswerOptionKeys

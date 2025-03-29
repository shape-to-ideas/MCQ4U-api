from typing import List
from dataclasses import dataclass
from pydantic import BaseModel

from app.shared.constants import AnswerOptionKeys

__all__ = ['CreateQuestionsDto', 'CreateTopicsDto', 'Options', 'QuestionPayload']


@dataclass
class Options(BaseModel):
    title: str
    key: AnswerOptionKeys


@dataclass
class QuestionPayload:
    title: str
    options: list[Options]
    tags: str
    is_active: bool
    topic_id: str
    answer: AnswerOptionKeys


@dataclass
class CreateQuestionsDto(BaseModel):
    data: List[QuestionPayload]


@dataclass
class CreateTopicsDto:
    topic_names: List[str]

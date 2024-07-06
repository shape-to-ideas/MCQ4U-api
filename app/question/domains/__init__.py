from typing import List
from dataclasses import dataclass
from pydantic import BaseModel

__all__ = ['CreateQuestionsDto', 'CreateTopicsDto', 'Options']


@dataclass
class Options(BaseModel):
    title: str
    key: str


@dataclass
class CreateQuestionsDto(BaseModel):
    title: str
    options: list[Options]
    tags: str
    is_active: bool
    topic_id: str


@dataclass
class CreateTopicsDto:
    topic_names: List[str]

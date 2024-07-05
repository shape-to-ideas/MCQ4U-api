from litestar import Controller, post
from typing import Annotated
from litestar.params import Body
from litestar.di import Provide
from app.question.domains import CreateQuestionsDto, CreateTopicsDto
from app.question.services import QuestionService

__all__ = [
    'QuestionController',
]


class QuestionController(Controller):
    tags = ['Question']
    dependencies = {
        "question_service": Provide(QuestionService, sync_to_thread=False),
    }

    signature_namespace = {
        "QuestionService": QuestionService,
    }

    @post('/questions/create', sync_to_thread=False)
    def create_question(
            self,
            data: Annotated[CreateQuestionsDto, Body(title="Create Question", description="Create a new question.")],
            question_service: QuestionService,
    ) -> str:
        return question_service.create_question(question_dto=data)

    @post('/questions/topics', sync_to_thread=False)
    def create_topic(
            self,
            data: Annotated[CreateTopicsDto, Body(title="Create Topics", description="Create topics")],
            question_service: QuestionService,
    ) -> str:
        return question_service.create_topics(topics_dto=data)

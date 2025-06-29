from litestar import Controller, post, get
from typing import Annotated, Any
from litestar.params import Body
from litestar.di import Provide
from litestar.types import Scope

from app.question.domains import CreateQuestionsDto, CreateTopicsDto
from app.question.services import QuestionService
from app.shared.middlewares import AuthorizationMiddleware

__all__ = [
    'QuestionController',
]


class QuestionController(Controller):
    tags = ['Question']
    dependencies = {
        'question_service': Provide(QuestionService, sync_to_thread=False),
    }

    signature_namespace = {
        'QuestionService': QuestionService,
    }

    @post(
        '/questions/create', middleware=[AuthorizationMiddleware], sync_to_thread=False
    )
    def create_question(
            self,
            data: Annotated[
                CreateQuestionsDto,
                Body(title='Create Question', description='Create a new question.'),
            ],
            question_service: QuestionService,
            scope: Scope,
    ) -> Any:
        return question_service.create_question(data, scope)

    @post(
        '/questions/topics', middleware=[AuthorizationMiddleware], sync_to_thread=False
    )
    def create_topic(
            self,
            data: Annotated[
                CreateTopicsDto, Body(title='Create Topics', description='Create topics')
            ],
            question_service: QuestionService,
            scope: Scope,
    ) -> Any:
        return question_service.create_topics(data, scope)

    # @TODO fix return type for all
    @get('/questions', middleware=[AuthorizationMiddleware], sync_to_thread=False)
    def get_questions(
            self,
            question_id: str,
            topic_id: str,
            is_active: str,
            question_service: QuestionService,
    ) -> Any:
        return question_service.get_questions(
            question_id=question_id, topic_id=topic_id, is_active=is_active
        )

    @get('/topics', middleware=[AuthorizationMiddleware], sync_to_thread=False)
    def get_topics_list(self, question_service: QuestionService) -> Any:
        return question_service.get_topics_list()
